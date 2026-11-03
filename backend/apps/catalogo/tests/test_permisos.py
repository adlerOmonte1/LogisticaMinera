"""Autorización de M02: todos consultan; Administrador y Administrativo
gestionan; el vehículo admite el alta de los tres roles y la tara solo la cambia
el Administrador (requerimientos/funcionales.md, matriz de permisos)."""

import pytest

from apps.auditoria.models import EventoAuditoria

from .factories import TipoMineralFactory

pytestmark = pytest.mark.django_db
TIPOS_MINERAL = "/api/v1/catalogo/tipos-mineral/"


def test_supervisor_puede_consultar(api_como, supervisor):
    TipoMineralFactory()
    r = api_como(supervisor).get(TIPOS_MINERAL)
    assert r.status_code == 200


def test_el_rechazo_queda_registrado_como_acceso_rechazado(api_como, supervisor):
    api_como(supervisor).post(TIPOS_MINERAL, {"codigo": "XX", "nombre": "X"})
    assert EventoAuditoria.objects.filter(accion="ACCESO_RECHAZADO", usuario=supervisor).exists()


def test_administrativo_puede_crear(api_como, administrativo):
    r = api_como(administrativo).post(TIPOS_MINERAL, {"codigo": "ADM", "nombre": "Ok"})
    assert r.status_code == 201


def test_sin_token_no_se_accede(api):
    assert api.get(TIPOS_MINERAL).status_code == 401
