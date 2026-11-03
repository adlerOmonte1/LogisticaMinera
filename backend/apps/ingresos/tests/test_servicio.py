"""`ServicioIngreso` con sus dependencias sustituidas: reloj fijo, reconocedor
determinista, auditoría que falla y un doble del puerto de lotes de M06. Cubre
lo que la API no puede fijar: los instantes, la atomicidad y la relación con M06."""

from datetime import datetime, time, timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from apps.auditoria.models import EventoAuditoria
from apps.catalogo.services import vehiculos as servicio_vehiculos
from apps.catalogo.tests.factories import TipoMineralFactory
from apps.ingresos.models import ContadorCorrelativo, Ingreso
from apps.ingresos.repositories import IngresoRepository
from apps.ingresos.services import DatosConfirmados, ServicioIngreso, correlativo
from apps.ingresos.services.lotes import LoteDelIngreso
from apps.reconocimiento.dominio import FECHA, PESO_BRUTO, PLACA
from apps.reconocimiento.motores.determinista import ReconocedorDeterminista
from apps.validacion.reglas import reglas_vigentes
from apps.validacion.services import ValidadorConsistencia
from common.eventos import registrador_por_defecto
from common.excepciones import ConflictoDeConcurrencia, ErrorDeValidacionDeDominio
from common.reloj import RelojFijo

pytestmark = pytest.mark.django_db

INICIO = timezone.make_aware(datetime(2027, 3, 15, 8, 0))
FECHA_TICKET = INICIO.date()


class AuditoriaQueFalla:
    def registrar(self, **evento):
        if evento["accion"] == "CREAR":
            raise RuntimeError("falla inducida dentro de la transacción")
        return registrador_por_defecto.registrar(**evento)


class LotesFalsos:
    def __init__(self, lote=None):
        self.lote = lote
        self.retirados = []

    def lote_del_ingreso(self, ingreso):
        return self.lote

    def retirar(self, ingreso, usuario):
        self.retirados.append(ingreso.pk)


@pytest.fixture
def reloj():
    return RelojFijo(INICIO)


@pytest.fixture
def reconocedor():
    return ReconocedorDeterminista(
        {PLACA: ("V2K-841", 0.97), FECHA: (FECHA_TICKET.isoformat(), 0.95), PESO_BRUTO: ("29.80", 0.91)}
    )


def construir(reloj, reconocedor=None, *, auditoria=None, lotes=None):
    return ServicioIngreso(
        fabrica_reconocedor=lambda: reconocedor,
        validador=ValidadorConsistencia(reglas_vigentes(IngresoRepository())),
        generador=correlativo.generador_por_defecto,
        reloj=reloj,
        auditoria=auditoria or registrador_por_defecto,
        lotes=lotes or LotesFalsos(),
    )


@pytest.fixture
def servicio(reloj, reconocedor):
    return construir(reloj, reconocedor)


def confirmados(mineral, **cambios):
    base = dict(placa="V2K-841", fecha=FECHA_TICKET, hora=time(7, 50), peso_bruto_tn=Decimal("29.80"),
                tipo_mineral=mineral.pk)
    base.update(cambios)
    return DatosConfirmados(**base)


def registrar(servicio, reloj, usuario, mineral, imagen, **cambios):
    token = servicio.iniciar_registro(usuario, archivo=imagen)["borrador"]
    reloj.adelantar(minutes=7)
    return servicio.registrar_ingreso(usuario, token, confirmados(mineral, **cambios))


def test_rn_m03_06_el_inicio_es_al_recibir_la_imagen_y_el_fin_al_confirmar(servicio, reloj, supervisor, mineral,
                                                                           vehiculo, imagen_png):
    """El riesgo principal de M03: que inicio y fin queden separados por milisegundos."""
    ingreso = registrar(servicio, reloj, supervisor, mineral, imagen_png)
    assert ingreso.hora_inicio_registro == INICIO
    assert ingreso.hora_fin_registro == INICIO + timedelta(minutes=7)
    assert timezone.localtime(ingreso.fecha_hora_pesaje).time() == time(7, 50)


def test_rn_m03_16_la_hora_del_pesaje_se_propone_con_la_de_la_revision(servicio, supervisor, imagen_png):
    propuesta = servicio.iniciar_registro(supervisor, archivo=imagen_png)["propuesta"]
    assert (propuesta["hora"], propuesta["hora_es_propuesta"]) == ("08:00", True)


def test_rn_m03_02_nada_se_persiste_antes_de_confirmar(servicio, supervisor, vehiculo, imagen_png):
    servicio.iniciar_registro(supervisor, archivo=imagen_png)
    assert Ingreso.objects.count() == 0 and EventoAuditoria.objects.filter(entidad="Ingreso").count() == 0


def test_hu_m04_01_ca06_la_propuesta_no_es_un_dato_del_ingreso(servicio, supervisor, vehiculo, imagen_png):
    propuesta = servicio.iniciar_registro(supervisor, archivo=imagen_png)
    assert propuesta["propuesta"]["placa"] == "V2K-841" and not Ingreso.objects.exists()


def test_hu_m03_01_ca12_una_falla_dentro_de_la_transaccion_no_deja_nada(reloj, reconocedor, supervisor, mineral,
                                                                       vehiculo, imagen_png):
    servicio = construir(reloj, reconocedor, auditoria=AuditoriaQueFalla())
    with pytest.raises(RuntimeError):
        registrar(servicio, reloj, supervisor, mineral, imagen_png)
    assert not Ingreso.objects.exists()
    assert not ContadorCorrelativo.objects.filter(ultimo_valor__gt=0).exists()
    assert not EventoAuditoria.objects.filter(accion="RECONOCER").exists()


def test_rn_m03_15_el_evento_se_registra_en_la_misma_transaccion(servicio, reloj, supervisor, mineral, vehiculo,
                                                                imagen_png):
    ingreso = registrar(servicio, reloj, supervisor, mineral, imagen_png)
    assert EventoAuditoria.objects.filter(entidad="Ingreso", id_entidad=ingreso.pk, accion="CREAR").exists()


def test_rn_m03_04_un_cambio_de_tara_no_reescribe_el_neto_registrado(servicio, reloj, supervisor, administrador,
                                                                    mineral, vehiculo, imagen_png):
    ingreso = registrar(servicio, reloj, supervisor, mineral, imagen_png)
    servicio_vehiculos.modificar_tara(vehiculo, Decimal("13.00"), "Cambio de tolva", administrador)
    ingreso.refresh_from_db()
    assert (ingreso.tara_tn, ingreso.peso_neto_tn) == (Decimal("11.80"), Decimal("18.00"))


def test_rn_m03_01_sin_imagen_ni_registro_sin_foto_no_hay_registro(servicio, supervisor):
    with pytest.raises(ErrorDeValidacionDeDominio, match="Debe adjuntar la imagen del ticket de balanza"):
        servicio.iniciar_registro(supervisor)


def test_rn_m03_03_lo_leido_y_lo_confirmado_quedan_separados(servicio, reloj, supervisor, mineral, vehiculo,
                                                            imagen_png):
    ingreso = registrar(servicio, reloj, supervisor, mineral, imagen_png, peso_bruto_tn=Decimal("29.70"))
    campo = ingreso.reconocimiento.campos.get(nombre_campo=PESO_BRUTO)
    assert (campo.valor_reconocido, campo.valor_confirmado, campo.fue_corregido) == ("29.80", "29.70", True)


def test_rn_m03_05_no_se_confirma_con_una_bloqueante(servicio, reloj, supervisor, mineral, vehiculo, imagen_png):
    with pytest.raises(ErrorDeValidacionDeDominio, match="Debe corregir o justificar las inconsistencias señaladas"):
        registrar(servicio, reloj, supervisor, mineral, imagen_png, fecha=FECHA_TICKET + timedelta(days=1))


def test_rn_m03_07_el_pesaje_no_es_posterior_al_registro(servicio, reloj, supervisor, mineral, vehiculo, imagen_png):
    with pytest.raises(ErrorDeValidacionDeDominio) as exc:
        registrar(servicio, reloj, supervisor, mineral, imagen_png, hora=time(9, 0))  # registro a las 08:07
    assert exc.value.detalles["inconsistencias"][0]["regla"] == "V5"


def test_rn_m03_08_el_vehiculo_debe_existir_y_estar_vigente(servicio, reloj, supervisor, mineral, vehiculo,
                                                           imagen_png, imagen_jpg):
    with pytest.raises(ErrorDeValidacionDeDominio, match="no está registrada"):
        registrar(servicio, reloj, supervisor, mineral, imagen_png, placa="ZZZ-111")
    vehiculo.activo = False
    vehiculo.save()
    with pytest.raises(ErrorDeValidacionDeDominio, match="está dado de baja"):
        registrar(servicio, reloj, supervisor, mineral, imagen_jpg)


def test_rn_m03_09_cada_registro_recibe_un_codigo_distinto(servicio, reloj, supervisor, mineral, vehiculo,
                                                          imagen_png, imagen_jpg):
    a = registrar(servicio, reloj, supervisor, mineral, imagen_png, hora=time(7, 0))
    b = registrar(servicio, reloj, supervisor, mineral, imagen_jpg, hora=time(7, 30),
                  peso_bruto_tn=Decimal("28.00"))
    assert (a.codigo, b.codigo) == ("ING-2027-00001", "ING-2027-00002")


def test_rn_m03_10_el_ingreso_no_registra_numero_de_ticket():
    assert not any("ticket" in f.name and f.name != "imagen_ticket" for f in Ingreso._meta.get_fields())


def test_rn_m03_17_sin_tara_queda_en_proceso_sin_neto(servicio, reloj, supervisor, mineral, vehiculo_sin_tara,
                                                     imagen_png):
    ingreso = registrar(servicio, reloj, supervisor, mineral, imagen_png, placa="E4R-208")
    assert (ingreso.estado, ingreso.tara_tn, ingreso.peso_neto_tn) == (Ingreso.EN_PROCESO, None, None)


def test_rn_m03_18_el_en_proceso_no_tiene_neto_que_sumar(servicio, reloj, supervisor, mineral, vehiculo_sin_tara,
                                                        imagen_png):
    registrar(servicio, reloj, supervisor, mineral, imagen_png, placa="E4R-208")
    computables = Ingreso.objects.filter(estado=Ingreso.REGISTRADO)
    assert not computables.exists()
    assert Ingreso.objects.filter(estado=Ingreso.EN_PROCESO, peso_neto_tn__isnull=False).count() == 0


def test_rn_m03_21_el_motivo_sin_foto_es_de_una_lista_cerrada_y_la_marca_es_permanente(
    servicio, reloj, supervisor, administrativo, mineral, vehiculo
):
    with pytest.raises(ErrorDeValidacionDeDominio, match="campos obligatorios"):
        servicio.iniciar_registro(supervisor, sin_foto=True, motivo="Se me olvidó")
    token = servicio.iniciar_registro(supervisor, sin_foto=True, motivo=Ingreso.OTRO)["borrador"]
    ingreso = servicio.registrar_ingreso(supervisor, token, confirmados(mineral))
    servicio.corregir_ingreso(ingreso.pk, {"peso_bruto_tn": Decimal("29.00")}, "Ajuste", administrativo)
    ingreso.refresh_from_db()
    assert ingreso.sin_respaldo_fotografico and ingreso.motivo_sin_respaldo == Ingreso.OTRO


def test_rn_m03_22_el_sin_foto_no_se_reconoce_pero_se_valida(servicio, reconocedor, supervisor, mineral, vehiculo):
    token = servicio.iniciar_registro(supervisor, sin_foto=True, motivo=Ingreso.SIN_CAMARA)["borrador"]
    with pytest.raises(ErrorDeValidacionDeDominio):
        servicio.registrar_ingreso(supervisor, token, confirmados(mineral, peso_bruto_tn=Decimal("5.00")))
    assert reconocedor.invocaciones == 0


def test_rn_m03_11_la_correccion_exige_motivo_y_se_revalida(servicio, reloj, supervisor, administrativo, mineral,
                                                           vehiculo, imagen_png):
    ingreso = registrar(servicio, reloj, supervisor, mineral, imagen_png)
    with pytest.raises(ErrorDeValidacionDeDominio, match="motivo de la corrección"):
        servicio.corregir_ingreso(ingreso.pk, {"peso_bruto_tn": Decimal("20.00")}, "", administrativo)
    with pytest.raises(ErrorDeValidacionDeDominio, match="La tara no puede ser mayor"):
        servicio.corregir_ingreso(ingreso.pk, {"peso_bruto_tn": Decimal("10.00")}, "Error", administrativo)


def test_rn_m03_12_la_correccion_conserva_los_valores_anteriores(servicio, reloj, supervisor, administrativo,
                                                                mineral, vehiculo, imagen_png):
    ingreso = registrar(servicio, reloj, supervisor, mineral, imagen_png)
    otro = TipoMineralFactory(codigo="MOB")
    servicio.corregir_ingreso(ingreso.pk, {"tipo_mineral": otro.pk}, "Mineral equivocado", administrativo)
    evento = EventoAuditoria.objects.filter(entidad="Ingreso", id_entidad=ingreso.pk, accion="MODIFICAR").order_by("id").last()
    assert evento.valores_anteriores == {"tipo_mineral": mineral.pk}


def test_rn_m03_13_un_anulado_no_se_corrige_ni_se_anula_otra_vez(servicio, reloj, supervisor, administrador,
                                                                mineral, vehiculo, imagen_png):
    ingreso = registrar(servicio, reloj, supervisor, mineral, imagen_png)
    servicio.anular_ingreso(ingreso.pk, "Duplicado", administrador)
    with pytest.raises(ConflictoDeConcurrencia):
        servicio.corregir_ingreso(ingreso.pk, {"peso_bruto_tn": Decimal("20.00")}, "x", administrador)
    with pytest.raises(ConflictoDeConcurrencia):
        servicio.anular_ingreso(ingreso.pk, "Otra vez", administrador)


def test_rn_m03_26_la_placa_de_un_vehiculo_sin_tara_retira_tara_y_neto(servicio, reloj, supervisor, administrativo,
                                                                      mineral, vehiculo, vehiculo_sin_tara,
                                                                      imagen_png):
    ingreso = registrar(servicio, reloj, supervisor, mineral, imagen_png)
    servicio.corregir_ingreso(ingreso.pk, {"placa": "E4R-208"}, "Placa mal leída", administrativo)
    ingreso.refresh_from_db()
    assert (ingreso.estado, ingreso.tara_tn, ingreso.peso_neto_tn) == (Ingreso.EN_PROCESO, None, None)


def test_hu_m03_02_ca09_mineral_fuera_de_la_lista_del_lote(reloj, reconocedor, supervisor, administrativo,
                                                           mineral, vehiculo, imagen_png):
    otro = TipoMineralFactory(codigo="MOB", nombre="Mineral óxido tipo B")
    lotes = LotesFalsos(LoteDelIngreso("Lote 12", frozenset({mineral.pk}), True))
    servicio = construir(reloj, reconocedor, lotes=lotes)
    ingreso = registrar(servicio, reloj, supervisor, mineral, imagen_png)
    with pytest.raises(ErrorDeValidacionDeDominio) as exc:
        servicio.corregir_ingreso(ingreso.pk, {"tipo_mineral": otro.pk}, "Mineral", administrativo)
    assert str(exc.value) == ("Mineral óxido tipo B no está en el lote Lote 12. "
                              "Agregue ese mineral al lote para corregir el ingreso")


def test_rn_m03_25_el_mineral_del_lote_si_se_admite(reloj, reconocedor, supervisor, administrativo, mineral,
                                                   vehiculo, imagen_png):
    otro = TipoMineralFactory(codigo="MOB")
    lotes = LotesFalsos(LoteDelIngreso("Lote 12", frozenset({mineral.pk, otro.pk}), True))
    servicio = construir(reloj, reconocedor, lotes=lotes)
    ingreso = registrar(servicio, reloj, supervisor, mineral, imagen_png)
    assert servicio.corregir_ingreso(ingreso.pk, {"tipo_mineral": otro.pk}, "x", administrativo).tipo_mineral == otro


def test_hu_m03_03_ca08_la_anulacion_retira_del_lote_que_reune_ingresos(reloj, reconocedor, supervisor,
                                                                        administrador, mineral, vehiculo, imagen_png):
    lotes = LotesFalsos(LoteDelIngreso("Lote 12", frozenset({mineral.pk}), True))
    servicio = construir(reloj, reconocedor, lotes=lotes)
    ingreso = registrar(servicio, reloj, supervisor, mineral, imagen_png)
    servicio.anular_ingreso(ingreso.pk, "No debió registrarse", administrador)
    assert lotes.retirados == [ingreso.pk]


def test_rn_m03_27_el_lote_que_ya_inicio_su_recorrido_conserva_el_ingreso(reloj, reconocedor, supervisor,
                                                                          administrador, mineral, vehiculo,
                                                                          imagen_png):
    lotes = LotesFalsos(LoteDelIngreso("Lote 12", frozenset({mineral.pk}), False))
    servicio = construir(reloj, reconocedor, lotes=lotes)
    ingreso = registrar(servicio, reloj, supervisor, mineral, imagen_png)
    servicio.anular_ingreso(ingreso.pk, "No debió registrarse", administrador)
    assert lotes.retirados == []


def test_rn_m03_28_solo_se_revierte_la_ultima_correccion_vigente(
    servicio, reloj, supervisor, administrativo, mineral, vehiculo, imagen_png
):
    ingreso = registrar(servicio, reloj, supervisor, mineral, imagen_png)
    servicio.corregir_ingreso(ingreso.pk, {"peso_bruto_tn": Decimal("29.00")}, "Error", administrativo)
    correccion = EventoAuditoria.objects.filter(entidad="Ingreso", accion="MODIFICAR").order_by("id").last()
    servicio.revertir_correccion(ingreso.pk, "Volver", administrativo)
    reversion = EventoAuditoria.objects.filter(entidad="Ingreso", accion="MODIFICAR").order_by("id").last()
    assert reversion.valores_nuevos["revierte"] == correccion.pk
    assert EventoAuditoria.objects.filter(pk=correccion.pk).exists()
    with pytest.raises(ConflictoDeConcurrencia, match="no tiene una corrección vigente"):
        servicio.revertir_correccion(ingreso.pk, "Otra vez", administrativo)


def test_rn_m03_29_la_correccion_revertida_permanece_atribuida(servicio, reloj, supervisor, administrativo,
                                                              administrador, mineral, vehiculo, imagen_png):
    ingreso = registrar(servicio, reloj, supervisor, mineral, imagen_png)
    servicio.corregir_ingreso(ingreso.pk, {"peso_bruto_tn": Decimal("29.00")}, "Error", administrativo)
    servicio.revertir_correccion(ingreso.pk, "Volver al ticket", administrador)
    eventos = list(EventoAuditoria.objects.filter(entidad="Ingreso", id_entidad=ingreso.pk, accion="MODIFICAR")
                   .order_by("id"))
    assert [(e.valores_nuevos["operacion"], e.usuario, e.motivo) for e in eventos] == [
        ("CORRECCION", administrativo, "Error"), ("REVERSION", administrador, "Volver al ticket")]


def test_rn_m05_06_cada_regla_queda_con_su_momento_y_su_resolucion(reloj, supervisor, mineral, vehiculo,
                                                                   imagen_png):
    lector = ReconocedorDeterminista(
        {PLACA: ("V2K841", 0.5), FECHA: (FECHA_TICKET.isoformat(), 0.9), PESO_BRUTO: ("29.80", 0.9)})
    servicio = construir(reloj, lector)
    ingreso = registrar(servicio, reloj, supervisor, mineral, imagen_png)  # la placa se corrige al confirmar
    v3 = {r.momento: r for r in ingreso.validaciones.filter(regla="V3")}
    assert (v3["PROPUESTA"].cumple, v3["PROPUESTA"].resolucion) == (False, "CORREGIDA")
    assert (v3["CONFIRMACION"].cumple, v3["CONFIRMACION"].resolucion) == (True, "CORREGIDA")
    assert "placa=V2K841" in v3["PROPUESTA"].detalle


def test_rn_m03_19_la_tara_se_registra_una_sola_vez(servicio, reloj, supervisor, mineral, vehiculo_sin_tara,
                                                   imagen_png):
    registrar(servicio, reloj, supervisor, mineral, imagen_png, placa="E4R-208")
    servicio.registrar_destare(vehiculo_sin_tara.pk, Decimal("12.50"), supervisor)
    with pytest.raises(ConflictoDeConcurrencia, match="ya tiene tara registrada"):
        servicio.registrar_destare(vehiculo_sin_tara.pk, Decimal("12.50"), supervisor)


def test_rn_m03_20_la_tara_es_menor_que_cada_bruto_en_proceso(servicio, reloj, supervisor, mineral,
                                                             vehiculo_sin_tara, imagen_png):
    registrar(servicio, reloj, supervisor, mineral, imagen_png, placa="E4R-208", peso_bruto_tn=Decimal("20.00"))
    with pytest.raises(ErrorDeValidacionDeDominio, match="La tara no puede ser mayor"):
        servicio.registrar_destare(vehiculo_sin_tara.pk, Decimal("20.00"), supervisor)


def test_rn_m03_23_el_destare_no_se_fecha_en_el_futuro(servicio, reloj, supervisor, mineral, vehiculo_sin_tara,
                                                      imagen_png):
    registrar(servicio, reloj, supervisor, mineral, imagen_png, placa="E4R-208")
    with pytest.raises(ErrorDeValidacionDeDominio, match="posterior a la fecha actual"):
        servicio.registrar_destare(vehiculo_sin_tara.pk, Decimal("12.00"), supervisor,
                                   fecha_destare=reloj.ahora() + timedelta(minutes=1))


def test_hu_m05_01_ca11_v2_y_v4_se_evaluan_al_registrar_el_destare(servicio, reloj, supervisor, mineral,
                                                                    vehiculo_sin_tara, imagen_png):
    ingreso = registrar(servicio, reloj, supervisor, mineral, imagen_png, placa="E4R-208")
    assert set(ingreso.validaciones.filter(momento="CONFIRMACION").values_list("regla", flat=True)) == {
        "V1", "V3", "V5"}
    servicio.registrar_destare(vehiculo_sin_tara.pk, Decimal("12.50"), supervisor)
    assert set(ingreso.validaciones.filter(momento="DESTARE").values_list("regla", flat=True)) == {"V2", "V4"}


def test_rn_m03_24_el_aviso_del_supervisor_sobre_el_alta_de_minerales(servicio, supervisor, administrativo,
                                                                     imagen_png, imagen_jpg):
    assert servicio.iniciar_registro(supervisor, archivo=imagen_png)["puede_agregar_tipo_mineral"] is False
    assert servicio.iniciar_registro(administrativo, archivo=imagen_jpg)["puede_agregar_tipo_mineral"] is True
