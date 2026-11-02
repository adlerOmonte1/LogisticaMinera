"""Puerto hacia M06 para la corrección y la anulación (RN-M03-25, RN-M03-27).

M03 no gestiona lotes: pregunta a M06 a qué lote pertenece el ingreso, qué
minerales admite y si todavía reúne ingresos, y le pide retirar el anulado. M06
se construye en F5 y aporta entonces su adaptador; hasta ese momento ningún
ingreso pertenece a un lote y el puerto responde en consecuencia.
"""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class LoteDelIngreso:
    nombre: str
    minerales: frozenset[int]
    reune_ingresos: bool


class PuertoLotes(Protocol):
    def lote_del_ingreso(self, ingreso) -> LoteDelIngreso | None: ...

    def retirar(self, ingreso, usuario) -> None: ...


class SinLotes:
    """Adaptador vigente mientras M06 no existe."""

    def lote_del_ingreso(self, ingreso) -> LoteDelIngreso | None:
        return None

    def retirar(self, ingreso, usuario) -> None:
        return None
