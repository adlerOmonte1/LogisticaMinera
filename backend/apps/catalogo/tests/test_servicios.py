"""Casos de uso de M02: validación de formato, coherencia de titularidad,
baja lógica y registro en auditoría."""

import logging

import pytest

from apps.catalogo.models import Vehiculo
from common.excepciones import ErrorDeValidacionDeDominio
from apps.catalogo.services import tipos_mineral, transportistas, vehiculos

from .factories import TransportistaFactory, VehiculoFactory

pytestmark = pytest.mark.django_db


def test_codigo_de_tipo_de_mineral_duplicado_es_rechazado(administrador):
    tipos_mineral.crear_tipo_mineral({"codigo": "SAR", "nombre": "Saranda"}, administrador)
    with pytest.raises(ErrorDeValidacionDeDominio) as exc:
        tipos_mineral.crear_tipo_mineral({"codigo": "SAR", "nombre": "Repetido"}, administrador)
    assert str(exc.value) == "El código ya está registrado"


def test_ruc_debe_tener_once_digitos(administrador):
    with pytest.raises(ErrorDeValidacionDeDominio) as exc:
        transportistas.crear_transportista({"razon_social": "X", "ruc": "123"}, administrador)
    assert str(exc.value) == "El RUC debe tener once dígitos"


def test_placa_invalida_es_rechazada(administrador):
    with pytest.raises(ErrorDeValidacionDeDominio) as exc:
        vehiculos.crear_vehiculo(
            {"placa": "12345", "tipo_titularidad": "PROPIO", "capacidad_tn": "20.00"}, administrador
        )
    assert str(exc.value) == "El formato de la placa no es válido"


def test_placa_se_normaliza_a_mayusculas(administrador):
    v = vehiculos.crear_vehiculo(
        {"placa": "abc-123", "tipo_titularidad": "PROPIO", "capacidad_tn": "20.00"}, administrador
    )
    assert v.placa == "ABC-123"


def test_vehiculo_externo_sin_transportista_es_rechazado(administrador):
    with pytest.raises(ErrorDeValidacionDeDominio) as exc:
        vehiculos.crear_vehiculo(
            {"placa": "EXT-900", "tipo_titularidad": "EXTERNO", "capacidad_tn": "20.00"}, administrador
        )
    assert str(exc.value) == "Debe indicar el transportista para un vehículo externo"


def test_vehiculo_propio_ignora_transportista_recibido(administrador):
    t = TransportistaFactory()
    v = vehiculos.crear_vehiculo(
        {"placa": "PRO-900", "tipo_titularidad": "PROPIO", "capacidad_tn": "20.00", "transportista": t.pk},
        administrador,
    )
    assert v.transportista is None


def test_placa_duplicada_es_rechazada(administrador):
    VehiculoFactory(placa="DUP-001")
    with pytest.raises(ErrorDeValidacionDeDominio) as exc:
        vehiculos.crear_vehiculo(
            {"placa": "DUP-001", "tipo_titularidad": "PROPIO", "capacidad_tn": "20.00"}, administrador
        )
    assert str(exc.value) == "La placa ya está registrada"


def test_desactivar_tipo_de_mineral_es_baja_logica(administrador):
    p = tipos_mineral.crear_tipo_mineral({"codigo": "BL", "nombre": "Baja"}, administrador)
    tipos_mineral.desactivar_tipo_mineral(p, administrador)
    p.refresh_from_db()
    assert p.activo is False


def test_desactivar_transportista_con_vehiculos_devuelve_mensaje(administrador):
    t = TransportistaFactory()
    VehiculoFactory(placa="EXT-777", tipo_titularidad=Vehiculo.EXTERNO, transportista=t)
    resultado = transportistas.desactivar_transportista(t, administrador)
    assert resultado.activo is False
    assert resultado.mensaje == "El transportista se desactivó porque tiene vehículos asociados"


def test_desactivar_transportista_sin_vehiculos_no_devuelve_mensaje(administrador):
    t = TransportistaFactory()
    resultado = transportistas.desactivar_transportista(t, administrador)
    assert resultado.mensaje is None


def test_crear_tipo_de_mineral_registra_evento_en_auditoria(administrador, caplog):
    with caplog.at_level(logging.INFO, logger="auditoria"):
        tipos_mineral.crear_tipo_mineral({"codigo": "AUD", "nombre": "Auditado"}, administrador)
    assert any("accion=CREAR" in m and "entidad=TipoMineral" in m for m in caplog.messages)
