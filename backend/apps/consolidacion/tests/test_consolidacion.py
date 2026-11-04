"""HU-M08-01, HU-M08-02 y RN-M08-01 a RN-M08-10."""

import io
from datetime import timedelta
from decimal import Decimal

import pytest
from openpyxl import load_workbook

from apps.auditoria.models import EventoAuditoria
from apps.consolidacion.exportadores import EXPORTADORES
from apps.consolidacion.repositories import ConsolidacionRepository, Periodo
from apps.ingresos.models import Ingreso

from .conftest import MENSUAL

pytestmark = pytest.mark.django_db


def consolidar(api, hoy, **p):
    return api.get(MENSUAL, {"anio": hoy.year, "mes": hoy.month, **p})


def exportar(api, hoy, **p):
    return api.get(MENSUAL + "exportar/", {"anio": hoy.year, "mes": hoy.month, **p})


def hoja(respuesta):
    return load_workbook(io.BytesIO(respuesta.content)).active


@pytest.fixture
def pasado(hoy):
    return hoy.replace(day=1) - timedelta(days=1)


# HU-M08-01


def test_hu_m08_01_ca01_total_por_tipo_de_mineral(api_como, administrativo, crear, otro_mineral, pasado):
    crear(dia=pasado)
    crear(dia=pasado, hora=9)
    crear(dia=pasado, hora=10, tipo_mineral=otro_mineral)
    d = consolidar(api_como(administrativo), pasado).data
    filas = {f["codigo"]: f for f in d["tipos_mineral"]}
    assert (filas["MOA"]["ingresos"], filas["MOA"]["toneladas"]) == (2, "40.40")
    assert (filas["MOB"]["ingresos"], filas["MOB"]["toneladas"]) == (1, "20.20")
    assert (d["total_toneladas"], d["total_ingresos"]) == ("60.60", 3)
    assert (filas["MOA"]["participacion"], filas["MOB"]["participacion"]) == ("66.67", "33.33")


def test_hu_m08_01_ca02_el_anulado_no_suma_ni_cuenta(api_como, administrativo, crear, pasado):
    crear(dia=pasado)
    crear(dia=pasado, estado=Ingreso.ANULADO)
    d = consolidar(api_como(administrativo), pasado).data
    assert (d["total_ingresos"], d["total_toneladas"], d["anulados_excluidos"]) == (1, "20.20", 1)


def test_hu_m08_01_ca03_mes_sin_ingresos(api_como, administrativo, pasado):
    d = consolidar(api_como(administrativo), pasado).data
    assert d["tipos_mineral"] == [] and d["mensaje"] == "No hay ingresos registrados para el periodo indicado"


def test_hu_m08_01_ca04_periodo_futuro(api_como, administrativo, hoy):
    siguiente = (hoy.replace(day=28) + timedelta(days=5))
    r = consolidar(api_como(administrativo), siguiente)
    assert r.status_code == 400 and r.data["mensaje"] == "No se puede consolidar un periodo futuro"


def test_hu_m08_01_ca05_la_correccion_se_refleja(api_como, administrativo, crear, pasado):
    ingreso = crear(dia=pasado)
    api = api_como(administrativo)
    assert consolidar(api, pasado).data["total_toneladas"] == "20.20"
    api.patch(f"/api/v1/ingresos/{ingreso.pk}/", {"peso_bruto_tn": "30.00", "motivo": "Bruto real"}, format="json")
    assert consolidar(api, pasado).data["total_toneladas"] == "17.70"


def test_hu_m08_01_ca06_el_supervisor_no_consolida(api_como, supervisor, hoy):
    r = consolidar(api_como(supervisor), hoy)
    assert r.status_code == 403 and r.data["mensaje"] == "Acción no autorizada"


def test_hu_m08_01_ca07_en_proceso_no_suma_y_se_avisa(api_como, administrativo, crear, pasado):
    crear(dia=pasado)
    en_proceso = crear(dia=pasado, estado=Ingreso.EN_PROCESO)
    d = consolidar(api_como(administrativo), pasado).data
    assert (d["total_ingresos"], d["total_toneladas"]) == (1, "20.20")
    assert d["en_proceso"]["codigos"] == [en_proceso.codigo]
    assert d["en_proceso_mensaje"] == "Hay 1 ingresos en proceso en el periodo, pendientes del destare"


def test_hu_m08_01_ca08_el_sin_foto_suma(api_como, administrativo, crear, pasado):
    crear(dia=pasado)  # el factory lo crea sin respaldo fotográfico
    assert consolidar(api_como(administrativo), pasado).data["total_ingresos"] == 1


def test_hu_m08_01_ca09_mes_en_curso_al_corte(api_como, administrativo, crear, hoy):
    crear()
    d = consolidar(api_como(administrativo), hoy).data
    assert d["al_corte"] == f"Total al corte de hoy, {hoy:%d/%m/%Y}"


def test_hu_m08_01_ca10_el_lote_no_cambia_el_total(api_como, administrativo, administrador, lotes, crear, hoy):
    ingreso = crear()
    api = api_como(administrativo)
    antes = consolidar(api, hoy).data["total_toneladas"]
    lote = lotes.completo(ingreso)
    api_como(administrador).patch(f"/api/v1/lotes/{lote['id']}/cerrar/", {"destino": "VENTA"}, format="json")
    assert consolidar(api_como(administrativo), hoy).data["total_toneladas"] == antes == "20.20"


# HU-M08-02


def test_hu_m08_02_ca01_archivo_con_total_y_numero_por_tipo(api_como, administrativo, crear, pasado):
    crear(dia=pasado)
    crear(dia=pasado, hora=9)
    r = exportar(api_como(administrativo), pasado)
    assert r.status_code == 200 and r["Content-Type"].startswith("application/vnd.openxmlformats")
    h = hoja(r)
    assert h["B6"].value == "Mineral óxido Pingüino" and (h["C6"].value, h["D6"].value) == (2, 40.4)


def test_hu_m08_02_ca02_exportar_un_periodo_sin_ingresos(api_como, administrativo, pasado):
    r = exportar(api_como(administrativo), pasado)
    assert r.status_code == 400 and r.data["mensaje"] == "No hay ingresos registrados para el periodo indicado"


def test_hu_m08_02_ca03_el_archivo_coincide_con_la_pantalla(api_como, administrativo, crear, otro_mineral, pasado):
    crear(dia=pasado)
    crear(dia=pasado, tipo_mineral=otro_mineral, peso_bruto_tn=Decimal("30.13"), peso_neto_tn=Decimal("17.83"))
    api = api_como(administrativo)
    pantalla = {f["nombre"]: (f["ingresos"], Decimal(f["toneladas"])) for f in consolidar(api, pasado).data["tipos_mineral"]}
    h = hoja(exportar(api, pasado))
    archivo = {h.cell(f, 2).value: (h.cell(f, 3).value, Decimal(str(h.cell(f, 4).value))) for f in range(6, 6 + len(pantalla))}
    assert archivo == pantalla


def test_hu_m08_02_ca04_el_supervisor_no_exporta(api_como, supervisor, hoy):
    r = exportar(api_como(supervisor), hoy)
    assert r.status_code == 403 and r.data["mensaje"] == "Acción no autorizada"


def test_hu_m08_02_ca05_la_exportacion_queda_en_auditoria(api_como, administrador, crear, pasado):
    crear(dia=pasado)
    exportar(api_como(administrador), pasado)
    evento = EventoAuditoria.objects.get(accion="EXPORTAR", entidad="Consolidado")
    assert evento.usuario == administrador and evento.valores_nuevos["periodo"] == f"{pasado.year}-{pasado.month:02d}"


# Reglas


def test_rn_m08_01_solo_registrados(crear, pasado):
    crear(dia=pasado)
    crear(dia=pasado, estado=Ingreso.EN_PROCESO)
    crear(dia=pasado, estado=Ingreso.ANULADO)
    c = ConsolidacionRepository.calcular(Periodo(pasado.year, pasado.month))
    assert (c.total_ingresos, c.total_toneladas) == (1, Decimal("20.20"))


def test_rn_m08_02_sin_acumulado_guardado():
    from django.apps import apps

    assert list(apps.get_app_config("consolidacion").get_models()) == []


def test_rn_m08_03_un_tipo_sin_ingresos_no_aparece(api_como, administrativo, crear, otro_mineral, pasado):
    crear(dia=pasado)
    nombres = [f["codigo"] for f in consolidar(api_como(administrativo), pasado).data["tipos_mineral"]]
    assert nombres == ["MOA"]


def test_rn_m08_04_ni_un_mes_despues_del_en_curso(api_como, administrativo, hoy):
    assert consolidar(api_como(administrativo), hoy.replace(year=hoy.year + 1)).status_code == 400
    assert consolidar(api_como(administrativo), hoy).status_code == 200


def test_rn_m08_05_el_total_exportado_es_el_de_pantalla(api_como, administrativo, crear, pasado):
    crear(dia=pasado)
    api = api_como(administrativo)
    h = hoja(exportar(api, pasado))
    total = next(r for r in h.iter_rows(values_only=True) if r[1] == "Total")
    assert Decimal(str(total[3])) == Decimal(consolidar(api, pasado).data["total_toneladas"])


def test_rn_m08_06_un_formato_nuevo_no_toca_el_calculo(api_como, administrativo, crear, pasado, monkeypatch):
    class ExportadorTexto:
        tipo_contenido, extension = "text/plain", "txt"

        def generar(self, consolidado, generado_en):
            return f"{consolidado.total_toneladas}".encode()

    monkeypatch.setitem(EXPORTADORES, "txt", ExportadorTexto())
    crear(dia=pasado)
    from apps.consolidacion.services import ServicioConsolidacion

    contenido, _ = ServicioConsolidacion().exportar(Periodo(pasado.year, pasado.month), administrativo, formato="txt")
    assert contenido == b"20.20"


def test_rn_m08_07_el_archivo_informa_los_en_proceso(api_como, administrativo, crear, pasado):
    crear(dia=pasado)
    en_proceso = crear(dia=pasado, estado=Ingreso.EN_PROCESO)
    filas = list(hoja(exportar(api_como(administrativo), pasado)).iter_rows(values_only=True))
    fila = next(r for r in filas if r[0] == "En proceso")
    assert fila[1] == 1 and en_proceso.codigo in fila[2]


def test_rn_m08_08_el_ingreso_sin_foto_suma(crear, pasado):
    ingreso = crear(dia=pasado)
    assert ingreso.sin_respaldo_fotografico
    assert ConsolidacionRepository.calcular(Periodo(pasado.year, pasado.month)).total_ingresos == 1


def test_rn_m08_09_la_division_del_lote_no_altera_el_total(api_como, administrativo, lotes, crear, hoy):
    ingreso = crear()
    lote = lotes.en_recorrido(ingreso)
    lotes.dividir(lote, [{"nombre": "A", "fraccion": "1/2", "ruta": "MOLIENDA_ENSACADO"},
                         {"nombre": "B", "fraccion": "1/2", "ruta": "ZARANDEO_ENSACADO"}])
    assert consolidar(api_como(administrativo), hoy).data["total_toneladas"] == "20.20"


def test_rn_m08_10_el_mes_es_el_del_pesaje(crear, hoy, pasado):
    crear(dia=pasado, hora=20)  # registrado al día siguiente: cuenta en el mes del pesaje
    assert ConsolidacionRepository.calcular(Periodo(pasado.year, pasado.month)).total_ingresos == 1
    assert ConsolidacionRepository.calcular(Periodo(hoy.year, hoy.month)).total_ingresos == 0


def test_hu_m07_03_ca08_el_calendario_coincide_con_el_consolidado(api_como, administrativo, crear, pasado):
    crear(dia=pasado)
    crear(dia=pasado, estado=Ingreso.EN_PROCESO)
    crear(dia=pasado, estado=Ingreso.ANULADO)
    api = api_como(administrativo)
    cal = api.get("/api/v1/consulta/calendario/", {"anio": pasado.year, "mes": pasado.month}).data["resumen"]
    assert cal["toneladas"] == consolidar(api, pasado).data["total_toneladas"]
