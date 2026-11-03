"""V3 · La placa tiene un formato válido. Bloquea.

El patrón se lee de `settings.PATRON_PLACA` (RNF-M05-08, D-24), el mismo con
que M02 da de alta los vehículos.
"""

import re

from django.conf import settings

from .base import DatosTicket, ReglaBase, Resultado


class V3Placa(ReglaBase):
    codigo = "V3"
    campo = "placa"
    mensaje = "La placa no tiene un formato válido"

    def datos_completos(self, datos: DatosTicket) -> bool:
        return bool(datos.placa)

    def evaluar(self, datos: DatosTicket) -> Resultado:
        if re.fullmatch(settings.PATRON_PLACA, datos.placa.strip().upper()):
            return Resultado(True)
        return Resultado(False, {}, f"placa={datos.placa} patron={settings.PATRON_PLACA}")
