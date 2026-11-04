"""Reglas RN-M07-01 a RN-M07-17 y no funcionales medibles de M07."""

from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from apps.auditoria.models import EventoAuditoria
from apps.ingresos.models import Ingreso
from apps.trazabilidad.services.recorrido import trazabilidad

from .conftest import CONSULTA

pytestmark = pytest.mark.django_db
INGRESOS = CONSULTA + "ingresos/"


def test_rn_m07_01_el_anulado_aparece(api_como, supervisor, crear):
    crear(estado=Ingreso.ANULADO)
    assert api_como(supervisor).get(INGRESOS).data["count"] == 1


def test_rn_m07_02_solo_suman_los_registrados(api_como, supervisor, crear):
    crear()
    crear(estado=Ingreso.ANULADO)
    crear(estado=Ingreso.EN_PROCESO)
    assert api_como(supervisor).get(INGRESOS).data["totales"]["toneladas"] == "20.20"


def test_rn_m07_03_el_detalle_presenta_la_imagen_junto_a_los_datos(api_como, supervisor, registrar, imagen_png):
    ingreso = registrar(supervisor, imagen_png).data
    d = api_como(supervisor).get(f"{INGRESOS}{ingreso['id']}/").data
    assert d["respaldo"]["url"].endswith("/ticket/") and d["peso_bruto_tn"] == "29.80"


def test_rn_m07_04_sin_foto_y_no_disponible_son_distintos(api_como, supervisor, crear):
    sin_foto = crear()
    perdida = crear(sin_respaldo_fotografico=False, motivo_sin_respaldo="", imagen_ticket="tickets/x.jpg", hora=9)
    api = api_como(supervisor)
    assert api.get(f"{INGRESOS}{sin_foto.pk}/").data["respaldo"]["tipo"] == "SIN_RESPALDO_FOTOGRAFICO"
    assert api.get(f"{INGRESOS}{perdida.pk}/").data["respaldo"]["tipo"] == "NO_DISPONIBLE"
    assert api.get(f"{INGRESOS}{perdida.pk}/ticket/").data["mensaje"] == "El respaldo no está disponible"


def test_rn_m07_05_la_busqueda_exige_un_criterio(api_como, supervisor):
    assert api_como(supervisor).get(INGRESOS, {"fecha": ""}).status_code == 400


def test_rn_m07_06_la_imagen_solo_con_sesion(registrar, supervisor, imagen_png):
    ingreso = registrar(supervisor, imagen_png).data
    assert APIClient().get(f"{INGRESOS}{ingreso['id']}/ticket/").status_code == 401


def test_rn_m07_07_tres_marcas_distintas(api_como, supervisor, crear):
    d = api_como(supervisor).get(f"{INGRESOS}{crear().pk}/").data
    assert len({d["fecha_hora_pesaje"], d["hora_inicio_registro"], d["hora_fin_registro"]}) == 3


def test_rn_m07_08_los_bloques_ausentes_se_indican(api_como, supervisor, crear):
    d = api_como(supervisor).get(f"{INGRESOS}{crear().pk}/").data
    assert {"reconocimiento", "validaciones", "trazabilidad", "historial"} <= set(d)
    assert d["reconocimiento"]["disponible"] is False


def test_rn_m07_09_la_consulta_no_modifica_nada(api_como, administrativo, crear):
    ingreso = crear()
    antes = (Ingreso.objects.count(), EventoAuditoria.objects.count())
    api = api_como(administrativo)
    for ruta in (INGRESOS, f"{INGRESOS}{ingreso.pk}/", CONSULTA + "calendario/", CONSULTA + "inicio/",
                 CONSULTA + "avisos/", CONSULTA + "cabecera/?q=1"):
        api.get(ruta)
    assert (Ingreso.objects.count(), EventoAuditoria.objects.count()) == antes
    assert api.post(INGRESOS, {}, format="json").status_code == 405


def test_rn_m07_10_el_en_proceso_aparece_sin_neto(api_como, supervisor, crear):
    crear(estado=Ingreso.EN_PROCESO)
    [fila] = api_como(supervisor).get(INGRESOS).data["results"]
    assert fila["peso_neto_tn"] is None and fila["pendiente_destare"] is True


def test_rn_m07_11_el_dia_es_el_del_pesaje_en_la_zona_de_la_planta(api_como, supervisor, crear, hoy):
    # Pesado a las 20:00 en Lima, ya es el día siguiente en UTC.
    tarde = crear(hora=20, hora_inicio_registro=timezone.now() + timedelta(days=3))
    d = api_como(supervisor).get(CONSULTA + "calendario/", {"anio": hoy.year, "mes": hoy.month, "dia": hoy.day}).data
    assert [x["id"] for x in d["dia"]["ingresos"]] == [tarde.pk]


def test_rn_m07_12_el_calendario_cuenta_y_suma_como_el_listado(api_como, supervisor, crear, hoy):
    crear()
    crear(estado=Ingreso.EN_PROCESO)
    crear(estado=Ingreso.ANULADO)
    api = api_como(supervisor)
    cal = api.get(CONSULTA + "calendario/").data["resumen"]
    lista = api.get(INGRESOS).data["totales"]
    assert cal["toneladas"] == lista["toneladas"] and cal["ingresos"] == lista["ingresos"] - lista["anulados"]


def test_rn_m07_13_la_trazabilidad_es_la_de_m06(api_como, supervisor, lotes, crear):
    ingreso = crear()
    lotes.completo(ingreso)
    d = api_como(supervisor).get(f"{INGRESOS}{ingreso.pk}/").data["trazabilidad"]
    ingreso.refresh_from_db()
    esperado = trazabilidad(ingreso)
    assert (d["etapas_recorridas"], d["etapas_totales"]) == (esperado["etapas_recorridas"], esperado["etapas_totales"])


def test_rn_m07_14_el_inicio_suma_con_el_criterio_del_calendario(api_como, supervisor, crear):
    crear()
    crear(estado=Ingreso.EN_PROCESO)
    api = api_como(supervisor)
    inicio = api.get(CONSULTA + "inicio/").data
    assert inicio["toneladas_hoy"]["toneladas"] == inicio["ultimos_siete_dias"][-1]["toneladas"] == "20.20"


def test_rn_m07_15_los_avisos_se_calculan_y_se_filtran_por_rol(api_como, supervisor, administrativo, crear):
    crear()  # sin lote: solo para quien compone lotes
    assert api_como(supervisor).get(CONSULTA + "avisos/").data["cantidad"] == 0
    assert api_como(administrativo).get(CONSULTA + "avisos/").data["cantidad"] == 1


def test_rn_m07_16_la_exportacion_es_el_conjunto_filtrado_con_estados(api_como, administrativo, crear):
    crear()
    crear(estado=Ingreso.EN_PROCESO, hora=9)
    crear(estado=Ingreso.ANULADO, hora=10)
    r = api_como(administrativo).get(INGRESOS + "exportar/", {"estado": "EN_PROCESO"})
    texto = b"".join(r.streaming_content).decode("utf-8-sig")
    assert texto.count("\n") == 2 and "En proceso" in texto and "Anulado" not in texto


def test_rn_m07_17_la_exportacion_queda_atribuida(api_como, administrador, crear):
    crear()
    api_como(administrador).get(INGRESOS + "exportar/")
    evento = EventoAuditoria.objects.get(accion="EXPORTAR")
    assert evento.usuario == administrador and evento.valores_nuevos["exportacion"] == "LISTADO_INGRESOS"


def test_hu_m09_01_ca06_la_exportacion_registra_el_criterio(api_como, administrativo, crear, hoy):
    crear()
    api_como(administrativo).get(INGRESOS + "exportar/", {"fecha_desde": hoy.isoformat()})
    filtros = EventoAuditoria.objects.get(accion="EXPORTAR").valores_nuevos["filtros"]
    assert filtros["desde"] == hoy.isoformat()


def test_rnf_m07_06_la_placa_sin_guiones_ni_mayusculas(api_como, supervisor, crear, hoy):
    crear(placa="C9K-741")
    api = api_como(supervisor)
    for escrito in ("c9k741", "C9K-741", "c9k 741", "9K7"):
        assert api.get(INGRESOS, {"placa": escrito, "fecha": hoy.isoformat()}).data["count"] == 1


def test_rnf_m07_03_el_listado_no_depende_del_numero_de_resultados(api_como, supervisor, crear,
                                                                     django_assert_max_num_queries):
    for h in range(20):
        crear(hora=h % 24)
    with django_assert_max_num_queries(12):
        api_como(supervisor).get(INGRESOS)
