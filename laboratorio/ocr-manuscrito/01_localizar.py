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
from pathlib import Path

import cv2
import numpy as np

DATOS = Path(__file__).parent / "datos"
ANCHO = 1500           # ancho del ticket enderezado, en píxeles
MIN_INLIERS = 30       # por debajo, la foto se informa como no localizada


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


def preparar(imagen):
    gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    return cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(gris)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--referencia", default="T017.jpg")
    args = parser.parse_args()

    ref = referencia(args.referencia)
    alto = ref.shape[0]
    sift = cv2.SIFT_create(nfeatures=8000)
    kp_ref, des_ref = sift.detectAndCompute(preparar(ref), None)
    emparejador = cv2.FlannBasedMatcher({"algorithm": 1, "trees": 5}, {"checks": 64})

    salida = DATOS / "enderezados"
    salida.mkdir(exist_ok=True)
    with open(DATOS / "transcripcion.csv", encoding="utf-8") as f:
        archivos = [r["archivo"] for r in csv.DictReader(f, delimiter=";")]

    informe = []
    for archivo in archivos:
        foto = cv2.imread(str(DATOS / "originales" / archivo))
        # Las fotos de WhatsApp son pequeñas: se amplían para que SIFT vea detalle.
        escala = max(1.0, 1600 / max(foto.shape[:2]))
        foto = cv2.resize(foto, None, fx=escala, fy=escala, interpolation=cv2.INTER_CUBIC)
        kp, des = sift.detectAndCompute(preparar(foto), None)
        pares = [m for m, n in emparejador.knnMatch(des_ref, des, k=2) if m.distance < 0.75 * n.distance]
        inliers, estado = 0, "no localizado"
        if len(pares) >= MIN_INLIERS:
            origen = np.float32([kp_ref[m.queryIdx].pt for m in pares])
            destino = np.float32([kp[m.trainIdx].pt for m in pares])
            H, mascara = cv2.findHomography(destino, origen, cv2.RANSAC, 6.0)
            inliers = int(mascara.sum()) if mascara is not None else 0
            if H is not None and inliers >= MIN_INLIERS:
                enderezado = cv2.warpPerspective(foto, H, (ANCHO, alto), borderValue=(255, 255, 255))
                cv2.imwrite(str(salida / archivo.replace(".jpg", ".png")), enderezado)
                estado = "ok"
        informe.append((archivo, estado, len(pares), inliers))
        print(f"{archivo}: {estado} ({len(pares)} pares, {inliers} coincidentes)")

    with open(DATOS / "localizacion.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";", lineterminator="\n")
        w.writerow(["archivo", "estado", "pares", "coincidentes"])
        w.writerows(informe)
    print(f"Localizados: {sum(e == 'ok' for _, e, _, _ in informe)} de {len(informe)}")


if __name__ == "__main__":
    main()
