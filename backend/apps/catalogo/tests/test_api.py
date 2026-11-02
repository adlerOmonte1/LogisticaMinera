"""Contrato HTTP de M02, un caso por criterio de aceptación de HU-M02-01 a
HU-M02-03. Las reglas sueltas están en `test_servicios.py` y `test_modelos.py`."""

from decimal import Decimal

import pytest

from apps.auditoria.models import EventoAuditoria
from apps.catalogo.models import TipoMineral, Transportista, Vehiculo
from apps.ingresos.tests.factories import IngresoFactory

from .factories import TipoMineralFactory, TransportistaFactory, VehiculoFactory

pytestmark = pytest.mark.django_db

TIPOS_MINERAL = "/api/v1/catalogo/tipos-mineral/"
VEHICULOS = "/api/v1/catalogo/vehiculos/"
TRANSPORTISTAS = "/api/v1/catalogo/transportistas/"
ACCION_NO_AUTORIZADA = "Acción no autorizada"


def _placas(respuesta):
    return [v["placa"] for v in respuesta.data["results"]]


# HU-M02-01 — Vehículos


def test_hu_m02_01_ca01_alta_de_vehiculo_activo(api_como, administrativo):
    r = api_como(administrativo).post(
        VEHICULOS, {"placa": "PRO-777", "tipo_titularidad": "PROPIO", "capacidad_tn": "32.50"}
    )
    assert r.status_code == 201
    assert r.data["activo"] is True and r.data["capacidad_tn"] == "32.50"


def test_hu_m02_01_ca02_placa_duplicada(api_como, administrativo):
    VehiculoFactory(placa="ABC-500")
    r = api_como(administrativo).post(
        VEHICULOS, {"placa": "ABC-500", "tipo_titularidad": "PROPIO", "capacidad_tn": "30.00"}
    )
    assert r.status_code == 400
    assert r.data["mensaje"] == "La placa ya está registrada"


def test_hu_m02_01_ca03_placa_con_formato_invalido(api_como, administrativo):
    r = api_como(administrativo).post(
        VEHICULOS, {"placa": "1234", "tipo_titularidad": "PROPIO", "capacidad_tn": "30.00"}
    )
    assert r.status_code == 400
    assert r.data["mensaje"] == "El formato de la placa no es válido"


def test_hu_m02_01_ca04_externo_sin_transportista(api_como, administrativo):
    r = api_como(administrativo).post(
        VEHICULOS, {"placa": "EXT-501", "tipo_titularidad": "EXTERNO", "capacidad_tn": "30.00"}
    )
    assert r.status_code == 400
    assert r.data["mensaje"] == "Debe indicar el transportista para un vehículo externo"


def test_hu_m02_01_ca05_propio_sin_transportista(api_como, administrativo):
    r = api_como(administrativo).post(
        VEHICULOS, {"placa": "PRO-778", "tipo_titularidad": "PROPIO", "capacidad_tn": "18.00"}
    )
    assert r.status_code == 201
    assert r.data["titularidad"] == "PROPIO" and r.data["transportista"] is None


def test_hu_m02_01_ca06_baja_de_vehiculo_con_ingresos(api_como, administrador):
    ingreso = IngresoFactory(vehiculo__placa="ING-001")
    r = api_como(administrador).patch(f"{VEHICULOS}{ingreso.vehiculo_id}/desactivar/")
    assert r.status_code == 200
    assert r.data["mensaje"] == "El vehículo se desactivó porque tiene ingresos registrados"
    assert r.data["activo"] is False
    assert Vehiculo.objects.filter(pk=ingreso.vehiculo_id).exists()
    assert ingreso.vehiculo.ingresos.count() == 1


def test_hu_m02_01_ca06_baja_de_vehiculo_sin_ingresos(api_como, administrador):
    v = VehiculoFactory()
    r = api_como(administrador).patch(f"{VEHICULOS}{v.pk}/desactivar/")
    assert r.data["mensaje"] == "Vehículo desactivado"


def test_hu_m02_01_ca07_vehiculo_desactivado_no_se_ofrece_al_registrar(api_como, supervisor):
    VehiculoFactory(placa="VIG-001")
    VehiculoFactory(placa="BAJ-001", activo=False)
    placas = _placas(api_como(supervisor).get(VEHICULOS))
    assert "VIG-001" in placas and "BAJ-001" not in placas


def test_hu_m02_01_ca08_alta_sin_tara_pendiente_de_destare(api_como, administrativo):
    r = api_como(administrativo).post(
        VEHICULOS,
        {"placa": "NUE-001", "tipo_titularidad": "PROPIO", "capacidad_tn": "17.50", "tara_tn": "11.00"},
    )
    assert r.status_code == 201
    assert r.data["tara_tn"] is None and r.data["pendiente_destare"] is True


def test_hu_m02_01_ca09_solo_el_administrador_modifica_la_tara(api_como, administrativo, supervisor):
    v = VehiculoFactory(tara_tn=Decimal("12.00"))
    for usuario in (administrativo, supervisor):
        r = api_como(usuario).patch(f"{VEHICULOS}{v.pk}/tara/", {"tara_tn": "13.00", "motivo": "x"})
        assert r.status_code == 403
        assert r.data["mensaje"] == "Solo el Administrador puede modificar la tara del vehículo"
    v.refresh_from_db()
    assert v.tara_tn == Decimal("12.00")


def test_hu_m02_01_ca09_la_tara_no_cambia_por_la_edicion_generica(api_como, administrativo):
    v = VehiculoFactory(tara_tn=Decimal("12.00"))
    r = api_como(administrativo).patch(f"{VEHICULOS}{v.pk}/", {"tara_tn": "99.00", "capacidad_tn": "21.00"})
    assert r.status_code == 200
    v.refresh_from_db()
    assert v.tara_tn == Decimal("12.00") and v.capacidad_tn == Decimal("21.00")


def test_hu_m02_01_ca10_cambio_de_tara_sin_motivo(api_como, administrador):
    v = VehiculoFactory(tara_tn=Decimal("12.00"))
    r = api_como(administrador).patch(f"{VEHICULOS}{v.pk}/tara/", {"tara_tn": "13.00"})
    assert r.status_code == 400
    assert r.data["mensaje"] == "Debe indicar el motivo del cambio de tara"


def test_hu_m02_01_ca11_cambio_de_tara_con_motivo(api_como, administrador):
    ingreso = IngresoFactory(vehiculo__placa="TAR-100", vehiculo__tara_tn=Decimal("12.30"))
    r = api_como(administrador).patch(
        f"{VEHICULOS}{ingreso.vehiculo_id}/tara/", {"tara_tn": "12.90", "motivo": "Cambio de tolva"}
    )
    assert r.status_code == 200 and r.data["tara_tn"] == "12.90"
    evento = EventoAuditoria.objects.filter(entidad="Vehiculo", id_entidad=ingreso.vehiculo_id).latest(
        "fecha_hora"
    )
    assert evento.valores_anteriores == {"tara_tn": "12.30"}
    assert evento.valores_nuevos == {"tara_tn": "12.90"} and evento.motivo == "Cambio de tolva"
    ingreso.refresh_from_db()
    assert ingreso.peso_neto_tn == Decimal("20.20")


def test_hu_m02_01_ca12_alta_desde_el_registro_con_las_mismas_validaciones(api_como, supervisor):
    VehiculoFactory(placa="TIC-001")
    api = api_como(supervisor)
    duplicada = api.post(VEHICULOS, {"placa": "TIC-001", "tipo_titularidad": "PROPIO", "capacidad_tn": "18"})
    assert duplicada.status_code == 400 and duplicada.data["mensaje"] == "La placa ya está registrada"
    externo = api.post(VEHICULOS, {"placa": "TIC-002", "tipo_titularidad": "EXTERNO", "capacidad_tn": "18"})
    assert externo.data["mensaje"] == "Debe indicar el transportista para un vehículo externo"
    nueva = api.post(VEHICULOS, {"placa": "tic-003", "tipo_titularidad": "PROPIO", "capacidad_tn": "18"})
    assert nueva.status_code == 201 and nueva.data["placa"] == "TIC-003"
    # El id devuelto es el que M03 asocia al ingreso en curso.
    assert Vehiculo.objects.get(pk=nueva.data["id"]).pendiente_destare


def test_hu_m02_01_ca13_reactivar_vehiculo_conserva_su_tara(api_como, administrador):
    v = VehiculoFactory(placa="REA-001", tara_tn=Decimal("12.60"), activo=False)
    api = api_como(administrador)
    r = api.patch(f"{VEHICULOS}{v.pk}/reactivar/")
    assert r.status_code == 200
    assert r.data["mensaje"] == "Vehículo reactivado"
    assert r.data["activo"] is True and r.data["tara_tn"] == "12.60"
    assert "REA-001" in _placas(api.get(VEHICULOS))
    assert EventoAuditoria.objects.filter(
        entidad="Vehiculo", id_entidad=v.pk, valores_nuevos={"activo": True}
    ).exists()


def test_hu_m02_01_ca14_el_supervisor_no_edita_ni_da_de_baja_ni_reactiva(api_como, supervisor):
    v = VehiculoFactory(activo=True)
    inactivo = VehiculoFactory(activo=False)
    api = api_como(supervisor)
    for respuesta in (
        api.patch(f"{VEHICULOS}{v.pk}/", {"capacidad_tn": "20.00"}),
        api.patch(f"{VEHICULOS}{v.pk}/desactivar/"),
        api.patch(f"{VEHICULOS}{inactivo.pk}/reactivar/"),
    ):
        assert respuesta.status_code == 403
        assert respuesta.data["mensaje"] == ACCION_NO_AUTORIZADA
    alta = api.post(VEHICULOS, {"placa": "SUP-001", "tipo_titularidad": "PROPIO", "capacidad_tn": "18"})
    assert alta.status_code == 201


def test_filtro_por_titularidad(api_como, administrativo):
    t = TransportistaFactory()
    VehiculoFactory(placa="PRO-001", tipo_titularidad=Vehiculo.PROPIO)
    VehiculoFactory(placa="PRO-002", tipo_titularidad=Vehiculo.PROPIO)
    VehiculoFactory(placa="EXT-001", tipo_titularidad=Vehiculo.EXTERNO, transportista=t)
    r = api_como(administrativo).get(VEHICULOS + "?titularidad=PROPIO")
    assert r.data["count"] == 2
    assert all(v["titularidad"] == "PROPIO" for v in r.data["results"])


def test_editar_vehiculo_de_propio_a_externo(api_como, administrativo):
    t = TransportistaFactory()
    v = VehiculoFactory(placa="CAM-010", tipo_titularidad=Vehiculo.PROPIO)
    r = api_como(administrativo).patch(
        f"{VEHICULOS}{v.pk}/", {"tipo_titularidad": "EXTERNO", "transportista": t.pk}
    )
    assert r.status_code == 200
    assert r.data["titularidad"] == "EXTERNO" and r.data["transportista"] == t.pk


# HU-M02-02 — Tipos de mineral


def test_hu_m02_02_ca01_crear_tipo_de_mineral_activo(api_como, administrativo):
    r = api_como(administrativo).post(TIPOS_MINERAL, {"codigo": "sar", "nombre": "Saranda"})
    assert r.status_code == 201
    assert r.data["activo"] is True and r.data["codigo"] == "SAR"
    assert TipoMineral.objects.get(codigo="SAR").unidad_medida == "TONELADA"


def test_hu_m02_02_ca02_codigo_duplicado(api_como, administrativo):
    TipoMineralFactory(codigo="SAR")
    r = api_como(administrativo).post(TIPOS_MINERAL, {"codigo": "SAR", "nombre": "Otro"})
    assert r.status_code == 400
    assert r.data["mensaje"] == "El código ya está registrado"


def test_hu_m02_02_ca03_baja_de_tipo_con_ingresos(api_como, administrador):
    ingreso = IngresoFactory()
    r = api_como(administrador).patch(f"{TIPOS_MINERAL}{ingreso.tipo_mineral_id}/desactivar/")
    assert r.status_code == 200
    assert r.data["mensaje"] == "El tipo de mineral se desactivó porque tiene ingresos registrados"
    ingreso.refresh_from_db()
    assert ingreso.tipo_mineral.activo is False


def test_hu_m02_02_ca04_tipo_desactivado_no_aparece_en_el_registro(api_como, supervisor):
    TipoMineralFactory(codigo="ACT")
    TipoMineralFactory(codigo="INA", activo=False)
    codigos = [p["codigo"] for p in api_como(supervisor).get(TIPOS_MINERAL).data["results"]]
    assert "ACT" in codigos and "INA" not in codigos


def test_hu_m02_02_ca04_el_historico_si_lo_incluye(api_como, administrativo):
    TipoMineralFactory(codigo="INA", activo=False)
    r = api_como(administrativo).get(TIPOS_MINERAL + "?incluir_inactivos=1")
    assert any(p["codigo"] == "INA" for p in r.data["results"])


def test_hu_m02_02_ca05_nombre_duplicado(api_como, administrativo):
    TipoMineralFactory(codigo="SAR", nombre="Saranda")
    r = api_como(administrativo).post(TIPOS_MINERAL, {"codigo": "SR2", "nombre": "SARANDA"})
    assert r.status_code == 400
    assert r.data["mensaje"] == "Ya existe un tipo de mineral con ese nombre"


def test_hu_m02_02_ca06_codigo_con_formato_invalido(api_como, administrativo):
    r = api_como(administrativo).post(TIPOS_MINERAL, {"codigo": "ABCDEFG", "nombre": "Largo"})
    assert r.status_code == 400
    assert r.data["mensaje"] == "El código debe tener de 2 a 6 letras o números"


def test_hu_m02_02_ca07_alta_desde_el_registro_genera_el_codigo(api_como, administrativo, administrador):
    for usuario, nombre in ((administrativo, "Mineral sulfuro fino"), (administrador, "Mineral sulfuro grueso")):
        r = api_como(usuario).post(TIPOS_MINERAL, {"nombre": nombre, "desde_registro": True})
        assert r.status_code == 201
        assert r.data["activo"] is True and 2 <= len(r.data["codigo"]) <= 6
    assert TipoMineral.objects.filter(codigo__startswith="MSF").count() == 1


def test_hu_m02_02_ca08_alta_desde_el_registro_sin_nombre(api_como, administrativo):
    r = api_como(administrativo).post(TIPOS_MINERAL, {"nombre": "", "desde_registro": True})
    assert r.status_code == 400
    assert r.data["mensaje"] == "Debe indicar el nombre del tipo de mineral"


def test_hu_m02_02_ca09_reactivar_tipo_de_mineral(api_como, administrativo):
    tipo = TipoMineralFactory(codigo="REA", activo=False)
    api = api_como(administrativo)
    r = api.patch(f"{TIPOS_MINERAL}{tipo.pk}/reactivar/")
    assert r.status_code == 200 and r.data["activo"] is True
    assert "REA" in [p["codigo"] for p in api.get(TIPOS_MINERAL).data["results"]]
    assert EventoAuditoria.objects.filter(
        entidad="TipoMineral", id_entidad=tipo.pk, valores_nuevos={"activo": True}
    ).exists()


def test_hu_m02_02_ca10_el_supervisor_no_gestiona_tipos_de_mineral(api_como, supervisor):
    tipo = TipoMineralFactory(activo=True)
    inactivo = TipoMineralFactory(activo=False)
    api = api_como(supervisor)
    for respuesta in (
        api.post(TIPOS_MINERAL, {"codigo": "SUP", "nombre": "Supervisor"}),
        api.post(TIPOS_MINERAL, {"nombre": "Desde registro", "desde_registro": True}),
        api.patch(f"{TIPOS_MINERAL}{tipo.pk}/", {"nombre": "Otro"}),
        api.patch(f"{TIPOS_MINERAL}{tipo.pk}/desactivar/"),
        api.patch(f"{TIPOS_MINERAL}{inactivo.pk}/reactivar/"),
    ):
        assert respuesta.status_code == 403
        assert respuesta.data["mensaje"] == ACCION_NO_AUTORIZADA


def test_editar_nombre_de_tipo_de_mineral(api_como, administrativo):
    p = TipoMineralFactory(codigo="ED", nombre="Viejo")
    r = api_como(administrativo).patch(f"{TIPOS_MINERAL}{p.pk}/", {"nombre": "Nuevo", "codigo": "XX"})
    assert r.status_code == 200
    assert r.data["nombre"] == "Nuevo" and r.data["codigo"] == "ED"


# HU-M02-03 — Transportistas


def test_hu_m02_03_ca01_crear_transportista(api_como, administrativo):
    r = api_como(administrativo).post(
        TRANSPORTISTAS, {"razon_social": "Transportes Andinos SAC", "ruc": "20123456789"}
    )
    assert r.status_code == 201
    assert r.data["activo"] is True


def test_hu_m02_03_ca02_ruc_invalido(api_como, administrativo):
    r = api_como(administrativo).post(TRANSPORTISTAS, {"razon_social": "X", "ruc": "123"})
    assert r.status_code == 400
    assert r.data["mensaje"] == "El RUC debe tener once dígitos"


def test_hu_m02_03_ca03_baja_de_transportista_con_vehiculos(api_como, administrador):
    t = TransportistaFactory()
    v = VehiculoFactory(placa="EXT-900", tipo_titularidad=Vehiculo.EXTERNO, transportista=t)
    r = api_como(administrador).patch(f"{TRANSPORTISTAS}{t.pk}/desactivar/")
    assert r.status_code == 200
    assert r.data["mensaje"] == "El transportista se desactivó porque tiene vehículos asociados"
    v.refresh_from_db()
    assert v.transportista_id == t.pk
    assert Transportista.objects.get(pk=t.pk).activo is False


def test_hu_m02_03_ca04_ruc_duplicado(api_como, administrativo):
    TransportistaFactory(ruc="20604123457")
    r = api_como(administrativo).post(TRANSPORTISTAS, {"razon_social": "Otro", "ruc": "20604123457"})
    assert r.status_code == 400
    assert r.data["mensaje"] == "El RUC ya está registrado"


def test_hu_m02_03_ca05_reactivar_transportista(api_como, administrativo):
    t = TransportistaFactory(activo=False)
    api = api_como(administrativo)
    r = api.patch(f"{TRANSPORTISTAS}{t.pk}/reactivar/")
    assert r.status_code == 200 and r.data["activo"] is True
    alta = api.post(
        VEHICULOS,
        {"placa": "EXT-950", "tipo_titularidad": "EXTERNO", "capacidad_tn": "20", "transportista": t.pk},
    )
    assert alta.status_code == 201 and alta.data["transportista"] == t.pk
    assert EventoAuditoria.objects.filter(
        entidad="Transportista", id_entidad=t.pk, valores_nuevos={"activo": True}
    ).exists()


def test_hu_m02_03_ca06_el_supervisor_no_gestiona_transportistas(api_como, supervisor):
    t = TransportistaFactory()
    inactivo = TransportistaFactory(activo=False)
    api = api_como(supervisor)
    for respuesta in (
        api.post(TRANSPORTISTAS, {"razon_social": "X", "ruc": "20999999999"}),
        api.patch(f"{TRANSPORTISTAS}{t.pk}/", {"razon_social": "Y"}),
        api.patch(f"{TRANSPORTISTAS}{t.pk}/desactivar/"),
        api.patch(f"{TRANSPORTISTAS}{inactivo.pk}/reactivar/"),
    ):
        assert respuesta.status_code == 403
        assert respuesta.data["mensaje"] == ACCION_NO_AUTORIZADA


# Transversales


@pytest.mark.parametrize("ruta", [TIPOS_MINERAL, VEHICULOS, TRANSPORTISTAS])
def test_rn_m02_08_no_existe_borrado_fisico(api_como, administrador, ruta):
    fabrica = {TIPOS_MINERAL: TipoMineralFactory, VEHICULOS: VehiculoFactory, TRANSPORTISTAS: TransportistaFactory}
    obj = fabrica[ruta]()
    r = api_como(administrador).delete(f"{ruta}{obj.pk}/")
    assert r.status_code == 405
    assert type(obj).objects.filter(pk=obj.pk).exists()


def test_rn_m02_09_las_consultas_historicas_muestran_el_desactivado(api_como, supervisor):
    v = VehiculoFactory(placa="HIS-001", activo=False)
    r = api_como(supervisor).get(f"{VEHICULOS}{v.pk}/")
    assert r.status_code == 200 and r.data["activo"] is False


@pytest.mark.parametrize("capacidad", ["0", "-5", "abc"])
def test_rn_m02_05_la_capacidad_es_un_decimal_positivo(api_como, administrativo, capacidad):
    r = api_como(administrativo).post(
        VEHICULOS, {"placa": "CAP-001", "tipo_titularidad": "PROPIO", "capacidad_tn": capacidad}
    )
    assert r.status_code == 400
    assert not Vehiculo.objects.filter(placa="CAP-001").exists()


def test_busqueda_exacta_por_placa_y_por_codigo(api_como, supervisor):
    VehiculoFactory(placa="BUS-001")
    VehiculoFactory(placa="BUS-002")
    TipoMineralFactory(codigo="BUS")
    api = api_como(supervisor)
    assert _placas(api.get(VEHICULOS + "?placa=bus-001")) == ["BUS-001"]
    assert [t["codigo"] for t in api.get(TIPOS_MINERAL + "?codigo=bus").data["results"]] == ["BUS"]
