"""Lee fotos nuevas del ticket con el modelo entrenado, sin transcripción previa.

Sirve para validar el entrenamiento con tickets que el modelo nunca vio, antes
de llevarlo al backend. Muestra lo que el sistema propondría al usuario: cada
campo con su confianza, y «VERIFICAR» cuando la confianza no llega al umbral.

Uso:
  python 06_leer.py datos/pruebas/entrada                 Todas las fotos de la carpeta
  python 06_leer.py foto1.jpg foto2.jpg --dispositivo cpu Tiempo real de un servidor sin GPU

Por cada foto guarda en `datos/pruebas/salida/` el ticket enderezado y los cinco
recortes, y agrega una fila a `datos/pruebas/lecturas.csv`.
"""

import argparse
import csv
from datetime import datetime
from pathlib import Path

import cv2

from lab.cadena import DATOS, ZONAS, Cadena

UMBRAL = 0.80
EXTENSIONES = {".jpg", ".jpeg", ".png", ".webp"}
NOMBRES = {"PLACA": "Placa", "FECHA": "Fecha", "PESO_BRUTO": "Peso bruto"}
UNIDAD = {"PESO_BRUTO": " t"}


def fotos(rutas):
    for r in map(Path, rutas):
        if r.is_dir():
            yield from sorted(p for p in r.iterdir() if p.suffix.lower() in EXTENSIONES)
        elif r.suffix.lower() in EXTENSIONES:
            yield r


def marca(campo):
    if campo.valor is None:
        return "sin lectura: el usuario lo digita"
    return f"confianza {campo.confianza:.2f}" + ("" if campo.confianza >= UMBRAL else "  << VERIFICAR")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("rutas", nargs="+", help="fotos o carpetas")
    p.add_argument("--modelo", default=str(DATOS / "modelos" / "trocr-ticket-v1"))
    p.add_argument("--dispositivo", help="cpu o cuda; por omisión, la GPU si existe")
    p.add_argument("--haces", type=int, default=4)
    args = p.parse_args()

    lista = list(fotos(args.rutas))
    if not lista:
        raise SystemExit("No se encontraron fotos (.jpg, .jpeg, .png, .webp) en las rutas indicadas")
    version = (Path(args.modelo) / "VERSION").read_text(encoding="utf-8").strip() if (Path(args.modelo) / "VERSION").exists() else Path(args.modelo).name
    cadena = Cadena(args.modelo, args.dispositivo, args.haces)
    print(f"Modelo {version} en {cadena.lector.dispositivo}, {len(lista)} foto(s)\n")

    salida = DATOS / "pruebas" / "salida"
    salida.mkdir(parents=True, exist_ok=True)
    registro = DATOS / "pruebas" / "lecturas.csv"
    nuevo = not registro.exists()
    with open(registro, "a", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";", lineterminator="\n")
        if nuevo:
            w.writerow(["fecha_prueba", "foto", "modelo", "localizado", "placa", "conf_placa", "fecha", "conf_fecha",
                        "peso_bruto_tn", "conf_peso", "segundos", "texto_zonas"])
        for foto in lista:
            imagen = cv2.imread(str(foto))
            if imagen is None:
                print(f"{foto.name}: no se pudo abrir la imagen\n")
                continue
            r = cadena.reconocer(imagen)
            print(f"{foto.name}  ({r.segundos:.1f} s)")
            if not r.localizado:
                print(f"  No fue posible localizar el ticket ({r.coincidentes} puntos coincidentes; mínimo 30).")
                print("  El sistema pediría tomar otra foto o ingresar los datos manualmente.\n")
                w.writerow([datetime.now().isoformat(timespec="seconds"), foto.name, version, "no",
                            "", "", "", "", "", "", round(r.segundos, 2), ""])
                continue
            for c in ("PLACA", "FECHA", "PESO_BRUTO"):
                valor = (r.campos[c].valor + UNIDAD.get(c, "")) if r.campos[c].valor else "—"
                print(f"  {NOMBRES[c]:<12} {valor:<12} {marca(r.campos[c])}")
            texto = " | ".join(f"{z}={r.lecturas[z].texto}" for z in ZONAS)
            print(f"  Escrito en el ticket, tal como se leyó: {texto}\n")
            cv2.imwrite(str(salida / f"{foto.stem}_enderezado.jpg"), r.enderezado)
            for z, img in r.recortes.items():
                cv2.imwrite(str(salida / f"{foto.stem}_{z}.png"), img)
            cs = [r.campos[c] for c in ("PLACA", "FECHA", "PESO_BRUTO")]
            w.writerow([datetime.now().isoformat(timespec="seconds"), foto.name, version, "si",
                        cs[0].valor or "", cs[0].confianza or "", cs[1].valor or "", cs[1].confianza or "",
                        cs[2].valor or "", cs[2].confianza or "", round(r.segundos, 2), texto])
    print(f"Lecturas agregadas a {registro}; recortes en {salida}")


if __name__ == "__main__":
    main()
