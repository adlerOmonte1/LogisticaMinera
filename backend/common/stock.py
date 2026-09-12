"""Puerto de movimientos de stock.

M05-existencias (RF-04) aún no está implementado. Los servicios que ya deben
generar o revertir un movimiento de stock —M03: entrada; M04 más adelante:
salida— dependen de esta abstracción y no de una implementación concreta
(DIP, solid-proyecto): cuando M05 exista, basta con registrar aquí su
implementación real, sin tocar `apps/ingresos` ni `apps/salidas`.

Es el mismo patrón que ya usa `common/eventos.py` para M08: un puerto más una
implementación provisional, documentados juntos para que no se pierda el
porqué.

La tabla `MOVIMIENTO_STOCK` pertenece al modelo entidad-relación de M05, no a
M03 (D-10: "una app solo tiene `models/` si aporta una entidad al ERD"), así
que `apps/ingresos` no puede crearla. Mientras tanto, `ServicioStockPendiente`
no persiste nada: el ingreso ya queda completo y trazable por sí mismo
(correlativo, usuario, auditoría); el movimiento de stock físico se generará
retroactivamente sobre los ingresos existentes cuando M05 se implemente, o se
sustituye esta implementación antes de esa fecha si el cronograma lo permite.
"""

from typing import Protocol


class ServicioStock(Protocol):
    def generar_movimiento_entrada(self, ingreso) -> None: ...

    def revertir_movimiento_entrada(self, ingreso) -> None: ...

    def recalcular_movimiento_entrada(self, ingreso) -> None: ...


class ServicioStockPendiente:
    """Implementación provisional: no hace nada. RN-M03-08 se completa al
    implementar M05; hasta entonces, el llamador no debe fallar ni bloquearse
    por una dependencia que todavía no existe."""

    def generar_movimiento_entrada(self, ingreso) -> None:
        pass

    def revertir_movimiento_entrada(self, ingreso) -> None:
        pass

    def recalcular_movimiento_entrada(self, ingreso) -> None:
        pass


servicio_stock_por_defecto = ServicioStockPendiente()
