"""Invariantes de `Salida`: en `clean()` con el mensaje de la historia, y en
la base de datos como salvaguarda (defensa en profundidad, igual que
`Vehiculo` en M02 e `Ingreso` en M03)."""

from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from apps.salidas.models import Salida, TipoMovimiento

from .factories import SalidaFactory

pytestmark = pytest.mark.django_db


# --- RN-M04-01: la cantidad es estrictamente mayor que cero --------------


def test_rn_m04_01_cantidad_cero_no_valida():
    salida = SalidaFactory.build(cantidad_tn=Decimal("0.00"))
    with pytest.raises(ValidationError) as exc:
        salida.clean()
    assert exc.value.message_dict["cantidad_tn"] == ["La cantidad debe ser mayor que cero"]


def test_rn_m04_01_cantidad_negativa_no_valida():
    salida = SalidaFactory.build(cantidad_tn=Decimal("-5.00"))
    with pytest.raises(ValidationError):
        salida.clean()


def test_rn_m04_01_la_base_de_datos_tambien_rechaza_cantidad_no_positiva():
    with pytest.raises(IntegrityError):
        SalidaFactory(cantidad_tn=Decimal("0.00"))


# --- RN-M04-03: una venta exige cliente ----------------------------------


def test_rn_m04_03_venta_sin_cliente_no_valida():
    salida = SalidaFactory.build(tipo_movimiento=TipoMovimiento.VENTA, cliente=None)
    with pytest.raises(ValidationError) as exc:
        salida.clean()
    assert exc.value.message_dict["cliente"] == [
        "Debe indicar el cliente para una salida por venta"
    ]


def test_rn_m04_03_la_base_de_datos_tambien_rechaza_una_venta_sin_cliente():
    with pytest.raises(IntegrityError):
        SalidaFactory(tipo_movimiento=TipoMovimiento.VENTA, cliente=None)


# --- RN-M04-04: una merma exige motivo -----------------------------------


def test_rn_m04_04_merma_sin_motivo_no_valida():
    salida = SalidaFactory.build(
        tipo_movimiento=TipoMovimiento.MERMA, cliente=None, motivo=None
    )
    with pytest.raises(ValidationError) as exc:
        salida.clean()
    assert exc.value.message_dict["motivo"] == ["Debe indicar el motivo de la merma"]


def test_rn_m04_04_un_motivo_en_blanco_no_cuenta_como_motivo():
    salida = SalidaFactory.build(
        tipo_movimiento=TipoMovimiento.MERMA, cliente=None, motivo="   "
    )
    with pytest.raises(ValidationError):
        salida.clean()


def test_rn_m04_04_la_base_de_datos_tambien_rechaza_una_merma_sin_motivo():
    with pytest.raises(IntegrityError):
        SalidaFactory(tipo_movimiento=TipoMovimiento.MERMA, cliente=None, motivo=None)


# --- HU-M04-02 CA01: traslado interno no exige cliente -------------------


def test_hu_m04_02_ca01_traslado_interno_no_exige_cliente():
    salida = SalidaFactory.build(tipo_movimiento=TipoMovimiento.TRASLADO_INTERNO, cliente=None)
    salida.clean()  # no lanza


def test_hu_m04_02_ca01_traslado_interno_se_persiste_sin_cliente():
    salida = SalidaFactory(tipo_movimiento=TipoMovimiento.TRASLADO_INTERNO, cliente=None)
    assert salida.pk is not None
    assert salida.cliente_id is None


def test_una_merma_con_motivo_es_valida():
    salida = SalidaFactory(
        tipo_movimiento=TipoMovimiento.MERMA, cliente=None, motivo="Humedad en cancha"
    )
    assert salida.pk is not None


# --- RN-M04-02 y estructura ----------------------------------------------


def test_rn_m04_02_el_tipo_de_movimiento_es_un_dominio_cerrado():
    assert set(TipoMovimiento.values) == {"VENTA", "TRASLADO_INTERNO", "MERMA"}


def test_el_correlativo_es_unico():
    SalidaFactory(correlativo="SAL-2026-00001")
    with pytest.raises(IntegrityError):
        SalidaFactory(correlativo="SAL-2026-00001")


def test_rn_m04_07_la_salida_nace_en_estado_registrado():
    salida = SalidaFactory()
    assert salida.estado == Salida.REGISTRADO
    assert salida.motivo_anulacion is None
