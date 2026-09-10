"""Casos de uso de productos (RS-M02-01, RS-M02-05, RS-M02-07). HU-M02-01."""

from apps.catalogo.models import Producto
from apps.catalogo.repositories import ProductoRepository
from common.excepciones import ErrorDeValidacionDeDominio

from ._eventos import registrar_evento

MENSAJE_CODIGO_DUPLICADO = "El código de producto ya está registrado"
MENSAJE_DESACTIVADO_CON_MOVIMIENTOS = (
    "El producto se desactivó porque tiene movimientos registrados"
)


def crear_producto(datos: dict, usuario) -> Producto:
    if ProductoRepository.existe_codigo(datos["codigo"]):
        raise ErrorDeValidacionDeDominio(MENSAJE_CODIGO_DUPLICADO, codigo="CODIGO_DUPLICADO")

    producto = Producto(
        codigo=datos["codigo"],
        nombre=datos["nombre"],
        unidad_medida=datos.get("unidad_medida", Producto.TONELADA),
    )
    producto.full_clean()
    producto.save()
    registrar_evento("CREADO", "Producto", producto, usuario)
    return producto


def actualizar_producto(producto: Producto, datos: dict, usuario) -> Producto:
    # El código es la identidad del producto y no se edita (RN-M02-01): cambiarlo
    # rompería la referencia de los consolidados históricos.
    if "nombre" in datos:
        producto.nombre = datos["nombre"]
    producto.full_clean()
    producto.save()
    registrar_evento("MODIFICADO", "Producto", producto, usuario)
    return producto


def desactivar_producto(producto: Producto, usuario) -> Producto:
    """RN-M02-07: baja lógica. El detalle de si tiene movimientos (HU-M02-01
    CA03) se resolverá cuando exista M05; hoy la tabla de movimientos aún no
    está creada, así que la baja es incondicional."""
    producto.activo = False
    producto.save(update_fields=["activo"])
    registrar_evento("DESACTIVADO", "Producto", producto, usuario)
    return producto
