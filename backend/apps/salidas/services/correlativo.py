"""Serie de correlativos de M04 (D-02, D-13).

La mecánica —bloqueo, incremento, formato— vive en `common/correlativo.py`,
compartida con M03. Aquí solo se ata el prefijo `SAL` a la tabla de contadores
de este módulo, de modo que la serie es independiente de la de ingresos
(RN-M04-10) sin que ninguna de las dos tenga que saber de la otra.
"""

from common.correlativo import GeneradorCorrelativo, GeneradorCorrelativoPorAnio

from apps.salidas.models import ContadorCorrelativo

PREFIJO_SALIDA = "SAL"

generador_por_defecto = GeneradorCorrelativoPorAnio(ContadorCorrelativo, PREFIJO_SALIDA)

__all__ = ["GeneradorCorrelativo", "GeneradorCorrelativoPorAnio", "generador_por_defecto"]
