"""Registro en auditoría de las operaciones de catálogo (RS-M02-07).

Depende del puerto `RegistradorDeEventos` de `common.eventos`, no de una
implementación concreta (solid-proyecto, DIP). Cuando M08 exista, basta con
registrar su implementación en `common.eventos`.
"""

from common.eventos import registrador_por_defecto


def registrar_evento(accion: str, entidad: str, obj, usuario, *, registrador=registrador_por_defecto):
    registrador.registrar(
        evento=f"CATALOGO_{accion}",
        usuario=usuario,
        detalles={"entidad": entidad, "id": obj.pk},
    )
