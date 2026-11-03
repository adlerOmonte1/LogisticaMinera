"""V1 · Ticket posiblemente duplicado. No bloquea: exige justificación (RN-M05-03).

Coincidencia exacta de placa, fecha del pesaje y peso bruto con un ingreso no
anulado (RN-M05-12), nunca con el propio en una corrección (RN-M05-13).
"""

from datetime import date
from decimal import Decimal
from typing import Protocol

from .base import DatosTicket, ReglaBase, Resultado


class RepositorioDuplicados(Protocol):
    def buscar_por_placa_fecha_peso(
        self, placa: str, fecha: date, peso_bruto_tn: Decimal, *, excluir: int | None = None
    ) -> str | None:
        """Código del primer ingreso no anulado que coincide, o None."""


class V1Duplicado(ReglaBase):
    codigo = "V1"
    bloqueante = False
    campo = "peso_bruto_tn"
    mensaje = "El ticket parece duplicado: ya existe el ingreso {codigo} con la misma placa, fecha y peso"
    mensaje_justificacion = "Debe indicar la justificación del posible duplicado"

    def __init__(self, repositorio: RepositorioDuplicados):
        self.repositorio = repositorio

    def datos_completos(self, datos: DatosTicket) -> bool:
        return bool(datos.placa) and datos.fecha_hora_pesaje is not None and datos.peso_bruto_tn is not None

    def evaluar(self, datos: DatosTicket) -> Resultado:
        codigo = self.repositorio.buscar_por_placa_fecha_peso(
            datos.placa, datos.fecha_pesaje, datos.peso_bruto_tn, excluir=datos.excluir_ingreso
        )
        if codigo is None:
            return Resultado(True)
        return Resultado(
            False,
            {"codigo": codigo},
            f"placa={datos.placa} fecha={datos.fecha_pesaje.isoformat()} "
            f"peso_bruto_tn={datos.peso_bruto_tn} coincide con {codigo}",
        )
