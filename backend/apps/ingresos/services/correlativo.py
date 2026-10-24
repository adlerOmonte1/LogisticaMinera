"""Serie de códigos de los ingresos (D-02).

La mecánica vive en `common/correlativo.py`. Aquí solo se ata el prefijo `ING`
a la tabla de contadores de este módulo.
"""

from common.correlativo import GeneradorCorrelativo, GeneradorCorrelativoPorAnio

from apps.ingresos.models import ContadorCorrelativo

PREFIJO_INGRESO = "ING"

generador_por_defecto = GeneradorCorrelativoPorAnio(ContadorCorrelativo, PREFIJO_INGRESO)

__all__ = ["GeneradorCorrelativo", "GeneradorCorrelativoPorAnio", "generador_por_defecto"]
