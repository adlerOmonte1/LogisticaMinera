"""Casos de prueba de HU-M01-01 (inicio de sesión) y HU-M01-02 (cierre).

Un caso por criterio de aceptación. Los mensajes se comparan por igualdad
exacta contra el texto literal de la historia (pruebas-y-desempeno).
"""

import logging
from datetime import timedelta

import pytest
from django.utils import timezone

from apps.accounts.services import autenticacion as svc
from apps.accounts.services.autenticacion import autenticar

from .factories import UsuarioFactory

pytestmark = pytest.mark.django_db
LOGIN = "/api/v1/auth/login/"


def test_ca01_credenciales_validas_establecen_sesion(api, supervisor, password):
    respuesta = api.post(LOGIN, {"username": supervisor.username, "password": password})

    assert respuesta.status_code == 200
    assert "access" in respuesta.data and "refresh" in respuesta.data
    assert respuesta.data["usuario"]["rol"] == "SUPERVISOR"


def test_ca02_credenciales_invalidas_mensaje_generico(api, supervisor):
    respuesta = api.post(LOGIN, {"username": supervisor.username, "password": "incorrecta"})

    assert respuesta.status_code == 400
    assert respuesta.data["mensaje"] == "Usuario o contraseña incorrectos"


def test_ca02_usuario_inexistente_mismo_mensaje_que_password_mala(api):
    respuesta = api.post(LOGIN, {"username": "no-existe", "password": "cualquiera"})

    assert respuesta.status_code == 400
    assert respuesta.data["mensaje"] == "Usuario o contraseña incorrectos"


def test_ca03_cinco_intentos_fallidos_bloquean_la_cuenta(api, supervisor):
    for _ in range(4):
        api.post(LOGIN, {"username": supervisor.username, "password": "mala"})

    quinto = api.post(LOGIN, {"username": supervisor.username, "password": "mala"})

    assert quinto.status_code == 400
    assert quinto.data["mensaje"] == (
        "Cuenta bloqueada temporalmente. Intente nuevamente en 15 minutos"
    )
    supervisor.refresh_from_db()
    assert supervisor.bloqueado_hasta is not None


def test_ca03_cuenta_bloqueada_rechaza_aun_con_password_correcta(api, supervisor, password):
    for _ in range(5):
        api.post(LOGIN, {"username": supervisor.username, "password": "mala"})

    respuesta = api.post(LOGIN, {"username": supervisor.username, "password": password})

    assert respuesta.status_code == 400
    assert respuesta.data["mensaje"] == (
        "Cuenta bloqueada temporalmente. Intente nuevamente en 15 minutos"
    )


def test_ca04_cuenta_inactiva_no_autentica_aunque_las_credenciales_sean_validas(api, password):
    inactivo = UsuarioFactory(is_active=False)

    respuesta = api.post(LOGIN, {"username": inactivo.username, "password": password})

    assert respuesta.status_code == 400
    assert respuesta.data["mensaje"] == (
        "La cuenta se encuentra inactiva. Contacte al administrador"
    )


def test_ca05_inicio_de_sesion_exitoso_registra_evento_en_auditoria(api, supervisor, password, caplog):
    with caplog.at_level(logging.INFO, logger="auditoria"):
        api.post(LOGIN, {"username": supervisor.username, "password": password})

    assert any("INICIO_DE_SESION" in m and supervisor.username in m for m in caplog.messages)


def test_rn_m01_07_contador_se_reinicia_tras_acceso_exitoso(api, supervisor, password):
    api.post(LOGIN, {"username": supervisor.username, "password": "mala"})
    api.post(LOGIN, {"username": supervisor.username, "password": "mala"})

    api.post(LOGIN, {"username": supervisor.username, "password": password})

    supervisor.refresh_from_db()
    assert supervisor.intentos_fallidos == 0


def test_rn_m01_07_el_bloqueo_expira_transcurridos_quince_minutos(supervisor, password):
    for _ in range(5):
        with pytest.raises(svc.ErrorDeValidacionDeDominio):
            autenticar(supervisor.username, "mala")

    despues = lambda: timezone.now() + timedelta(minutes=16)  # noqa: E731
    usuario = autenticar(supervisor.username, password, ahora=despues)

    assert usuario.pk == supervisor.pk


# --- HU-M01-02 -------------------------------------------------------------

def test_hu02_ca01_logout_invalida_el_refresh(api, supervisor, password):
    login = api.post(LOGIN, {"username": supervisor.username, "password": password})
    refresh = login.data["refresh"]

    salida = api.post("/api/v1/auth/logout/", {"refresh": refresh})
    reuso = api.post("/api/v1/auth/refresh/", {"refresh": refresh})

    assert salida.status_code == 204
    assert reuso.status_code == 401


def test_hu02_ca02_endpoint_protegido_sin_token_responde_401(api):
    respuesta = api.get("/api/v1/usuarios/")

    assert respuesta.status_code == 401
