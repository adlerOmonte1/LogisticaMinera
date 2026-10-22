"""Contrato HTTP de M04: alta, listado con filtros, detalle y anulación."""

from datetime import date

import pytest
from django.utils import timezone

from apps.catalogo.tests.factories import ClienteFactory, ProductoFactory
from apps.salidas.models import Salida, TipoMovimiento

from .factories import SalidaFactory

pytestmark = pytest.mark.django_db

SALIDAS = "/api/v1/salidas/"


def _payload(producto, cliente=None, **cambios):
    base = {
        "fecha": "2026-05-10",
        "producto": producto.pk,
        "tipo_movimiento": TipoMovimiento.VENTA,
        "cantidad_tn": "15.00",
    }
    if cliente is not None:
        base["cliente"] = cliente.pk
    base.update(cambios)
    return base


def _del_mes_en_curso(**cambios):
    """El listado sin filtro muestra el mes en curso (HU-M04-03 CA01), así que
    las pruebas de listado fechan sus salidas en el mes de hoy."""
    return SalidaFactory(fecha=timezone.localdate(), **cambios)


# --- HU-M04-01 / HU-M04-02: alta -----------------------------------------


def test_hu_m04_01_ca01_alta_de_salida(api_como, administrativo):
    producto, cliente = ProductoFactory(), ClienteFactory()

    r = api_como(administrativo).post(SALIDAS, _payload(producto, cliente))

    assert r.status_code == 201
    assert r.data["correlativo"].startswith("SAL-")
    assert r.data["estado"] == "REGISTRADO"
    assert r.data["tipo_movimiento"] == TipoMovimiento.VENTA


def test_hu_m04_01_ca03_cantidad_cero(api_como, administrativo):
    producto, cliente = ProductoFactory(), ClienteFactory()

    r = api_como(administrativo).post(
        SALIDAS, _payload(producto, cliente, cantidad_tn="0.00")
    )
    assert r.status_code == 400


def test_hu_m04_01_ca04_venta_sin_cliente(api_como, administrativo):
    r = api_como(administrativo).post(SALIDAS, _payload(ProductoFactory()))

    assert r.status_code == 400
    assert r.data["mensaje"] == "Debe indicar el cliente para una salida por venta"


def test_hu_m04_02_ca02_merma_sin_motivo(api_como, administrativo):
    r = api_como(administrativo).post(
        SALIDAS,
        _payload(ProductoFactory(), tipo_movimiento=TipoMovimiento.MERMA),
    )

    assert r.status_code == 400
    assert r.data["mensaje"] == "Debe indicar el motivo de la merma"


def test_hu_m04_02_ca01_traslado_interno_sin_cliente(api_como, administrativo):
    r = api_como(administrativo).post(
        SALIDAS,
        _payload(ProductoFactory(), tipo_movimiento=TipoMovimiento.TRASLADO_INTERNO),
    )

    assert r.status_code == 201
    assert r.data["cliente"] is None


def test_el_correlativo_y_la_hora_de_registro_no_se_aceptan_del_cliente(
    api_como, administrativo
):
    producto, cliente = ProductoFactory(), ClienteFactory()

    r = api_como(administrativo).post(
        SALIDAS, _payload(producto, cliente, correlativo="SAL-1999-00001")
    )

    assert r.status_code == 201
    assert r.data["correlativo"] != "SAL-1999-00001"


# --- HU-M04-03 CA01: listado y filtros ------------------------------------


def test_hu_m04_03_ca01_el_listado_muestra_el_mes_en_curso(api_como, supervisor):
    _del_mes_en_curso()
    SalidaFactory(fecha=date(2020, 1, 15))

    r = api_como(supervisor).get(SALIDAS)

    assert r.status_code == 200
    assert r.data["count"] == 1


def test_hu_m04_02_ca04_filtro_por_tipo_de_movimiento(api_como, supervisor):
    _del_mes_en_curso(tipo_movimiento=TipoMovimiento.VENTA)
    _del_mes_en_curso(tipo_movimiento=TipoMovimiento.MERMA, cliente=None, motivo="Humedad")

    r = api_como(supervisor).get(SALIDAS, {"tipo_movimiento": TipoMovimiento.MERMA})

    assert r.data["count"] == 1
    assert r.data["results"][0]["tipo_movimiento"] == TipoMovimiento.MERMA


def test_hu_m04_03_ca01_filtros_por_producto_cliente_y_fecha(api_como, supervisor):
    producto = ProductoFactory()
    buscada = SalidaFactory(fecha=date(2026, 5, 10), producto=producto)
    SalidaFactory(fecha=date(2026, 5, 10))

    r = api_como(supervisor).get(
        SALIDAS,
        {"producto": producto.pk, "cliente": buscada.cliente_id,
         "fecha_desde": "2026-05-01", "fecha_hasta": "2026-05-31"},
    )

    assert r.data["count"] == 1
    assert r.data["results"][0]["correlativo"] == buscada.correlativo


def test_el_detalle_incluye_el_usuario_que_registro(api_como, supervisor):
    salida = SalidaFactory()

    r = api_como(supervisor).get(f"{SALIDAS}{salida.pk}/")

    assert r.status_code == 200
    assert r.data["usuario_registro"] == salida.usuario_registro.username


# --- HU-M04-03 CA02/CA03/CA04: anulación ----------------------------------


def test_hu_m04_03_ca02_anular_salida(api_como, administrativo):
    salida = SalidaFactory()

    r = api_como(administrativo).post(
        f"{SALIDAS}{salida.pk}/anular/", {"motivo": "Registrada por error"}
    )

    assert r.status_code == 200
    assert r.data["estado"] == Salida.ANULADO
    assert r.data["motivo_anulacion"] == "Registrada por error"


def test_hu_m04_03_ca03_anular_sin_motivo(api_como, administrativo):
    salida = SalidaFactory()

    r = api_como(administrativo).post(f"{SALIDAS}{salida.pk}/anular/", {"motivo": ""})

    assert r.status_code == 400
    assert r.data["mensaje"] == "Debe indicar el motivo de la anulación"


def test_hu_m04_03_ca04_no_existe_eliminacion_fisica(api_como, administrador):
    salida = SalidaFactory()

    r = api_como(administrador).delete(f"{SALIDAS}{salida.pk}/")

    assert r.status_code == 405
    assert Salida.objects.filter(pk=salida.pk).exists()
