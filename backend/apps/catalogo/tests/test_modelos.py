"""Reglas de negocio de M02 verificadas en la capa de modelo."""

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from apps.catalogo.models import Producto, Vehiculo

from .factories import ProductoFactory, TransportistaFactory, VehiculoFactory

pytestmark = pytest.mark.django_db


def test_rn_m02_01_codigo_de_producto_es_unico():
    ProductoFactory(codigo="SARANDA")
    with pytest.raises(IntegrityError):
        Producto.objects.create(codigo="SARANDA", nombre="Otro")


def test_rn_m02_02_placa_es_unica():
    VehiculoFactory(placa="XYZ-100")
    with pytest.raises(IntegrityError):
        Vehiculo.objects.create(placa="XYZ-100", tipo_titularidad=Vehiculo.PROPIO, capacidad_tn="20.00")


def test_rn_m02_09_unidad_de_medida_por_defecto_es_tonelada():
    p = ProductoFactory()
    assert p.unidad_medida == Producto.TONELADA


def test_rn_m02_04_vehiculo_externo_sin_transportista_no_valida():
    vehiculo = Vehiculo(placa="EXT-001", tipo_titularidad=Vehiculo.EXTERNO, capacidad_tn="25.00")
    with pytest.raises(ValidationError):
        vehiculo.full_clean()


def test_rn_m02_05_vehiculo_propio_con_transportista_no_valida():
    t = TransportistaFactory()
    vehiculo = Vehiculo(
        placa="PRO-001", tipo_titularidad=Vehiculo.PROPIO, capacidad_tn="25.00", transportista=t
    )
    with pytest.raises(ValidationError):
        vehiculo.full_clean()


def test_rn_m02_04_vehiculo_externo_con_transportista_valida():
    t = TransportistaFactory()
    vehiculo = Vehiculo(
        placa="EXT-002", tipo_titularidad=Vehiculo.EXTERNO, capacidad_tn="25.00", transportista=t
    )
    vehiculo.full_clean()  # no lanza
