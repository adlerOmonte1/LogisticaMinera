"""Evaluación de un lector contra la verdad: exactitud por campo, errores con
confianza sobre el umbral (los que no se habrían resaltado) y tiempo por ticket."""

import csv
import time

from lab import conjunto as C
from lab.lector import armar_campos, coincide

CAMPOS = ("PLACA", "FECHA", "PESO_BRUTO")
COLUMNA = {"PLACA": "placa", "FECHA": "fecha", "PESO_BRUTO": "peso_bruto_tn"}
UMBRAL = 0.80


def evaluar(lector, archivos, nombre):
    verdad = C.verdad()
    filas, tiempos = [], []
    for a in archivos:
        inicio = time.perf_counter()
        lecturas = {z: lector.leer([C.recorte(a, z)], z)[0] for z in C.ZONAS}
        campos = armar_campos(lecturas)
        tiempos.append(time.perf_counter() - inicio)
        for c in CAMPOS:
            v = verdad[a][COLUMNA[c]]
            ok = coincide(c, campos[c].valor, v)
            filas.append({"archivo": a, "campo": c, "verdad": v, "leido": campos[c].valor or "",
                          "confianza": campos[c].confianza if campos[c].confianza is not None else "",
                          "correcto": int(ok),
                          "texto": " | ".join(f"{z}={lecturas[z].texto}" for z in C.ZONAS)})
    return filas, tiempos


def resumen(filas, tiempos):
    r = {"lecturas": len(filas), "tickets": len(tiempos)}
    for c in CAMPOS:
        fc = [f for f in filas if f["campo"] == c]
        r[c] = round(100 * sum(f["correcto"] for f in fc) / len(fc), 1)
        r[f"{c}_confiados"] = sum(1 for f in fc if not f["correcto"] and f["confianza"] != "" and f["confianza"] >= UMBRAL)
    r["global"] = round(100 * sum(f["correcto"] for f in filas) / len(filas), 1)
    r["errores_confiados"] = sum(r[f"{c}_confiados"] for c in CAMPOS)
    r["s_por_ticket"] = round(sum(tiempos) / len(tiempos), 2)
    return r


def guardar(filas, nombre):
    destino = C.DATOS / "resultados"
    destino.mkdir(exist_ok=True)
    with open(destino / f"{nombre}.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, list(filas[0]), delimiter=";", lineterminator="\n")
        w.writeheader()
        w.writerows(filas)
