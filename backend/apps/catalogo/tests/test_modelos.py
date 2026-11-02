"""Reglas de negocio de M02 verificadas en la capa de modelo y en la base de datos."""

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from apps.catalogo.models import TipoMineral, Transportista, Vehiculo

from .factories import TipoMineralFactory, TransportistaFactory, VehiculoFactory

pytestmark = pytest.mark.django_db


def test_rn_m02_06_codigo_de_tipo_de_mineral_es_unico():
    TipoMineralFactory(codigo="SARAND")
    with pytest.raises(IntegrityError):
        TipoMineral.objects.create(codigo="SARAND", nombre="Otro")


def test_rn_m02_15_nombre_de_tipo_de_mineral_es_unico_sin_distinguir_mayusculas():
    TipoMineralFactory(codigo="SAR", nombre="Saranda")
    with pytest.raises(IntegrityError):
        TipoMineral.objects.create(codigo="SAR2", nombre="SARANDA")


def test_rn_m02_18_ruc_de_transportista_es_unico():
    TransportistaFactory(ruc="20604123457")
    with pytest.raises(IntegrityError):
        Transportista.objects.create(razon_social="Otro", ruc="20604123457")


def test_rn_m02_01_placa_es_unica():
    VehiculoFactory(placa="XYZ-100")
    with pytest.raises(IntegrityError):
        Vehiculo.objects.create(placa="XYZ-100", tipo_titularidad=Vehiculo.PROPIO, capacidad_tn="20.00")


def test_rn_m02_10_unidad_de_medida_por_defecto_es_tonelada():
    p = TipoMineralFactory()
    assert p.unidad_medida == TipoMineral.TONELADA


def test_rn_m02_02_titularidad_fuera_del_dominio_no_valida():
    vehiculo = Vehiculo(placa="ABC-101", tipo_titularidad="ALQUILADO", capacidad_tn="25.00")
    with pytest.raises(ValidationError):
        vehiculo.full_clean()


def test_rn_m02_03_vehiculo_externo_sin_transportista_no_valida():
    vehiculo = Vehiculo(placa="EXT-001", tipo_titularidad=Vehiculo.EXTERNO, capacidad_tn="25.00")
    with pytest.raises(ValidationError):
        vehiculo.full_clean()


def test_rn_m02_04_vehiculo_propio_con_transportista_no_valida():
    t = TransportistaFactory()
    vehiculo = Vehiculo(
        placa="PRO-001", tipo_titularidad=Vehiculo.PROPIO, capacidad_tn="25.00", transportista=t
    )
    with pytest.raises(ValidationError):
        vehiculo.full_clean()


def test_rn_m02_03_vehiculo_externo_con_transportista_valida():
    t = TransportistaFactory()
    vehiculo = Vehiculo(
        placa="EXT-002", tipo_titularidad=Vehiculo.EXTERNO, capacidad_tn="25.00", transportista=t
    )
    vehiculo.full_clean()  # no lanza


def test_rn_m02_11_el_vehiculo_nace_sin_tara_y_pendiente_de_destare():
    v = VehiculoFactory()
    assert v.tara_tn is None and v.fecha_destare is None and v.usuario_destare is None
    assert v.pendiente_destare is True


def test_rn_m02_08_el_modelo_no_ofrece_baja_fisica_desde_la_api():
    # La protección real es de la API (sin DELETE, D-22); el modelo conserva el
    # vínculo con los ingresos por PROTECT.
    from apps.ingresos.tests.factories import IngresoFactory

    ingreso = IngresoFactory()
    with pytest.raises(Exception):
        ingreso.vehiculo.delete()
    assert Vehiculo.objects.filter(pk=ingreso.vehiculo_id).exists()
