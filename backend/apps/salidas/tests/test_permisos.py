"""Matriz de permisos de M04 (`requerimientos/funcionales.md`): el Supervisor
consulta, pero no registra ni anula — su rol opera en la recepción de
material, no en el despacho."""

import pytest

from apps.catalogo.tests.factories import ClienteFactory, ProductoFactory
from apps.salidas.models import TipoMovimiento

from .factories import SalidaFactory

pytestmark = pytest.mark.django_db

SALIDAS = "/api/v1/salidas/"


def _payload():
    return {
        "fecha": "2026-05-10",
        "producto": ProductoFactory().pk,
        "cliente": ClienteFactory().pk,
        "tipo_movimiento": TipoMovimiento.VENTA,
        "cantidad_tn": "12.00",
    }


@pytest.mark.parametrize("rol", ["administrador", "administrativo"])
def test_los_roles_de_despacho_registran_salidas(request, api_como, rol):
    usuario = request.getfixturevalue(rol)
    r = api_como(usuario).post(SALIDAS, _payload())
    assert r.status_code == 201


def test_el_supervisor_no_registra_salidas(api_como, supervisor):
    r = api_como(supervisor).post(SALIDAS, _payload())
    assert r.status_code == 403
    assert r.data["mensaje"] == "Acción no autorizada"


def test_el_supervisor_no_anula_salidas(api_como, supervisor):
    salida = SalidaFactory()
    r = api_como(supervisor).post(f"{SALIDAS}{salida.pk}/anular/", {"motivo": "x"})
    assert r.status_code == 403


@pytest.mark.parametrize("rol", ["administrador", "administrativo", "supervisor"])
def test_los_tres_roles_consultan(request, api_como, rol):
    SalidaFactory()
    usuario = request.getfixturevalue(rol)
    r = api_como(usuario).get(SALIDAS)
    assert r.status_code == 200


def test_sin_autenticar_no_se_accede(api):
    assert api.get(SALIDAS).status_code == 401
