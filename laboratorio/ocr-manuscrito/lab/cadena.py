"""Cadena de reconocimiento de una foto: localizar el ticket, enderezarlo,
recortar las cinco zonas, leerlas y normalizar los tres campos.

La comparten el laboratorio (01, 02, 06) y será la base del adaptador del
backend en el saneamiento (S2).
"""

import json
import time
from dataclasses import dataclass, field
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

BASE = Path(__file__).resolve().parent.parent
DATOS = BASE / "datos"
ANCHO = 1500          # ancho del ticket enderezado, en píxeles
MIN_INLIERS = 30      # por debajo, la foto se informa como no localizada
ZONAS = ("peso", "placa", "dia", "mes", "anio")


def preparar(imagen):
    gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    return cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(gris)


def plantilla() -> dict:
    datos = json.loads((BASE / "plantilla.json").read_text(encoding="utf-8"))
    return {k: v for k, v in datos.items() if not k.startswith("_")}


def recortar(enderezado, zonas: dict) -> dict:
    h, w = enderezado.shape[:2]
    return {c: enderezado[int(y0 * h):int(y1 * h), int(x0 * w):int(x1 * w)]
            for c, (x0, y0, x1, y1) in zonas.items()}


class Localizador:
    """Registra una foto contra el ticket de referencia por sus partes impresas
    (SIFT y RANSAC) y la devuelve enderezada al tamaño de la referencia."""

    def __init__(self, referencia: Path = DATOS / "referencia.png"):
        if not referencia.exists():
            raise FileNotFoundError(f"Falta {referencia}: ejecute primero 01_localizar.py")
        ref = cv2.imread(str(referencia))
        self.alto = ref.shape[0]
        self.sift = cv2.SIFT_create(nfeatures=8000)
        self.kp_ref, self.des_ref = self.sift.detectAndCompute(preparar(ref), None)
        # Emparejamiento exhaustivo, no FLANN: FLANN usa árboles aleatorios y la misma
        # foto podía enderezarse distinto en cada corrida, y cambiar la lectura.
        self.emparejador = cv2.BFMatcher(cv2.NORM_L2)

    def enderezar(self, foto) -> tuple[np.ndarray | None, int]:
        # Las fotos de WhatsApp son pequeñas: se amplían para que SIFT vea detalle.
        escala = max(1.0, 1600 / max(foto.shape[:2]))
        foto = cv2.resize(foto, None, fx=escala, fy=escala, interpolation=cv2.INTER_CUBIC)
        kp, des = self.sift.detectAndCompute(preparar(foto), None)
        if des is None or len(kp) < MIN_INLIERS:
            return None, 0
        pares = [m for m, n in self.emparejador.knnMatch(self.des_ref, des, k=2) if m.distance < 0.75 * n.distance]
        if len(pares) < MIN_INLIERS:
            return None, len(pares)
        origen = np.float32([self.kp_ref[m.queryIdx].pt for m in pares])
        destino = np.float32([kp[m.trainIdx].pt for m in pares])
        H, mascara = cv2.findHomography(destino, origen, cv2.RANSAC, 6.0)
        inliers = int(mascara.sum()) if mascara is not None else 0
        if H is None or inliers < MIN_INLIERS:
            return None, inliers
        return cv2.warpPerspective(foto, H, (ANCHO, self.alto), borderValue=(255, 255, 255)), inliers


@dataclass
class Resultado:
    localizado: bool
    coincidentes: int
    campos: dict = field(default_factory=dict)    # nombre -> Campo
    lecturas: dict = field(default_factory=dict)  # zona -> Lectura
    segundos: float = 0.0
    enderezado: np.ndarray | None = None
    recortes: dict = field(default_factory=dict)


class Cadena:
    def __init__(self, modelo: str, dispositivo: str | None = None, haces: int = 4):
        from lab.lector import LectorTrOCR  # noqa: PLC0415 — carga PyTorch solo si se usa

        self.localizador = Localizador()
        self.zonas = plantilla()
        self.lector = LectorTrOCR(modelo, dispositivo, haces)

    def reconocer(self, foto) -> Resultado:
        from lab.lector import armar_campos  # noqa: PLC0415

        inicio = time.perf_counter()
        enderezado, inliers = self.localizador.enderezar(foto)
        if enderezado is None:
            return Resultado(False, inliers, segundos=time.perf_counter() - inicio)
        recortes = recortar(enderezado, self.zonas)
        lecturas = {}
        for z in ZONAS:
            img = Image.fromarray(cv2.cvtColor(recortes[z], cv2.COLOR_BGR2RGB))
            lecturas[z] = self.lector.leer([img], z)[0]
        return Resultado(True, inliers, armar_campos(lecturas), lecturas, time.perf_counter() - inicio,
                         enderezado, recortes)
