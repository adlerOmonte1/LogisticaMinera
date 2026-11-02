"""V5 · La fecha y hora del pesaje no son posteriores al momento del registro.
Bloquea. Se evalúa con la hora que ajustó el usuario (HU-M05-01, detalles)."""

from .base import DatosTicket, ReglaBase, Resultado


class V5Fecha(ReglaBase):
    codigo = "V5"
    campo = "fecha"
    mensaje = "La fecha del ticket no puede ser posterior a la fecha de registro"

    def datos_completos(self, datos: DatosTicket) -> bool:
        return datos.fecha_hora_pesaje is not None

    def evaluar(self, datos: DatosTicket) -> Resultado:
        if datos.fecha_hora_pesaje <= datos.momento_registro:
            return Resultado(True)
        return Resultado(
            False,
            {},
            f"fecha_hora_pesaje={datos.fecha_hora_pesaje.isoformat()} "
            f"momento_registro={datos.momento_registro.isoformat()}",
        )
