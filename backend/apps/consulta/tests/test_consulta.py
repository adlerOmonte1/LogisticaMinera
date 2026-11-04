"""Contrato HTTP de M07, un caso por criterio de HU-M07-01 a HU-M07-04."""

import csv
import io
from datetime import timedelta

import pytest
from rest_framework.test import APIClient

from apps.auditoria.models import EventoAuditoria
from apps.ingresos.models import Ingreso
from apps.validacion.models import ResultadoValidacion

from .conftest import CONSULTA

pytestmark = pytest.mark.django_db
INGRESOS = CONSULTA + "ingresos/"


def buscar(api, **params):
    return api.get(INGRESOS, params)


# HU-M07-01 — Consulta por placa y fecha


def test_hu_m07_01_ca01_placa_y_fecha_del_mas_reciente(api_como, supervisor, crear, hoy):
    temprano, tarde = crear(hora=7), crear(hora=15)
    crear(dia=hoy - timedelta(days=1))
    r = buscar(api_como(supervisor), placa="V2K-841", fecha=hoy.isoformat())
    assert [x["id"] for x in r.data["results"]] == [tarde.pk, temprano.pk]


def test_hu_m07_01_ca02_placa_parcial(api_como, supervisor, crear, hoy):
    crear(placa="C9K-741")
    crear(placa="C9K-742")
    crear(placa="V2K-841")
    r = buscar(api_como(supervisor), placa="c9k", fecha=hoy.isoformat())
    assert sorted(x["placa"] for x in r.data["results"]) == ["C9K-741", "C9K-742"]


def test_hu_m07_01_ca03_el_detalle_presenta_la_imagen(api_como, supervisor, registrar, imagen_png):
    ingreso = registrar(supervisor, imagen_png).data
    d = api_como(supervisor).get(f"{INGRESOS}{ingreso['id']}/").data
    assert d["respaldo"]["tipo"] == "IMAGEN"
    imagen = api_como(supervisor).get(d["respaldo"]["url"])
    assert imagen.status_code == 200
    imagen.close()


def test_hu_m07_01_ca04_sin_resultados(api_como, supervisor, hoy):
    r = buscar(api_como(supervisor), placa="ZZZ", fecha=hoy.isoformat())
    assert r.status_code == 200 and r.data["mensaje"] == "No se encontraron ingresos con los criterios indicados"


def test_hu_m07_01_ca05_el_anulado_aparece_con_su_motivo(api_como, supervisor, crear, hoy):
    crear(estado=Ingreso.ANULADO)
    [fila] = buscar(api_como(supervisor), placa="V2K", fecha=hoy.isoformat()).data["results"]
    assert (fila["estado"], fila["motivo_anulacion"]) == ("ANULADO", "Duplicado")


def test_hu_m07_01_ca06_sin_criterios(api_como, supervisor):
    r = buscar(api_como(supervisor), placa="", fecha="")
    assert r.status_code == 400 and r.data["mensaje"] == "Debe indicar al menos la placa o la fecha"


def test_hu_m07_01_ca07_respaldo_no_disponible(api_como, supervisor, crear):
    ingreso = crear(sin_respaldo_fotografico=False, motivo_sin_respaldo="", imagen_ticket="tickets/perdida.jpg")
    d = api_como(supervisor).get(f"{INGRESOS}{ingreso.pk}/").data
    assert d["respaldo"] == {"tipo": "NO_DISPONIBLE", "mensaje": "El respaldo no está disponible", "url": None}
    assert d["codigo"] == ingreso.codigo


def test_hu_m07_01_ca08_en_proceso_con_neto_pendiente(api_como, supervisor, crear, hoy):
    crear(estado=Ingreso.EN_PROCESO)
    [fila] = buscar(api_como(supervisor), fecha=hoy.isoformat()).data["results"]
    assert (fila["estado"], fila["peso_neto_tn"], fila["pendiente_destare"]) == ("EN_PROCESO", None, True)
    assert fila["peso_bruto_tn"] == "32.50"


def test_hu_m07_01_ca09_sin_foto_con_su_motivo(api_como, supervisor, crear):
    ingreso = crear()
    d = api_como(supervisor).get(f"{INGRESOS}{ingreso.pk}/").data
    assert d["respaldo"] == {"tipo": "SIN_RESPALDO_FOTOGRAFICO", "motivo": "Otro", "url": None}


def test_hu_m07_01_ca10_lote_y_recorrido(api_como, supervisor, lotes, crear):
    ingreso = crear()
    lote = lotes.en_recorrido(ingreso)
    lotes.etapa(lote, etapa="SECADO")
    d = api_como(supervisor).get(f"{INGRESOS}{ingreso.pk}/").data["trazabilidad"]
    assert d["lote"]["codigo"] == lote["codigo"] and d["secado"]["completado"] is True


def test_hu_m07_01_ca11_sin_lote_espera_en_cancha(api_como, supervisor, crear):
    d = api_como(supervisor).get(f"{INGRESOS}{crear().pk}/").data["trazabilidad"]
    assert d["lote"] is None and d["etapas_recorridas"] == 0
    assert d["mensaje"] == "El mineral espera en cancha: aún no tiene lote ni ha recorrido ninguna etapa"


def test_hu_m07_01_ca12_rango_inverso(api_como, supervisor, hoy):
    r = buscar(api_como(supervisor), placa="V2K", fecha_desde=hoy.isoformat(),
               fecha_hasta=(hoy - timedelta(days=1)).isoformat())
    assert r.status_code == 400 and r.data["mensaje"] == "La fecha inicial no puede ser posterior a la fecha final"


# HU-M07-02 — Listado y detalle


def test_hu_m07_02_ca01_rango_paginado_y_descendente(api_como, administrativo, crear, hoy):
    for h in range(6, 10):
        crear(hora=h)
    r = api_como(administrativo).get(INGRESOS, {"fecha_desde": hoy.isoformat(), "fecha_hasta": hoy.isoformat()})
    horas = [x["fecha_hora_pesaje"] for x in r.data["results"]]
    assert r.data["count"] == 4 and horas == sorted(horas, reverse=True) and "next" in r.data


def test_hu_m07_02_ca02_filtros_combinados(api_como, administrativo, crear, otro_mineral):
    crear(estado=Ingreso.EN_PROCESO, placa="E4R-208")
    crear(placa="E4R-209", tipo_mineral=otro_mineral)
    objetivo = crear(placa="E4R-210")
    r = api_como(administrativo).get(INGRESOS, {"estado": "REGISTRADO", "tipo_mineral": objetivo.tipo_mineral_id,
                                                "titularidad": "PROPIO"})
    assert [x["id"] for x in r.data["results"]] == [objetivo.pk]


def test_hu_m07_02_ca03_totales_solo_de_registrados(api_como, administrativo, crear):
    crear()
    crear(estado=Ingreso.EN_PROCESO)
    crear(estado=Ingreso.ANULADO)
    t = api_como(administrativo).get(INGRESOS).data["totales"]
    assert (t["ingresos"], t["registrados"], t["toneladas"]) == (3, 1, "20.20")


def test_hu_m07_02_ca04_detalle_con_marcas_usuario_estado_tara_y_neto(api_como, administrativo, crear):
    ingreso = crear()
    d = api_como(administrativo).get(f"{INGRESOS}{ingreso.pk}/").data
    assert len({d["fecha_hora_pesaje"], d["hora_inicio_registro"], d["hora_fin_registro"]}) == 3
    assert (d["registrado_por"], d["estado"], d["tara_tn"], d["peso_neto_tn"]) == (
        ingreso.usuario_registro.username, "REGISTRADO", "12.30", "20.20")


def test_hu_m07_02_ca05_bloques_presentes(api_como, supervisor, registrar, imagen_png):
    ingreso = registrar(supervisor, imagen_png).data
    d = api_como(supervisor).get(f"{INGRESOS}{ingreso['id']}/").data
    assert d["reconocimiento"]["disponible"] and d["validaciones"]["disponible"]
    assert len(d["reconocimiento"]["campos"]) == 3 and len(d["validaciones"]["resultados"]) >= 5


def test_hu_m07_02_ca06_bloques_ausentes_se_indican(api_como, administrativo, crear):
    d = api_como(administrativo).get(f"{INGRESOS}{crear().pk}/").data
    assert d["reconocimiento"]["disponible"] is False and d["reconocimiento"]["mensaje"]
    assert d["validaciones"] == {"disponible": False, "mensaje": "El ingreso no tiene validaciones registradas"}


def test_hu_m07_02_ca07_rango_inverso(api_como, administrativo, hoy):
    r = api_como(administrativo).get(INGRESOS, {"fecha_desde": hoy.isoformat(),
                                                "fecha_hasta": (hoy - timedelta(days=3)).isoformat()})
    assert r.status_code == 400 and r.data["mensaje"] == "La fecha inicial no puede ser posterior a la fecha final"


def test_hu_m07_02_ca08_sin_fechas_el_mes_en_curso(api_como, administrativo, crear, hoy):
    del_mes = crear()
    crear(dia=hoy.replace(day=1) - timedelta(days=1))
    r = api_como(administrativo).get(INGRESOS)
    assert [x["id"] for x in r.data["results"]] == [del_mes.pk]
    assert (r.data["filtros"]["fecha_desde"], r.data["filtros"]["fecha_hasta"]) == (hoy.replace(day=1), hoy)


def test_hu_m07_02_ca09_sin_foto_se_senala_en_la_lista(api_como, administrativo, crear):
    crear()
    [fila] = api_como(administrativo).get(INGRESOS).data["results"]
    assert fila["sin_respaldo_fotografico"] is True and fila["motivo_sin_respaldo"] == "Otro"


def test_hu_m07_02_ca10_busqueda_por_parte_de_placa_o_codigo(api_como, administrativo, crear):
    por_codigo = crear(codigo="ING-2026-00777", placa="AAA-111")
    por_placa = crear(placa="B7B-777")
    crear(placa="CCC-333")
    r = api_como(administrativo).get(INGRESOS, {"q": "777"})
    assert sorted(x["id"] for x in r.data["results"]) == sorted([por_codigo.pk, por_placa.pk])


def test_hu_m07_02_ca11_listado_sin_resultados(api_como, administrativo):
    r = api_como(administrativo).get(INGRESOS, {"estado": "ANULADO"})
    assert r.data["mensaje"] == "No hay ingresos con estos filtros"


def test_hu_m07_02_ca12_historial_cronologico(api_como, supervisor, administrativo, registrar, imagen_png):
    ingreso = registrar(supervisor, imagen_png).data
    api_como(administrativo).patch(f"/api/v1/ingresos/{ingreso['id']}/", {"peso_bruto_tn": "29.00",
                                                                          "motivo": "Error"}, format="json")
    historial = api_como(supervisor).get(f"{INGRESOS}{ingreso['id']}/").data["historial"]
    assert [e["accion"] for e in historial] == ["RECONOCER", "CREAR", "MODIFICAR"]


def leer_csv(respuesta):
    texto = b"".join(respuesta.streaming_content).decode("utf-8-sig")
    return list(csv.reader(io.StringIO(texto), delimiter=";"))


def test_hu_m07_02_ca13_exportar_el_conjunto_completo(api_como, administrativo, crear, settings):
    settings.REST_FRAMEWORK = {**settings.REST_FRAMEWORK, "PAGE_SIZE": 2}
    for h in range(6, 11):
        crear(hora=h)
    crear(estado=Ingreso.ANULADO, hora=12)
    r = api_como(administrativo).get(INGRESOS + "exportar/")
    assert r.status_code == 200 and r["Content-Type"].startswith("text/csv")
    filas = leer_csv(r)
    assert filas[0][0] == "Código" and len(filas) == 7
    assert any(f[8] == "Anulado" for f in filas[1:]) and filas[1][7] in ("20,20", "")
    evento = EventoAuditoria.objects.get(accion="EXPORTAR")
    assert evento.valores_nuevos["cantidad"] == 6 and evento.usuario == administrativo


def test_hu_m07_02_ca14_nada_que_exportar(api_como, administrativo):
    r = api_como(administrativo).get(INGRESOS + "exportar/", {"estado": "ANULADO"})
    assert r.status_code == 400 and r.data["mensaje"] == "No hay ingresos para exportar"


def test_hu_m07_02_ca15_el_supervisor_no_exporta(api_como, supervisor, crear):
    crear()
    r = api_como(supervisor).get(INGRESOS + "exportar/")
    assert r.status_code == 403 and r.data["mensaje"] == "Acción no autorizada"


def test_hu_m07_02_ca16_cabecera_por_codigo_o_digitos_finales(api_como, supervisor, crear):
    ingreso = crear(codigo="ING-2026-00042")
    api = api_como(supervisor)
    for texto in ("ING-2026-00042", "ing-2026-00042", "42", "00042"):
        assert api.get(CONSULTA + "cabecera/", {"q": texto}).data == {"tipo": "INGRESO", "id": ingreso.pk,
                                                                     "codigo": "ING-2026-00042"}


def test_hu_m07_02_ca17_cabecera_sin_codigo_es_placa(api_como, supervisor, crear):
    crear(codigo="ING-2026-00042")
    assert api_como(supervisor).get(CONSULTA + "cabecera/", {"q": "V2K"}).data == {"tipo": "PLACA", "placa": "V2K"}


# HU-M07-03 — Calendario


def calendario(api, hoy, **p):
    return api.get(CONSULTA + "calendario/", {"anio": hoy.year, "mes": hoy.month, **p}).data


def test_hu_m07_03_ca01_mes_en_curso_por_dia(api_como, administrativo, crear, hoy):
    crear()
    crear(hora=10)
    d = api_como(administrativo).get(CONSULTA + "calendario/").data
    dia = next(x for x in d["dias"] if x["fecha"] == hoy)
    assert (d["anio"], d["mes"], dia["ingresos"], dia["toneladas"]) == (hoy.year, hoy.month, 2, "40.40")


def test_hu_m07_03_ca02_anulados_no_cuentan_y_marcan(api_como, administrativo, crear, hoy):
    crear()
    crear(estado=Ingreso.ANULADO)
    dia = next(x for x in calendario(api_como(administrativo), hoy)["dias"] if x["fecha"] == hoy)
    assert (dia["ingresos"], dia["toneladas"], dia["con_anulados"]) == (1, "20.20", True)


def test_hu_m07_03_ca03_en_proceso_cuenta_sin_sumar(api_como, administrativo, crear, hoy):
    crear()
    crear(estado=Ingreso.EN_PROCESO)
    d = calendario(api_como(administrativo), hoy)
    dia = next(x for x in d["dias"] if x["fecha"] == hoy)
    assert (dia["ingresos"], dia["toneladas"], dia["con_en_proceso"]) == (2, "20.20", True)
    assert d["resumen"]["en_proceso"] == 1


def test_hu_m07_03_ca04_lista_del_dia(api_como, administrativo, crear, hoy):
    ingreso = crear(hora=9)
    d = calendario(api_como(administrativo), hoy, dia=hoy.day)["dia"]
    [fila] = d["ingresos"]
    assert (fila["codigo"], fila["placa"], fila["peso_neto_tn"], fila["estado"]) == (
        ingreso.codigo, "V2K-841", "20.20", "REGISTRADO")


def test_hu_m07_03_ca05_dia_sin_llegadas(api_como, administrativo, hoy):
    d = calendario(api_como(administrativo), hoy, dia=hoy.day)["dia"]
    assert d["ingresos"] == [] and d["mensaje"] == "No llegaron volquetes este día"


def test_hu_m07_03_ca06_otro_mes_con_el_mismo_criterio(api_como, administrativo, crear, hoy):
    pasado = hoy.replace(day=1) - timedelta(days=1)
    crear(dia=pasado)
    crear(dia=pasado, estado=Ingreso.EN_PROCESO)
    d = api_como(administrativo).get(CONSULTA + "calendario/", {"anio": pasado.year, "mes": pasado.month}).data
    assert d["resumen"] == {"ingresos": 2, "toneladas": "20.20", "dias_con_llegadas": 1, "en_proceso": 1}


def test_hu_m07_03_ca07_del_dia_al_detalle(api_como, administrativo, crear, hoy):
    ingreso = crear()
    fila = calendario(api_como(administrativo), hoy, dia=hoy.day)["dia"]["ingresos"][0]
    assert api_como(administrativo).get(f"{INGRESOS}{fila['id']}/").data["codigo"] == ingreso.codigo


def test_hu_m07_03_ca08_el_mes_coincide_con_los_computables(api_como, administrativo, crear, hoy):
    crear()
    crear(estado=Ingreso.EN_PROCESO)
    crear(estado=Ingreso.ANULADO)
    from django.db.models import Sum

    esperado = Ingreso.objects.computables().filter(
        fecha_hora_pesaje__year=hoy.year, fecha_hora_pesaje__month=hoy.month).aggregate(t=Sum("peso_neto_tn"))["t"]
    assert calendario(api_como(administrativo), hoy)["resumen"]["toneladas"] == str(esperado)


# HU-M07-04 — Inicio y avisos


def test_hu_m07_04_ca01_cifras_del_dia(api_como, supervisor, crear, lotes):
    crear()
    crear(estado=Ingreso.ANULADO)
    crear(estado=Ingreso.EN_PROCESO, placa="E4R-208")
    lotes.abrir()
    d = api_como(supervisor).get(CONSULTA + "inicio/").data
    assert d["ingresos_hoy"]["cantidad"] == 2 and d["toneladas_hoy"]["toneladas"] == "20.20"
    assert d["pendientes_destare"] == {"cantidad": 1, "placas": ["E4R-208"], "enlace": "/ingresos/destares"}
    assert d["lotes_en_proceso"]["cantidad"] == 1


def test_hu_m07_04_ca02_sin_contar_en_proceso(api_como, supervisor, crear):
    crear()
    crear(estado=Ingreso.EN_PROCESO)
    assert api_como(supervisor).get(CONSULTA + "inicio/").data["toneladas_hoy"]["mensaje"] == "Sin contar 1 en proceso"


def test_hu_m07_04_ca03_aun_no_hay_ingresos_hoy(api_como, supervisor):
    d = api_como(supervisor).get(CONSULTA + "inicio/").data["ingresos_hoy"]
    assert (d["cantidad"], d["mensaje"]) == (0, "Aún no hay ingresos hoy")


def test_hu_m07_04_ca04_siete_dias_como_el_calendario(api_como, supervisor, crear, hoy):
    ayer = hoy - timedelta(days=1)
    crear(dia=ayer)
    crear(dia=ayer, estado=Ingreso.EN_PROCESO)
    semana = api_como(supervisor).get(CONSULTA + "inicio/").data["ultimos_siete_dias"]
    assert len(semana) == 7 and semana[-1]["fecha"] == hoy
    del_dia = next(d for d in semana if d["fecha"] == ayer)["toneladas"]
    cal = api_como(supervisor).get(CONSULTA + "calendario/", {"anio": ayer.year, "mes": ayer.month}).data
    assert del_dia == next(d for d in cal["dias"] if d["fecha"] == ayer)["toneladas"] == "20.20"


def test_hu_m07_04_ca05_ultimos_ingresos_al_detalle(api_como, supervisor, crear):
    for h in range(6, 13):
        crear(hora=h)
    ultimos = api_como(supervisor).get(CONSULTA + "inicio/").data["ultimos_ingresos"]
    assert len(ultimos) == 5
    assert api_como(supervisor).get(f"{INGRESOS}{ultimos[0]['id']}/").status_code == 200


def avisos(api):
    return api.get(CONSULTA + "avisos/").data


def test_hu_m07_04_ca06_aviso_por_ingreso_sin_destare(api_como, supervisor, crear):
    ingreso = crear(estado=Ingreso.EN_PROCESO, placa="E4R-208")
    [aviso] = [a for a in avisos(api_como(supervisor))["avisos"] if a["tipo"] == "DESTARE"]
    assert aviso["titulo"] == f"{ingreso.codigo} espera el destare"
    assert aviso["detalle"] == "Vehículo E4R-208, peso bruto 32.50 t" and aviso["enlace"] == "/ingresos/destares"


def test_hu_m07_04_ca07_lote_listo_para_cerrar_para_el_administrador(api_como, administrador, lotes, crear):
    lotes.completo(crear())
    [aviso] = [a for a in avisos(api_como(administrador))["avisos"] if a["tipo"] == "LOTE_LISTO"]
    assert aviso["titulo"] == "Lote 1 listo para cerrar con su destino" and aviso["enlace"].endswith("/cerrar")


def test_hu_m07_04_ca08_el_supervisor_no_ve_cierre_ni_sin_lote(api_como, supervisor, lotes, crear):
    lotes.completo(crear())
    crear()  # registrado sin lote
    tipos = {a["tipo"] for a in avisos(api_como(supervisor))["avisos"]}
    assert "LOTE_LISTO" not in tipos and "SIN_LOTE" not in tipos


def test_hu_m07_04_ca09_nada_pendiente(api_como, supervisor):
    assert avisos(api_como(supervisor)) == {"cantidad": 0, "avisos": [], "mensaje": "No hay nada pendiente"}


def test_hu_m07_04_ca10_el_aviso_desaparece_con_el_destare(api_como, supervisor, crear):
    ingreso = crear(estado=Ingreso.EN_PROCESO, placa="E4R-208")
    api = api_como(supervisor)
    assert avisos(api)["cantidad"] == 1
    api.post("/api/v1/ingresos/destares/", {"vehiculo": ingreso.vehiculo_id, "tara_tn": "12.00"}, format="json")
    assert avisos(api)["cantidad"] == 0


def test_hu_m07_04_ca11_cifra_sin_enlace_si_el_rol_no_accede(api_como, supervisor, administrativo):
    assert api_como(supervisor).get(CONSULTA + "inicio/").data["toneladas_hoy"]["enlace"] is None
    assert api_como(administrativo).get(CONSULTA + "inicio/").data["toneladas_hoy"]["enlace"] == "/consolidacion"


def test_aviso_v4_justificada_hoy_y_sin_lote_para_gestion(api_como, administrativo, crear):
    ingreso = crear()
    from django.utils import timezone

    ResultadoValidacion.objects.create(ingreso=ingreso, regla="V4", momento="CONFIRMACION", cumple=False,
                                       resolucion="JUSTIFICADA", justificacion="Sobrecarga", fecha_hora=timezone.now())
    tipos = [a["tipo"] for a in avisos(api_como(administrativo))["avisos"]]
    assert tipos == ["V4_JUSTIFICADA", "SIN_LOTE"]


def test_la_consulta_sin_sesion_responde_401():
    assert APIClient().get(INGRESOS).status_code == 401
