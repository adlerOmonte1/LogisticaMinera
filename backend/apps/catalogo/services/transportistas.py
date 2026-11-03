"""Casos de uso de transportistas. HU-M02-03: RUC de once dígitos (RN-M02-07) y
único (RN-M02-18); baja lógica y reactivación."""

from django.db import transaction

from apps.catalogo.models import Transportista
from apps.catalogo.repositories import TransportistaRepository
from common.excepciones import ErrorDeValidacionDeDominio

from ._eventos import cambiar_estado, registrar_creacion, registrar_edicion
from .validadores import validar_ruc

MENSAJE_RUC_DUPLICADO = "El RUC ya está registrado"
MENSAJE_DESACTIVADO_CON_VEHICULOS = "El transportista se desactivó porque tiene vehículos asociados"
# Sin un mensaje propio en el criterio, la baja y la reactivación usan el
# genérico de la maqueta.
MENSAJE_DESACTIVADO = "Cambios guardados"
MENSAJE_REACTIVADO = "Cambios guardados"


def _validar_ruc_unico(ruc: str, *, excluir_id=None) -> str:
    ruc = validar_ruc(ruc)
    if TransportistaRepository.existe_ruc(ruc, excluir_id=excluir_id):
        raise ErrorDeValidacionDeDominio(MENSAJE_RUC_DUPLICADO, codigo="RUC_DUPLICADO")
    return ruc


def crear_transportista(datos: dict, usuario) -> Transportista:
    """HU-M02-03 CA01, CA02 y CA04."""
    ruc = _validar_ruc_unico(datos["ruc"])
    with transaction.atomic():
        transportista = Transportista(razon_social=datos["razon_social"], ruc=ruc)
        transportista.full_clean()
        transportista.save()
        registrar_creacion("Transportista", transportista, usuario, nuevos={"ruc": ruc})
    return transportista


def actualizar_transportista(transportista: Transportista, datos: dict, usuario) -> Transportista:
    antes = {"razon_social": transportista.razon_social, "ruc": transportista.ruc}
    if "razon_social" in datos:
        transportista.razon_social = datos["razon_social"]
    if "ruc" in datos:
        transportista.ruc = _validar_ruc_unico(datos["ruc"], excluir_id=transportista.pk)
    with transaction.atomic():
        transportista.full_clean()
        transportista.save()
        registrar_edicion(
            "Transportista", transportista, usuario, antes,
            {"razon_social": transportista.razon_social, "ruc": transportista.ruc},
        )
    return transportista


def desactivar_transportista(transportista: Transportista, usuario) -> Transportista:
    """HU-M02-03 CA03. Nunca se elimina; se informa si arrastra vehículos, porque
    esos vehículos externos quedan sin proveedor vigente y hay que revisarlos."""
    tenia_vehiculos = TransportistaRepository.tiene_vehiculos(transportista)
    with transaction.atomic():
        cambiar_estado("Transportista", transportista, usuario, False)
    transportista.mensaje = MENSAJE_DESACTIVADO_CON_VEHICULOS if tenia_vehiculos else MENSAJE_DESACTIVADO
    return transportista


def reactivar_transportista(transportista: Transportista, usuario) -> Transportista:
    """HU-M02-03 CA05."""
    with transaction.atomic():
        cambiar_estado("Transportista", transportista, usuario, True)
    transportista.mensaje = MENSAJE_REACTIVADO
    return transportista
