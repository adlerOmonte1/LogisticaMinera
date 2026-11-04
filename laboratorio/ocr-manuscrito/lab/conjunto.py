"""Acceso a los datos del laboratorio: transcripción, verdad, partición y recortes."""

import csv
from pathlib import Path

from PIL import Image

DATOS = Path(__file__).resolve().parent.parent / "datos"
ZONAS = ("peso", "placa", "dia", "mes", "anio")
# Columna de la transcripción que es la etiqueta de cada zona: lo escrito, tal cual.
ETIQUETA = {"peso": "peso_linea", "placa": "placa_linea", "dia": "dia", "mes": "mes", "anio": "anio"}


def _leer(nombre):
    with open(DATOS / nombre, encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter=";"))


def transcripcion():
    return {r["archivo"]: r for r in _leer("transcripcion.csv")}


def verdad():
    return {r["archivo"]: r for r in _leer("verdad.csv")}


def particion():
    return {r["archivo"]: int(r["grupo"]) for r in _leer("particion.csv")}


def recorte(archivo: str, zona: str) -> Image.Image:
    return Image.open(DATOS / "recortes" / zona / archivo.replace(".jpg", ".png")).convert("RGB")


def muestras(archivos):
    """(imagen, etiqueta, zona) de cada zona con etiqueta. Una zona ilegible
    para la persona (vacía) no se usa para entrenar."""
    t = transcripcion()
    salida = []
    for a in archivos:
        for z in ZONAS:
            etiqueta = t[a][ETIQUETA[z]].strip()
            if etiqueta:
                salida.append((recorte(a, z), etiqueta, z))
    return salida
