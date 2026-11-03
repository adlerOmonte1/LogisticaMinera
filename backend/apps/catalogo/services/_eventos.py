"""Registro en auditoría de las operaciones de catálogo (RS-M02-08).

La baja y la reactivación se auditan como `MODIFICAR` del campo `activo`:
`ANULAR` está reservado para los ingresos.
"""

from common.eventos import Accion, diferencias, registrador_por_defecto


def registrar_creacion(entidad: str, obj, usuario, *, nuevos=None, registrador=registrador_por_defecto):
    registrador.registrar(
        accion=Accion.CREAR, entidad=entidad, id_entidad=obj.pk, usuario=usuario,
        valores_nuevos=nuevos or {"activo": obj.activo},
    )


def registrar_modificacion(
    entidad: str, obj, usuario, *, anteriores=None, nuevos=None, motivo="",
    ingresos_relacionados=None, registrador=registrador_por_defecto,
):
    registrador.registrar(
        accion=Accion.MODIFICAR, entidad=entidad, id_entidad=obj.pk, usuario=usuario,
        valores_anteriores=anteriores, valores_nuevos=nuevos, motivo=motivo,
        ingresos_relacionados=ingresos_relacionados,
    )


def registrar_edicion(entidad: str, obj, usuario, antes: dict, despues: dict) -> None:
    """Edición de datos: solo los campos que cambiaron, con ambos valores (RS-M09-06)."""
    anteriores, nuevos = diferencias(antes, despues)
    registrar_modificacion(entidad, obj, usuario, anteriores=anteriores, nuevos=nuevos)


def registrar_cambio_de_estado(entidad: str, obj, usuario, activo: bool, *, registrador=registrador_por_defecto):
    registrar_modificacion(
        entidad, obj, usuario, anteriores={"activo": not activo}, nuevos={"activo": activo},
        registrador=registrador,
    )


def cambiar_estado(entidad: str, obj, usuario, activo: bool) -> None:
    """Baja lógica o reactivación, con los mismos datos (RN-M02-08, RN-M02-19)."""
    obj.activo = activo
    obj.save(update_fields=["activo"])
    registrar_cambio_de_estado(entidad, obj, usuario, activo)
