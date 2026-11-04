"""L5 y L7: evalúa un lector sobre los recortes y lo compara con la verdad.

Uso:
  python 03_evaluar.py --modelo microsoft/trocr-base-handwritten
  python 03_evaluar.py --modelo datos/modelos/cv/grupo1 --grupos 1

Escribe `datos/resultados/<nombre>.csv` con cada lectura y devuelve el resumen.
"""

import argparse
import json
from pathlib import Path

from lab import conjunto as C
from lab.evaluacion import evaluar, guardar, resumen
from lab.lector import LectorTrOCR


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--modelo", required=True)
    p.add_argument("--grupos", default="", help="p. ej. 1,2: solo las fotos de esos grupos")
    p.add_argument("--nombre")
    p.add_argument("--dispositivo")
    args = p.parse_args()
    particion = C.particion()
    grupos = {int(g) for g in args.grupos.split(",") if g}
    archivos = sorted(a for a, g in particion.items() if not grupos or g in grupos)
    nombre = args.nombre or Path(args.modelo).name
    lector = LectorTrOCR(args.modelo, args.dispositivo)
    filas, tiempos = evaluar(lector, archivos, nombre)
    guardar(filas, nombre)
    print(json.dumps(resumen(filas, tiempos), ensure_ascii=False))


if __name__ == "__main__":
    main()
