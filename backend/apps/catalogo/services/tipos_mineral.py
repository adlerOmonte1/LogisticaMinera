"""Casos de uso del catálogo de tipos de mineral. HU-M02-02."""

from apps.catalogo.models import TipoMineral
from apps.catalogo.repositories import TipoMineralRepository
from common.excepciones import ErrorDeValidacionDeDominio

from ._eventos import registrar_creacion, registrar_desactivacion, registrar_modificacion

MENSAJE_CODIGO_DUPLICADO = "El código ya está registrado"
MENSAJE_DESACTIVADO_CON_INGRESOS = (
    "El tipo de mineral se desactivó porque tiene ingresos registrados"
)


def crear_tipo_mineral(datos: dict, usuario) -> TipoMineral:
    if TipoMineralRepository.existe_codigo(datos["codigo"]):
        raise ErrorDeValidacionDeDominio(MENSAJE_CODIGO_DUPLICADO, codigo="CODIGO_DUPLICADO")

    tipo = TipoMineral(
        codigo=datos["codigo"],
        nombre=datos["nombre"],
        unidad_medida=datos.get("unidad_medida", TipoMineral.TONELADA),
    )
    tipo.full_clean()
    tipo.save()
    registrar_creacion("TipoMineral", tipo, usuario)
    return tipo


def actualizar_tipo_mineral(tipo: TipoMineral, datos: dict, usuario) -> TipoMineral:
    # El código no se modifica tras el alta: cambiarlo desconectaría la
    # clasificación de los ingresos ya consolidados de su etiqueta.
    if "nombre" in datos:
        tipo.nombre = datos["nombre"]
    tipo.full_clean()
    tipo.save()
    registrar_modificacion("TipoMineral", tipo, usuario)
    return tipo


def desactivar_tipo_mineral(tipo: TipoMineral, usuario) -> TipoMineral:
    """RN-M02-08: baja lógica, nunca física."""
    tipo.activo = False
    tipo.save(update_fields=["activo"])
    registrar_desactivacion("TipoMineral", tipo, usuario)
    return tipo
