"""Contrato de las reglas de consistencia (notas de M05).

Cada regla es una clase que no conoce a las demás ni accede a la base: recibe
los datos ya reunidos —con la tara y la capacidad del vehículo— y responde si
los datos que necesita están completos y si se cumple. V1 es la única que busca
otros ingresos, a través de un repositorio de lectura que recibe inyectado.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Protocol


@dataclass(frozen=True)
class DatosTicket:
    """Lo que se evalúa: del reconocimiento, del teclado o de una corrección.

    `momento_registro` es la referencia de V5. `excluir_ingreso` evita que, en
    una corrección, V1 compare el ingreso consigo mismo (RN-M05-13).
    """

    momento_registro: datetime
    placa: str | None = None
    fecha_hora_pesaje: datetime | None = None
    peso_bruto_tn: Decimal | None = None
    tara_tn: Decimal | None = None
    capacidad_tn: Decimal | None = None
    excluir_ingreso: int | None = None

    @property
    def fecha_pesaje(self) -> date | None:
        if self.fecha_hora_pesaje is None:
            return None
        from django.utils import timezone

        return timezone.localtime(self.fecha_hora_pesaje).date()

    @property
    def peso_neto_tn(self) -> Decimal | None:
        if self.peso_bruto_tn is None or self.tara_tn is None:
            return None
        return self.peso_bruto_tn - self.tara_tn


@dataclass(frozen=True)
class Resultado:
    """Respuesta de una regla: si se cumple, los marcadores de su mensaje y los
    valores concretos que la motivaron (el `detalle` que se persiste)."""

    cumple: bool
    marcadores: dict = field(default_factory=dict)
    detalle: str = ""


class Regla(Protocol):
    codigo: str
    bloqueante: bool
    requiere_tara: bool
    campo: str
    mensaje: str
    mensaje_justificacion: str  # solo las que no bloquean (V1 y V4)

    def datos_completos(self, datos: DatosTicket) -> bool: ...

    def evaluar(self, datos: DatosTicket) -> Resultado: ...


class ReglaBase:
    bloqueante = True
    requiere_tara = False
    mensaje_justificacion = ""
