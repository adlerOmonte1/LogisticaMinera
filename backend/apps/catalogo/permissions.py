"""Autorización del catálogo (ISP — solid-proyecto, backend-auth-permisos).

Matriz de `requerimientos/funcionales.md`:
- Consultar catálogos: los tres roles.
- Crear, editar y desactivar: Administrador y Administrativo.
"""

from rest_framework.permissions import SAFE_METHODS, BasePermission

from apps.accounts.models import Rol
from common.excepciones import AccionNoAutorizada

ROLES_GESTION = (Rol.ADMINISTRADOR, Rol.ADMINISTRATIVO)


class PuedeGestionarCatalogo(BasePermission):
    """Lectura para cualquier usuario autenticado; escritura solo para los
    roles de gestión. El rechazo se lanza como excepción para que el manejador
    uniforme lo traduzca a 403 y lo registre en auditoría."""

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return True
        if request.user.tiene_rol(*ROLES_GESTION):
            return True
        raise AccionNoAutorizada("Acción no autorizada")
