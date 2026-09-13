"""D-02, HU-M03-03: unicidad, orden creciente y reinicio anual."""

from datetime import datetime

import pytest

from apps.ingresos.models import ContadorCorrelativo
from apps.ingresos.services.correlativo import PREFIJO_INGRESO, generador_por_defecto
from common.correlativo import GeneradorCorrelativoPorAnio

pytestmark = pytest.mark.django_db


def test_hu_m03_03_ca01_correlativos_sucesivos_son_distintos_y_crecientes():
    generador = generador_por_defecto
    momento = datetime(2026, 5, 1, 10, 0)

    primero = generador.siguiente(momento)
    segundo = generador.siguiente(momento)

    assert primero == "ING-2026-00001"
    assert segundo == "ING-2026-00002"


def test_el_correlativo_se_reinicia_por_anio():
    generador = generador_por_defecto
    generador.siguiente(datetime(2026, 12, 31, 23, 0))

    primero_del_anio_siguiente = generador.siguiente(datetime(2027, 1, 1, 0, 5))

    assert primero_del_anio_siguiente == "ING-2027-00001"


def test_el_contador_persiste_el_ultimo_valor_por_anio():
    generador = generador_por_defecto
    generador.siguiente(datetime(2026, 5, 1, 10, 0))
    generador.siguiente(datetime(2026, 5, 1, 10, 1))

    contador = ContadorCorrelativo.objects.get(anio=2026)
    assert contador.ultimo_valor == 2


def test_rn_m04_10_el_prefijo_de_la_serie_es_parametrizable():
    """M04 usará su propia tabla de contadores y su propio prefijo, de modo
    que las series de ingresos y salidas son independientes por construcción."""
    otra_serie = GeneradorCorrelativoPorAnio(ContadorCorrelativo, "SAL")

    assert PREFIJO_INGRESO == "ING"
    assert otra_serie.siguiente(datetime(2026, 5, 1, 10, 0)).startswith("SAL-2026-")
