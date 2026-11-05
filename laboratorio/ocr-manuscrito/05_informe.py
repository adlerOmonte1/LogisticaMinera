"""L7: arma `datos/informe_capacidad.md` con los resultados de cada lector y
mide el tiempo por ticket del modelo ajustado en CPU, que es lo que tendrá el
servidor en la nube (D-15)."""

import csv
import json
import re
import time

from lab import conjunto as C
from lab.evaluacion import CAMPOS, UMBRAL, resumen

LECTORES = [
    ("TrOCR small sin ajuste", "trocr-small-sin-ajuste"),
    ("TrOCR base sin ajuste", "trocr-base-sin-ajuste"),
    ("TrOCR base ajustado, 20 épocas (validación cruzada)", "trocr-base-handwritten-ajustado-validacion-cruzada"),
    ("TrOCR base ajustado, 12 épocas (validación cruzada)", "trocr-base-handwritten-ajustado-e12-validacion-cruzada"),
]
ELEGIDO = "trocr-base-handwritten-ajustado-e12-validacion-cruzada"


def leer_csv(nombre):
    with open(C.DATOS / "resultados" / f"{nombre}.csv", encoding="utf-8") as f:
        filas = list(csv.DictReader(f, delimiter=";"))
    for r in filas:
        r["correcto"] = int(r["correcto"])
        r["confianza"] = float(r["confianza"]) if r["confianza"] else ""
    return filas


def tiempo_cpu(modelo, n=8):
    from lab.lector import LectorTrOCR

    lector = LectorTrOCR(str(modelo), dispositivo="cpu")
    archivos = sorted(C.particion())[:n]
    lector.leer([C.recorte(archivos[0], "peso")], "peso")  # calentamiento
    tiempos = []
    for a in archivos:
        inicio = time.perf_counter()
        for z in C.ZONAS:
            lector.leer([C.recorte(a, z)], z)
        tiempos.append(time.perf_counter() - inicio)
    return round(sum(tiempos) / len(tiempos), 2), round(max(tiempos), 2)


def main():
    lineas = ["# Informe de capacidad — reconocimiento manuscrito en local", "",
              f"Conjunto de desarrollo: 32 fotos (29 tickets), 96 lecturas. Umbral de confianza: {UMBRAL}.",
              "Una lectura es correcta si coincide con la verdad; si la verdad está vacía (placa escrita",
              "como nombre, día tapado), es correcta solo si el lector no propone valor (RN-M04-03).", "",
              "| Lector | Placa | Fecha | Peso bruto | Global | Errores con confianza ≥ umbral | s/ticket (GPU) |",
              "|---|---:|---:|---:|---:|---:|---:|"]
    tess = (C.DATOS / "resultados" / "tesseract-piloto.md").read_text(encoding="utf-8")
    m = re.search(r"\| tesseract \|[^\n]*", tess)
    if m:
        c = [x.strip() for x in m.group(0).strip("|").split("|")]
        lineas.append(f"| Tesseract actual (piloto_motores, foto completa) | {c[3]} | {c[4]} | {c[5]} | {c[6]} | 0 | {c[7]} (CPU) |")
    detalle = {}
    for titulo, nombre in LECTORES:
        try:
            filas = leer_csv(nombre)
        except FileNotFoundError:
            continue
        tickets = len({f["archivo"] for f in filas})
        r = resumen(filas, [0.0] * tickets)
        lineas.append(f"| {titulo} | {r['PLACA']} % | {r['FECHA']} % | {r['PESO_BRUTO']} % | {r['global']} % "
                      f"| {r['errores_confiados']} | — |")
        detalle[nombre] = filas

    cv = C.DATOS / "resultados" / f"{ELEGIDO}.json"
    if cv.exists():
        datos = json.loads(cv.read_text(encoding="utf-8"))
        lineas += ["", "## Validación cruzada por grupo", "",
                   "| Grupo | Placa | Fecha | Peso bruto | Global | Errores confiados |", "|---|---:|---:|---:|---:|---:|"]
        for g, r in datos["por_grupo"].items():
            lineas.append(f"| {g} | {r['PLACA']} % | {r['FECHA']} % | {r['PESO_BRUTO']} % | {r['global']} % | {r['errores_confiados']} |")
        lineas += ["", f"Tiempo medio por ticket en GPU: {datos['total']['s_por_ticket']} s.",
                   f"Parámetros: {json.dumps(datos['parametros'], ensure_ascii=False)}"]

    final = C.DATOS / "modelos" / "trocr-ticket-v1"
    if final.exists():
        medio, maximo = tiempo_cpu(final)
        version = (final / "VERSION").read_text(encoding="utf-8").strip()
        lineas += ["", "## Modelo candidato", "", f"- Versión: `{version}` (entrenado con las 32 fotos).",
                   f"- Tiempo por ticket en **CPU**: medio {medio} s, máximo {maximo} s (5 zonas, haz de 4).",
                   "- Su exactitud real solo se conoce con tickets nuevos: la de arriba es la de validación cruzada."]

    nombre = ELEGIDO
    if nombre in detalle:
        lineas += ["", "## Lecturas equivocadas del modelo ajustado", "",
                   "| Foto | Campo | Verdad | Leído | Confianza | Texto leído en las zonas |", "|---|---|---|---|---:|---|"]
        for f in detalle[nombre]:
            if not f["correcto"]:
                lineas.append(f"| {f['archivo'][:-4]} | {f['campo']} | {f['verdad'] or '(vacío)'} | {f['leido'] or '(sin lectura)'} "
                              f"| {f['confianza']} | {f['texto']} |")
    (C.DATOS / "informe_capacidad.md").write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print("\n".join(lineas))


if __name__ == "__main__":
    main()
