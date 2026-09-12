"""Invariantes de `Ingreso` a nivel de base de datos: salvaguarda además del
mensaje de dominio que da el servicio (defensa en profundidad, igual que
`Vehiculo.clean()` en M02)."""

import pytest
from django.db import IntegrityError

from apps.ingresos.models import Ingreso

from .factories import IngresoFactory

pytestmark = pytest.mark.django_db


def test_rn_m03_03_la_base_de_datos_rechaza_tara_mayor_o_igual_al_bruto():
    with pytest.raises(IntegrityError):
        IngresoFactory(peso_bruto_tn="10.00", tara_tn="10.00")


def test_rn_m03_05_ticket_unico_solo_entre_no_anulados():
    IngresoFactory(numero_ticket="TCK-0001", estado=Ingreso.ANULADO)
    # Un ticket anulado no bloquea su reutilización (nota de reglas_negocio.md).
    IngresoFactory(numero_ticket="TCK-0001", estado=Ingreso.REGISTRADO)


def test_rn_m03_05_la_base_de_datos_rechaza_dos_activos_con_el_mismo_ticket():
    IngresoFactory(numero_ticket="TCK-0002", estado=Ingreso.REGISTRADO)
    with pytest.raises(IntegrityError):
        IngresoFactory(numero_ticket="TCK-0002", estado=Ingreso.REGISTRADO)


def test_pesos_deben_ser_positivos():
    with pytest.raises(IntegrityError):
        IngresoFactory(peso_bruto_tn="-1.00", tara_tn="0.50")
