"""Gestión de usuarios y de la propia contraseña. HU-M01-02, RS-M01-07, RS-M01-09,
RS-M01-12 a RS-M01-14.

Las funciones reciben instancias ya resueltas por la vista: la búsqueda por id
y el 404 son asunto de HTTP, no del dominio. Toda operación queda en auditoría,
nunca con una contraseña (RS-M09-16).
"""

import secrets
import string

from django.db import transaction

from apps.accounts.models import Usuario
from apps.accounts.repositories import UsuarioRepository
from common.eventos import Accion, RegistradorDeEventos, registrador_por_defecto
from common.excepciones import ErrorDeValidacionDeDominio

# Mensajes literales de HU-M01-02.
MENSAJE_USUARIO_YA_EXISTE = "El nombre de usuario ya está registrado"
MENSAJE_PASSWORD_DEBIL = "La contraseña debe tener al menos ocho caracteres"
MENSAJE_PASSWORD_ACTUAL_INCORRECTA = "La contraseña actual no es correcta"
MENSAJE_PASSWORDS_NO_COINCIDEN = "Las contraseñas no coinciden"
MENSAJE_DESACTIVAR_PROPIA = "No puede desactivar su propia cuenta"
MENSAJE_DESACTIVADO = "Usuario desactivado"
MENSAJE_REACTIVADO = "Usuario reactivado"
MENSAJE_CLAVE_CAMBIADA = "Contraseña cambiada. Inicie sesión nuevamente"

LONGITUD_MINIMA_PASSWORD = 8  # RN-M01-04
LONGITUD_CLAVE_TEMPORAL = 12  # RNF-M01-07: al menos ocho caracteres
_ALFABETO_TEMPORAL = string.ascii_letters + string.digits


def _validar_fortaleza_password(password: str) -> None:
    if len(password) < LONGITUD_MINIMA_PASSWORD:
        raise ErrorDeValidacionDeDominio(MENSAJE_PASSWORD_DEBIL, codigo="PASSWORD_DEBIL")


def _datos(usuario: Usuario) -> dict:
    return {
        "username": usuario.username,
        "nombres": usuario.nombres,
        "apellidos": usuario.apellidos,
        "rol": usuario.rol.nombre,
        "activo": usuario.is_active,
    }


def crear_usuario(
    datos: dict, autor, *, registrador: RegistradorDeEventos = registrador_por_defecto
) -> Usuario:
    """HU-M01-02 CA01. `datos["rol"]` llega como instancia `Rol`."""
    username = datos["username"]
    if UsuarioRepository.existe_username(username):
        raise ErrorDeValidacionDeDominio(MENSAJE_USUARIO_YA_EXISTE, codigo="USUARIO_YA_EXISTE")
    _validar_fortaleza_password(datos["password"])

    with transaction.atomic():
        usuario = Usuario(
            username=username,
            nombres=datos["nombres"],
            apellidos=datos["apellidos"],
            rol=datos["rol"],
        )
        usuario.set_password(datos["password"])
        usuario.full_clean(exclude=["password"])
        usuario.save()
        registrador.registrar(
            accion=Accion.CREAR, entidad="Usuario", id_entidad=usuario.pk,
            usuario=autor, valores_nuevos=_datos(usuario),
        )
    return usuario


def actualizar_usuario(
    usuario: Usuario, datos: dict, autor, *, registrador: RegistradorDeEventos = registrador_por_defecto
) -> Usuario:
    """HU-M01-02. Un cambio de rol se aplica en la siguiente solicitud del
    usuario, porque la autenticación relee el usuario de la base en cada una
    (HU-M01-03 CA03)."""
    anteriores = _datos(usuario)
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

    with transaction.atomic():
        usuario.full_clean(exclude=["password"])
        usuario.save()
        registrador.registrar(
            accion=Accion.MODIFICAR, entidad="Usuario", id_entidad=usuario.pk, usuario=autor,
            valores_anteriores=anteriores, valores_nuevos=_datos(usuario),
        )
    return usuario


def _cambiar_estado(usuario: Usuario, activo: bool, autor, registrador) -> Usuario:
    with transaction.atomic():
        usuario.is_active = activo
        usuario.save(update_fields=["is_active"])
        registrador.registrar(
            accion=Accion.MODIFICAR, entidad="Usuario", id_entidad=usuario.pk, usuario=autor,
            valores_anteriores={"activo": not activo}, valores_nuevos={"activo": activo},
        )
    return usuario


def desactivar_usuario(
    usuario: Usuario, autor, *, registrador: RegistradorDeEventos = registrador_por_defecto
) -> Usuario:
    """HU-M01-02 CA03 y CA09. Baja lógica, nunca física (RN-M01-03); nadie
    desactiva su propia cuenta (RN-M01-12)."""
    if usuario.pk == autor.pk:
        raise ErrorDeValidacionDeDominio(MENSAJE_DESACTIVAR_PROPIA, codigo="DESACTIVAR_PROPIA")
    return _cambiar_estado(usuario, False, autor, registrador)


def reactivar_usuario(
    usuario: Usuario, autor, *, registrador: RegistradorDeEventos = registrador_por_defecto
) -> Usuario:
    """HU-M01-02 CA10: devuelve el acceso con el mismo rol y el mismo historial."""
    return _cambiar_estado(usuario, True, autor, registrador)


def restablecer_clave(
    usuario: Usuario, autor, *, registrador: RegistradorDeEventos = registrador_por_defecto
) -> str:
    """HU-M01-02 CA08, RS-M01-12, RNF-M01-07. Devuelve la contraseña temporal,
    que la vista muestra una sola vez y que no se guarda legible en ningún lado."""
    temporal = "".join(secrets.choice(_ALFABETO_TEMPORAL) for _ in range(LONGITUD_CLAVE_TEMPORAL))
    with transaction.atomic():
        usuario.set_password(temporal)
        usuario.debe_cambiar_clave = True
        usuario.intentos_fallidos = 0
        usuario.bloqueado_hasta = None
        usuario.save(
            update_fields=["password", "debe_cambiar_clave", "intentos_fallidos", "bloqueado_hasta"]
        )
        registrador.registrar(
            accion=Accion.MODIFICAR, entidad="Usuario", id_entidad=usuario.pk, usuario=autor,
            valores_nuevos={"debe_cambiar_clave": True}, motivo="Restablecimiento de contraseña",
        )
    return temporal


def cambiar_password_propia(
    usuario: Usuario,
    password_actual: str,
    password_nueva: str,
    confirmacion: str,
    *,
    registrador: RegistradorDeEventos = registrador_por_defecto,
) -> None:
    """HU-M01-02 CA05 a CA07 y CA11; HU-M01-01 CA09. Retira la marca de
    contraseña temporal (RS-M01-13)."""
    if not usuario.check_password(password_actual):
        raise ErrorDeValidacionDeDominio(
            MENSAJE_PASSWORD_ACTUAL_INCORRECTA, codigo="PASSWORD_ACTUAL_INCORRECTA"
        )
    _validar_fortaleza_password(password_nueva)
    if password_nueva != confirmacion:
        raise ErrorDeValidacionDeDominio(
            MENSAJE_PASSWORDS_NO_COINCIDEN, codigo="PASSWORDS_NO_COINCIDEN"
        )
    with transaction.atomic():
        temporal = usuario.debe_cambiar_clave
        usuario.set_password(password_nueva)
        usuario.debe_cambiar_clave = False
        usuario.save(update_fields=["password", "debe_cambiar_clave"])
        registrador.registrar(
            accion=Accion.MODIFICAR, entidad="Usuario", id_entidad=usuario.pk, usuario=usuario,
            valores_nuevos={"debe_cambiar_clave": False} if temporal else None,
            motivo="Cambio de la propia contraseña",
        )
