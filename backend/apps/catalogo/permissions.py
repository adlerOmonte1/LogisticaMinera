"""Autorización del catálogo por acción. Las clases son las de M01, la única
definición de la matriz (RN-M01-09); aquí solo se decide cuál aplica a cada
acción del `ViewSet` (requerimientos/funcionales.md, matriz de permisos).

- Consultar: los tres roles.
- Crear, editar, dar de baja y reactivar: Administrador y Administrativo.
- Crear un vehículo: los tres roles, porque el alta desde el registro y el
  destare ocurren en planta (HU-M02-01 CA14, DR-17).
- Modificar una tara registrada: solo el Administrador (HU-M02-01 CA09).
"""

from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import (
    PuedeDarAltaVehiculo,
    PuedeGestionarCatalogo,
    PuedeModificarTara,
)

LECTURA = ("list", "retrieve")


def permisos_de(accion: str, *, alta_abierta: bool = False) -> list:
    if accion in LECTURA or accion is None:
        return [IsAuthenticated()]
    if accion == "create" and alta_abierta:
        return [IsAuthenticated(), PuedeDarAltaVehiculo()]
    if accion == "tara":
        return [IsAuthenticated(), PuedeModificarTara()]
    return [IsAuthenticated(), PuedeGestionarCatalogo()]
