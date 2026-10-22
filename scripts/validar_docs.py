#!/usr/bin/env python3
"""Valida la coherencia interna de la documentación de docs/ y skills/.

Uso:
    python3 scripts/validar_docs.py

Complementa a verificar_migracion.sh, que busca conceptos del sistema anterior.
Este script comprueba que la documentación vigente sea coherente consigo misma:

1. Bloques Mermaid según CLAUDE.md: sin tildes, eñes ni signos de apertura, sin
   HTML, y sin paréntesis ni comas dentro de [ ] o { } en los diagramas de flujo.
2. Enlaces relativos de Markdown que apuntan a un archivo existente.
3. Referencias cruzadas definidas: HU, RU, RS, RNF, RN, S, A, D-nn y DR-nn.
4. Ningún indicador de la tesis citado en docs/modulos/ (fuera de los diagramas).
5. Índice de historias, matriz de trazabilidad y HU.md de cada módulo con las
   mismas historias, el mismo título y la misma prioridad, y la cabecera de
   cada HU.md con el número real de historias.

Termina con código 1 si encuentra algún problema.
"""

import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DOCS = RAIZ / "docs"
MODULOS = DOCS / "modulos"
EXCEPCION = "migracion:ok"

MERMAID = re.compile(r"```mermaid\n(.*?)```", re.S)
ACENTOS = re.compile(r"[áéíóúÁÉÍÓÚñÑ¿¡]")
ENLACE = re.compile(r"\]\(([^)#\s]+)(?:#[^)]*)?\)")
REFERENCIA = re.compile(r"\b((?:RNF|RN|RS|RU)-M\d\d-\d\d|HU-M\d\d-\d\d|[SA]-M\d\d-\d\d)\b")
INDICADOR = re.compile(r"\b(I[1-6]|ERA|TDI|SUS|TCA|RFC|CPS)\b")

problemas = []


def reportar(archivo, linea, mensaje):
    problemas.append(f"{archivo.relative_to(RAIZ)}:{linea}: {mensaje}")


def linea_de(texto, posicion):
    return texto.count("\n", 0, posicion) + 1


def archivos():
    yield from sorted(DOCS.rglob("*.md"))
    yield from sorted((RAIZ / "skills").rglob("*.md"))


def definiciones():
    """Códigos que algún documento define como fila de tabla o como título."""
    codigos = set()
    for f in MODULOS.rglob("*.md"):
        t = f.read_text(encoding="utf-8")
        codigos |= set(re.findall(r"^\| ((?:RNF|RN|RS|RU)-M\d\d-\d\d) \|", t, re.M))
        codigos |= set(re.findall(r"^## (HU-M\d\d-\d\d)", t, re.M))
        codigos |= set(re.findall(r"^## ([SA]-M\d\d-\d\d)", t, re.M))
    d = set(re.findall(r"\b(D-\d\d)\b", (DOCS / "00-arquitectura/decisiones_diseno.md").read_text(encoding="utf-8")))
    dr = set(re.findall(r"^\| (DR-\d\d) \|", (DOCS / "00-tesis/decisiones_reformulacion.md").read_text(encoding="utf-8"), re.M))
    return codigos, d, dr


def validar_mermaid(f, texto):
    for m in MERMAID.finditer(texto):
        bloque, inicio = m.group(1), linea_de(texto, m.start())
        if ACENTOS.search(bloque):
            reportar(f, inicio, "Mermaid con tildes, eñes o signos de apertura")
        if re.search(r"<(?!<)[a-zA-Z/]", re.sub(r"<<\w+>>", "", bloque)):
            reportar(f, inicio, "Mermaid con HTML")
        if re.match(r"\s*(erDiagram|classDiagram|sequenceDiagram)", bloque):
            continue
        for etiqueta in re.findall(r"\[([^\]]*)\]", bloque):
            interior = etiqueta.strip('"').strip("/").strip("(").strip(")")
            if re.search(r"[(),]", interior):
                reportar(f, inicio, f"Mermaid con paréntesis o coma dentro de [ ]: {etiqueta}")
        for etiqueta in re.findall(r"\{([^}]*)\}", bloque):
            if re.search(r"[(),]", etiqueta):
                reportar(f, inicio, f"Mermaid con paréntesis o coma dentro de {{ }}: {etiqueta}")


def validar_enlaces(f, texto):
    for m in ENLACE.finditer(texto):
        destino = m.group(1)
        if destino.startswith(("http://", "https://", "mailto:")):
            continue
        if not (f.parent / destino).resolve().exists():
            reportar(f, linea_de(texto, m.start()), f"enlace roto: {destino}")


def validar_referencias(f, texto, codigos, d, dr):
    for m in REFERENCIA.finditer(texto):
        if m.group(1) not in codigos:
            reportar(f, linea_de(texto, m.start()), f"referencia sin definir: {m.group(1)}")
    for m in re.finditer(r"\b(DR-\d\d)\b", texto):
        if m.group(1) not in dr:
            reportar(f, linea_de(texto, m.start()), f"decisión de reformulación sin definir: {m.group(1)}")
    for m in re.finditer(r"\b(D-\d\d)\b", texto):
        if m.group(1) not in d:
            reportar(f, linea_de(texto, m.start()), f"decisión de diseño sin definir: {m.group(1)}")


def validar_indicadores(f, texto):
    sin_diagramas = MERMAID.sub(lambda m: "\n" * m.group(0).count("\n"), texto)
    for numero, linea in enumerate(sin_diagramas.splitlines(), 1):
        if EXCEPCION in linea:
            continue
        for codigo in INDICADOR.findall(linea):
            reportar(f, numero, f"indicador de la tesis en un módulo: {codigo}")


def historias_de_modulos():
    historias = {}
    for f in sorted(MODULOS.glob("*/HU.md")):
        t = f.read_text(encoding="utf-8")
        partes = re.split(r"^## (HU-M\d\d-\d\d) — (.+)$", t, flags=re.M)
        encontradas = []
        for i in range(1, len(partes), 3):
            prioridad = re.search(r"\*\*Prioridad\*\* \| (\w+)", partes[i + 2])
            encontradas.append(partes[i])
            historias[partes[i]] = (partes[i + 1].strip(), prioridad.group(1) if prioridad else "")
        cabecera = re.search(r"\*\*Historias:\*\* (\d+)", t)
        if cabecera and int(cabecera.group(1)) != len(encontradas):
            reportar(f, 1, f"la cabecera declara {cabecera.group(1)} historias y hay {len(encontradas)}")
    return historias


def tabla_de_historias(f):
    filas = re.findall(r"^\| (HU-M\d\d-\d\d) \| ([^|]+?) \| [^|]+? \| (\w+) \|", f.read_text(encoding="utf-8"), re.M)
    return {hu: (titulo, prioridad) for hu, titulo, prioridad in filas}


def validar_historias():
    modulos = historias_de_modulos()
    for f in (DOCS / "HistoriasUsuario.md", DOCS / "02-trazabilidad/matriz_HU_RF_indicador.md"):
        tabla = tabla_de_historias(f)
        for hu in sorted(set(modulos) - set(tabla)):
            reportar(f, 0, f"falta {hu}, que existe en su HU.md")
        for hu in sorted(set(tabla) - set(modulos)):
            reportar(f, 0, f"{hu} no existe en ningún HU.md")
        for hu in sorted(set(modulos) & set(tabla)):
            titulo, prioridad = modulos[hu]
            if not tabla[hu][0].startswith(titulo):
                reportar(f, 0, f"{hu}: título distinto del de su HU.md")
            if tabla[hu][1] != prioridad:
                reportar(f, 0, f"{hu}: prioridad {tabla[hu][1]}, en su HU.md {prioridad}")


def main():
    codigos, d, dr = definiciones()
    for f in archivos():
        texto = f.read_text(encoding="utf-8")
        validar_mermaid(f, texto)
        validar_enlaces(f, texto)
        validar_referencias(f, texto, codigos, d, dr)
        if MODULOS in f.parents:
            validar_indicadores(f, texto)
    validar_historias()

    for p in problemas:
        print(p)
    if problemas:
        print(f"\n{len(problemas)} problema(s) en la documentación.")
        return 1
    print("OK: documentación coherente")
    return 0


if __name__ == "__main__":
    sys.exit(main())
