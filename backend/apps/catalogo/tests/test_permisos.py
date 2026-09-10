"""Autorización de M02: todos consultan, solo Administrador y Administrativo
escriben (requerimientos/funcionales.md, matriz de permisos)."""

import pytest

from .factories import ProductoFactory

pytestmark = pytest.mark.django_db
PRODUCTOS = "/api/v1/catalogo/productos/"


def test_supervisor_puede_consultar(api_como, supervisor):
    ProductoFactory()
    r = api_como(supervisor).get(PRODUCTOS)
    assert r.status_code == 200


def test_supervisor_no_puede_crear(api_como, supervisor):
    r = api_como(supervisor).post(PRODUCTOS, {"codigo": "X", "nombre": "X"})
    assert r.status_code == 403
    assert r.data["mensaje"] == "Acción no autorizada"


def test_administrativo_puede_crear(api_como, administrativo):
    r = api_como(administrativo).post(PRODUCTOS, {"codigo": "ADM", "nombre": "Ok"})
    assert r.status_code == 201


def test_sin_token_no_se_accede(api):
    assert api.get(PRODUCTOS).status_code == 401
