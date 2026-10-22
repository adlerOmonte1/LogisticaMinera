"""Autorización por acción (ISP). Matriz de `requerimientos/funcionales.md`:
el Supervisor consulta, pero no registra ni anula salidas — su rol opera en la
recepción de material, no en el despacho.

Son dos clases y no una sola «puede operar salidas» porque son dos acciones
distintas del contrato: si mañana el Supervisor pudiera registrar sin poder
anular, cambia una clase y no la otra.
"""

from rest_framework.permissions import BasePermission

from apps.accounts.models import Rol
from common.excepciones import AccionNoAutorizada

ROLES_DESPACHO = (Rol.ADMINISTRADOR, Rol.ADMINISTRATIVO)


class _PermisoDeDespacho(BasePermission):
    """Autenticado y con rol de despacho. El rechazo es una excepción de
    dominio y no un `False` silencioso para que quede registrado en auditoría
    por el manejador uniforme (HU-M01-04 CA02)."""

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.user.tiene_rol(*ROLES_DESPACHO):
            return True
        raise AccionNoAutorizada("Acción no autorizada")


class PuedeRegistrarSalida(_PermisoDeDespacho):
    """HU-M04-01, HU-M04-02."""


class PuedeAnularSalida(_PermisoDeDespacho):
    """HU-M04-03 CA02."""
