"""Reglas RN-M06-01 a RN-M06-24, la integración con M03 (corrección y
anulación) y con M09 (historial del ingreso)."""

from decimal import Decimal

import pytest
from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.auditoria.models import EventoAuditoria
from apps.ingresos.models import Ingreso
from apps.trazabilidad.dominio import ETAPAS_POR_RUTA, Ruta
from apps.trazabilidad.models import EtapaProceso, LoteProceso, PasoEtapa
from apps.trazabilidad.services import leer_fraccion

from .conftest import LOTES

pytestmark = pytest.mark.django_db
PARTES = [{"nombre": "Molino", "fraccion": "1/3", "ruta": "MOLIENDA_ENSACADO"},
          {"nombre": "Zaranda", "fraccion": "2/3", "ruta": "ZARANDEO_ENSACADO"}]


def test_rn_m06_01_un_ingreso_en_un_solo_lote(lotes, nuevo_ingreso):
    ingreso = nuevo_ingreso()
    a, b = lotes.abrir("A"), lotes.abrir("B")
    lotes.asignar(a, ingreso)
    lotes.asignar(b, ingreso)
    assert Ingreso.objects.get(pk=ingreso.pk).lote_id == b["id"]
    assert lotes.detalle(a)["total"]["ingresos"] == 0


def test_rn_m06_02_otro_mineral_solo_con_autorizacion(lotes, nuevo_ingreso, otro_mineral):
    lote = lotes.abrir()
    ajeno = nuevo_ingreso(tipo_mineral=otro_mineral)
    assert lotes.asignar(lote, ajeno).status_code == 400
    assert lotes.asignar(lote, ajeno, autorizacion="Gerencia").status_code == 200


def test_rn_m06_03_el_anulado_sale_del_lote_abierto_y_queda_en_el_que_recorre(lotes, nuevo_ingreso):
    a, b, c = nuevo_ingreso(), nuevo_ingreso(), nuevo_ingreso()
    abierto = lotes.abrir("Abierto")
    lotes.asignar(abierto, a)
    recorre = lotes.en_recorrido(b, c, nombre="Recorre")
    for ingreso in (a, b):
        lotes.admin().patch(f"/api/v1/ingresos/{ingreso.pk}/anular/", {"motivo": "Error"}, format="json")
    a.refresh_from_db()
    b.refresh_from_db()
    assert a.lote_id is None and b.lote_id == recorre["id"]
    assert lotes.detalle(recorre)["total"] == {"ingresos": 1, "toneladas": "20.20"}


def test_hu_m03_03_ca08_la_anulacion_retira_del_lote_que_reune_ingresos(lotes, nuevo_ingreso):
    ingreso = nuevo_ingreso()
    lote = lotes.abrir()
    lotes.asignar(lote, ingreso)
    lotes.admin().patch(f"/api/v1/ingresos/{ingreso.pk}/anular/", {"motivo": "No debió registrarse"}, format="json")
    retiro = EventoAuditoria.objects.filter(entidad="Lote", valores_nuevos__operacion="RETIRAR").get()
    assert retiro.motivo == "Anulación del ingreso" and retiro.ingresos_relacionados == [ingreso.pk]


def test_hu_m03_03_ca06_el_anulado_no_cuenta_en_los_totales(lotes, nuevo_ingreso):
    a, b = nuevo_ingreso(), nuevo_ingreso()
    lote = lotes.en_recorrido(a, b)
    lotes.admin().patch(f"/api/v1/ingresos/{a.pk}/anular/", {"motivo": "Duplicado"}, format="json")
    assert lotes.detalle(lote)["total"]["toneladas"] == "20.20"
    assert lotes.sup().get(LOTES).data["results"][0]["toneladas"] == "20.20"


def test_hu_m03_02_ca09_mineral_fuera_de_la_lista_del_lote(lotes, nuevo_ingreso, otro_mineral, mineral):
    ingreso = nuevo_ingreso()
    lote = lotes.abrir()
    lotes.asignar(lote, ingreso)
    r = lotes.adm().patch(f"/api/v1/ingresos/{ingreso.pk}/", {"tipo_mineral": otro_mineral.pk, "motivo": "Error"},
                          format="json")
    assert r.status_code == 400
    assert r.data["mensaje"] == (f"{otro_mineral.nombre} no está en el lote {lote['nombre']}. "
                                 "Agregue ese mineral al lote para corregir el ingreso")


def test_hu_m03_02_ca11_el_lote_refleja_la_correccion(lotes, nuevo_ingreso):
    ingreso = nuevo_ingreso()
    lote = lotes.en_recorrido(ingreso)
    lotes.adm().patch(f"/api/v1/ingresos/{ingreso.pk}/", {"peso_bruto_tn": "30.00", "motivo": "Bruto real"},
                      format="json")
    assert lotes.detalle(lote)["total"]["toneladas"] == "17.70"
    lotes.adm().post(f"/api/v1/ingresos/{ingreso.pk}/revertir-correccion/", {"motivo": "Volver"}, format="json")
    assert lotes.detalle(lote)["total"]["toneladas"] == "20.20"


def test_rn_m06_04_retiro_hasta_el_zarandeo_y_el_tardio_por_sus_porciones(lotes, nuevo_ingreso):
    a, b = nuevo_ingreso(), nuevo_ingreso()
    lote = lotes.en_recorrido(a, b)
    lotes.etapa(lote, etapa="SECADO")
    tardio = nuevo_ingreso()
    lotes.asignar(lote, tardio)
    lotes.sup().post(f"{LOTES}{lote['id']}/ingresos/{tardio.pk}/secado/", {}, format="json")
    lotes.etapa(lote, ruta="ZARANDEO_ENSACADO")
    assert lotes.retirar(lote, a).status_code == 409  # el lote ya zarandeó
    assert lotes.retirar(lote, tardio).status_code == 200  # su porción aún no empezó la ruta


def test_rn_m06_05_solo_el_lote_en_recorrido_registra_etapas(lotes, nuevo_ingreso):
    assert lotes.etapa(lotes.abrir(), etapa="SECADO").status_code == 409


def test_rn_m06_06_las_etapas_siguen_el_orden_de_la_ruta(lotes, nuevo_ingreso):
    lote = lotes.en_recorrido(nuevo_ingreso())
    lotes.etapa(lote, etapa="SECADO")
    lotes.etapa(lote, ruta="ZARANDEO_MOLIENDA_ENSACADO")
    assert lotes.etapa(lote, etapa="ENSACADO").data["mensaje"] == "El lote debe pasar primero por la etapa Molienda"


def test_rn_m06_07_una_etapa_una_vez_por_carga(lotes, nuevo_ingreso, supervisor):
    lote = lotes.en_recorrido(nuevo_ingreso())
    lotes.etapa(lote, etapa="SECADO")
    secado = EtapaProceso.objects.get(codigo="SECADO")
    with pytest.raises(IntegrityError), transaction.atomic():
        PasoEtapa.objects.create(lote_id=lote["id"], etapa=secado, fecha_hora=timezone.now(),
                                 usuario_registro=supervisor, fecha_registro=timezone.now())


def test_rn_m06_08_fechas_coherentes(lotes, nuevo_ingreso):
    lote = lotes.en_recorrido(nuevo_ingreso())
    futura = (timezone.now() + timezone.timedelta(minutes=5)).isoformat()
    assert lotes.etapa(lote, etapa="SECADO", fecha_hora=futura).status_code == 400


def test_rn_m06_09_catalogos_cerrados(lotes):
    etapas = lotes.sup().get("/api/v1/etapas/").data
    rutas = lotes.sup().get("/api/v1/rutas/").data["rutas"]
    assert [e["codigo"] for e in etapas] == ["SECADO", "ZARANDEO", "MOLIENDA", "ENSACADO"]
    assert {r["codigo"]: r["etapas"] for r in rutas} == {
        "ZARANDEO_ENSACADO": ["ZARANDEO", "ENSACADO"], "MOLIENDA_ENSACADO": ["MOLIENDA", "ENSACADO"],
        "ZARANDEO_MOLIENDA_ENSACADO": ["ZARANDEO", "MOLIENDA", "ENSACADO"]}
    assert [r["nombre"] for r in rutas] == ["Zaranda", "Molido", "Zarandeado y molido"]
    assert all("SECADO" not in e for e in ETAPAS_POR_RUTA.values())
    assert lotes.admin().post("/api/v1/etapas/", {"codigo": "LAVADO"}, format="json").status_code == 405


def test_rn_m06_10_sin_ingresos_no_inicia(lotes, nuevo_ingreso):
    lote = lotes.abrir()
    ingreso = nuevo_ingreso()
    lotes.asignar(lote, ingreso)
    lotes.retirar(lote, ingreso)
    assert lotes.iniciar(lote).status_code == 409


def test_rn_m06_11_el_recorrido_del_ingreso_es_el_de_su_lote(lotes, nuevo_ingreso):
    ingreso = nuevo_ingreso()
    sin = lotes.sup().get(f"/api/v1/ingresos/{ingreso.pk}/trazabilidad/").data
    assert sin["lote"] is None and sin["lineas"] == []
    lote = lotes.en_recorrido(ingreso)
    lotes.etapa(lote, etapa="SECADO")
    con = lotes.sup().get(f"/api/v1/ingresos/{ingreso.pk}/trazabilidad/").data
    assert con["lote"]["codigo"] == lote["codigo"] and con["secado"]["completado"] is True


def test_rn_m06_12_la_etapa_queda_atribuida_a_quien_la_registro(lotes, nuevo_ingreso, administrador):
    lote = lotes.en_recorrido(nuevo_ingreso())
    lotes.etapa(lote, api=lotes.admin(), etapa="SECADO", usuario_registro=999)
    assert PasoEtapa.objects.get().usuario_registro == administrador


def test_rn_m06_13_el_en_proceso_no_entra_a_un_lote(lotes, nuevo_ingreso):
    r = lotes.asignar(lotes.abrir(), nuevo_ingreso(estado=Ingreso.EN_PROCESO, tara_tn=None, peso_neto_tn=None))
    assert r.status_code == 409


def test_rn_m06_14_nombre_unico(lotes):
    lotes.abrir("Cancha")
    with pytest.raises(IntegrityError), transaction.atomic():
        LoteProceso.objects.create(codigo="X", nombre="CANCHA", tipo_mineral_id=LoteProceso.objects.get().tipo_mineral_id,
                                   fecha_apertura=timezone.localdate(), usuario_registro_id=LoteProceso.objects.get()
                                   .usuario_registro_id, fecha_registro=timezone.now())


def test_rn_m06_15_sin_ruta_no_hay_etapa_posterior_al_secado(lotes, nuevo_ingreso):
    lote = lotes.en_recorrido(nuevo_ingreso())
    lotes.etapa(lote, etapa="SECADO")
    assert lotes.etapa(lote, etapa="ENSACADO").status_code == 400
    assert lotes.detalle(lote)["siguientes"] == [{"carga": "Lote 1", "parte": None, "ingreso": None, "etapa": None,
                                                  "elegir_ruta": True}]


def test_rn_m06_16_fracciones_exactas_en_sextos(lotes, nuevo_ingreso):
    lote = lotes.en_recorrido(nuevo_ingreso())
    seis = [{"nombre": f"P{n}", "fraccion": "1/6", "ruta": "ZARANDEO_ENSACADO"} for n in range(6)]
    assert lotes.dividir(lote, seis).status_code == 201
    assert sum(leer_fraccion(x) for x in ("1/3", "1/3", "1/3")) == 1
    assert leer_fraccion("50%") + leer_fraccion("0.5") == 1


def test_rn_m06_17_las_estimaciones_no_entran_en_el_total(lotes, nuevo_ingreso):
    lote = lotes.en_recorrido(nuevo_ingreso())
    lotes.etapa(lote, etapa="SECADO")
    lotes.etapa(lote, ruta="ZARANDEO_ENSACADO")
    lotes.etapa(lote, etapa="ENSACADO", bigbags={"cantidad": 2, "recalcular": True, "peso_aproximado_tn": "15.00"})
    d = lotes.sup().get(f"{LOTES}{lote['id']}/resumen/").data
    assert d["toneladas_registradas"] == "20.20" and d["ensacado_aproximado_tn"] == "30.00"


def test_rn_m06_18_el_tardio_tras_el_secado_queda_pendiente_de_su_secado(lotes, nuevo_ingreso):
    lote = lotes.en_recorrido(nuevo_ingreso())
    lotes.etapa(lote, etapa="SECADO")
    tardio = nuevo_ingreso()
    lotes.asignar(lote, tardio)
    assert f"{tardio.codigo}: falta su secado" in lotes.detalle(lote)["pendientes"]


def test_rn_m06_19_bigbags_solo_con_ensacado(lotes, nuevo_ingreso):
    lote = lotes.en_recorrido(nuevo_ingreso())
    assert lotes.sup().post(f"{LOTES}{lote['id']}/bigbags/", {"cantidad": 1}, format="json").status_code == 400


def test_rn_m06_20_cierre_del_administrador_con_todo_ensacado_y_destino(lotes, nuevo_ingreso):
    lote = lotes.en_recorrido(nuevo_ingreso())
    r = lotes.admin().patch(f"{LOTES}{lote['id']}/cerrar/", {"destino": "VENTA"}, format="json")
    assert r.status_code == 409 and r.data["detalles"]["pendientes"] == ["falta el secado del lote"]


def test_rn_m06_21_el_cerrado_no_admite_cambios(lotes, nuevo_ingreso):
    lote = lotes.completo(nuevo_ingreso())
    lotes.admin().patch(f"{LOTES}{lote['id']}/cerrar/", {"destino": "VENTA"}, format="json")
    for r in (lotes.asignar(lote, nuevo_ingreso()), lotes.etapa(lote, etapa="SECADO"),
              lotes.dividir(lote, PARTES)):
        assert r.status_code == 409


def test_rn_m06_22_proporcion_sobre_la_ruta_no_sobre_cuatro_etapas(lotes, nuevo_ingreso):
    ingreso = nuevo_ingreso()
    lotes.completo(ingreso, ruta="MOLIENDA_ENSACADO")
    d = lotes.sup().get(f"/api/v1/ingresos/{ingreso.pk}/trazabilidad/").data
    assert (d["etapas_recorridas"], d["etapas_totales"]) == (3, 3)


def test_rn_m06_23_solo_se_quita_un_mineral_sin_ingresos_y_con_el_lote_abierto(lotes, nuevo_ingreso, otro_mineral):
    lote = lotes.en_recorrido(nuevo_ingreso())
    lotes.adm().post(f"{LOTES}{lote['id']}/minerales/", {"tipo_mineral": otro_mineral.pk}, format="json")
    r = lotes.adm().post(f"{LOTES}{lote['id']}/minerales/{otro_mineral.pk}/quitar/")
    assert r.status_code == 409 and r.data["mensaje"] == "Solo se quitan minerales mientras el lote está Abierto"


def test_rn_m06_24_las_cifras_se_calculan_sobre_los_ingresos(lotes, nuevo_ingreso):
    ingreso = nuevo_ingreso()
    lote = lotes.en_recorrido(ingreso)
    partes = lotes.dividir(lote, PARTES).data["partes"]
    assert partes[0]["toneladas_aproximadas"] == "6.73"
    Ingreso.objects.filter(pk=ingreso.pk).update(peso_bruto_tn=Decimal("42.30"), peso_neto_tn=Decimal("30.00"))
    assert lotes.detalle(lote)["partes"][0]["toneladas_aproximadas"] == "10.00"


def test_hu_m09_02_ca03_el_historial_del_ingreso_incluye_su_lote(lotes, nuevo_ingreso):
    ingreso = nuevo_ingreso()
    lote = lotes.completo(ingreso)
    lotes.admin().patch(f"{LOTES}{lote['id']}/cerrar/", {"destino": "VENTA"}, format="json")
    eventos = lotes.sup().get(f"/api/v1/ingresos/{ingreso.pk}/historial/").data["results"]
    operaciones = [e["operacion"] for e in eventos if e["entidad"] == "Lote"]
    assert operaciones[:3] == ["ASIGNAR", "INICIAR_RECORRIDO", "ETAPA"] and operaciones[-1] == "CERRAR"


def test_rnf_m06_02_el_detalle_del_lote_no_recorre_los_ingresos_uno_a_uno(lotes, nuevo_ingreso,
                                                                          django_assert_max_num_queries):
    lote = lotes.abrir()
    lotes.asignar(lote, *[nuevo_ingreso() for _ in range(40)])
    with django_assert_max_num_queries(40):
        lotes.sup().get(f"{LOTES}{lote['id']}/")


def test_la_ruta_es_un_dominio_cerrado():
    assert set(Ruta.values) == {"ZARANDEO_ENSACADO", "MOLIENDA_ENSACADO", "ZARANDEO_MOLIENDA_ENSACADO"}
