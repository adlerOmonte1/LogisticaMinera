"""Empaqueta el modelo entrenado para repartirlo a los equipos de desarrollo y al
servidor por un almacenamiento privado. El paquete lleva los pesos, el
procesador, la referencia y la plantilla, que juntos son la versión del motor.

Uso: python 07_empaquetar.py [--nombre trocr-ticket-v1]
Salida: datos/paquetes/<nombre>.zip. En cada equipo se instala con
  python manage.py obtener_modelo --desde <paquete.zip>   (o --url <enlace privado>)
"""

import argparse
import hashlib
import shutil
import zipfile

from lab.cadena import BASE, DATOS


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--nombre", default="trocr-ticket-v1")
    args = p.parse_args()
    carpeta = DATOS / "modelos" / args.nombre
    # La referencia y la plantilla viajan con el modelo: forman parte de su versión.
    shutil.copy(DATOS / "referencia.png", carpeta / "referencia.png")
    shutil.copy(BASE / "plantilla.json", carpeta / "plantilla.json")
    destino = DATOS / "paquetes"
    destino.mkdir(exist_ok=True)
    paquete = destino / f"{args.nombre}.zip"
    with zipfile.ZipFile(paquete, "w", zipfile.ZIP_STORED) as z:
        for archivo in sorted(carpeta.iterdir()):
            z.write(archivo, f"{args.nombre}/{archivo.name}")
    huella = hashlib.sha256(paquete.read_bytes()).hexdigest()
    version = (carpeta / "VERSION").read_text(encoding="utf-8").strip()
    print(f"{paquete} ({paquete.stat().st_size / 1e9:.2f} GB)")
    print(f"Versión del modelo: {version}")
    print(f"SHA-256 del paquete: {huella}")


if __name__ == "__main__":
    main()
