"""Contrato HTTP de M06, un caso por criterio de HU-M06-01 a HU-M06-05."""

from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from apps.auditoria.models import EventoAuditoria
from apps.ingresos.models import Ingreso
from apps.trazabilidad.models import Bigbag, LoteMineral, PasoEtapa

from .conftest import LOTES

pytestmark = pytest.mark.django_db
NAU = "Acción no autorizada"


# HU-M06-01 — Gestión de lotes


def test_hu_m06_01_ca01_abrir_lote(lotes):
    r = lotes.adm().post(LOTES, {"nombre": "Cancha norte", "tipo_mineral": lotes.abrir("x")["composicion"][0]
                                 ["tipo_mineral"]["id"], "fecha_apertura": timezone.localdate().isoformat()},
                         format="json")
    assert r.status_code == 201 and r.data["mensaje"] == "Lote Cancha norte abierto"
    assert r.data["estado"] == "ABIERTO" and r.data["codigo"].startswith("LOT-")


def test_hu_m06_01_ca02_nombre_duplicado(lotes, mineral):
    lotes.abrir("Cancha norte")
    r = lotes.adm().post(LOTES, {"nombre": "cancha NORTE", "tipo_mineral": mineral.pk,
                                 "fecha_apertura": timezone.localdate().isoformat()}, format="json")
    assert r.status_code == 400 and r.data["mensaje"] == "Ya existe un lote con el nombre «cancha NORTE»"


def test_hu_m06_01_ca03_apertura_futura(lotes, mineral):
    r = lotes.adm().post(LOTES, {"nombre": "Futuro", "tipo_mineral": mineral.pk,
                                 "fecha_apertura": (timezone.localdate() + timedelta(days=1)).isoformat()},
                         format="json")
    assert r.status_code == 400 and r.data["mensaje"] == "La fecha de apertura no puede ser posterior a hoy"


def test_hu_m06_01_ca04_asignar_y_totales_por_mineral(lotes, nuevo_ingreso):
    lote = lotes.abrir()
    r = lotes.asignar(lote, nuevo_ingreso(), nuevo_ingreso())
    assert r.status_code == 200
    assert r.data["total"] == {"ingresos": 2, "toneladas": "40.40"}
    assert (r.data["composicion"][0]["cantidad"], r.data["composicion"][0]["toneladas"]) == (2, "40.40")


def test_hu_m06_01_ca05_otro_mineral_se_ofrece_aparte(lotes, nuevo_ingreso, otro_mineral):
    lote = lotes.abrir()
    propio, ajeno = nuevo_ingreso(), nuevo_ingreso(tipo_mineral=otro_mineral)
    d = lotes.adm().get(f"{LOTES}{lote['id']}/ingresos/").data
    assert [i["id"] for i in d["ingresos"]] == [propio.pk]
    assert d["otros_minerales"][0]["tipo_mineral"]["codigo"] == "MOB"
    assert [i["id"] for i in d["otros_minerales"][0]["ingresos"]] == [ajeno.pk]


def test_hu_m06_01_ca06_ingreso_anulado(lotes, nuevo_ingreso):
    r = lotes.asignar(lotes.abrir(), nuevo_ingreso(estado=Ingreso.ANULADO, motivo_anulacion="Duplicado"))
    assert r.status_code == 409 and r.data["mensaje"] == "No se puede asignar un ingreso anulado"


def test_hu_m06_01_ca07_ingreso_en_proceso(lotes, nuevo_ingreso):
    ingreso = nuevo_ingreso(estado=Ingreso.EN_PROCESO, tara_tn=None, peso_neto_tn=None)
    r = lotes.asignar(lotes.abrir(), ingreso)
    assert r.status_code == 409
    assert r.data["mensaje"] == f"El ingreso {ingreso.codigo} está en proceso: falta el destare del vehículo"


def test_hu_m06_01_ca08_traslado_con_constancia_en_ambos_lotes(lotes, nuevo_ingreso):
    ingreso = nuevo_ingreso()
    origen, destino = lotes.abrir("Origen"), lotes.abrir("Destino")
    lotes.asignar(origen, ingreso)
    assert lotes.asignar(destino, ingreso).status_code == 200
    ingreso.refresh_from_db()
    assert ingreso.lote_id == destino["id"]
    ops = {(e.id_entidad, e.valores_nuevos["operacion"]) for e in EventoAuditoria.objects.filter(entidad="Lote")}
    assert (origen["id"], "TRASLADAR") in ops and (destino["id"], "ASIGNAR") in ops


def test_hu_m06_01_ca09_no_se_retira_tras_zarandeo(lotes, nuevo_ingreso):
    a, b = nuevo_ingreso(), nuevo_ingreso()
    lote = lotes.en_recorrido(a, b)
    lotes.etapa(lote, etapa="SECADO")
    lotes.etapa(lote, ruta="ZARANDEO_ENSACADO")
    r = lotes.retirar(lote, a)
    assert r.status_code == 409 and r.data["mensaje"] == f"El mineral del ingreso {a.codigo} ya pasó por zarandeo o molienda"
    traslado = lotes.asignar(lotes.abrir("Otro"), a)
    assert traslado.status_code == 409


def test_hu_m06_01_ca10_iniciar_recorrido(lotes, nuevo_ingreso):
    lote = lotes.abrir()
    lotes.asignar(lote, nuevo_ingreso())
    r = lotes.iniciar(lote)
    assert r.status_code == 200 and r.data["mensaje"] == "Recorrido del lote Lote 1 iniciado"
    assert r.data["estado"] == "EN_RECORRIDO" and r.data["fecha_inicio_recorrido"]


def test_hu_m06_01_ca11_sin_ingresos_no_inicia(lotes):
    r = lotes.iniciar(lotes.abrir())
    assert r.status_code == 409 and r.data["mensaje"] == "El lote no tiene ingresos asignados"


def test_hu_m06_01_ca12_tardio_antes_del_secado_se_seca_con_el_lote(lotes, nuevo_ingreso):
    lote = lotes.en_recorrido(nuevo_ingreso())
    tardio = nuevo_ingreso()
    assert lotes.asignar(lote, tardio).status_code == 200
    fila = next(i for i in lotes.detalle(lote)["composicion"][0]["ingresos"] if i["id"] == tardio.pk)
    assert (fila["tardio"], fila["secado_propio"]) == (True, False)


def test_hu_m06_01_ca13_tardio_despues_del_secado_tiene_secado_propio(lotes, nuevo_ingreso):
    lote = lotes.en_recorrido(nuevo_ingreso())
    lotes.etapa(lote, etapa="SECADO")
    tardio = nuevo_ingreso()
    lotes.asignar(lote, tardio)
    fila = next(i for i in lotes.detalle(lote)["composicion"][0]["ingresos"] if i["id"] == tardio.pk)
    assert (fila["tardio"], fila["secado_propio"]) == (True, True)


def test_hu_m06_01_ca14_sin_seleccion(lotes):
    r = lotes.asignar(lotes.abrir())
    assert r.status_code == 400 and r.data["mensaje"] == "Seleccione al menos un ingreso"


def test_hu_m06_01_ca15_el_supervisor_no_compone_lotes(lotes, nuevo_ingreso, mineral):
    lote = lotes.abrir()
    sup = lotes.sup()
    ingreso = nuevo_ingreso()
    for r in (
        sup.post(LOTES, {"nombre": "X", "tipo_mineral": mineral.pk,
                         "fecha_apertura": timezone.localdate().isoformat()}, format="json"),
        lotes.asignar(lote, ingreso, api=sup),
        lotes.retirar(lote, ingreso, api=sup),
        lotes.iniciar(lote, api=sup),
    ):
        assert r.status_code in (403, 404)
    assert lotes.asignar(lote, ingreso, api=lotes.sup()).data["mensaje"] == NAU


def test_hu_m06_01_ca16_detalle_con_composicion_tardios_y_total(lotes, nuevo_ingreso):
    lote = lotes.en_recorrido(nuevo_ingreso())
    lotes.asignar(lote, nuevo_ingreso())
    d = lotes.detalle(lote)
    assert d["estado"] == "EN_RECORRIDO" and d["total"]["toneladas"] == "40.40"
    filas = d["composicion"][0]["ingresos"]
    assert {"codigo", "fecha_hora_pesaje", "peso_neto_tn", "tardio"} <= set(filas[0])
    assert sorted(f["tardio"] for f in filas) == [False, True]


def test_hu_m06_01_ca17_agregar_otro_mineral(lotes, otro_mineral):
    lote = lotes.abrir()
    r = lotes.adm().post(f"{LOTES}{lote['id']}/minerales/", {"tipo_mineral": otro_mineral.pk}, format="json")
    assert r.status_code == 200 and r.data["mensaje"] == "Mineral óxido tipo B agregado al lote"
    grupo = next(g for g in r.data["composicion"] if g["tipo_mineral"]["codigo"] == "MOB")
    assert grupo["ingresos"] == [] and grupo["cantidad"] == 0
    assert EventoAuditoria.objects.filter(entidad="Lote", valores_nuevos__operacion="AGREGAR_MINERAL").exists()


def test_hu_m06_01_ca18_mineral_repetido(lotes, mineral):
    lote = lotes.abrir()
    r = lotes.adm().post(f"{LOTES}{lote['id']}/minerales/", {"tipo_mineral": mineral.pk}, format="json")
    assert r.status_code == 409 and r.data["mensaje"] == f"El mineral {mineral.nombre} ya está en el lote"


def test_hu_m06_01_ca19_quitar_mineral_con_ingresos(lotes, nuevo_ingreso, mineral, otro_mineral):
    lote = lotes.abrir()
    lotes.asignar(lote, nuevo_ingreso())
    lotes.adm().post(f"{LOTES}{lote['id']}/minerales/", {"tipo_mineral": otro_mineral.pk}, format="json")
    r = lotes.adm().post(f"{LOTES}{lote['id']}/minerales/{mineral.pk}/quitar/")
    assert r.status_code == 409 and r.data["mensaje"] == f"No se puede quitar {mineral.nombre}: tiene ingresos en el lote"
    sin = lotes.adm().post(f"{LOTES}{lote['id']}/minerales/{otro_mineral.pk}/quitar/")
    assert sin.status_code == 200 and sin.data["mensaje"] == "Mineral óxido tipo B quitado del lote"
    assert LoteMineral.objects.filter(tipo_mineral=otro_mineral, fecha_retiro__isnull=False).exists()


def test_hu_m06_01_ca20_otro_mineral_sin_autorizacion(lotes, nuevo_ingreso, otro_mineral):
    r = lotes.asignar(lotes.abrir(), nuevo_ingreso(tipo_mineral=otro_mineral))
    assert r.status_code == 400
    assert r.data["mensaje"] == "Indique quién autorizó o el motivo para unificar otro tipo de mineral"


def test_hu_m06_01_ca21_otro_mineral_con_autorizacion(lotes, nuevo_ingreso, otro_mineral):
    lote = lotes.abrir()
    r = lotes.asignar(lote, nuevo_ingreso(tipo_mineral=otro_mineral), autorizacion="Aprobado por el gerente")
    grupo = next(g for g in r.data["composicion"] if g["tipo_mineral"]["codigo"] == "MOB")
    assert grupo["otro_mineral"] is True and grupo["autorizacion"] == "Aprobado por el gerente"
    assert grupo["ingresos"][0]["otro_mineral"] is True
    ops = [e.valores_nuevos["operacion"] for e in EventoAuditoria.objects.filter(entidad="Lote").order_by("id")]
    assert ops[-2:] == ["AGREGAR_MINERAL", "ASIGNAR"]


def test_hu_m06_01_ca22_retiro_en_recorrido_conserva_el_secado(lotes, nuevo_ingreso):
    a, b = nuevo_ingreso(), nuevo_ingreso()
    lote = lotes.en_recorrido(a, b)
    lotes.etapa(lote, etapa="SECADO")
    r = lotes.retirar(lote, a)
    assert r.status_code == 200 and r.data["mensaje"] == "Ingreso retirado del lote"
    assert r.data["total"]["toneladas"] == "20.20"
    assert PasoEtapa.objects.filter(lote_id=lote["id"], etapa__codigo="SECADO").exists()
    a.refresh_from_db()
    assert a.lote_id is None
    assert EventoAuditoria.objects.filter(entidad="Lote", valores_nuevos__operacion="RETIRAR").exists()


def test_hu_m06_01_ca23_el_lote_en_recorrido_conserva_un_ingreso(lotes, nuevo_ingreso):
    unico = nuevo_ingreso()
    lote = lotes.en_recorrido(unico)
    r = lotes.retirar(lote, unico)
    assert r.status_code == 409
    assert r.data["mensaje"] == f"El lote {lote['codigo']} en recorrido debe conservar al menos un ingreso"


# HU-M06-02 — Paso por etapa


def test_hu_m06_02_ca01_secado_y_ruta(lotes, nuevo_ingreso):
    lote = lotes.en_recorrido(nuevo_ingreso())
    r = lotes.etapa(lote, etapa="SECADO")
    assert r.status_code == 201 and r.data["mensaje"] == "Etapa Secado registrada para Lote 1"
    r = lotes.etapa(lote, ruta="MOLIENDA_ENSACADO")
    assert r.data["mensaje"] == "Etapa Molienda registrada para Lote 1" and r.data["ruta"] == "MOLIENDA_ENSACADO"


def test_hu_m06_02_ca02_elegir_la_ruta(lotes, nuevo_ingreso):
    lote = lotes.en_recorrido(nuevo_ingreso())
    lotes.etapa(lote, etapa="SECADO")
    r = lotes.etapa(lote, etapa="ZARANDEO")
    assert r.status_code == 400 and r.data["mensaje"] == "Elija qué etapa sigue después del secado"


def test_hu_m06_02_ca03_etapa_previa(lotes, nuevo_ingreso):
    lote = lotes.en_recorrido(nuevo_ingreso())
    r = lotes.etapa(lote, etapa="ZARANDEO")
    assert r.status_code == 400 and r.data["mensaje"] == "El lote debe pasar primero por la etapa Secado"
    lotes.etapa(lote, etapa="SECADO")
    r = lotes.etapa(lote, ruta="ZARANDEO_MOLIENDA_ENSACADO", etapa="MOLIENDA")
    assert r.data["mensaje"] == "El lote debe pasar primero por la etapa Zarandeo"


def test_hu_m06_02_ca04_etapa_repetida(lotes, nuevo_ingreso):
    lote = lotes.en_recorrido(nuevo_ingreso())
    lotes.etapa(lote, etapa="SECADO")
    r = lotes.etapa(lote, etapa="SECADO")
    assert r.status_code == 409 and r.data["mensaje"] == "La etapa Secado ya fue registrada para Lote 1"


def test_hu_m06_02_ca05_lote_abierto(lotes):
    r = lotes.etapa(lotes.abrir(), etapa="SECADO")
    assert r.status_code == 409 and r.data["mensaje"] == "El lote debe iniciar su recorrido antes de registrar etapas"


def test_hu_m06_02_ca06_fecha_futura(lotes, nuevo_ingreso):
    lote = lotes.en_recorrido(nuevo_ingreso())
    r = lotes.etapa(lote, etapa="SECADO", fecha_hora=(timezone.now() + timedelta(hours=1)).isoformat())
    assert r.status_code == 400 and r.data["mensaje"] == "La fecha de la etapa no puede ser posterior a la fecha actual"


def test_hu_m06_02_ca07_fecha_anterior_a_la_etapa_previa(lotes, nuevo_ingreso):
    lote = lotes.en_recorrido(nuevo_ingreso())
    lotes.etapa(lote, etapa="SECADO")
    r = lotes.etapa(lote, ruta="ZARANDEO_ENSACADO", fecha_hora=(timezone.now() - timedelta(hours=1)).isoformat())
    assert r.status_code == 400 and r.data["mensaje"] == "La fecha de la etapa no puede ser anterior a la de la etapa Secado"


def test_hu_m06_02_ca08_fecha_anterior_al_inicio(lotes, nuevo_ingreso):
    lote = lotes.en_recorrido(nuevo_ingreso())
    r = lotes.etapa(lote, etapa="SECADO", fecha_hora=(timezone.now() - timedelta(days=1)).isoformat())
    assert r.status_code == 400 and r.data["mensaje"] == "La fecha de la etapa no puede ser anterior al inicio del recorrido"


def test_hu_m06_02_ca09_ruta_completa(lotes, nuevo_ingreso):
    lote = lotes.completo(nuevo_ingreso())
    r = lotes.etapa(lote, etapa="MOLIENDA")
    assert r.status_code == 409 and r.data["mensaje"] == "No hay etapas pendientes para este lote"


def test_hu_m06_02_ca10_horas_de_molienda(lotes, nuevo_ingreso):
    lote = lotes.en_recorrido(nuevo_ingreso())
    lotes.etapa(lote, etapa="SECADO")
    r = lotes.etapa(lote, ruta="MOLIENDA_ENSACADO", horas_molienda="0")
    assert r.status_code == 400 and r.data["mensaje"] == "Las horas de molienda deben ser mayores que cero"
    r = lotes.etapa(lote, ruta="MOLIENDA_ENSACADO", horas_molienda="4.04")
    assert r.status_code == 201 and r.data["paso"]["toneladas_por_hora"] == "5.00"


def test_hu_m06_02_ca11_bigbags_al_ensacar(lotes, nuevo_ingreso):
    lote = lotes.en_recorrido(nuevo_ingreso())
    lotes.etapa(lote, etapa="SECADO")
    lotes.etapa(lote, ruta="ZARANDEO_ENSACADO")
    r = lotes.etapa(lote, etapa="ENSACADO", bigbags={"cantidad": 4})
    assert r.status_code == 201
    assert r.data["paso"]["bigbags"] == {"cantidad": 4, "peso_aproximado_tn": "5.05", "recalculado": False,
                                         "es_estimacion": True}


def test_hu_m06_02_ca12_ya_ensacado_sin_recalcular(lotes, nuevo_ingreso):
    lote = lotes.completo(nuevo_ingreso())
    url = f"{LOTES}{lote['id']}/bigbags/"
    assert lotes.sup().post(url, {"cantidad": 2}, format="json").status_code == 201
    r = lotes.sup().post(url, {"cantidad": 1}, format="json")
    assert r.status_code == 400
    assert r.data["mensaje"] == "Lo registrado ya está ensacado: marque Recalcular e indique el peso de cada bigbag"
    r = lotes.sup().post(url, {"cantidad": 1, "recalcular": True, "peso_aproximado_tn": "1.10"}, format="json")
    assert r.status_code == 201 and r.data["registro"]["recalculado"] is True


def test_hu_m06_02_ca13_bigbags_sin_ensacado(lotes, nuevo_ingreso):
    lote = lotes.en_recorrido(nuevo_ingreso())
    r = lotes.sup().post(f"{LOTES}{lote['id']}/bigbags/", {"cantidad": 2}, format="json")
    assert r.status_code == 400 and r.data["mensaje"] == "Los bigbags se asocian al registrar el ensacado"


def test_hu_m06_02_ca14_secado_propio_del_tardio(lotes, nuevo_ingreso):
    lote = lotes.en_recorrido(nuevo_ingreso())
    lotes.etapa(lote, etapa="SECADO")
    tardio = nuevo_ingreso()
    lotes.asignar(lote, tardio)
    r = lotes.sup().post(f"{LOTES}{lote['id']}/ingresos/{tardio.pk}/secado/", {}, format="json")
    assert r.status_code == 201 and r.data["mensaje"] == f"Secado de {tardio.codigo} registrado"
    assert PasoEtapa.objects.filter(ingreso_tardio=tardio, etapa__codigo="SECADO").exists()
    # Sus porciones esperan la ruta del lote: aún no puede avanzar por su cuenta.
    r = lotes.etapa(lote, ingreso=tardio.pk, etapa="ZARANDEO")
    assert r.status_code == 400 and r.data["mensaje"] == "Elija qué etapa sigue después del secado"


def test_hu_m06_02_ca15_lote_cerrado_no_registra(lotes, nuevo_ingreso):
    lote = lotes.completo(nuevo_ingreso())
    lotes.admin().patch(f"{LOTES}{lote['id']}/cerrar/", {"destino": "VENTA"}, format="json")
    r = lotes.etapa(lote, etapa="SECADO")
    assert r.status_code == 409 and r.data["mensaje"] == f"El lote {lote['codigo']} ya fue cerrado"
    r = lotes.sup().post(f"{LOTES}{lote['id']}/bigbags/", {"cantidad": 1}, format="json")
    assert r.status_code == 409


def test_hu_m06_02_ca16_paso_atribuido_y_auditado(lotes, nuevo_ingreso, supervisor):
    ingreso = nuevo_ingreso()
    lote = lotes.en_recorrido(ingreso)
    lotes.etapa(lote, etapa="SECADO")
    assert PasoEtapa.objects.get(lote_id=lote["id"]).usuario_registro == supervisor
    evento = EventoAuditoria.objects.filter(entidad="Lote", valores_nuevos__operacion="ETAPA").get()
    assert evento.usuario == supervisor and evento.ingresos_relacionados == [ingreso.pk]


# HU-M06-03 — Trazabilidad de un ingreso


def trazabilidad(api, ingreso):
    return api.get(f"/api/v1/ingresos/{ingreso.pk}/trazabilidad/").data


def test_hu_m06_03_ca01_etapas_de_la_ruta_con_fecha_y_responsable(lotes, nuevo_ingreso, supervisor):
    ingreso = nuevo_ingreso()
    lote = lotes.en_recorrido(ingreso)
    lotes.etapa(lote, etapa="SECADO")
    lotes.etapa(lote, ruta="ZARANDEO_ENSACADO")
    d = trazabilidad(lotes.adm(), ingreso)
    etapas = d["lineas"][0]["etapas"]
    assert [(e["codigo"], e["completada"]) for e in etapas] == [("SECADO", True), ("ZARANDEO", True),
                                                                 ("ENSACADO", False)]
    assert etapas[0]["usuario"] == supervisor.username and etapas[0]["fecha_hora"]


def test_hu_m06_03_ca02_sin_lote(lotes, nuevo_ingreso):
    d = trazabilidad(lotes.sup(), nuevo_ingreso())
    assert d["lote"] is None and d["etapas_recorridas"] == 0
    assert d["mensaje"] == "El ingreso aún no tiene lote y no ha recorrido ninguna etapa"


def test_hu_m06_03_ca03_proceso_completo_sin_contar_cuatro_etapas(lotes, nuevo_ingreso):
    ingreso = nuevo_ingreso()
    lotes.completo(ingreso, ruta="ZARANDEO_ENSACADO")
    d = trazabilidad(lotes.sup(), ingreso)
    assert d["proceso_completo"] is True and (d["etapas_recorridas"], d["etapas_totales"]) == (3, 3)


def test_hu_m06_03_ca04_recorridas_sobre_el_total_de_la_ruta(lotes, nuevo_ingreso):
    ingreso = nuevo_ingreso()
    lote = lotes.en_recorrido(ingreso)
    lotes.etapa(lote, etapa="SECADO")
    lotes.etapa(lote, ruta="ZARANDEO_MOLIENDA_ENSACADO")
    d = trazabilidad(lotes.sup(), ingreso)
    assert (d["etapas_recorridas"], d["etapas_totales"]) == (2, 4)


def test_hu_m06_03_ca05_anulado_despues_de_asignado(lotes, nuevo_ingreso, administrador):
    a, b = nuevo_ingreso(), nuevo_ingreso()
    lotes.en_recorrido(a, b)
    lotes.admin().patch(f"/api/v1/ingresos/{a.pk}/anular/", {"motivo": "Duplicado"}, format="json")
    d = trazabilidad(lotes.sup(), a)
    assert d["anulado"] is True and d["lote"] is not None


def test_hu_m06_03_ca06_lote_dividido_sobre_la_union_de_rutas(lotes, nuevo_ingreso):
    """CP07: una parte zarandeada y otra molida suman cuatro etapas de cuatro."""
    ingreso = nuevo_ingreso()
    lote = lotes.en_recorrido(ingreso)
    lotes.etapa(lote, etapa="SECADO")
    r = lotes.dividir(lote, [{"nombre": "Molino", "fraccion": "1/3", "ruta": "MOLIENDA_ENSACADO"},
                             {"nombre": "Zaranda", "fraccion": "2/3", "ruta": "ZARANDEO_ENSACADO"}])
    partes = {p["nombre"]: p["id"] for p in r.data["partes"]}
    for parte, etapas in (("Molino", ["MOLIENDA", "ENSACADO"]), ("Zaranda", ["ZARANDEO", "ENSACADO"])):
        for etapa in etapas:
            assert lotes.etapa(lote, parte=partes[parte], etapa=etapa).status_code == 201
    d = trazabilidad(lotes.sup(), ingreso)
    assert [linea["nombre"] for linea in d["lineas"]] == ["Molino", "Zaranda"]
    assert (d["etapas_recorridas"], d["etapas_totales"], d["proceso_completo"]) == (4, 4, True)


def test_hu_m06_03_ca07_ruta_por_decidir_sin_proporcion(lotes, nuevo_ingreso):
    ingreso = nuevo_ingreso()
    lote = lotes.en_recorrido(ingreso)
    lotes.etapa(lote, etapa="SECADO")
    d = trazabilidad(lotes.sup(), ingreso)
    assert d["secado"]["completado"] is True and d["ruta_por_decidir"] is True and d["etapas_totales"] is None


def test_hu_m06_03_ca08_lote_cerrado_con_destino_y_fecha(lotes, nuevo_ingreso):
    ingreso = nuevo_ingreso()
    lote = lotes.completo(ingreso)
    lotes.admin().patch(f"{LOTES}{lote['id']}/cerrar/", {"destino": "TRASLADO"}, format="json")
    d = trazabilidad(lotes.sup(), ingreso)
    assert d["lote"]["destino"] == "TRASLADO" and d["lote"]["fecha_cierre"]


# HU-M06-04 — División


PARTES = [{"nombre": "Molino", "fraccion": "1/3", "ruta": "MOLIENDA_ENSACADO"},
          {"nombre": "Zaranda", "fraccion": "2/3", "ruta": "ZARANDEO_ENSACADO"}]


def test_hu_m06_04_ca01_division_en_tercios(lotes, nuevo_ingreso):
    lote = lotes.en_recorrido(nuevo_ingreso())
    r = lotes.dividir(lote, PARTES)
    assert r.status_code == 201 and r.data["mensaje"] == "Lote dividido en 2 partes"


def test_hu_m06_04_ca02_campos_de_cada_parte(lotes, nuevo_ingreso):
    lote = lotes.en_recorrido(nuevo_ingreso())
    r = lotes.dividir(lote, [{"nombre": "A", "fraccion": "1/2", "ruta": ""}, PARTES[1]])
    assert r.status_code == 400 and r.data["mensaje"] == "Debe completar los campos obligatorios de cada parte"


def test_hu_m06_04_ca03_nombres_distintos(lotes, nuevo_ingreso):
    lote = lotes.en_recorrido(nuevo_ingreso())
    r = lotes.dividir(lote, [{**PARTES[0], "nombre": "Uno"}, {**PARTES[1], "nombre": "uno"}])
    assert r.status_code == 400 and r.data["mensaje"] == "Cada parte debe tener un nombre distinto"


def test_hu_m06_04_ca04_fracciones_que_no_suman(lotes, nuevo_ingreso):
    lote = lotes.en_recorrido(nuevo_ingreso())
    r = lotes.dividir(lote, [{**PARTES[0], "fraccion": "1/2"}, {**PARTES[1], "fraccion": "1/3"}])
    assert r.status_code == 400 and r.data["mensaje"] == "Las fracciones suman 5/6 y deben sumar la unidad"


def test_hu_m06_04_ca05_mas_de_seis_partes(lotes, nuevo_ingreso):
    lote = lotes.en_recorrido(nuevo_ingreso())
    siete = [{"nombre": f"P{n}", "fraccion": "1/7", "ruta": "ZARANDEO_ENSACADO"} for n in range(7)]
    r = lotes.dividir(lote, siete)
    assert r.status_code == 400 and r.data["mensaje"] == "Puede dividir el lote en seis partes como máximo"


def test_hu_m06_04_ca06_ya_dividido(lotes, nuevo_ingreso):
    lote = lotes.en_recorrido(nuevo_ingreso())
    lotes.dividir(lote, PARTES)
    r = lotes.dividir(lote, [{**p, "nombre": p["nombre"] + "2"} for p in PARTES])
    assert r.status_code == 409 and r.data["mensaje"] == "El lote ya fue dividido"


def test_hu_m06_04_ca07_ya_avanzo_por_su_ruta(lotes, nuevo_ingreso):
    lote = lotes.en_recorrido(nuevo_ingreso())
    lotes.etapa(lote, etapa="SECADO")
    lotes.etapa(lote, ruta="ZARANDEO_ENSACADO")
    r = lotes.dividir(lote, PARTES)
    assert r.status_code == 409 and r.data["mensaje"] == "No se puede dividir: el lote ya avanzó por su ruta"


def test_hu_m06_04_ca08_partes_con_estimacion(lotes, nuevo_ingreso):
    lote = lotes.en_recorrido(nuevo_ingreso(), nuevo_ingreso(), nuevo_ingreso())
    partes = lotes.dividir(lote, PARTES).data["partes"]
    assert [(p["fraccion"], p["toneladas_aproximadas"], p["es_estimacion"]) for p in partes] == [
        ("1/3", "20.20", True), ("2/3", "40.40", True)]


def test_hu_m06_04_ca09_reparto_del_tardio(lotes, nuevo_ingreso):
    lote = lotes.en_recorrido(nuevo_ingreso())
    lotes.etapa(lote, etapa="SECADO")
    partes = {p["nombre"]: p["id"] for p in lotes.dividir(lote, PARTES).data["partes"]}
    tardio = nuevo_ingreso()
    lotes.asignar(lote, tardio)
    url = f"{LOTES}{lote['id']}/ingresos/{tardio.pk}/secado/"
    r = lotes.sup().post(url, {"fracciones": [{"parte": partes["Molino"], "fraccion": "1/2"},
                                              {"parte": partes["Zaranda"], "fraccion": "1/4"}]}, format="json")
    assert r.status_code == 400 and r.data["mensaje"] == "Las fracciones del reparto suman 3/4 y deben sumar la unidad"
    r = lotes.sup().post(url, {}, format="json")  # por defecto, las del lote
    assert r.status_code == 201
    assert sorted((rp.numerador, rp.denominador) for rp in tardio.repartos.all()) == [(1, 3), (2, 3)]


def test_hu_m06_04_ca10_el_supervisor_no_divide(lotes, nuevo_ingreso):
    lote = lotes.en_recorrido(nuevo_ingreso())
    r = lotes.dividir(lote, PARTES, api=lotes.sup())
    assert r.status_code == 403 and r.data["mensaje"] == NAU


# HU-M06-05 — Cierre


def cerrar(lotes, lote, api=None, **datos):
    return (api or lotes.admin()).patch(f"{LOTES}{lote['id']}/cerrar/", datos, format="json")


def test_hu_m06_05_ca01_cierre_con_destino(lotes, nuevo_ingreso, administrador):
    lote = lotes.completo(nuevo_ingreso())
    r = cerrar(lotes, lote, destino="VENTA")
    assert r.status_code == 200 and r.data["mensaje"] == "Lote Lote 1 cerrado con destino venta"
    assert r.data["estado"] == "CERRADO" and r.data["usuario_cierre"] == administrador.username and r.data["fecha_cierre"]


def test_hu_m06_05_ca02_pendientes(lotes, nuevo_ingreso):
    lote = lotes.en_recorrido(nuevo_ingreso())
    lotes.etapa(lote, etapa="SECADO")
    r = cerrar(lotes, lote, destino="VENTA")
    assert r.status_code == 409
    assert r.data["mensaje"] == "Todavía no se puede cerrar el lote. Pendiente: Lote 1: definir la ruta"


def test_hu_m06_05_ca03_sin_destino(lotes, nuevo_ingreso):
    lote = lotes.completo(nuevo_ingreso())
    r = cerrar(lotes, lote)
    assert r.status_code == 400 and r.data["mensaje"] == "Debe indicar el destino del lote"


def test_hu_m06_05_ca04_ya_cerrado(lotes, nuevo_ingreso):
    lote = lotes.completo(nuevo_ingreso())
    cerrar(lotes, lote, destino="VENTA")
    r = cerrar(lotes, lote, destino="VENTA")
    assert r.status_code == 409 and r.data["mensaje"] == "El lote ya fue cerrado"


@pytest.mark.parametrize("rol", ["adm", "sup"])
def test_hu_m06_05_ca05_solo_el_administrador_cierra(lotes, nuevo_ingreso, rol):
    lote = lotes.completo(nuevo_ingreso())
    r = cerrar(lotes, lote, api=getattr(lotes, rol)(), destino="VENTA")
    assert r.status_code == 403 and r.data["mensaje"] == NAU


def test_hu_m06_05_ca06_resumen_con_estimacion(lotes, nuevo_ingreso):
    lote = lotes.en_recorrido(nuevo_ingreso(), nuevo_ingreso())
    lotes.etapa(lote, etapa="SECADO")
    lotes.etapa(lote, ruta="MOLIENDA_ENSACADO", horas_molienda="8.08")
    lotes.etapa(lote, etapa="ENSACADO", bigbags={"cantidad": 4, "recalcular": True, "peso_aproximado_tn": "10.00"})
    d = lotes.sup().get(f"{LOTES}{lote['id']}/resumen/").data
    assert (d["pendientes"], d["toneladas_registradas"], d["bigbags"]) == ([], "40.40", 4)
    assert (d["ensacado_aproximado_tn"], d["diferencia_tn"], d["es_estimacion"]) == ("40.00", "-0.40", True)
    assert d["partes"][0]["toneladas_por_hora"] == "5.00" and d["horas_desde_inicio"] is not None


def test_hu_m06_05_ca07_cerrado_no_admite_ingresos(lotes, nuevo_ingreso):
    lote = lotes.completo(nuevo_ingreso())
    cerrar(lotes, lote, destino="VENTA")
    r = lotes.asignar(lote, nuevo_ingreso())
    assert r.status_code == 409 and r.data["mensaje"] == f"El lote {lote['codigo']} ya fue cerrado"


def test_hu_m06_05_ca08_cierre_auditado_con_destino_y_resumen(lotes, nuevo_ingreso, administrador):
    lote = lotes.completo(nuevo_ingreso())
    cerrar(lotes, lote, destino="TRASLADO", observacion="Ley baja")
    evento = EventoAuditoria.objects.get(entidad="Lote", valores_nuevos__operacion="CERRAR")
    assert evento.usuario == administrador and evento.valores_nuevos["destino"] == "TRASLADO"
    assert evento.valores_nuevos["resumen"]["toneladas_registradas"] == "20.20" and evento.motivo == "Ley baja"


def test_bigbags_y_partes_no_cambian_las_toneladas_registradas(lotes, nuevo_ingreso):
    """Riesgo principal de M06: que una estimación se filtre a un total."""
    lote = lotes.en_recorrido(nuevo_ingreso(), nuevo_ingreso())
    lotes.etapa(lote, etapa="SECADO")
    partes = {p["nombre"]: p["id"] for p in lotes.dividir(lote, PARTES).data["partes"]}
    lotes.etapa(lote, parte=partes["Molino"], etapa="MOLIENDA")
    lotes.etapa(lote, parte=partes["Molino"], etapa="ENSACADO",
                bigbags={"cantidad": 3, "recalcular": True, "peso_aproximado_tn": "9.99"})
    assert lotes.detalle(lote)["total"]["toneladas"] == "40.40"
    assert Bigbag.objects.get().peso_aproximado_tn == Decimal("9.99")
