"""Casos de uso de clientes (HU-M02-04)."""

from apps.catalogo.models import Cliente

from ._eventos import registrar_evento
from .validadores import validar_ruc


def crear_cliente(datos: dict, usuario) -> Cliente:
    cliente = Cliente(
        razon_social=datos["razon_social"],
        ruc=validar_ruc(datos["ruc"]),
    )
    cliente.full_clean()
    cliente.save()
    registrar_evento("CREADO", "Cliente", cliente, usuario)
    return cliente


def actualizar_cliente(cliente: Cliente, datos: dict, usuario) -> Cliente:
    if "razon_social" in datos:
        cliente.razon_social = datos["razon_social"]
    if "ruc" in datos:
        cliente.ruc = validar_ruc(datos["ruc"])
    cliente.full_clean()
    cliente.save()
    registrar_evento("MODIFICADO", "Cliente", cliente, usuario)
    return cliente


def desactivar_cliente(cliente: Cliente, usuario) -> Cliente:
    """RN-M02-07: baja lógica. La comprobación de salidas asociadas (HU-M02-04
    CA02) llegará con M04."""
    cliente.activo = False
    cliente.save(update_fields=["activo"])
    registrar_evento("DESACTIVADO", "Cliente", cliente, usuario)
    return cliente
