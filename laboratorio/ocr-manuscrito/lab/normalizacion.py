"""Reglas de L6: de lo escrito en el ticket al valor del campo.

Las usan tanto la generación de `verdad.csv` como la evaluación de los lectores,
para que ambos lados se normalicen igual. Un campo que no cumple su regla
devuelve None: sin lectura, nunca un valor estimado (RN-M04-03).
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
    («13. 400») es un hueco de la escritura, no otro número."""
    texto = re.sub(r"(\d)\s*([.,:])\s*(\d)", r"\1\2\3", texto or "")
    valores = [v for v in (a_toneladas(n) for n in _NUMERO.findall(texto)) if v is not None]
    # En toneladas con dos decimales, como lo guarda el ingreso (peso_bruto_tn).
    return max(valores).quantize(Decimal("0.01"), ROUND_HALF_UP) if valores else None


def placa(texto: str) -> str | None:
    """Formato XXX-NNN. En las tres últimas posiciones, que son dígitos, se
    corrigen las confusiones de forma. Un nombre o un apodo no es placa."""
    for m in _PLACA.finditer((texto or "").upper()):
        # Al menos dos dígitos reales en la parte numérica: una palabra no es placa.
        if sum(c.isdigit() for c in m.group(2)) >= 2:
            return f"{m.group(1)}-{m.group(2).translate(_A_DIGITO)}"
    return None


def fecha(dia: str, mes: str, anio: str) -> str | None:
    if not (1 <= len(dia or "") <= 2 and 1 <= len(mes or "") <= 2 and len(anio or "") in (2, 4)):
        return None
    try:
        d, m, a = int(dia), int(mes), int(anio)
    except (TypeError, ValueError):
        return None
    if a < 100:
        a += 2000
    try:
        return date(a, m, d).isoformat()
    except ValueError:
        return None


def solo_digitos(texto: str) -> str:
    return re.sub(r"\D", "", texto or "")
