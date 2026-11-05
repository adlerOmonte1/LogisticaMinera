"""Reglas que convierten lo escrito en el ticket de la Balanza (DR-09) en el valor
de cada campo. Las comparten todos los motores, para que dos motores que leen
el mismo texto propongan el mismo valor.

Un campo que no cumple su regla devuelve None: sin lectura, nunca un valor
estimado (RN-M04-03). Calibradas en `laboratorio/ocr-manuscrito` (L6).
"""

import re
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

# Un número de peso: con separador (13.400, 13.4, 13,4), con espacio de miles
# (15 720) o sin separador (15720).
_NUMERO = re.compile(r"\d{1,2}[.,:]\d{1,3}|\d{1,2} \d{3}(?!\d)|\d{4,5}")
_PLACA = re.compile(r"([A-Z0-9]{3})\s*[-–.]?\s*([0-9OSBIZGQDL]{3})(?![A-Z0-9])")
_A_DIGITO = str.maketrans("OQDSBIZGL", "000581261")


def a_toneladas(numero: str) -> Decimal | None:
    """Con separador y parte entera de 1 o 2 dígitos son toneladas; sin separador
    y de 4 o 5 dígitos, kilogramos."""
    numero = numero.strip()
    if re.fullmatch(r"\d{1,2}[.,:]\d{1,3}", numero):
        entero, fraccion = re.split(r"[.,:]", numero)
        return Decimal(f"{entero}.{fraccion}")
    if re.fullmatch(r"\d{1,2} \d{3}|\d{4,5}", numero):
        return Decimal(numero.replace(" ", "")) / 1000
    return None


def peso_bruto(texto: str) -> Decimal | None:
    """El peso bruto es el mayor número de la línea: a veces la línea trae el
    cálculo de tara y neto, en cualquier orden. Un espacio junto al separador
    («13. 400») es un hueco de la escritura, no otro número. Se devuelve en
    toneladas con dos decimales, como lo guarda el ingreso."""
    texto = re.sub(r"(\d)\s*([.,:])\s*(\d)", r"\1\2\3", texto or "")
    valores = [v for v in (a_toneladas(n) for n in _NUMERO.findall(texto)) if v is not None]
    return max(valores).quantize(Decimal("0.01"), ROUND_HALF_UP) if valores else None


def placa(texto: str) -> str | None:
    """Formato XXX-NNN. En las tres últimas posiciones, que son dígitos, se
    corrigen las confusiones de forma. Un nombre o un apodo no es placa: la
    parte numérica exige al menos dos dígitos reales."""
    for m in _PLACA.finditer((texto or "").upper()):
        if sum(c.isdigit() for c in m.group(2)) >= 2:
            return f"{m.group(1)}-{m.group(2).translate(_A_DIGITO)}"
    return None


def fecha(dia: str, mes: str, anio: str) -> str | None:
    """Día y mes de 1 o 2 dígitos; año de 2 dígitos (se completa a 20AA) o de 4.
    Devuelve la fecha en ISO, o None si falta una casilla o la fecha no existe."""
    dia, mes, anio = (re.sub(r"\D", "", x or "") for x in (dia, mes, anio))
    if not (1 <= len(dia) <= 2 and 1 <= len(mes) <= 2 and len(anio) in (2, 4)):
        return None
    d, m, a = int(dia), int(mes), int(anio)
    if a < 100:
        a += 2000
    try:
        return date(a, m, d).isoformat()
    except ValueError:
        return None
