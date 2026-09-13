"""Contrato HTTP de M03: alta, listado con filtros, edición y anulación."""

from datetime import timedelta

import pytest
from django.utils import timezone

from apps.catalogo.models import Vehiculo
from apps.catalogo.tests.factories import ProductoFactory, TransportistaFactory, VehiculoFactory
from apps.ingresos.models import Ingreso

from .factories import IngresoFactory

pytestmark = pytest.mark.django_db

INGRESOS = "/api/v1/ingresos/"


def _payload(vehiculo, producto, **cambios):
    base = {
        "fecha_pesaje": "2026-03-15",
        "hora_pesaje": "08:30:00",
        "numero_ticket": "TCK-API-0001",
        "vehiculo": vehiculo.pk,
        "producto": producto.pk,
        "peso_bruto_tn": "32.50",
        "tara_tn": "12.30",
    }
    base.update(cambios)
    return base


def test_hu_m03_01_ca01_alta_de_ingreso(api_como, administrativo):
    vehiculo, producto = VehiculoFactory(), ProductoFactory()
    r = api_como(administrativo).post(INGRESOS, _payload(vehiculo, producto))

    assert r.status_code == 201
    assert r.data["correlativo"].startswith("ING-")
    assert r.data["peso_neto_tn"] == "20.20"
    assert r.data["estado"] == "REGISTRADO"


def test_hu_m03_01_ca02_campo_obligatorio_faltante(api_como, administrativo):
    vehiculo, producto = VehiculoFactory(), ProductoFactory()
    datos = _payload(vehiculo, producto)
    del datos["numero_ticket"]

    r = api_como(administrativo).post(INGRESOS, datos)
    assert r.status_code == 400
    assert "numero_ticket" in r.data["detalles"]


def test_hu_m03_01_ca03_tara_invalida(api_como, administrativo):
    vehiculo, producto = VehiculoFactory(), ProductoFactory()
    r = api_como(administrativo).post(
        INGRESOS, _payload(vehiculo, producto, peso_bruto_tn="10.00", tara_tn="15.00")
    )
    assert r.status_code == 400
    assert r.data["mensaje"] == "La tara no puede ser mayor o igual al peso bruto"


def test_hu_m03_01_ca04_ticket_duplicado_responde_409(api_como, administrativo):
    vehiculo, producto = VehiculoFactory(), ProductoFactory()
    cliente = api_como(administrativo)
    cliente.post(INGRESOS, _payload(vehiculo, producto, numero_ticket="TCK-REPETIDO"))

    r = cliente.post(INGRESOS, _payload(vehiculo, producto, numero_ticket="TCK-REPETIDO"))
    assert r.status_code == 409
    assert "TCK-REPETIDO" in r.data["mensaje"]


def test_hu_m03_01_ca06_fecha_futura_es_rechazada(api_como, administrativo):
    vehiculo, producto = VehiculoFactory(), ProductoFactory()
    manana = (timezone.localdate() + timedelta(days=1)).isoformat()
    r = api_como(administrativo).post(
        INGRESOS, _payload(vehiculo, producto, fecha_pesaje=manana)
    )
    assert r.status_code == 400
    assert r.data["mensaje"] == "La fecha y hora de pesaje no pueden ser posteriores a la hora actual"


def test_hu_m03_04_ca01_listado_por_defecto_es_del_mes_en_curso(api_como, administrativo):
    hoy = timezone.localdate()
    mes_pasado = hoy.replace(day=1) - timedelta(days=1)
    IngresoFactory(numero_ticket="ACTUAL", fecha_pesaje=hoy)
    IngresoFactory(numero_ticket="ANTERIOR", fecha_pesaje=mes_pasado)

    r = api_como(administrativo).get(INGRESOS)
    tickets = [i["numero_ticket"] for i in r.data["results"]]
    assert "ACTUAL" in tickets
    assert "ANTERIOR" not in tickets


def test_hu_m03_04_ca02_filtro_por_rango_de_fechas_incluye_meses_anteriores(api_como, administrativo):
    IngresoFactory(numero_ticket="ENERO", fecha_pesaje="2026-01-10")
    IngresoFactory(numero_ticket="FEBRERO", fecha_pesaje="2026-02-10")

    r = api_como(administrativo).get(
        INGRESOS + "?fecha_desde=2026-01-01&fecha_hasta=2026-01-31"
    )
    tickets = [i["numero_ticket"] for i in r.data["results"]]
    assert tickets == ["ENERO"]


def test_hu_m03_04_ca04_ingreso_anulado_aparece_en_el_listado_con_su_estado(api_como, administrativo):
    IngresoFactory(numero_ticket="ANULADO-1", estado=Ingreso.ANULADO, motivo_anulacion="Error")
    r = api_como(administrativo).get(INGRESOS + "?fecha_desde=2026-01-01&estado=ANULADO")
    assert any(i["numero_ticket"] == "ANULADO-1" and i["estado"] == "ANULADO" for i in r.data["results"])


def test_filtro_titularidad_alimenta_el_indicador_i2(api_como, administrativo):
    transportista = TransportistaFactory()
    externo = VehiculoFactory(tipo_titularidad=Vehiculo.EXTERNO, transportista=transportista)
    propio = VehiculoFactory(tipo_titularidad=Vehiculo.PROPIO)
    hoy = timezone.localdate()
    IngresoFactory(numero_ticket="EXT-1", vehiculo=externo, fecha_pesaje=hoy)
    IngresoFactory(numero_ticket="PRO-1", vehiculo=propio, fecha_pesaje=hoy)

    r = api_como(administrativo).get(INGRESOS + "?titularidad=EXTERNO")
    tickets = [i["numero_ticket"] for i in r.data["results"]]
    assert tickets == ["EXT-1"]


def test_hu_m03_05_ca01_detalle_incluye_las_tres_marcas_temporales(api_como, administrativo):
    ingreso = IngresoFactory()
    r = api_como(administrativo).get(f"{INGRESOS}{ingreso.pk}/")
    assert r.status_code == 200
    for campo in ("hora_pesaje", "hora_registro", "hora_sincronizacion"):
        assert campo in r.data


def test_hu_m03_06_ca01_edicion_por_administrativo(api_como, administrativo):
    ingreso = IngresoFactory(numero_ticket="ORIGINAL")
    r = api_como(administrativo).patch(f"{INGRESOS}{ingreso.pk}/", {"numero_ticket": "CORREGIDO"})
    assert r.status_code == 200
    assert r.data["numero_ticket"] == "CORREGIDO"


def test_hu_m03_06_ca02_intento_de_editar_correlativo_es_rechazado(api_como, administrativo):
    ingreso = IngresoFactory()
    r = api_como(administrativo).patch(f"{INGRESOS}{ingreso.pk}/", {"correlativo": "ING-2026-99999"})
    assert r.status_code == 400
    assert r.data["mensaje"] == "El campo indicado no es editable"


def test_hu_m03_06_ca04_no_se_edita_un_ingreso_anulado(api_como, administrativo):
    ingreso = IngresoFactory(estado=Ingreso.ANULADO, motivo_anulacion="Error de digitación")
    r = api_como(administrativo).patch(f"{INGRESOS}{ingreso.pk}/", {"numero_ticket": "X"})
    assert r.status_code == 409
    assert r.data["mensaje"] == "No se puede editar un ingreso anulado"


def test_hu_m03_07_ca01_anular_con_motivo(api_como, administrativo):
    ingreso = IngresoFactory()
    r = api_como(administrativo).post(f"{INGRESOS}{ingreso.pk}/anular/", {"motivo": "Duplicado"})
    assert r.status_code == 200
    assert r.data["estado"] == "ANULADO"
    assert r.data["motivo_anulacion"] == "Duplicado"


def test_hu_m03_07_ca02_anular_sin_motivo(api_como, administrativo):
    ingreso = IngresoFactory()
    r = api_como(administrativo).post(f"{INGRESOS}{ingreso.pk}/anular/", {})
    assert r.status_code == 400
    assert r.data["mensaje"] == "Debe indicar el motivo de la anulación"


def test_hu_m03_07_ca03_no_existe_borrado_fisico(api_como, administrativo):
    ingreso = IngresoFactory()
    r = api_como(administrativo).delete(f"{INGRESOS}{ingreso.pk}/")
    assert r.status_code == 405
    assert Ingreso.objects.filter(pk=ingreso.pk).exists()


def test_hu_m07_05_filtro_de_ingresos_capturados_sin_conexion(api_como, administrativo):
    hoy = timezone.localdate()
    IngresoFactory(numero_ticket="EN-LINEA", fecha_pesaje=hoy, capturado_offline=False)
    IngresoFactory(numero_ticket="OFFLINE", fecha_pesaje=hoy, capturado_offline=True)

    r = api_como(administrativo).get(INGRESOS + "?capturado_offline=true")

    tickets = [i["numero_ticket"] for i in r.data["results"]]
    assert tickets == ["OFFLINE"]
