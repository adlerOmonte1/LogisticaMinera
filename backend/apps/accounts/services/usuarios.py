"""RS-M01-06, RS-M01-07. HU-M01-03, HU-M01-04, HU-M01-05.

Las funciones reciben instancias de `Usuario` ya resueltas por la vista
(`get_object_or_404` o `request.user`), no identificadores: la búsqueda por
id y el 404 son asunto de HTTP (views.py), no del dominio.
"""

from apps.accounts.models import Rol, Usuario
from apps.accounts.repositories import UsuarioRepository
from common.excepciones import ErrorDeValidacionDeDominio

# Mensajes literales — HU-M01-03 CA02, HU-M01-05 CA02 y CA03.
MENSAJE_USUARIO_YA_EXISTE = "El nombre de usuario ya está registrado"
MENSAJE_PASSWORD_DEBIL = "La contraseña debe tener al menos ocho caracteres"
MENSAJE_PASSWORD_ACTUAL_INCORRECTA = "La contraseña actual no es correcta"

LONGITUD_MINIMA_PASSWORD = 8  # RN-M01-04


def _validar_fortaleza_password(password: str) -> None:
    if len(password) < LONGITUD_MINIMA_PASSWORD:
        raise ErrorDeValidacionDeDominio(MENSAJE_PASSWORD_DEBIL, codigo="PASSWORD_DEBIL")


def crear_usuario(datos: dict) -> Usuario:
    """HU-M01-03 CA01. `datos["rol"]` ya llega como instancia `Rol`
    (lo resuelve `UsuarioCreateSerializer.validate_rol`)."""
    username = datos["username"]
    if UsuarioRepository.existe_username(username):
        raise ErrorDeValidacionDeDominio(MENSAJE_USUARIO_YA_EXISTE, codigo="USUARIO_YA_EXISTE")

    _validar_fortaleza_password(datos["password"])

    usuario = Usuario(
        username=username,
        nombres=datos["nombres"],
        apellidos=datos["apellidos"],
        rol=datos["rol"],
    )
    usuario.set_password(datos["password"])
    usuario.full_clean(exclude=["password"])
    usuario.save()
    return usuario


def actualizar_usuario(usuario: Usuario, datos: dict) -> Usuario:
    """HU-M01-04. El cambio de rol se aplica en la siguiente sesión del
    usuario (HU-M01-04 CA03): esto ya se cumple solo con guardar el nuevo
    rol, porque el rol vigente de una sesión activa vive en el token JWT
    emitido en el login anterior, no se relee del modelo en cada request.
    """
    nuevo_username = datos.get("username")
    if nuevo_username and nuevo_username != usuario.username:
        if UsuarioRepository.existe_username(nuevo_username, excluir_id=usuario.pk):
            raise ErrorDeValidacionDeDominio(MENSAJE_USUARIO_YA_EXISTE, codigo="USUARIO_YA_EXISTE")
        usuario.username = nuevo_username

    for campo in ("nombres", "apellidos"):
        if campo in datos:
            setattr(usuario, campo, datos[campo])

    if "rol" in datos:
        usuario.rol = datos["rol"]

    usuario.full_clean(exclude=["password"])
    usuario.save()
    return usuario


def desactivar_usuario(usuario: Usuario) -> Usuario:
    """RN-M01-03: baja lógica, nunca `DELETE`."""
    usuario.is_active = False
    usuario.save(update_fields=["is_active"])
    return usuario


def cambiar_password_propia(usuario: Usuario, password_actual: str, password_nueva: str) -> None:
    """HU-M01-05 CA01-CA03. Un usuario solo cambia la suya: la vista nunca
    recibe un id de otro usuario para esta operación (no existe esa ruta)."""
    if not usuario.check_password(password_actual):
        raise ErrorDeValidacionDeDominio(
            MENSAJE_PASSWORD_ACTUAL_INCORRECTA, codigo="PASSWORD_ACTUAL_INCORRECTA"
        )
    _validar_fortaleza_password(password_nueva)
    usuario.set_password(password_nueva)
    usuario.save(update_fields=["password"])
