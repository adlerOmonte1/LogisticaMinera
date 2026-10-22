#!/usr/bin/env python3
"""Genera docs/INDICE.md: el inventario de la documentación y de las skills.

Uso:
    python3 scripts/indexar_docs.py

Una fila por archivo, agrupada por carpeta, con su título (primer encabezado de
nivel 1 o el `name` de una skill), su número de líneas y su tamaño. Los archivos
que no son Markdown (PDF, HTML) se listan con su tamaño. El índice se regenera,
no se edita a mano.
"""

import re
from collections import defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "docs" / "INDICE.md"
CARPETAS = ["docs", "skills", "Mockup", "scripts"]
IGNORAR = {"INDICE.md"}


def titulo(ruta):
    if ruta.suffix != ".md":
        return "—"
    texto = ruta.read_text(encoding="utf-8")
    nombre = re.search(r"^name:\s*(.+)$", texto, re.M)
    if ruta.name == "SKILL.md" and nombre:
        return f"Skill `{nombre.group(1).strip()}`"
    h1 = re.search(r"^# (.+)$", texto, re.M)
    return h1.group(1).strip() if h1 else "—"


def main():
    grupos = defaultdict(list)
    total_archivos = total_lineas = 0
    for carpeta in CARPETAS:
        for ruta in sorted((RAIZ / carpeta).rglob("*")):
            if not ruta.is_file() or ruta.name in IGNORAR or "__pycache__" in ruta.parts or ruta.name.startswith("_build"):
                continue
            rel = ruta.relative_to(RAIZ)
            texto = ruta.suffix in {".md", ".py", ".sh", ".html"}
            lineas = ruta.read_text(encoding="utf-8").count("\n") if texto else 0
            grupos[str(rel.parent)].append((rel, titulo(ruta), lineas, ruta.stat().st_size))
            total_archivos += 1
            total_lineas += lineas

    salida = [
        "# Índice de la documentación",
        "",
        "Generado por `scripts/indexar_docs.py`; no se edita a mano.",
        f"**{total_archivos} archivos · {total_lineas} líneas de texto.**",
        "",
    ]
    for carpeta in sorted(grupos):
        salida += [f"## `{carpeta}/`", "", "| Archivo | Título | Líneas | KB |", "|---|---|---:|---:|"]
        for rel, t, lineas, peso in grupos[carpeta]:
            enlace = Path("..") / rel if rel.parts[0] != "docs" else rel.relative_to("docs")
            salida.append(f"| [{rel.name}]({enlace.as_posix()}) | {t} | {lineas or '—'} | {peso // 1024} |")
        salida.append("")
    SALIDA.write_text("\n".join(salida), encoding="utf-8")
    print(f"{SALIDA.relative_to(RAIZ)}: {total_archivos} archivos")


if __name__ == "__main__":
    main()
