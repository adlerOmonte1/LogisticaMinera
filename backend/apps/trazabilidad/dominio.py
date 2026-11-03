"""Catálogos cerrados de M06 (RN-M06-09, D-21): cuatro etapas y tres rutas.

La ruta no es una tabla: es un dominio cerrado que asocia a cada valor sus
etapas en orden. El secado no forma parte de ninguna ruta porque es común a todo
el lote (DR-16). Una etapa o una ruta nueva cambiaría la comparabilidad de los
recorridos anteriores: se decide expresamente, no dando de alta una fila.
"""

from django.db import models

SECADO = "SECADO"
ZARANDEO = "ZARANDEO"
MOLIENDA = "MOLIENDA"
ENSACADO = "ENSACADO"

ETAPAS = [(SECADO, "Secado", 1), (ZARANDEO, "Zarandeo", 2), (MOLIENDA, "Molienda", 3), (ENSACADO, "Ensacado", 4)]
NOMBRE_ETAPA = {codigo: nombre for codigo, nombre, _ in ETAPAS}
TRANSFORMAN = {ZARANDEO, MOLIENDA}  # después de ellas el mineral ya no se separa (DR-29)


class Ruta(models.TextChoices):
    ZARANDEO_ENSACADO = "ZARANDEO_ENSACADO", "Zaranda"
    MOLIENDA_ENSACADO = "MOLIENDA_ENSACADO", "Molido"
    ZARANDEO_MOLIENDA_ENSACADO = "ZARANDEO_MOLIENDA_ENSACADO", "Zarandeado y molido"


ETAPAS_POR_RUTA = {
    Ruta.ZARANDEO_ENSACADO: (ZARANDEO, ENSACADO),
    Ruta.MOLIENDA_ENSACADO: (MOLIENDA, ENSACADO),
    Ruta.ZARANDEO_MOLIENDA_ENSACADO: (ZARANDEO, MOLIENDA, ENSACADO),
}


class Destino(models.TextChoices):
    """DR-14: a dónde va el mineral; el sistema no registra la venta ni el traslado."""

    VENTA = "VENTA", "Venta"
    TRASLADO = "TRASLADO", "Traslado a otro punto"
