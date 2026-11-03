"""Autorización por operación, una clase por acción (RN-M01-09, ISP).

Es la única definición de la matriz de permisos del sistema (notas de M01): los
demás módulos importan estas clases y no escriben su propia comprobación de rol.

Un usuario sin sesión recibe el 401 estándar (`return False`). Uno autenticado
sin el rol recibe `AccionNoAutorizada`, que el manejador uniforme traduce a 403
con «Acción no autorizada» y registra como acceso rechazado (HU-M01-03 CA02, CA04).
"""

from rest_framework.permissions import BasePermission

from apps.accounts.models import Rol
from common.excepciones import AccionNoAutorizada

TODOS = (Rol.ADMINISTRADOR, Rol.ADMINISTRATIVO, Rol.SUPERVISOR)
GESTION = (Rol.ADMINISTRADOR, Rol.ADMINISTRATIVO)
SOLO_ADMINISTRADOR = (Rol.ADMINISTRADOR,)


class _PermisoPorRol(BasePermission):
    roles: tuple[str, ...] = ()
    mensaje = "Acción no autorizada"

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.user.tiene_rol(*self.roles):
            return True
        raise AccionNoAutorizada(self.mensaje)


# Los tres roles
class PuedeConsultar(_PermisoPorRol):
    """Consultas de M04, M05, M06, M07 y el historial de M09 (DR-31)."""

    roles = TODOS


class PuedeRegistrarIngreso(_PermisoPorRol):
    roles = TODOS


class PuedeRegistrarDestare(_PermisoPorRol):
    roles = TODOS


class PuedeDarAltaVehiculo(_PermisoPorRol):
    """Alta del vehículo desde el registro de un ingreso (DR-17)."""

    roles = TODOS


class PuedeRegistrarEtapa(_PermisoPorRol):
    """Etapas, secado de un ingreso tardío y bigbags (M06)."""

    roles = TODOS


# Administrador y Administrativo
class PuedeCorregirIngreso(_PermisoPorRol):
    """Corrección y reversión de la última corrección (M03)."""

    roles = GESTION


class PuedeGestionarCatalogo(_PermisoPorRol):
    """Alta, edición, baja y reactivación del catálogo; tipo de mineral desde el registro."""

    roles = GESTION


class PuedeComponerLote(_PermisoPorRol):
    """Abrir, minerales, asignar, retirar, iniciar el recorrido y dividir (M06)."""

    roles = GESTION


class PuedeExportarListado(_PermisoPorRol):
    roles = GESTION


class PuedeConsolidar(_PermisoPorRol):
    roles = GESTION


# Solo Administrador
class PuedeAnularIngreso(_PermisoPorRol):
    roles = SOLO_ADMINISTRADOR


class PuedeModificarTara(_PermisoPorRol):
    """HU-M02-01 CA09: la única operación con un mensaje de rechazo propio."""

    roles = SOLO_ADMINISTRADOR
    mensaje = "Solo el Administrador puede modificar la tara del vehículo"


class PuedeCerrarLote(_PermisoPorRol):
    roles = SOLO_ADMINISTRADOR


class PuedeGestionarUsuarios(_PermisoPorRol):
    """Alta, edición, baja, reactivación y restablecimiento de contraseñas (RN-M01-06, RN-M01-11)."""

    roles = SOLO_ADMINISTRADOR


class PuedeConsultarAuditoria(_PermisoPorRol):
    roles = SOLO_ADMINISTRADOR
