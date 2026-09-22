"""Generación de correlativos por año (D-02).

Cada documento numerado del sistema —ingresos (M03) y salidas (M04)— lleva su
**serie independiente** (RN-M04-10). La independencia se consigue por
construcción: cada módulo mantiene su propia tabla de contadores y le pasa a
este generador su modelo y su prefijo. No hay una tabla compartida que
pudiera solapar dos series en la misma fila del año.

Aquí vive solo la mecánica —bloqueo, incremento, formato—, que es idéntica
para todas las series. La tabla concreta la aporta cada módulo, porque es su
infraestructura y no una entidad del modelo entidad-relación (D-10).

Formato: `{PREFIJO}-{año}-{cinco dígitos}` (p. ej. `ING-2026-00001`,
`SAL-2026-00001`).
"""

from datetime import datetime
from typing import Protocol

from django.db import transaction

LONGITUD_NUMERO = 5


class GeneradorCorrelativo(Protocol):
    def siguiente(self, momento: datetime) -> str: ...


class GeneradorCorrelativoPorAnio:
    """Tabla de contadores bloqueada con `select_for_update()` dentro de la
    transacción del llamador. Nunca `MAX(correlativo) + 1`: bajo concurrencia
    produce duplicados (D-02).

    Se inyecta en el servicio que lo usa (DIP, solid-proyecto): en las pruebas
    se sustituye por uno determinista sin tocar el caso de uso.
    """

    def __init__(self, modelo_contador, prefijo: str):
        self.modelo_contador = modelo_contador
        self.prefijo = prefijo

    def siguiente(self, momento: datetime) -> str:
        anio = momento.year
        with transaction.atomic():
            contador = self.modelo_contador.objects.select_for_update().filter(anio=anio).first()
            if contador is None:
                # La creación y el bloqueo no pueden ser la misma operación:
                # se crea y se vuelve a leer bajo select_for_update para que
                # una segunda transacción concurrente quede bloqueada aquí,
                # no en el create() (que fallaría por la unicidad de `anio`).
                contador = self.modelo_contador.objects.create(anio=anio, ultimo_valor=0)
                contador = self.modelo_contador.objects.select_for_update().get(pk=contador.pk)
            contador.ultimo_valor += 1
            contador.save(update_fields=["ultimo_valor"])
            return f"{self.prefijo}-{anio}-{contador.ultimo_valor:0{LONGITUD_NUMERO}d}"
