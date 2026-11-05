"""Localización del ticket de la Balanza en la foto y recorte de sus cinco zonas
manuscritas: peso, placa, día, mes y año (DR-09). Lo demás del ticket no se lee.

La foto se registra contra un ticket de referencia por sus partes impresas: SIFT
encuentra puntos comunes, el emparejamiento exhaustivo los asocia y RANSAC
descarta como ruido lo manuscrito. La referencia y las coordenadas de las zonas
viajan con el modelo (`referencia.png`, `plantilla.json`), porque forman parte de
la versión del motor y la referencia es una foto real que no se versiona en git.

Solo los adaptadores de `motores/` importan este módulo (RNF-M04-05).
"""

import json
from pathlib import Path

import cv2
import numpy as np

ANCHO = 1500       # ancho del ticket enderezado, en píxeles
MIN_INLIERS = 30   # por debajo, la foto se considera sin ticket reconocible
ZONAS = ("peso", "placa", "dia", "mes", "anio")


def _preparar(imagen):
    gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    return cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(gris)


class TicketBalanza:
    def __init__(self, carpeta: Path):
        datos = json.loads((carpeta / "plantilla.json").read_text(encoding="utf-8"))
        self.zonas = {k: v for k, v in datos.items() if k in ZONAS}
        referencia = cv2.imread(str(carpeta / "referencia.png"))
        if referencia is None:
            raise FileNotFoundError(f"Falta la referencia del ticket en {carpeta}")
        self.alto = referencia.shape[0]
        self.sift = cv2.SIFT_create(nfeatures=8000)
        self.kp_ref, self.des_ref = self.sift.detectAndCompute(_preparar(referencia), None)
        # Exhaustivo y no FLANN: FLANN usa árboles aleatorios y la misma foto podía
        # enderezarse distinto en cada intento, y cambiar la lectura.
        self.emparejador = cv2.BFMatcher(cv2.NORM_L2)

    def enderezar(self, foto):
        """El ticket enderezado al tamaño de la referencia, o None si la foto no
        contiene un ticket reconocible."""
        escala = max(1.0, 1600 / max(foto.shape[:2]))  # las fotos de WhatsApp son pequeñas
        foto = cv2.resize(foto, None, fx=escala, fy=escala, interpolation=cv2.INTER_CUBIC)
        kp, des = self.sift.detectAndCompute(_preparar(foto), None)
        if des is None or len(kp) < MIN_INLIERS:
            return None
        pares = [m for m, n in self.emparejador.knnMatch(self.des_ref, des, k=2) if m.distance < 0.75 * n.distance]
        if len(pares) < MIN_INLIERS:
            return None
        origen = np.float32([self.kp_ref[m.queryIdx].pt for m in pares])
        destino = np.float32([kp[m.trainIdx].pt for m in pares])
        H, mascara = cv2.findHomography(destino, origen, cv2.RANSAC, 6.0)
        if H is None or mascara is None or int(mascara.sum()) < MIN_INLIERS:
            return None
        return cv2.warpPerspective(foto, H, (ANCHO, self.alto), borderValue=(255, 255, 255))

    def recortar(self, enderezado) -> dict:
        h, w = enderezado.shape[:2]
        return {z: enderezado[int(y0 * h):int(y1 * h), int(x0 * w):int(x1 * w)]
                for z, (x0, y0, x1, y1) in self.zonas.items()}

    def zonas_de(self, imagen: bytes) -> dict | None:
        """De los bytes de la foto a las cinco zonas en RGB, o None si no hay ticket."""
        foto = cv2.imdecode(np.frombuffer(imagen, np.uint8), cv2.IMREAD_COLOR)
        if foto is None:
            return None
        enderezado = self.enderezar(foto)
        if enderezado is None:
            return None
        return {z: cv2.cvtColor(img, cv2.COLOR_BGR2RGB) for z, img in self.recortar(enderezado).items()}
