"""Autorización de M02: todos consultan, solo Administrador y Administrativo
escriben (requerimientos/funcionales.md, matriz de permisos)."""

import pytest

from .factories import TipoMineralFactory

pytestmark = pytest.mark.django_db
TIPOS_MINERAL = "/api/v1/catalogo/tipos-mineral/"


def test_supervisor_puede_consultar(api_como, supervisor):
    TipoMineralFactory()
    r = api_como(supervisor).get(TIPOS_MINERAL)
    assert r.status_code == 200


def test_supervisor_no_puede_crear(api_como, supervisor):
    r = api_como(supervisor).post(TIPOS_MINERAL, {"codigo": "XX", "nombre": "X"})
    assert r.status_code == 403
    assert r.data["mensaje"] == "Acción no autorizada"


def test_administrativo_puede_crear(api_como, administrativo):
    r = api_como(administrativo).post(TIPOS_MINERAL, {"codigo": "ADM", "nombre": "Ok"})
    assert r.status_code == 201


def test_sin_token_no_se_accede(api):
    assert api.get(TIPOS_MINERAL).status_code == 401
