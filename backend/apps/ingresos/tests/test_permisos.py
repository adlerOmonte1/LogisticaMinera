"""Matriz de permisos de M03 (requerimientos/funcionales.md):
los tres roles registran y consultan; solo Administrador y Administrativo
editan o anulan."""

import pytest

from apps.catalogo.tests.factories import ProductoFactory, VehiculoFactory

from .factories import IngresoFactory

pytestmark = pytest.mark.django_db

INGRESOS = "/api/v1/ingresos/"


def _payload():
    vehiculo, producto = VehiculoFactory(), ProductoFactory()
    return {
        "fecha_pesaje": "2026-03-15", "hora_pesaje": "08:30:00",
        "numero_ticket": "TCK-PERM", "vehiculo": vehiculo.pk, "producto": producto.pk,
        "peso_bruto_tn": "32.50", "tara_tn": "12.30",
    }


@pytest.mark.parametrize("rol", ["administrador", "administrativo", "supervisor"])
def test_los_tres_roles_registran_ingresos(request, api_como, rol):
    usuario = request.getfixturevalue(rol)
    r = api_como(usuario).post(INGRESOS, _payload())
    assert r.status_code == 201


@pytest.mark.parametrize("rol", ["administrador", "administrativo", "supervisor"])
def test_los_tres_roles_consultan(request, api_como, rol):
    IngresoFactory()
    usuario = request.getfixturevalue(rol)
    r = api_como(usuario).get(INGRESOS)
    assert r.status_code == 200


def test_hu_m03_05_ca03_supervisor_no_puede_editar(api_como, supervisor):
    ingreso = IngresoFactory()
    r = api_como(supervisor).patch(f"{INGRESOS}{ingreso.pk}/", {"numero_ticket": "X"})
    assert r.status_code == 403
    assert r.data["mensaje"] == "Acción no autorizada"


def test_supervisor_no_puede_anular(api_como, supervisor):
    ingreso = IngresoFactory()
    r = api_como(supervisor).post(f"{INGRESOS}{ingreso.pk}/anular/", {"motivo": "x"})
    assert r.status_code == 403


def test_administrativo_puede_editar_y_anular(api_como, administrativo):
    ingreso = IngresoFactory()
    r1 = api_como(administrativo).patch(f"{INGRESOS}{ingreso.pk}/", {"numero_ticket": "OK"})
    assert r1.status_code == 200

    otro = IngresoFactory()
    r2 = api_como(administrativo).post(f"{INGRESOS}{otro.pk}/anular/", {"motivo": "x"})
    assert r2.status_code == 200


def test_sin_token_no_se_accede(api):
    assert api.get(INGRESOS).status_code == 401
