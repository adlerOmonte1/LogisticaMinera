"""RN-M04-10 y D-13: la serie de salidas es independiente de la de ingresos."""

from datetime import datetime

import pytest

from apps.ingresos.services.correlativo import generador_por_defecto as generador_ingresos
from apps.salidas.models import ContadorCorrelativo
from apps.salidas.services.correlativo import PREFIJO_SALIDA, generador_por_defecto

pytestmark = pytest.mark.django_db


def test_la_serie_de_salidas_lleva_su_propio_prefijo():
    assert PREFIJO_SALIDA == "SAL"
    assert generador_por_defecto.siguiente(datetime(2026, 5, 1, 10, 0)) == "SAL-2026-00001"


def test_los_correlativos_de_salida_son_crecientes():
    momento = datetime(2026, 5, 1, 10, 0)

    primero = generador_por_defecto.siguiente(momento)
    segundo = generador_por_defecto.siguiente(momento)

    assert (primero, segundo) == ("SAL-2026-00001", "SAL-2026-00002")


def test_rn_m04_10_las_dos_series_no_se_pisan():
    """Cada módulo tiene su propia tabla de contadores: consumir la serie de
    ingresos no adelanta la de salidas ni al revés."""
    momento = datetime(2026, 5, 1, 10, 0)

    generador_ingresos.siguiente(momento)
    generador_ingresos.siguiente(momento)
    primera_salida = generador_por_defecto.siguiente(momento)

    assert primera_salida == "SAL-2026-00001"


def test_la_serie_de_salidas_se_reinicia_por_anio():
    generador_por_defecto.siguiente(datetime(2026, 12, 31, 23, 0))

    primero = generador_por_defecto.siguiente(datetime(2027, 1, 1, 0, 5))

    assert primero == "SAL-2027-00001"


def test_el_contador_de_salidas_persiste_su_ultimo_valor():
    generador_por_defecto.siguiente(datetime(2026, 5, 1, 10, 0))
    generador_por_defecto.siguiente(datetime(2026, 5, 1, 10, 1))

    assert ContadorCorrelativo.objects.get(anio=2026).ultimo_valor == 2
