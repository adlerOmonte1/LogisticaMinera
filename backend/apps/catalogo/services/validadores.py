"""Validación de formato de placa y RUC (RS-M02-04, RNF-M02-04).

Se ejecuta en el servicio, antes de persistir, con independencia de lo que
valide el formulario Angular. Lanza excepción de dominio con el mensaje
literal del criterio de aceptación.
"""

import re

from common.excepciones import ErrorDeValidacionDeDominio

# Placa vehicular peruana: tres letras, guion, tres dígitos (p. ej. ABC-123).
# Decisión D-M02-01: se adopta este formato único; los formatos antiguos y de
# vehículo menor quedan fuera de alcance (no circulan volquetes con ellos).
_PLACA = re.compile(r"^[A-Z]{3}-\d{3}$")
_RUC = re.compile(r"^\d{11}$")

MENSAJE_PLACA_INVALIDA = "El formato de la placa no es válido"
MENSAJE_RUC_INVALIDO = "El RUC debe tener once dígitos"


def normalizar_placa(placa: str) -> str:
    return (placa or "").strip().upper()


def validar_placa(placa: str) -> str:
    placa = normalizar_placa(placa)
    if not _PLACA.match(placa):
        raise ErrorDeValidacionDeDominio(MENSAJE_PLACA_INVALIDA, codigo="PLACA_INVALIDA")
    return placa


def validar_ruc(ruc: str) -> str:
    ruc = (ruc or "").strip()
    if not _RUC.match(ruc):
        raise ErrorDeValidacionDeDominio(MENSAJE_RUC_INVALIDO, codigo="RUC_INVALIDO")
    return ruc
