"""HU-M01-01 — Inicio y cierre de sesión. Una prueba por criterio de aceptación;
los mensajes se comparan con el texto literal de la historia (D-23)."""

from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework_simplejwt.tokens import AccessToken

from apps.accounts.services.autenticacion import CredencialesInvalidas, CuentaBloqueada, autenticar
from apps.auditoria.models import EventoAuditoria
from common.eventos import Accion

from .factories import UsuarioFactory

pytestmark = pytest.mark.django_db
LOGIN = "/api/v1/auth/login/"
BLOQUEADA = "Cuenta bloqueada temporalmente. Intente nuevamente en 15 minutos"


def test_hu_m01_01_ca01_credenciales_validas_establecen_la_sesion(api, supervisor, password):
    r = api.post(LOGIN, {"username": supervisor.username, "password": password})

    assert r.status_code == 200
    assert r.data["access"] and r.data["refresh"]
    assert r.data["usuario"]["rol"] == "SUPERVISOR"
    assert r.data["usuario"]["debe_cambiar_clave"] is False


def test_hu_m01_01_ca02_credenciales_invalidas_no_dicen_que_campo_fallo(api, supervisor):
    mala = api.post(LOGIN, {"username": supervisor.username, "password": "incorrecta"})
    inexistente = api.post(LOGIN, {"username": "no-existe", "password": "cualquiera"})

    for r in (mala, inexistente):
        assert r.status_code == 401
        assert r.data["mensaje"] == "Usuario o contraseña incorrectos"


def test_hu_m01_01_ca03_cinco_intentos_fallidos_bloquean_la_cuenta(api, supervisor, password):
    for _ in range(4):
        api.post(LOGIN, {"username": supervisor.username, "password": "mala"})
    quinto = api.post(LOGIN, {"username": supervisor.username, "password": "mala"})
    sexto = api.post(LOGIN, {"username": supervisor.username, "password": password})

    for r in (quinto, sexto):
        assert r.status_code == 423
        assert r.data["mensaje"] == BLOQUEADA


def test_hu_m01_01_ca04_cuenta_inactiva_no_autentica(api, password):
    inactivo = UsuarioFactory(is_active=False)

    r = api.post(LOGIN, {"username": inactivo.username, "password": password})

    assert r.status_code == 401
    assert r.data["mensaje"] == "La cuenta se encuentra inactiva. Contacte al administrador"


def test_hu_m01_01_ca05_cerrar_sesion_invalida_el_token(api, supervisor, password):
    refresh = api.post(LOGIN, {"username": supervisor.username, "password": password}).data["refresh"]

    salida = api.post("/api/v1/auth/logout/", {"refresh": refresh})
    reuso = api.post("/api/v1/auth/refresh/", {"refresh": refresh})

    assert salida.status_code == 204
    assert reuso.status_code == 401


def test_hu_m01_01_ca06_sesion_expirada(api, supervisor):
    token = AccessToken.for_user(supervisor)
    token.set_exp(lifetime=-timedelta(minutes=1))
    api.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    r = api.get("/api/v1/catalogo/tipos-mineral/")

    assert r.status_code == 401
    assert r.data["mensaje"] == "Su sesión ha expirado. Ingrese nuevamente"


def test_hu_m01_01_ca07_inicio_y_cierre_quedan_en_auditoria(api, supervisor, password):
    login = api.post(LOGIN, {"username": supervisor.username, "password": password}, REMOTE_ADDR="10.0.0.7")
    api.post("/api/v1/auth/logout/", {"refresh": login.data["refresh"]})

    inicio = EventoAuditoria.objects.get(accion=Accion.INICIAR_SESION, usuario=supervisor)
    assert inicio.direccion_ip == "10.0.0.7"
    assert EventoAuditoria.objects.filter(accion=Accion.CERRAR_SESION, usuario=supervisor).exists()


def test_hu_m01_01_ca09_la_clave_temporal_obliga_a_cambiarla(api, supervisor, password):
    supervisor.debe_cambiar_clave = True
    supervisor.save()
    login = api.post(LOGIN, {"username": supervisor.username, "password": password})
    assert login.data["usuario"]["debe_cambiar_clave"] is True
    api.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

    bloqueada = api.get("/api/v1/catalogo/tipos-mineral/")
    cambio = api.post(
        "/api/v1/usuarios/cambiar-clave/",
        {"password_actual": password, "password_nueva": "nueva-clave-1", "password_nueva_confirmacion": "nueva-clave-1"},
    )
    liberada = api.get("/api/v1/catalogo/tipos-mineral/")

    assert bloqueada.status_code == 403
    assert bloqueada.data["mensaje"] == "Debe cambiar la contraseña temporal antes de continuar"
    assert cambio.status_code == 200
    assert liberada.status_code == 200


def test_rn_m01_05_un_usuario_inactivo_no_se_autentica(password):
    inactivo = UsuarioFactory(is_active=False)
    with pytest.raises(Exception) as exc:
        autenticar(inactivo.username, password)
    assert exc.value.codigo == "CUENTA_INACTIVA"


def test_rn_m01_07_el_contador_se_reinicia_tras_un_acceso_exitoso(api, supervisor, password):
    api.post(LOGIN, {"username": supervisor.username, "password": "mala"})
    api.post(LOGIN, {"username": supervisor.username, "password": password})

    supervisor.refresh_from_db()
    assert supervisor.intentos_fallidos == 0


def test_rn_m01_07_el_bloqueo_expira_a_los_quince_minutos(supervisor, password):
    for _ in range(4):
        with pytest.raises(CredencialesInvalidas):
            autenticar(supervisor.username, "mala")
    with pytest.raises(CuentaBloqueada):
        autenticar(supervisor.username, "mala")

    despues = lambda: timezone.now() + timedelta(minutes=16)  # noqa: E731
    assert autenticar(supervisor.username, password, ahora=despues).pk == supervisor.pk
