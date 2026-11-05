"""Piloto de motores de reconocimiento (PLAN-02 7.3, D-12, D-15).

Recorre un conjunto de tickets con su valor verdadero, los procesa con cada
motor y mide lo que D-12 exige comparar: exactitud por campo, tiempo por ticket
—que decide D-15— y la utilidad del umbral, que es el riesgo principal de las
notas de M04: cuántas lecturas equivocadas tenían una confianza por encima del
umbral y no se habrían resaltado. El costo y la dependencia de conexión no se
miden aquí: se anotan en el informe del piloto.

El conjunto es una carpeta con las imágenes y un `verdad.csv` separado por
punto y coma: `archivo;placa;fecha;peso_bruto_tn`, con la fecha en AAAA-MM-DD.
"""

import csv
import time
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path

from apps.reconocimiento import services
from apps.reconocimiento.dominio import CAMPOS, FECHA, PESO_BRUTO, PLACA


@dataclass
class Caso:
    archivo: str
    verdad: dict


@dataclass
class ResultadoMotor:
    motor: str
    version: str = "-"
    tickets: int = 0
    exitos: int = 0
    aciertos: dict = field(default_factory=lambda: {c: 0 for c in CAMPOS})
    errores_confiados: dict = field(default_factory=lambda: {c: 0 for c in CAMPOS})
    tiempos: list = field(default_factory=list)

    def exactitud(self, campo) -> float:
        return round(100 * self.aciertos[campo] / self.tickets, 1) if self.tickets else 0.0

    @property
    def exactitud_global(self) -> float:
        total = self.tickets * len(CAMPOS)
        return round(100 * sum(self.aciertos.values()) / total, 1) if total else 0.0

    @property
    def tiempo_medio(self) -> float:
        return round(sum(self.tiempos) / len(self.tiempos), 2) if self.tiempos else 0.0

    @property
    def tiempo_maximo(self) -> float:
        return round(max(self.tiempos), 2) if self.tiempos else 0.0


def leer_conjunto(carpeta: Path) -> list[Caso]:
    with open(carpeta / "verdad.csv", encoding="utf-8-sig") as f:
        filas = list(csv.DictReader(f, delimiter=";"))
    return [Caso(fila["archivo"], {PLACA: fila["placa"].strip().upper(), FECHA: fila["fecha"].strip(),
                                    PESO_BRUTO: _peso(fila["peso_bruto_tn"])})
            for fila in filas]


def _peso(texto: str) -> str:
    texto = texto.strip().replace(",", ".")
    return str(Decimal(texto)) if texto else ""


def _coincide(campo, leido, verdadero) -> bool:
    """Un campo sin valor verdadero —la placa escrita como nombre, una casilla
    tapada— es correcto solo si el motor tampoco propone valor (RN-M04-03)."""
    if not verdadero:
        return leido is None
    if leido is None:
        return False
    if campo == PESO_BRUTO:
        try:
            return Decimal(leido) == Decimal(verdadero)
        except Exception:
            return False
    return leido.strip().upper() == verdadero


def evaluar(motores: dict, carpeta: Path) -> list[ResultadoMotor]:
    """`motores`: {nombre: reconocedor}. Cada ticket pasa por el mismo servicio
    que usa el registro, con su tiempo de espera."""
    casos = leer_conjunto(carpeta)
    umbral = services.umbral_vigente()
    resultados = []
    for nombre, reconocedor in motores.items():
        r = ResultadoMotor(nombre)
        for caso in casos:
            imagen = (carpeta / caso.archivo).read_bytes()
            inicio = time.perf_counter()
            leido = services.reconocer(reconocedor, imagen)
            r.tiempos.append(time.perf_counter() - inicio)
            r.version = leido.version_motor
            r.tickets += 1
            r.exitos += int(leido.exito)
            for campo in CAMPOS:
                c = leido.campo(campo)
                if _coincide(campo, c.valor, caso.verdad[campo]):
                    r.aciertos[campo] += 1
                elif c.valor is not None and c.confianza is not None and Decimal(str(c.confianza)) >= umbral:
                    r.errores_confiados[campo] += 1
        resultados.append(r)
    return resultados


def informe(resultados: list[ResultadoMotor], carpeta: Path, tickets: int) -> str:
    umbral = services.umbral_vigente()
    lineas = [
        "# Informe del piloto de motores de reconocimiento",
        "",
        f"Conjunto: `{carpeta.name}`, {tickets} tickets, {tickets * len(CAMPOS)} lecturas. "
        f"Umbral de confianza: {umbral}.",
        "",
        "| Motor | Versión | Éxito | Placa | Fecha | Peso bruto | Global | Tiempo medio (s) | Tiempo máximo (s) |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in resultados:
        lineas.append(
            f"| {r.motor} | {r.version} | {r.exitos}/{r.tickets} | {r.exactitud(PLACA)} % | {r.exactitud(FECHA)} % "
            f"| {r.exactitud(PESO_BRUTO)} % | {r.exactitud_global} % | {r.tiempo_medio} | {r.tiempo_maximo} |"
        )
    lineas += [
        "",
        "## Utilidad del umbral",
        "",
        "Lecturas equivocadas con confianza igual o mayor que el umbral: no se habrían resaltado (notas de M04).",
        "",
        "| Motor | Placa | Fecha | Peso bruto |",
        "|---|---:|---:|---:|",
    ]
    for r in resultados:
        e = r.errores_confiados
        lineas.append(f"| {r.motor} | {e[PLACA]} | {e[FECHA]} | {e[PESO_BRUTO]} |")
    lineas += [
        "",
        "## Para completar a mano",
        "",
        "- Costo por ticket y dependencia de conexión de cada motor (D-12).",
        "- Motor elegido y su justificación; con él se cierran D-12 y, por el tiempo por ticket, D-15.",
    ]
    return "\n".join(lineas) + "\n"
