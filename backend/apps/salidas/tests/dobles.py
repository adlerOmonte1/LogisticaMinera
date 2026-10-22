"""Dobles de prueba para las dependencias inyectadas del servicio (DIP).

Existen porque las pruebas los exigen —el criterio de `solid-proyecto` para
crear una abstracción—, no por simetría: sin ellos no se puede verificar que
el correlativo sea determinista ni que el movimiento de stock y el evento de
auditoría ocurran exactamente una vez.
"""

from decimal import Decimal


class GeneradorFijo:
    def __init__(self, valor="SAL-2026-00001"):
        self.valor = valor
        self.llamadas = 0

    def siguiente(self, momento) -> str:
        self.llamadas += 1
        return self.valor


class ServicioStockEspia:
    """Registra las llamadas y devuelve el saldo que se le configure."""

    def __init__(self, saldo: Decimal | None = None):
        self.saldo = saldo
        self.salidas_generadas = []
        self.salidas_revertidas = []

    def saldo_actual(self, producto):
        return self.saldo

    def generar_movimiento_salida(self, salida) -> None:
        self.salidas_generadas.append(salida)

    def revertir_movimiento_salida(self, salida) -> None:
        self.salidas_revertidas.append(salida)


class RegistradorEspia:
    def __init__(self):
        self.eventos = []

    def registrar(self, **evento) -> None:
        self.eventos.append(evento)
