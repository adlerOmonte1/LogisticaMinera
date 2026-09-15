"""Registro en auditoría de las operaciones de catálogo (RS-M02-07).

Depende del puerto `RegistradorDeEventos` de `common.eventos`, no de una
implementación concreta (solid-proyecto, DIP). Cuando M08 exista, basta con
registrar su implementación en `common.eventos`.

La desactivación de una entidad de catálogo se audita como `MODIFICAR` con el
cambio de `activo` en los valores anterior y nuevo: `ANULAR` está reservado
para los documentos (ingresos y salidas), que es lo que el modelo
entidad-relación entiende por anulación.
"""

from common.eventos import Accion, registrador_por_defecto


def registrar_creacion(entidad: str, obj, usuario, *, registrador=registrador_por_defecto):
    registrador.registrar(
        accion=Accion.CREAR,
        entidad=entidad,
        id_entidad=obj.pk,
        usuario=usuario,
        valores_nuevos={"activo": obj.activo},
    )


def registrar_modificacion(
    entidad: str, obj, usuario, *, anteriores=None, nuevos=None, registrador=registrador_por_defecto
):
    registrador.registrar(
        accion=Accion.MODIFICAR,
        entidad=entidad,
        id_entidad=obj.pk,
        usuario=usuario,
        valores_anteriores=anteriores,
        valores_nuevos=nuevos,
    )


def registrar_desactivacion(entidad: str, obj, usuario, *, registrador=registrador_por_defecto):
    registrar_modificacion(
        entidad,
        obj,
        usuario,
        anteriores={"activo": True},
        nuevos={"activo": False},
        registrador=registrador,
    )
