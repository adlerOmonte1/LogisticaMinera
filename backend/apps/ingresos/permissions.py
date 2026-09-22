"""Autorización por acción (ISP). Matriz de `requerimientos/funcionales.md`:
los tres roles registran, listan y consultan; solo Administrador y
Administrativo editan o anulan.
"""

from rest_framework.permissions import BasePermission

from apps.accounts.models import Rol
from common.excepciones import AccionNoAutorizada

ROLES_EDICION = (Rol.ADMINISTRADOR, Rol.ADMINISTRATIVO)


class PuedeEditarOAnularIngreso(BasePermission):
    """HU-M03-06, HU-M03-07. El Supervisor puede consultar (HU-M03-05 CA03)
    pero no llega aquí: esta clase solo se aplica a `update` y `anular`."""

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.user.tiene_rol(*ROLES_EDICION):
            return True
        raise AccionNoAutorizada("Acción no autorizada")
