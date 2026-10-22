#!/usr/bin/env python3
"""Reporta qué reglas y criterios de aceptación tienen una prueba automatizada.

Uso:
    python3 scripts/reporte_trazabilidad.py [--estricto]

Recorre las pruebas de backend/ y lee el código que cada una declara en su
nombre, según PLAN_DE_TRABAJO.md §6.2: `test_rn_m03_04_...` verifica RN-M03-04
y `test_hu_m03_01_ca02_...` verifica el criterio CA02 de HU-M03-01. Lo contrasta
con las reglas y los criterios que definen los módulos de docs/modulos/.

Solo cuentan las pruebas de las apps del mapa de módulos. Las de apps del
alcance anterior (salidas, existencias, sincronizacion) se listan aparte: su
numeración antigua coincide con la vigente —HU-M04 era Salidas— y contarlas
inflaría la cobertura de módulos que todavía no tienen código.

El reporte tiene tres partes: cobertura por módulo, códigos que las pruebas
citan pero la documentación no define —pruebas de un diseño anterior o con el
código mal escrito— y reglas y criterios todavía sin prueba.

Sin opciones solo informa. Con --estricto termina con código 1 si alguna prueba
cita un código que la documentación no define.
"""

import re
import sys
from collections import defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
MODULOS = RAIZ / "docs" / "modulos"
BACKEND = RAIZ / "backend"

PRUEBA = re.compile(r"^\s*def (test_\w+)", re.M)
CODIGO_RN = re.compile(r"^test_rn_m(\d\d)_(\d\d)", re.I)
CODIGO_CA = re.compile(r"^test_hu_m(\d\d)_(\d\d)_ca(\d\d)", re.I)

# Apps del mapa de módulos (ARQ-02 §4); busqueda y reportes se renombran en la
# preparación del repositorio a consulta y consolidacion.
APPS_VIGENTES = {
    "accounts", "catalogo", "ingresos", "reconocimiento", "validacion", "trazabilidad",
    "consulta", "consolidacion", "auditoria", "busqueda", "reportes",
}


def definidos():
    """Reglas de negocio y criterios de aceptación de la documentación vigente."""
    codigos = {}
    for f in sorted(MODULOS.glob("M*/")):
        modulo = f.name[:3]
        rn = (f / "requerimientos" / "reglas_negocio.md").read_text(encoding="utf-8")
        for c in re.findall(r"^\| (RN-M\d\d-\d\d) \|", rn, re.M):
            codigos[c] = modulo
        hu = (f / "HU.md").read_text(encoding="utf-8")
        partes = re.split(r"^## (HU-M\d\d-\d\d) — .+$", hu, flags=re.M)
        for i in range(1, len(partes), 2):
            for ca in re.findall(r"\*\*(CA\d\d)\.\*\*", partes[i + 1]):
                codigos[f"{partes[i]} {ca}"] = modulo
    return codigos


def citados():
    """Código declarado en el nombre de cada prueba, con el archivo que la contiene."""
    pruebas = defaultdict(list)
    sin_codigo = 0
    fuera = defaultdict(int)
    for f in sorted(BACKEND.rglob("test_*.py")):
        partes = f.relative_to(BACKEND).parts
        if partes[0] == "apps" and partes[1] not in APPS_VIGENTES:
            fuera[partes[1]] += len(PRUEBA.findall(f.read_text(encoding="utf-8")))
            continue
        for nombre in PRUEBA.findall(f.read_text(encoding="utf-8")):
            rn, ca = CODIGO_RN.match(nombre), CODIGO_CA.match(nombre)
            if rn:
                codigo = f"RN-M{rn.group(1)}-{rn.group(2)}"
            elif ca:
                codigo = f"HU-M{ca.group(1)}-{ca.group(2)} CA{ca.group(3)}"
            else:
                sin_codigo += 1
                continue
            pruebas[codigo].append(str(f.relative_to(RAIZ)))
    return pruebas, sin_codigo, fuera


def main():
    estricto = "--estricto" in sys.argv[1:]
    codigos = definidos()
    pruebas, sin_codigo, fuera = citados()

    huerfanos = sorted(set(pruebas) - set(codigos))
    sin_prueba = sorted(set(codigos) - set(pruebas))

    salida = ["## Trazabilidad de las pruebas automatizadas", ""]
    salida += ["| Módulo | Reglas y criterios | Con prueba | Cobertura |", "|---|---:|---:|---:|"]
    por_modulo = defaultdict(lambda: [0, 0])
    for codigo, modulo in codigos.items():
        por_modulo[modulo][0] += 1
        por_modulo[modulo][1] += codigo in pruebas
    for modulo in sorted(por_modulo):
        total, cubiertos = por_modulo[modulo]
        salida.append(f"| {modulo} | {total} | {cubiertos} | {100 * cubiertos // total} % |")

    total_pruebas = sum(len(v) for v in pruebas.values())
    salida += ["", f"Pruebas que declaran un código: {total_pruebas}. Pruebas sin código en el nombre: {sin_codigo}.", ""]
    if fuera:
        detalle = ", ".join(f"`{app}` ({n})" for app, n in sorted(fuera.items()))
        salida += [f"Pruebas de apps fuera del mapa de módulos, no contadas: {detalle}. Se retiran en la "
                   "preparación del repositorio (`PLAN_DE_TRABAJO.md` §8).", ""]

    salida.append(f"### Códigos citados por pruebas y no definidos en docs/modulos ({len(huerfanos)})")
    salida.append("")
    salida += [f"- `{c}` — {', '.join(sorted(set(pruebas[c])))}" for c in huerfanos] or ["Ninguno."]
    salida += ["", f"### Reglas y criterios sin prueba ({len(sin_prueba)})", ""]
    salida.append(", ".join(f"`{c}`" for c in sin_prueba) or "Ninguno.")

    print("\n".join(salida))
    return 1 if estricto and huerfanos else 0


if __name__ == "__main__":
    sys.exit(main())
