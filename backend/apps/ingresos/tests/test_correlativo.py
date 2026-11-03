"""D-02: el código del ingreso es único, creciente y se reinicia cada año."""

from datetime import datetime

import pytest

from apps.ingresos.models import ContadorCorrelativo
from apps.ingresos.services.correlativo import PREFIJO_INGRESO, generador_por_defecto
from common.correlativo import GeneradorCorrelativoPorAnio

pytestmark = pytest.mark.django_db


def test_d_02_codigos_sucesivos_son_distintos_y_crecientes():
    generador = generador_por_defecto
    momento = datetime(2027, 5, 1, 10, 0)

    primero = generador.siguiente(momento)
    segundo = generador.siguiente(momento)

    assert primero == "ING-2027-00001"
    assert segundo == "ING-2027-00002"


def test_d_02_el_codigo_se_reinicia_por_anio():
    generador = generador_por_defecto
    generador.siguiente(datetime(2027, 12, 31, 23, 0))

    primero_del_anio_siguiente = generador.siguiente(datetime(2028, 1, 1, 0, 5))

    assert primero_del_anio_siguiente == "ING-2028-00001"


def test_d_02_el_contador_persiste_el_ultimo_valor_por_anio():
    generador = generador_por_defecto
    generador.siguiente(datetime(2027, 5, 1, 10, 0))
    generador.siguiente(datetime(2027, 5, 1, 10, 1))

    contador = ContadorCorrelativo.objects.get(anio=2027)
    assert contador.ultimo_valor == 2


def test_d_02_el_prefijo_de_la_serie_es_parametrizable():
    otra_serie = GeneradorCorrelativoPorAnio(ContadorCorrelativo, "PRB")

    assert PREFIJO_INGRESO == "ING"
    assert otra_serie.siguiente(datetime(2027, 5, 1, 10, 0)).startswith("PRB-2027-")
