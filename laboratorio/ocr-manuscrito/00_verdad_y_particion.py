"""L2 y L3: genera `datos/verdad.csv` desde la transcripción y reparte las fotos
en cinco grupos fijos. Las fotos de un mismo ticket caen siempre en el mismo
grupo, para que ningún modelo se evalúe con un ticket que vio al entrenar."""

import csv
import random
from collections import defaultdict
from pathlib import Path

from lab import normalizacion as N

DATOS = Path(__file__).parent / "datos"
SEMILLA, GRUPOS = 2026, 5


def leer(nombre):
    with open(DATOS / nombre, encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter=";"))


def main():
    filas = leer("transcripcion.csv")
    inventario = {r["archivo"]: r for r in leer("inventario.csv")}

    with open(DATOS / "verdad.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";", lineterminator="\n")
        w.writerow(["archivo", "placa", "fecha", "peso_bruto_tn"])
        for r in filas:
            peso = N.peso_bruto(r["peso_linea"])
            w.writerow([r["archivo"], N.placa(r["placa"]) or "", N.fecha(r["dia"], r["mes"], r["anio"]) or "",
                        peso if peso is not None else ""])

    # Un ticket sin número visible es su propio grupo de fotos.
    por_ticket = defaultdict(list)
    for r in filas:
        ticket = inventario[r["archivo"]]["ticket_no"].rstrip("?")
        clave = ticket if ticket and "?" not in inventario[r["archivo"]]["ticket_no"] else r["archivo"]
        if r["archivo"] == "T001.jpg":
            clave = "005853"  # Probable mismo ticket que T005
        por_ticket[clave].append(r["archivo"])

    tickets = sorted(por_ticket)
    random.Random(SEMILLA).shuffle(tickets)
    carga = [0] * GRUPOS
    asignacion = {}
    for t in sorted(tickets, key=lambda t: -len(por_ticket[t])):
        g = carga.index(min(carga))
        carga[g] += len(por_ticket[t])
        for archivo in por_ticket[t]:
            asignacion[archivo] = (g + 1, t)

    with open(DATOS / "particion.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";", lineterminator="\n")
        w.writerow(["archivo", "grupo", "ticket"])
        for archivo in sorted(asignacion):
            w.writerow([archivo, *asignacion[archivo]])
    print(f"{len(filas)} fotos, {len(tickets)} tickets, fotos por grupo: {carga}")


if __name__ == "__main__":
    main()
