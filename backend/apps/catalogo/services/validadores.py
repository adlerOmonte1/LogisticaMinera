"""Validación de formato de placa y RUC (RS-M02-04, RNF-M02-04).

Se ejecuta en el servicio, antes de persistir, con independencia de lo que
valide el formulario Angular. Lanza excepción de dominio con el mensaje
literal del criterio de aceptación.
"""

import re

from django.conf import settings

from common.excepciones import ErrorDeValidacionDeDominio

# El patrón de placa no se escribe aquí: viene de `settings.PATRON_PLACA` (D-24),
# el mismo que leerá la regla V3 de M05 (RNF-M05-08). Por defecto, tres letras o
# dígitos, guion y tres letras o dígitos, como ABC-123 o C9K-741.
_RUC = re.compile(r"^\d{11}$")

MENSAJE_PLACA_INVALIDA = "El formato de la placa no es válido"
MENSAJE_RUC_INVALIDO = "El RUC debe tener once dígitos"


def normalizar_placa(placa: str) -> str:
    return (placa or "").strip().upper()


def validar_placa(placa: str) -> str:
    placa = normalizar_placa(placa)
    if not re.fullmatch(settings.PATRON_PLACA, placa):
        raise ErrorDeValidacionDeDominio(MENSAJE_PLACA_INVALIDA, codigo="PLACA_INVALIDA")
    return placa


def validar_ruc(ruc: str) -> str:
    ruc = (ruc or "").strip()
    if not _RUC.match(ruc):
        raise ErrorDeValidacionDeDominio(MENSAJE_RUC_INVALIDO, codigo="RUC_INVALIDO")
    return ruc
