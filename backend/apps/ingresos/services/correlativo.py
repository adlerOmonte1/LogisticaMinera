"""D-02, D-09: el correlativo lo asigna el servidor con garantía de unicidad
bajo concurrencia. Nunca `Ingreso.objects.aggregate(Max("correlativo"))` fuera
de transacción: dos altas simultáneas producirían el mismo valor.

Tabla de contadores con `select_for_update()`, no secuencia de PostgreSQL:
el correlativo se reinicia por año y lleva prefijo (`ING-{año}-{cinco
dígitos}`), y una secuencia nativa no resuelve el reinicio anual
(`skills/base-datos-postgresql`).

`GeneradorCorrelativo` se inyecta en `registrar_ingreso` (DIP,
solid-proyecto): en las pruebas se sustituye por uno determinista sin tocar
el caso de uso, y es la abstracción que D-09 señala como la única en este
proyecto que se justifica de antemano.
"""

from datetime import datetime
from typing import Protocol

from django.db import transaction

from apps.ingresos.models import ContadorCorrelativo


class GeneradorCorrelativo(Protocol):
    def siguiente(self, momento: datetime) -> str: ...


class GeneradorCorrelativoPorAnio:
    """Implementación adoptada: tabla de contadores bloqueada con
    `select_for_update()` dentro de la transacción del llamador."""

    PREFIJO = "ING"

    def siguiente(self, momento: datetime) -> str:
        anio = momento.year
        with transaction.atomic():
            contador = ContadorCorrelativo.objects.select_for_update().filter(anio=anio).first()
            if contador is None:
                # La creación y el bloqueo no pueden ser la misma operación:
                # se crea y se vuelve a leer bajo select_for_update para que
                # una segunda transacción concurrente quede bloqueada aquí,
                # no en el create() (que fallaría por la unicidad de `anio`).
                contador = ContadorCorrelativo.objects.create(anio=anio, ultimo_valor=0)
                contador = ContadorCorrelativo.objects.select_for_update().get(pk=contador.pk)
            contador.ultimo_valor += 1
            contador.save(update_fields=["ultimo_valor"])
            return f"{self.PREFIJO}-{anio}-{contador.ultimo_valor:05d}"


generador_por_defecto = GeneradorCorrelativoPorAnio()
