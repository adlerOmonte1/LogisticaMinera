"""Serie de correlativos de M03 (D-02).

La mecánica vive en `common/correlativo.py`, compartida con las demás series
del sistema. Aquí solo se ata el prefijo `ING` a la tabla de contadores de
este módulo: M04 hará lo propio con `SAL` y su propia tabla, de modo que las
dos series son independientes por construcción (RN-M04-10).
"""

from common.correlativo import GeneradorCorrelativo, GeneradorCorrelativoPorAnio

from apps.ingresos.models import ContadorCorrelativo

PREFIJO_INGRESO = "ING"

generador_por_defecto = GeneradorCorrelativoPorAnio(ContadorCorrelativo, PREFIJO_INGRESO)

__all__ = ["GeneradorCorrelativo", "GeneradorCorrelativoPorAnio", "generador_por_defecto"]
