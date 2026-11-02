"""HU-M01-03 — Control de acceso por rol."""

import pytest
from rest_framework.test import APIRequestFactory

from apps.accounts import permissions as p
from apps.accounts.models import Rol
from apps.auditoria.models import EventoAuditoria
from common.eventos import Accion
from common.excepciones import AccionNoAutorizada

from .factories import RolFactory

pytestmark = pytest.mark.django_db


def _permite(permiso, usuario):
    solicitud = APIRequestFactory().get("/")
    solicitud.user = usuario
    try:
        return permiso().has_permission(solicitud, None)
    except AccionNoAutorizada:
        return False


def test_hu_m01_03_ca02_endpoint_fuera_del_rol_responde_403(api_como, supervisor):
    r = api_como(supervisor).post("/api/v1/usuarios/", {})

    assert r.status_code == 403
    assert r.data["mensaje"] == "Acción no autorizada"


def test_hu_m01_03_ca03_el_cambio_de_rol_aplica_en_la_siguiente_accion(api_como, supervisor):
    cliente = api_como(supervisor)
    assert cliente.get("/api/v1/usuarios/").status_code == 403

    supervisor.rol = RolFactory(nombre=Rol.ADMINISTRADOR)
    supervisor.save()

    assert cliente.get("/api/v1/usuarios/").status_code == 200


def test_hu_m01_03_ca04_el_rechazo_queda_en_auditoria(api_como, supervisor):
    api_como(supervisor).get("/api/v1/usuarios/")

    evento = EventoAuditoria.objects.get(accion=Accion.ACCESO_RECHAZADO)
    assert evento.usuario == supervisor
    assert evento.valores_nuevos["ruta"] == "/api/v1/usuarios/"


def test_hu_m01_03_ca05_el_supervisor_da_de_alta_vehiculos_y_registra_destares(supervisor):
    assert _permite(p.PuedeDarAltaVehiculo, supervisor)
    assert _permite(p.PuedeRegistrarDestare, supervisor)
    assert not _permite(p.PuedeGestionarCatalogo, supervisor)


@pytest.mark.parametrize("rol", ["administrativo", "supervisor"])
def test_hu_m01_03_ca06_solo_el_administrador_cierra_lotes(request, rol, administrador):
    assert not _permite(p.PuedeCerrarLote, request.getfixturevalue(rol))
    assert _permite(p.PuedeCerrarLote, administrador)


def test_rn_m01_06_solo_el_administrador_gestiona_usuarios(administrador, administrativo):
    assert _permite(p.PuedeGestionarUsuarios, administrador)
    assert not _permite(p.PuedeGestionarUsuarios, administrativo)


def test_rn_m01_09_el_permiso_es_por_operacion(supervisor):
    assert _permite(p.PuedeRegistrarIngreso, supervisor)
    assert not _permite(p.PuedeCorregirIngreso, supervisor)
    assert not _permite(p.PuedeAnularIngreso, supervisor)


def test_rn_m01_10_cierre_de_lote_reservado(administrativo):
    assert not _permite(p.PuedeCerrarLote, administrativo)


def test_sin_sesion_responde_401(api):
    assert api.get("/api/v1/usuarios/").status_code == 401
