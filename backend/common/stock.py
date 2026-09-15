"""Puerto de movimientos de stock.

M05-existencias (RF-04) aún no está implementado. Los servicios que ya deben
mover stock —M03: entradas; M04: salidas— dependen de esta abstracción y no de
una implementación concreta (DIP, solid-proyecto): cuando M05 exista, basta
con registrar aquí su implementación real, sin tocar `apps/ingresos` ni
`apps/salidas`.

Es el mismo patrón que usa `common/eventos.py` para M08.

La tabla `MOVIMIENTO_STOCK` pertenece al modelo entidad-relación de M05, no a
M03 (D-10), así que `apps/ingresos` no puede crearla. Mientras tanto,
`ServicioStockPendiente` no persiste nada: el ingreso ya queda completo y
trazable por sí mismo (correlativo, usuario, auditoría).

## El libro mayor es de solo-anexado

`MOVIMIENTO_STOCK` es una tabla de asiento: RN-M05-01 y RN-M05-02 fijan que el
saldo es siempre la suma algebraica de los movimientos y que **no se escribe
directamente por ninguna vía**; RN-M05-09 fija que una corrección **genera un
movimiento nuevo** y que el original permanece en el kardex.

Por eso la corrección de un ingreso se expresa como `ajustar_por_edicion`, que
generará movimientos compensatorios, y no como un «recalcular» que mutaría el
asiento original. Ver la nota de HU-M03-06 CA03.
"""

from decimal import Decimal
from typing import Protocol


class ServicioStock(Protocol):
    # --- M03: entradas ---
    def generar_movimiento_entrada(self, ingreso) -> None: ...

    def revertir_movimiento_entrada(self, ingreso) -> None: ...

    def ajustar_por_edicion(self, ingreso, valores_anteriores: dict) -> None: ...

    # --- M04: salidas ---
    def generar_movimiento_salida(self, salida) -> None: ...

    def revertir_movimiento_salida(self, salida) -> None: ...

    # --- M05: ajustes de inventario (RN-M05-06, RN-M05-07) ---
    def registrar_ajuste(self, producto, diferencia_tn: Decimal, motivo: str, usuario) -> None: ...


class ServicioStockPendiente:
    """Implementación provisional: no hace nada. RN-M03-08 y RN-M04-05 se
    completan al implementar M05; hasta entonces el llamador no debe fallar ni
    bloquearse por una dependencia que todavía no existe."""

    def generar_movimiento_entrada(self, ingreso) -> None:
        pass

    def revertir_movimiento_entrada(self, ingreso) -> None:
        pass

    def ajustar_por_edicion(self, ingreso, valores_anteriores: dict) -> None:
        pass

    def generar_movimiento_salida(self, salida) -> None:
        pass

    def revertir_movimiento_salida(self, salida) -> None:
        pass

    def registrar_ajuste(self, producto, diferencia_tn: Decimal, motivo: str, usuario) -> None:
        pass


servicio_stock_por_defecto = ServicioStockPendiente()
