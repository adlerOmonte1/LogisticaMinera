"""V4 · El peso neto está dentro del rango de carga del vehículo. No bloquea:
exige justificación (RN-M05-03), porque una sobrecarga real puede ocurrir.

El neto se calcula con la tara del catálogo y se compara con la capacidad
declarada del vehículo (RN-M05-10). Sin tara se omite y se evalúa en el destare.
"""

from .base import DatosTicket, ReglaBase, Resultado


class V4Capacidad(ReglaBase):
    codigo = "V4"
    bloqueante = False
    requiere_tara = True
    campo = "peso_bruto_tn"
    mensaje = "El peso neto está fuera del rango de carga del vehículo {placa}"
    mensaje_justificacion = "Debe indicar la justificación del peso fuera de rango"

    def datos_completos(self, datos: DatosTicket) -> bool:
        return (
            datos.peso_bruto_tn is not None
            and datos.tara_tn is not None
            and datos.capacidad_tn is not None
            and bool(datos.placa)
        )

    def evaluar(self, datos: DatosTicket) -> Resultado:
        neto = datos.peso_neto_tn
        if neto <= datos.capacidad_tn:
            return Resultado(True)
        return Resultado(
            False,
            {"placa": datos.placa},
            f"peso_neto_tn={neto} capacidad_tn={datos.capacidad_tn}",
        )
