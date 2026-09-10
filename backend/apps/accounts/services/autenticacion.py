"""RS-M01-01, RS-M01-03, RS-M01-04, RS-M01-08. HU-M01-01, HU-M01-02.

No importa nada de `rest_framework`: el dominio del login es independiente
del transporte (backend-django, "Excepciones de dominio"). La vista traduce
estas excepciones a HTTP a través de `utils.manejador_errores`.
"""

from datetime import timedelta

from django.utils import timezone

from apps.accounts.models import Usuario
from apps.accounts.repositories import UsuarioRepository
from common.eventos import RegistradorDeEventos, registrador_por_defecto
from common.excepciones import ErrorDeValidacionDeDominio

MAX_INTENTOS_FALLIDOS = 5  # RN-M01-07
MINUTOS_BLOQUEO = 15  # RS-M01-04

# Mensajes literales — coinciden con los criterios de aceptación de HU-M01-01
# y HU-M01-02. Las pruebas los verifican por igualdad exacta; si cambian aquí,
# cambian también en el HU.md del módulo.
MENSAJE_CREDENCIALES_INVALIDAS = "Usuario o contraseña incorrectos"
MENSAJE_CUENTA_BLOQUEADA = "Cuenta bloqueada temporalmente. Intente nuevamente en 15 minutos"
MENSAJE_CUENTA_INACTIVA = "La cuenta se encuentra inactiva. Contacte al administrador"
MENSAJE_TOKEN_INVALIDO = "El token de sesión no es válido"


class CredencialesInvalidas(ErrorDeValidacionDeDominio):
    """No distingue usuario inexistente de contraseña incorrecta (RNF-M01-02)."""

    def __init__(self):
        super().__init__(MENSAJE_CREDENCIALES_INVALIDAS, codigo="CREDENCIALES_INVALIDAS")


class CuentaBloqueada(ErrorDeValidacionDeDominio):
    def __init__(self):
        super().__init__(MENSAJE_CUENTA_BLOQUEADA, codigo="CUENTA_BLOQUEADA")


class CuentaInactiva(ErrorDeValidacionDeDominio):
    def __init__(self):
        super().__init__(MENSAJE_CUENTA_INACTIVA, codigo="CUENTA_INACTIVA")


def autenticar(
    username: str,
    password: str,
    *,
    ip: str | None = None,
    registrador: RegistradorDeEventos = registrador_por_defecto,
) -> Usuario:
    """HU-M01-01 CA01-CA05.

    Orden de las comprobaciones (importa, ver notas.md):
    1. Bloqueo vigente -> rechaza de inmediato, sin gastar el intento.
    2. Bloqueo ya expirado -> se limpia antes de evaluar la contraseña.
    3. Usuario inexistente o contraseña incorrecta -> mismo mensaje genérico,
       incrementa el contador y bloquea al llegar al quinto fallo.
    4. Contraseña correcta pero cuenta inactiva -> rechaza y NO cuenta como
       fallo (la credencial era válida).
    5. Éxito -> reinicia contador, actualiza `last_login`, registra evento.
    """
    usuario = UsuarioRepository.obtener_por_username(username)

    if usuario is not None and usuario.bloqueado_hasta is not None:
        if usuario.bloqueado_hasta > timezone.now():
            raise CuentaBloqueada()
        usuario.bloqueado_hasta = None
        usuario.intentos_fallidos = 0

    if usuario is None or not usuario.check_password(password):
        if usuario is not None:
            usuario.intentos_fallidos += 1
            if usuario.intentos_fallidos >= MAX_INTENTOS_FALLIDOS:
                usuario.bloqueado_hasta = timezone.now() + timedelta(minutes=MINUTOS_BLOQUEO)
            usuario.save(update_fields=["intentos_fallidos", "bloqueado_hasta"])
            if usuario.bloqueado_hasta is not None:
                raise CuentaBloqueada()
        raise CredencialesInvalidas()

    usuario.intentos_fallidos = 0
    usuario.bloqueado_hasta = None

    if not usuario.is_active:
        usuario.save(update_fields=["intentos_fallidos", "bloqueado_hasta"])
        raise CuentaInactiva()

    usuario.last_login = timezone.now()
    usuario.save(update_fields=["intentos_fallidos", "bloqueado_hasta", "last_login"])

    registrador.registrar(evento="INICIO_DE_SESION", usuario=usuario, ip=ip, detalles={})
    return usuario


def cerrar_sesion(refresh_token: str) -> None:
    """HU-M01-02 CA01: invalida el token vigente.

    Requiere `rest_framework_simplejwt.token_blacklist` instalada (ver
    settings): sin la tabla de lista negra, `blacklist()` no tiene dónde
    persistir la invalidación y el token seguiría siendo válido hasta expirar
    por tiempo — contradiría CA01 y CA02.
    """
    from rest_framework_simplejwt.exceptions import TokenError
    from rest_framework_simplejwt.tokens import RefreshToken

    try:
        RefreshToken(refresh_token).blacklist()
    except TokenError as exc:
        raise ErrorDeValidacionDeDominio(MENSAJE_TOKEN_INVALIDO, codigo="TOKEN_INVALIDO") from exc
