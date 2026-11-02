"""Casos de uso de M02: formato, coherencia de titularidad, tara, alta desde el
registro, baja lógica, reactivación y auditoría."""

from decimal import Decimal

import pytest
from django.utils import timezone

from apps.auditoria.models import EventoAuditoria
from apps.catalogo.models import TipoMineral, Vehiculo
from apps.catalogo.services import tipos_mineral, transportistas, vehiculos
from apps.catalogo.services.validadores import validar_placa
from apps.ingresos.tests.factories import IngresoFactory
from common.excepciones import ConflictoDeConcurrencia, ErrorDeValidacionDeDominio

from .factories import TipoMineralFactory, TransportistaFactory, VehiculoFactory

pytestmark = pytest.mark.django_db

PROPIO = {"tipo_titularidad": "PROPIO", "capacidad_tn": Decimal("20.00")}


def _rechazo(fn, *args, **kwargs) -> str:
    with pytest.raises(ErrorDeValidacionDeDominio) as exc:
        fn(*args, **kwargs)
    return str(exc.value)


@pytest.mark.parametrize("placa", ["ABC-123", "V2K-841", "C9K-741", "e4r-208"])
def test_rn_m02_01_placas_validas_de_la_maqueta(placa):
    assert validar_placa(placa) == placa.upper()


def test_rn_m02_01_el_patron_de_placa_se_cambia_por_configuracion(settings):
    settings.PATRON_PLACA = r"^[A-Z]{3}-\d{3}$"
    assert validar_placa("ABC-123") == "ABC-123"
    assert _rechazo(validar_placa, "C9K-741") == "El formato de la placa no es válido"


@pytest.mark.parametrize("placa", ["1234", "ABC123", "AB-1234", "ABC-12", "AB C-123"])
def test_rn_m02_01_placas_con_formato_invalido(placa):
    assert _rechazo(validar_placa, placa) == "El formato de la placa no es válido"


def test_rn_m02_01_placa_duplicada_es_rechazada(administrador):
    VehiculoFactory(placa="DUP-001")
    assert (
        _rechazo(vehiculos.crear_vehiculo, {"placa": "dup-001", **PROPIO}, administrador)
        == "La placa ya está registrada"
    )


def test_rn_m02_03_vehiculo_externo_sin_transportista_es_rechazado(administrador):
    datos = {"placa": "EXT-900", "tipo_titularidad": "EXTERNO", "capacidad_tn": Decimal("20")}
    assert (
        _rechazo(vehiculos.crear_vehiculo, datos, administrador)
        == "Debe indicar el transportista para un vehículo externo"
    )


def test_rn_m02_03_transportista_desactivado_no_se_asocia(administrador):
    t = TransportistaFactory(activo=False)
    datos = {"placa": "EXT-901", "tipo_titularidad": "EXTERNO", "capacidad_tn": Decimal("20"),
             "transportista": t.pk}
    assert (
        _rechazo(vehiculos.crear_vehiculo, datos, administrador)
        == "Debe indicar el transportista para un vehículo externo"
    )


def test_rn_m02_04_vehiculo_propio_con_transportista_es_rechazado(administrador):
    t = TransportistaFactory()
    assert (
        _rechazo(vehiculos.crear_vehiculo, {"placa": "PRO-900", **PROPIO, "transportista": t.pk}, administrador)
        == "Un vehículo propio no lleva transportista asociado"
    )


def test_rn_m02_04_pasar_a_propio_suelta_el_transportista(administrador):
    t = TransportistaFactory()
    v = VehiculoFactory(placa="EXT-902", tipo_titularidad=Vehiculo.EXTERNO, transportista=t)
    vehiculos.actualizar_vehiculo(v, {"tipo_titularidad": "PROPIO"}, administrador)
    v.refresh_from_db()
    assert v.tipo_titularidad == "PROPIO" and v.transportista is None


def test_rn_m02_14_el_alta_desde_el_registro_usa_el_mismo_servicio(supervisor):
    # Mismo servicio, mismas reglas: el rol del Supervisor no relaja ninguna.
    VehiculoFactory(placa="REG-001")
    assert (
        _rechazo(vehiculos.crear_vehiculo, {"placa": "REG-001", **PROPIO}, supervisor)
        == "La placa ya está registrada"
    )
    v = vehiculos.crear_vehiculo({"placa": "REG-002", **PROPIO}, supervisor)
    assert v.pendiente_destare


def test_rn_m02_11_registrar_tara_fija_fecha_y_usuario(supervisor):
    v = VehiculoFactory(placa="TAR-001")
    momento = timezone.now()
    vehiculos.registrar_tara(v, Decimal("12.40"), momento, supervisor)
    v.refresh_from_db()
    assert v.tara_tn == Decimal("12.40")
    assert v.fecha_destare == momento and v.usuario_destare == supervisor
    assert v.pendiente_destare is False


def test_rn_m02_11_la_primera_tara_no_se_registra_dos_veces(supervisor):
    v = VehiculoFactory(placa="TAR-002", tara_tn=Decimal("12.00"))
    with pytest.raises(ConflictoDeConcurrencia) as exc:
        vehiculos.registrar_tara(v, Decimal("13.00"), timezone.now(), supervisor)
    assert str(exc.value) == "El vehículo TAR-002 ya tiene tara registrada"


def test_rn_m02_12_modificar_tara_exige_motivo(administrador):
    v = VehiculoFactory(placa="TAR-003", tara_tn=Decimal("12.00"))
    assert (
        _rechazo(vehiculos.modificar_tara, v, Decimal("12.50"), "  ", administrador)
        == "Debe indicar el motivo del cambio de tara"
    )


def test_rn_m02_12_modificar_tara_queda_en_auditoria(administrador):
    v = VehiculoFactory(placa="TAR-004", tara_tn=Decimal("12.00"))
    vehiculos.modificar_tara(v, Decimal("12.50"), "Cambio de tolva", administrador)
    evento = EventoAuditoria.objects.filter(entidad="Vehiculo", id_entidad=v.pk).latest("fecha_hora")
    assert evento.valores_anteriores == {"tara_tn": "12.00"}
    assert evento.valores_nuevos == {"tara_tn": "12.50"}
    assert evento.motivo == "Cambio de tolva" and evento.usuario == administrador


def test_rn_m02_12_sin_tara_registrada_no_hay_cambio_de_tara(administrador):
    v = VehiculoFactory(placa="TAR-005")
    with pytest.raises(ConflictoDeConcurrencia):
        vehiculos.modificar_tara(v, Decimal("12.50"), "Motivo", administrador)


def test_rn_m02_13_el_cambio_de_tara_no_altera_ingresos_registrados(administrador):
    ingreso = IngresoFactory(vehiculo__placa="TAR-006", vehiculo__tara_tn=Decimal("12.30"))
    vehiculos.modificar_tara(ingreso.vehiculo, Decimal("13.00"), "Recalibración", administrador)
    ingreso.refresh_from_db()
    assert ingreso.tara_tn == Decimal("12.30") and ingreso.peso_neto_tn == Decimal("20.20")


def test_rn_m02_16_codigo_con_formato_invalido(administrador):
    for codigo in ("A", "ABCDEFG", "AB-1"):
        assert (
            _rechazo(tipos_mineral.crear_tipo_mineral, {"codigo": codigo, "nombre": f"N {codigo}"}, administrador)
            == "El código debe tener de 2 a 6 letras o números"
        )


def test_rn_m02_16_el_codigo_no_se_modifica_tras_el_alta(administrador):
    tipo = TipoMineralFactory(codigo="FIJ", nombre="Fijo")
    tipos_mineral.actualizar_tipo_mineral(tipo, {"codigo": "OTRO", "nombre": "Renombrado"}, administrador)
    tipo.refresh_from_db()
    assert tipo.codigo == "FIJ" and tipo.nombre == "Renombrado"


def test_rn_m02_15_nombre_duplicado_sin_distinguir_mayusculas(administrador):
    TipoMineralFactory(codigo="SAR", nombre="Saranda")
    assert (
        _rechazo(tipos_mineral.crear_tipo_mineral, {"codigo": "SR2", "nombre": "sARANDA "}, administrador)
        == "Ya existe un tipo de mineral con ese nombre"
    )


def test_rn_m02_15_renombrar_a_un_nombre_existente(administrador):
    TipoMineralFactory(codigo="AAA", nombre="Saranda")
    otro = TipoMineralFactory(codigo="BBB", nombre="Otro")
    assert (
        _rechazo(tipos_mineral.actualizar_tipo_mineral, otro, {"nombre": "SARANDA"}, administrador)
        == "Ya existe un tipo de mineral con ese nombre"
    )


def test_rn_m02_17_desde_el_registro_el_codigo_se_genera_sin_repetirse(administrativo):
    TipoMineralFactory(codigo="MOP", nombre="Existente")
    tipo = tipos_mineral.crear_tipo_mineral(
        {"nombre": "Mineral óxido Pingüino"}, administrativo, desde_registro=True
    )
    assert tipo.codigo != "MOP" and tipo.codigo.startswith("MOP")
    otro = tipos_mineral.crear_tipo_mineral(
        {"nombre": "Mineral oxido pinguino fino"}, administrativo, desde_registro=True
    )
    assert otro.codigo not in ("MOP", tipo.codigo)
    assert TipoMineral.objects.filter(codigo=otro.codigo).count() == 1


def test_rn_m02_17_desde_el_catalogo_el_codigo_es_obligatorio(administrativo):
    assert (
        _rechazo(tipos_mineral.crear_tipo_mineral, {"nombre": "Sin código"}, administrativo)
        == "Debe completar los campos obligatorios"
    )


def test_rn_m02_07_ruc_debe_tener_once_digitos(administrador):
    assert (
        _rechazo(transportistas.crear_transportista, {"razon_social": "X", "ruc": "123"}, administrador)
        == "El RUC debe tener once dígitos"
    )


def test_rn_m02_18_ruc_duplicado_al_editar(administrador):
    TransportistaFactory(ruc="20604123457")
    otro = TransportistaFactory(ruc="20611890231")
    assert (
        _rechazo(transportistas.actualizar_transportista, otro, {"ruc": "20604123457"}, administrador)
        == "El RUC ya está registrado"
    )


def test_rn_m02_08_la_baja_de_cada_entidad_es_logica(administrador):
    tipo, t, v = TipoMineralFactory(), TransportistaFactory(), VehiculoFactory()
    tipos_mineral.desactivar_tipo_mineral(tipo, administrador)
    transportistas.desactivar_transportista(t, administrador)
    vehiculos.desactivar_vehiculo(v, administrador)
    for obj in (tipo, t, v):
        obj.refresh_from_db()
        assert obj.activo is False


def test_rn_m02_08_la_baja_queda_en_auditoria_como_cambio_de_vigencia(administrador):
    v = VehiculoFactory()
    vehiculos.desactivar_vehiculo(v, administrador)
    evento = EventoAuditoria.objects.filter(entidad="Vehiculo", id_entidad=v.pk).latest("fecha_hora")
    assert evento.accion == "MODIFICAR"
    assert evento.valores_anteriores == {"activo": True} and evento.valores_nuevos == {"activo": False}


def test_rn_m02_19_el_vehiculo_reactivado_conserva_su_tara(administrador):
    v = VehiculoFactory(tara_tn=Decimal("12.60"), activo=False)
    vehiculos.reactivar_vehiculo(v, administrador)
    v.refresh_from_db()
    assert v.activo is True and v.tara_tn == Decimal("12.60")


def test_desactivar_transportista_sin_vehiculos_usa_el_mensaje_generico(administrador):
    resultado = transportistas.desactivar_transportista(TransportistaFactory(), administrador)
    assert resultado.mensaje == "Cambios guardados"


def test_crear_tipo_de_mineral_registra_evento_en_auditoria(administrador):
    tipo = tipos_mineral.crear_tipo_mineral({"codigo": "AUD", "nombre": "Auditado"}, administrador)
    evento = EventoAuditoria.objects.get(entidad="TipoMineral", id_entidad=tipo.pk)
    assert evento.accion == "CREAR" and evento.usuario == administrador
