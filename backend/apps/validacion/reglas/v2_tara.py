"""V2 · La tara del vehículo es menor que el peso bruto. Bloquea.

Se omite si el vehículo aún no tiene tara y se evalúa en el destare (HU-M05-01
CA11). La tara llega del catálogo, nunca de un valor fijo (RN-M05-10).
"""

from .base import DatosTicket, ReglaBase, Resultado


class V2Tara(ReglaBase):
    codigo = "V2"
    requiere_tara = True
    campo = "peso_bruto_tn"
    mensaje = "La tara no puede ser mayor o igual que el peso bruto"

    def datos_completos(self, datos: DatosTicket) -> bool:
        return datos.peso_bruto_tn is not None and datos.tara_tn is not None

    def evaluar(self, datos: DatosTicket) -> Resultado:
        if datos.tara_tn < datos.peso_bruto_tn:
            return Resultado(True)
        return Resultado(False, {}, f"tara_tn={datos.tara_tn} peso_bruto_tn={datos.peso_bruto_tn}")
