"""L4, parte 2: recorta las cinco zonas manuscritas de cada ticket enderezado
según `plantilla.json`, y arma una hoja con todos los recortes para revisarlos.
Solo se recortan peso, placa, día, mes y año: lo demás del ticket no se lee."""

import cv2
import numpy as np

from lab.cadena import DATOS, ZONAS as CAMPOS, plantilla, recortar


def main():
    zonas = plantilla()
    for c in CAMPOS:
        (DATOS / "recortes" / c).mkdir(parents=True, exist_ok=True)
    filas = []
    for archivo in sorted((DATOS / "enderezados").glob("*.png")):
        partes = recortar(cv2.imread(str(archivo)), zonas)
        for c, img in partes.items():
            cv2.imwrite(str(DATOS / "recortes" / c / archivo.name), img)
        # Hoja de revisión: una fila por ticket, a la misma altura.
        alto = 70
        piezas = [cv2.resize(partes[c], (int(partes[c].shape[1] * alto / partes[c].shape[0]), alto)) for c in CAMPOS]
        fila = np.hstack([np.full((alto, 60, 3), 255, np.uint8)] + [np.pad(p, ((0, 0), (0, 6), (0, 0)), constant_values=200) for p in piezas])
        cv2.putText(fila, archivo.stem, (2, 40), 0, 0.5, (0, 0, 255), 1)
        filas.append(fila)
    ancho = max(f.shape[1] for f in filas)
    hoja = np.vstack([np.pad(f, ((0, 4), (0, ancho - f.shape[1]), (0, 0)), constant_values=255) for f in filas])
    cv2.imwrite(str(DATOS / "revision_recortes.png"), hoja)
    print(f"{len(filas)} tickets recortados en {len(CAMPOS)} zonas")


if __name__ == "__main__":
    main()
