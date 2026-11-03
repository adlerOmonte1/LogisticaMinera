"""Ensamblado de `ServicioIngreso` con sus dependencias de producción. Las
pruebas construyen el servicio con dobles: reloj fijo, reconocedor determinista,
auditoría o generador que fallan."""

from apps.reconocimiento import motores
from apps.validacion.reglas import reglas_vigentes
from apps.validacion.services import ValidadorConsistencia
from common.eventos import registrador_por_defecto
from common.reloj import reloj_del_sistema

from . import correlativo, mensajes
from .lotes import SinLotes
from .registro import DatosConfirmados, ServicioIngreso


def servicio_por_defecto() -> ServicioIngreso:
    from apps.ingresos.repositories import IngresoRepository  # noqa: PLC0415

    return ServicioIngreso(
        fabrica_reconocedor=lambda: motores.obtener_reconocedor(),
        validador=ValidadorConsistencia(reglas_vigentes(IngresoRepository())),
        generador=correlativo.generador_por_defecto,
        reloj=reloj_del_sistema,
        auditoria=registrador_por_defecto,
        lotes=SinLotes(),
    )


__all__ = ["DatosConfirmados", "ServicioIngreso", "correlativo", "mensajes", "servicio_por_defecto"]
