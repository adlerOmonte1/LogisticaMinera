"""Casos de uso de transportistas (HU-M02-03)."""

from apps.catalogo.models import Transportista
from apps.catalogo.repositories import TransportistaRepository

from ._eventos import registrar_evento
from .validadores import validar_ruc

MENSAJE_DESACTIVADO_CON_VEHICULOS = (
    "El transportista se desactivó porque tiene vehículos asociados"
)


def crear_transportista(datos: dict, usuario) -> Transportista:
    transportista = Transportista(
        razon_social=datos["razon_social"],
        ruc=validar_ruc(datos["ruc"]),
    )
    transportista.full_clean()
    transportista.save()
    registrar_evento("CREADO", "Transportista", transportista, usuario)
    return transportista


def actualizar_transportista(transportista: Transportista, datos: dict, usuario) -> Transportista:
    if "razon_social" in datos:
        transportista.razon_social = datos["razon_social"]
    if "ruc" in datos:
        transportista.ruc = validar_ruc(datos["ruc"])
    transportista.full_clean()
    transportista.save()
    registrar_evento("MODIFICADO", "Transportista", transportista, usuario)
    return transportista


def desactivar_transportista(transportista: Transportista, usuario) -> Transportista:
    """HU-M02-03 CA03 / RN-M02-07: siempre baja lógica. Se informa si además
    arrastra vehículos, porque esos vehículos externos quedan sin proveedor
    válido y hay que revisarlos."""
    tenia_vehiculos = TransportistaRepository.tiene_vehiculos(transportista)
    transportista.activo = False
    transportista.save(update_fields=["activo"])
    registrar_evento("DESACTIVADO", "Transportista", transportista, usuario)
    transportista.mensaje = (
        MENSAJE_DESACTIVADO_CON_VEHICULOS if tenia_vehiculos else None
    )
    return transportista
