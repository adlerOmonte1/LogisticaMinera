"""L4, parte 1: localiza el ticket en la foto y lo endereza.

El formato de la Balanza es fijo, así que cada foto se registra contra un
ticket de referencia por sus partes impresas (marco, títulos, etiquetas): SIFT
encuentra puntos comunes y RANSAC calcula la homografía. Funciona con el ticket
rotado, inclinado, de cabeza o con un borde fuera de la foto. Lo manuscrito
cambia de un ticket a otro y RANSAC lo descarta como ruido.

Uso: python 01_localizar.py [--referencia T017.jpg]
"""

import argparse
import csv

import cv2
import numpy as np

from lab.cadena import ANCHO, DATOS, Localizador


def recortar_por_marco(imagen):
    """Recorte del ticket por su marco azul impreso; solo para la referencia."""
    hsv = cv2.cvtColor(imagen, cv2.COLOR_BGR2HSV)
    mascara = cv2.dilate(cv2.inRange(hsv, (95, 70, 50), (135, 255, 255)), np.ones((5, 5), np.uint8))
    contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    x, y, w, h = cv2.boundingRect(max(contornos, key=cv2.contourArea))
    p = 15
    return imagen[max(0, y - p):y + h + p, max(0, x - p):x + w + p]


def referencia(nombre):
    ref = recortar_por_marco(cv2.imread(str(DATOS / "originales" / nombre)))
    escala = ANCHO / ref.shape[1]
    ref = cv2.resize(ref, None, fx=escala, fy=escala, interpolation=cv2.INTER_CUBIC)
    cv2.imwrite(str(DATOS / "referencia.png"), ref)
    return ref


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--referencia", default="T017.jpg")
    args = parser.parse_args()

    referencia(args.referencia)
    localizador = Localizador()
    salida = DATOS / "enderezados"
    salida.mkdir(exist_ok=True)
    with open(DATOS / "transcripcion.csv", encoding="utf-8") as f:
        archivos = [r["archivo"] for r in csv.DictReader(f, delimiter=";")]

    informe = []
    for archivo in archivos:
        enderezado, inliers = localizador.enderezar(cv2.imread(str(DATOS / "originales" / archivo)))
        estado = "ok" if enderezado is not None else "no localizado"
        if enderezado is not None:
            cv2.imwrite(str(salida / archivo.replace(".jpg", ".png")), enderezado)
        informe.append((archivo, estado, inliers))
        print(f"{archivo}: {estado} ({inliers} coincidentes)")

    with open(DATOS / "localizacion.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";", lineterminator="\n")
        w.writerow(["archivo", "estado", "coincidentes"])
        w.writerows(informe)
    print(f"Localizados: {sum(e == 'ok' for _, e, _ in informe)} de {len(informe)}")


if __name__ == "__main__":
    main()
