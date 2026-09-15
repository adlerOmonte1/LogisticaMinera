"""Casos de prueba de HU-M01-03 CA04 y HU-M01-04 CA02: la autorización se
resuelve en el servidor y los rechazos quedan en auditoría.

backend-auth-permisos: "por cada opción que el frontend oculta según el rol,
debe existir un permiso del backend que rechace la misma operación, y una
prueba que lo verifique".
"""

import logging

import pytest

pytestmark = pytest.mark.django_db
USUARIOS = "/api/v1/usuarios/"


@pytest.mark.parametrize("rol_no_autorizado", ["supervisor", "administrativo"])
def test_ca04_rol_no_administrador_no_gestiona_usuarios(request, api_como, rol_no_autorizado):
    usuario = request.getfixturevalue(rol_no_autorizado)

    respuesta = api_como(usuario).get(USUARIOS)

    assert respuesta.status_code == 403
    assert respuesta.data["mensaje"] == "Acción no autorizada"


def test_ca04_solicitud_sin_autenticar_responde_401(api):
    respuesta = api.post(USUARIOS, {})

    assert respuesta.status_code == 401


def test_administrador_si_gestiona_usuarios(api_como, administrador):
    respuesta = api_como(administrador).get(USUARIOS)

    assert respuesta.status_code == 200


def test_hu01_04_ca02_el_rechazo_por_autorizacion_queda_en_auditoria(api_como, supervisor, caplog):
    with caplog.at_level(logging.INFO, logger="auditoria"):
        api_como(supervisor).post(USUARIOS, {})

    assert any(
        "ACCESO_RECHAZADO" in m and supervisor.username in m for m in caplog.messages
    )
