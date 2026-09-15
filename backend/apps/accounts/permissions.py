"""Autorización por acción (ISP — solid-proyecto, backend-auth-permisos).

Un permiso por acción, nunca `IsAdminUser` genérico: el Supervisor no debe
recibir ni siquiera la interfaz de gestión de usuarios.
"""

from rest_framework.permissions import BasePermission

from apps.accounts.models import Rol
from common.excepciones import AccionNoAutorizada


class PuedeGestionarUsuarios(BasePermission):
    """RN-M01-06: solo el rol Administrador crea, modifica o desactiva usuarios.

    Un usuario no autenticado recibe el 401 estándar de DRF (`return False`);
    uno autenticado con rol distinto de Administrador recibe el rechazo por
    autorización — que se lanza como excepción, no como `False`, para que
    `utils.manejador_errores` lo traduzca al contrato uniforme **y** lo
    registre en auditoría (backend-auth-permisos: "Toda solicitud rechazada
    por autorización se registra en auditoría").
    """

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if not request.user.tiene_rol(Rol.ADMINISTRADOR):
            raise AccionNoAutorizada("Acción no autorizada")
        return True
