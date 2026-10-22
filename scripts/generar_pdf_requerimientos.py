#!/usr/bin/env python3
"""Genera la especificacion de requerimientos y modelado del sistema en HTML listo para PDF.

Uso:
    python3 scripts/generar_pdf_requerimientos.py

Lee los archivos de requerimientos/ y diagramas/ de los nueve modulos, el marco y las
decisiones, y produce un HTML con los diagramas Mermaid renderizados en el navegador. La
conversion a PDF se hace despues con Chrome en modo headless; ver el final del archivo.

El documento no copia contenido: todo sale de docs/, de modo que regenerarlo basta para que
refleje el estado vigente del repositorio. Tambien comprueba que toda referencia citada
(RU, RS, RNF, RN, HU, S, A, CU, RF, V, D, DR) este definida en algun lugar del documento.
"""

import html
import re
import subprocess
import sys
import unicodedata
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import generar_pdf_hu as base  # noqa: E402  estilo y lector de Markdown compartidos

RAIZ = base.RAIZ
CODIGO_DOC = "SWI-ERS-01"
VERSION = "1.0"
MODULOS = list(base.NOMBRES_MODULO.keys())
MERMAID_CDN = "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"

ARCHIVOS_REQ = [
    ("usuario", "Requerimientos de usuario",
     "Necesidades expresadas por quienes operan el proceso, en su propio lenguaje."),
    ("sistema", "Requerimientos de sistema",
     "Traducción técnica de las necesidades: qué hace el sistema, con los nombres de campo que usa."),
    ("funcionales", "Requerimientos funcionales",
     "Funciones que el módulo expone, su endpoint, su responsabilidad, sus permisos y sus dependencias."),
    ("no_funcionales", "Requerimientos no funcionales",
     "Atributos de calidad según ISO/IEC 25010:2023, cada uno con su método de verificación."),
    ("reglas_negocio", "Reglas de negocio",
     "Invariantes del dominio y la consecuencia concreta de violarlas."),
]

# Codigos que se definen en el documento y a los que se puede enlazar.
PATRON_REF = re.compile(
    r"(?<![\w-])((?:RU|RS|RNF|RN|HU|FN|CU)-M\d{2}-\d{2}|CU-M\d{2}|[SA]-M\d{2}-\d{2}"
    r"|RF\d{2}|DR-\d{2}|D-\d{2}|V[1-5])(?![\w-])"
)
PATRON_DEF_TABLA = re.compile(r"^(?:RU|RS|RNF|RN)-M\d{2}-\d{2}$")

definidos = set()   # anclas existentes en el documento
anclados = set()    # anclas ya emitidas, para no duplicar id
citados = {}        # codigo -> lugares donde se cita
_lugar = ["preliminares"]


# --------------------------------------------------------------------------- enlaces

_en_linea_base = base.en_linea


def enlazar(fragmento_html):
    """Convierte en enlace interno cada codigo citado que exista en el documento."""
    def sustituir(m):
        cod = m.group(1)
        citados.setdefault(cod, set()).add(_lugar[0])
        if cod in definidos:
            return f'<a class="ref" href="#{cod}">{cod}</a>'
        return cod
    return PATRON_REF.sub(sustituir, fragmento_html)


def en_linea(texto):
    return enlazar(_en_linea_base(texto))


def celda_codigo(cod):
    """Celda que define un codigo: lo muestra como distintivo y fija su ancla."""
    ancla = ""
    if cod not in anclados:
        anclados.add(cod)
        ancla = f' id="{cod}"'
    return f'<td class="cod"{ancla}><span>{cod}</span></td>'


def tabla(lineas):
    filas = [[c.strip() for c in ln.strip().strip("|").split("|")] for ln in lineas]
    if len(filas) >= 2 and all(set(c) <= set("-: ") for c in filas[1]):
        cabecera, cuerpo = filas[0], filas[2:]
    else:
        cabecera, cuerpo = None, filas
    out = ["<table>"]
    if cabecera:
        out.append("<thead><tr>" + "".join(f"<th>{_en_linea_base(c)}</th>" for c in cabecera)
                   + "</tr></thead>")
    out.append("<tbody>")
    for fila in cuerpo:
        celdas = []
        for i, c in enumerate(fila):
            if i == 0 and PATRON_DEF_TABLA.match(c):
                celdas.append(celda_codigo(c))
            else:
                celdas.append(f"<td>{en_linea(c)}</td>")
        out.append("<tr>" + "".join(celdas) + "</tr>")
    out.append("</tbody></table>")
    return "\n".join(out)


# El lector de bloques del PDF de historias resuelve en tiempo de llamada estas dos funciones:
# sustituirlas hace que enlace los codigos y ancle las definiciones sin duplicar el lector.
base.en_linea = en_linea
base.tabla = tabla
bloques = base.bloques


# --------------------------------------------------------------------------- lectura


def leer(ruta):
    return ruta.read_text(encoding="utf-8") if ruta.exists() else ""


def sin_rutas(texto):
    """Sustituye rutas relativas del repositorio por el codigo del elemento que citan."""
    return re.sub(r"`(?:\.\./)+(M\d{2})-[a-z-]+/diagramas/caso_uso\.md`", r"el diagrama CU-\1", texto)


def sin_titulo(texto):
    """Quita el encabezado de nivel 1 y baja un nivel los de nivel 2."""
    texto = re.sub(r"\A# .+\n", "", sin_rutas(texto).lstrip())
    return re.sub(r"^## ", "### ", texto, flags=re.M)


def normalizar(t):
    t = unicodedata.normalize("NFD", t)
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", t).strip().lower()


def trozos(texto):
    """Separa texto y bloques Mermaid, en orden."""
    partes = re.split(r"```mermaid\n(.*?)```", texto, flags=re.S)
    return [("md" if i % 2 == 0 else "mermaid", p) for i, p in enumerate(partes)]


def leer_marco():
    marco = leer(RAIZ / "docs" / "00-tesis" / "marco_tesis.md")
    fila = lambda pat: [[c.strip() for c in m.group(0).strip().strip("|").split("|")]
                        for m in re.finditer(pat, marco, re.M)]
    return {
        "rf": fila(r"^\| RF\d{2} \|.+\|$"),
        "v": fila(r"^\| V[1-5] \|.+\|$"),
        "modulos": fila(r"^\| M0\d \|.+\|$"),
        "roles": fila(r"^\| (?:Administrador|Administrativo|Supervisor de planta) \|.+\|$"),
    }


def leer_decisiones():
    dd = leer(RAIZ / "docs" / "00-arquitectura" / "decisiones_diseno.md")
    d = []
    for m in re.finditer(r"^## (D-\d{2})\. (.+)$", dd, re.M):
        titulo = m.group(2)
        estado = "Pendiente" if "pendiente" in titulo.lower() else "Cerrada"
        titulo = re.sub(r"\s+—\s+\*.+\*$", "", titulo).replace("`", "")
        d.append((m.group(1), titulo, estado))
    d.sort()
    dr_txt = leer(RAIZ / "docs" / "00-tesis" / "decisiones_reformulacion.md")
    dr, vistos = [], set()
    for m in re.finditer(r"^\| (DR-\d{2}) \| ([^|]+) \|", dr_txt, re.M):
        if m.group(1) not in vistos:
            vistos.add(m.group(1))
            dr.append((m.group(1), m.group(2).strip()))
    return d, dr


def leer_modulo(slug):
    raiz = RAIZ / "docs" / "modulos" / slug
    cod = slug[:3]
    hu = base.leer_modulo(slug)
    historias = []
    for h in hu["historias"]:
        pri = re.search(r"\*\*Prioridad\*\*\s*\|\s*([^|]+)\|", h["cuerpo"])
        historias.append((h["id"], h["titulo"], pri.group(1).strip() if pri else ""))

    req = {}
    for clave, _, _ in ARCHIVOS_REQ:
        req[clave] = leer(raiz / "requerimientos" / f"{clave}.md")

    rf_linea = re.search(r"^\*\*RF asociad.*?(?=\n\n)", req["funcionales"], re.M | re.S)
    rf_linea = rf_linea.group(0).replace("\n", " ") if rf_linea else ""
    if rf_linea:
        req["funcionales"] = re.sub(r"^\*\*RF asociad.*?(?=\n\n)", "", req["funcionales"],
                                    count=1, flags=re.M | re.S)

    # Diagramas de secuencia y actividades: una seccion por codigo S- o A-.
    diagramas = {}
    for tipo in ("secuencia", "actividades"):
        texto = leer(raiz / "diagramas" / f"{tipo}.md")
        secciones = re.split(r"^## ", texto, flags=re.M)[1:]
        lista = []
        for sec in secciones:
            cab, _, cuerpo = sec.partition("\n")
            m = re.match(r"([SA]-M\d{2}-\d{2}) · (.+?)(?: \(([^()]*)\))?\s*$", cab)
            if not m:
                continue
            lista.append({"cod": m.group(1), "titulo": m.group(2), "refs": m.group(3) or "",
                          "cuerpo": cuerpo})
        diagramas[tipo] = lista

    # Casos de uso: el diagrama del modulo y su tabla, con codigo por caso.
    cu_txt = leer(raiz / "diagramas" / "caso_uso.md")
    cu_mermaid = re.search(r"```mermaid\n(.*?)```", cu_txt, re.S)
    cu_mermaid = cu_mermaid.group(1) if cu_mermaid else ""
    nodos = {normalizar(lbl): int(n) for n, lbl in re.findall(r'UC(\d+)\["([^"]+)"\]', cu_mermaid)}
    tabla_cu = re.search(r"^## Casos de uso\n\n((?:\|.*\n)+)", cu_txt, re.M)
    casos = []
    if tabla_cu:
        filas = [[c.strip() for c in ln.strip().strip("|").split("|")]
                 for ln in tabla_cu.group(1).strip().split("\n")][2:]
        usados = set()
        for i, f in enumerate(filas, 1):
            n = nodos.get(normalizar(f[0]))
            if n is None or n in usados:
                n = i
            usados.add(n)
            casos.append({"cod": f"{cod[0]}{cod[1:]}", "n": n, "fila": f,
                          "codigo": f"CU-{cod}-{n:02d}"})
    cu_despues = cu_txt[tabla_cu.end():] if tabla_cu else ""
    # Etiqueta cada nodo del diagrama con su codigo, para que la figura sea identificable.
    for n in {c["n"] for c in casos}:
        cu_mermaid = re.sub(rf'(UC{n}\[")', rf'\1CU-{cod}-{n:02d} · ', cu_mermaid, count=1)

    return {
        "slug": slug, "cod": cod, "nombre": base.NOMBRES_MODULO[slug],
        "historias": historias, "rf_linea": rf_linea, "req": req,
        "diagramas": diagramas, "cu_mermaid": cu_mermaid, "casos": casos,
        "cu_despues": cu_despues, "cu_cab": tabla_cu.group(1).split("\n")[0] if tabla_cu else "",
    }


def funciones_de(mod):
    """Filas de la tabla de funciones de funcionales.md, con su codigo FN asignado."""
    m = re.search(r"^(\| Función \|.*\n(?:\|.*\n)+)", mod["req"]["funcionales"], re.M)
    if not m:
        return None, []
    lineas = m.group(1).strip().split("\n")
    filas = [[c.strip() for c in ln.strip().strip("|").split("|")] for ln in lineas[2:]]
    return m, [(f"FN-{mod['cod']}-{i:02d}", f) for i, f in enumerate(filas, 1)]


def contar(mod):
    def filas(clave, pref):
        return len(set(re.findall(rf"^\| ({pref}-{mod['cod']}-\d{{2}}) \|", mod["req"][clave], re.M)))
    return {
        "HU": len(mod["historias"]),
        "RU": filas("usuario", "RU"),
        "RS": filas("sistema", "RS"),
        "FN": len(funciones_de(mod)[1]),
        "RNF": filas("no_funcionales", "RNF"),
        "RN": filas("reglas_negocio", "RN"),
        "CU": len(mod["casos"]),
        "S": len(mod["diagramas"]["secuencia"]),
        "A": len(mod["diagramas"]["actividades"]),
    }


duplicados = []  # codigos definidos dos veces en la tabla principal de un archivo


def registrar_definiciones(modulos, marco, decisiones, reformulacion):
    for f in marco["rf"]:
        definidos.add(f[0])
    for f in marco["v"]:
        definidos.add(f[0])
    for d in decisiones:
        definidos.add(d[0])
    for d in reformulacion:
        definidos.add(d[0])
    for mod in modulos:
        definidos.add(mod["cod"])
        for h in mod["historias"]:
            definidos.add(h[0])
        for clave, _, _ in ARCHIVOS_REQ:
            codigos = re.findall(r"^\| ((?:RU|RS|RNF|RN)-M\d{2}-\d{2}) \|", mod["req"][clave], re.M)
            definidos.update(codigos)
            if clave != "usuario":  # usuario.md repite sus codigos en el contexto del diagnostico
                duplicados.extend(sorted({c for c in codigos if codigos.count(c) > 1}))
        for cod, _ in funciones_de(mod)[1]:
            definidos.add(cod)
        definidos.add(f"CU-{mod['cod']}")
        for c in mod["casos"]:
            definidos.add(c["codigo"])
        for tipo in ("secuencia", "actividades"):
            for d in mod["diagramas"][tipo]:
                definidos.add(d["cod"])


# --------------------------------------------------------------------------- render


def figura(cod, titulo, tipo, refs, mermaid, pie=""):
    refs_html = f'<div class="fig-refs">Referencias: {en_linea(refs)}</div>' if refs else ""
    anclados.add(cod)
    return (
        f'<div class="fig" id="{cod}">'
        f'<div class="fig-cab"><span class="fig-cod">{cod}</span>'
        f'<span class="fig-tipo">{tipo}</span></div>'
        f'<div class="fig-tit">{html.escape(titulo)}</div>{refs_html}'
        f'<div class="fig-lienzo"><pre class="mermaid">{html.escape(mermaid.strip())}</pre></div>'
        f'<div class="fig-pie">Figura {cod}. {html.escape(titulo)}.</div>'
        f'{pie}</div>'
    )


def subtitulo(num, texto, ancla, salto=False):
    clase = ' class="sub salto"' if salto else ' class="sub"'
    return f'<h3{clase} id="{ancla}"><span class="sub-num">{num}</span>{texto}</h3>'


def render_funcionales(mod):
    texto = mod["req"]["funcionales"]
    m, funciones = funciones_de(mod)
    if not m:
        return bloques(sin_titulo(texto))
    antes, despues = texto[:m.start()], texto[m.end():]
    filas = []
    for cod, f in funciones:
        filas.append("<tr>" + celda_codigo(cod) + "".join(f"<td>{en_linea(c)}</td>" for c in f) + "</tr>")
    cab = [c.strip() for c in m.group(1).split("\n")[0].strip().strip("|").split("|")]
    tabla_html = ('<table class="fn"><thead><tr><th>Código</th>'
                  + "".join(f"<th>{html.escape(c)}</th>" for c in cab)
                  + "</tr></thead><tbody>" + "\n".join(filas) + "</tbody></table>")
    return bloques(sin_titulo(antes)) + tabla_html + bloques(sin_titulo(despues))


def render_cu(mod):
    cod = mod["cod"]
    partes = [figura(f"CU-{cod}", f"Diagrama de casos de uso — {mod['nombre'].split(' · ')[1]}",
                     "Casos de uso", "", mod["cu_mermaid"])]
    if mod["casos"]:
        cab = [c.strip() for c in mod["cu_cab"].strip().strip("|").split("|")]
        filas = []
        for c in sorted(mod["casos"], key=lambda x: x["n"]):
            filas.append("<tr>" + celda_codigo(c["codigo"])
                         + "".join(f"<td>{en_linea(x)}</td>" for x in c["fila"]) + "</tr>")
        partes.append('<h4>Especificación de los casos de uso</h4>')
        partes.append('<table class="cu"><thead><tr><th>Código</th>'
                      + "".join(f"<th>{html.escape(x)}</th>" for x in cab)
                      + "</tr></thead><tbody>" + "\n".join(filas) + "</tbody></table>")
    resto = sin_rutas(re.sub(r"^## .+\n", "", mod["cu_despues"], flags=re.M))
    partes.append(bloques(resto))
    return "\n".join(partes)


def render_diagramas(mod, tipo, nombre_tipo):
    partes = []
    for d in mod["diagramas"][tipo]:
        mermaid, texto = "", []
        for clase, contenido in trozos(d["cuerpo"]):
            if clase == "mermaid" and not mermaid:
                mermaid = contenido
            elif clase == "md":
                texto.append(contenido)
        pie = bloques(sin_rutas("\n".join(texto))) if "".join(texto).strip() else ""
        if pie:
            pie = f'<div class="fig-nota">{pie}</div>'
        partes.append(figura(d["cod"], d["titulo"], nombre_tipo, d["refs"], mermaid, pie))
    return "\n".join(partes)


def render_modulo(mod, marco_mod):
    cod = mod["cod"]
    _lugar[0] = cod
    n = contar(mod)
    resp = next((f[2] for f in marco_mod if f[0] == cod), "")
    anclados.add(cod)

    hu_filas = "".join(
        f'<tr>{celda_codigo(h[0])}<td>{html.escape(h[1])}</td><td>{html.escape(h[2])}</td></tr>'
        for h in mod["historias"])
    rf = en_linea(re.sub(r"^\*\*RF asociad[oa]s?:\*\*\s*", "", mod["rf_linea"]))
    contenido = " · ".join(f"{v} {k}" for k, v in n.items() if v)

    out = [f'<div class="seccion" id="{cod}"><h2 class="seccion-tit">'
           f'<span class="num">{cod[1:]}</span>{html.escape(mod["nombre"])}</h2>']
    out.append('<table class="ficha"><tbody>'
               f'<tr><th>Código del módulo</th><td>{cod}</td></tr>'
               f'<tr><th>Responsabilidad</th><td>{html.escape(resp)}</td></tr>'
               f'<tr><th>Requerimientos funcionales</th><td>{rf}</td></tr>'
               f'<tr><th>Contenido</th><td>{contenido}</td></tr>'
               '</tbody></table>')
    out.append('<div class="rotulo">Historias de usuario del módulo</div>')
    out.append('<table class="hu-lista"><thead><tr><th>Código</th><th>Historia</th>'
               f'<th>Prioridad</th></tr></thead><tbody>{hu_filas}</tbody></table>')
    out.append('<p class="pendiente">La especificación completa de cada historia está en el '
               'documento de historias de usuario.</p>')

    for i, (clave, titulo, intro) in enumerate(ARCHIVOS_REQ, 1):
        out.append(subtitulo(f"{cod}.{i}", titulo, f"{cod}-{i}"))
        out.append(f'<p class="intro-sub">{intro}</p>')
        if clave == "funcionales":
            out.append(render_funcionales(mod))
        else:
            out.append(bloques(sin_titulo(mod["req"][clave])))

    out.append(subtitulo(f"{cod}.6", "Modelo de casos de uso", f"{cod}-6", salto=True))
    out.append(render_cu(mod))
    if mod["diagramas"]["secuencia"]:
        out.append(subtitulo(f"{cod}.7", "Diagramas de secuencia", f"{cod}-7", salto=True))
        out.append(render_diagramas(mod, "secuencia", "Secuencia"))
    if mod["diagramas"]["actividades"]:
        out.append(subtitulo(f"{cod}.8", "Diagramas de actividades", f"{cod}-8", salto=True))
        out.append(render_diagramas(mod, "actividades", "Actividades"))
    out.append("</div>")
    return "\n".join(out)


# --------------------------------------------------------------------------- secciones fijas


def portada(hoy):
    return f"""
<div class="portada">
  <div class="barra"></div>
  <div class="kicker">Especificación de requerimientos · {CODIGO_DOC}</div>
  <h1>Requerimientos y modelado del sistema web inteligente para el control de inventarios de ingreso de mineral</h1>
  <div class="sub">Requerimientos de usuario, de sistema, funcionales y no funcionales, reglas de
  negocio y diagramas de casos de uso, secuencia y actividades de los nueve módulos del sistema.</div>
  <div class="pie">
    <div><span class="et">Organización</span>Construcción y Minería<br>Planta de Pillcomarca — Huánuco</div>
    <div><span class="et">Documento</span>{CODIGO_DOC}<br>Versión {VERSION}</div>
    <div><span class="et">Fecha</span>{hoy}</div>
  </div>
</div>"""


def control(hoy, commit, totales):
    return f"""
<div class="seccion" id="control">
<h2 class="seccion-tit"><span class="num">I</span>Control del documento</h2>
<table class="ficha"><tbody>
<tr><th>Código</th><td>{CODIGO_DOC}</td></tr>
<tr><th>Título</th><td>Requerimientos y modelado del sistema</td></tr>
<tr><th>Sistema</th><td>Sistema web inteligente para el control de inventarios de ingreso de mineral</td></tr>
<tr><th>Organización</th><td>Construcción y Minería — Planta de procesamiento de Pillcomarca, Huánuco</td></tr>
<tr><th>Versión</th><td>{VERSION}</td></tr>
<tr><th>Estado</th><td>Vigente</td></tr>
<tr><th>Fecha de emisión</th><td>{hoy}</td></tr>
<tr><th>Origen</th><td>Generado desde el repositorio del proyecto, rama <code>docs/reformulacion/sistema-inteligente</code>, revisión <code>{commit}</code></td></tr>
<tr><th>Documento relacionado</th><td>Especificación de historias de usuario (<code>Historias_de_Usuario.pdf</code>)</td></tr>
</tbody></table>

<div class="rotulo">Historial de versiones</div>
<table><thead><tr><th style="width:18mm">Versión</th><th style="width:26mm">Fecha</th><th>Descripción del cambio</th></tr></thead>
<tbody><tr><td>{VERSION}</td><td>{hoy}</td><td>Emisión inicial: {totales}.</td></tr></tbody></table>

<div class="rotulo">Contenido</div>
{{INDICE}}
</div>"""


def indice(modulos):
    filas = [
        ("I", "Control del documento", "control"),
        ("II", "Introducción y sistema de codificación", "intro"),
        ("III", "Visión general del sistema", "vision"),
    ]
    out = ['<table class="toc"><tbody>']
    for num, tit, ancla in filas:
        out.append(f'<tr class="toc-cap"><td>{num}</td><td><a href="#{ancla}">{tit}</a></td></tr>')
    for mod in modulos:
        cod = mod["cod"]
        out.append(f'<tr class="toc-cap"><td>{cod}</td><td><a href="#{cod}">'
                   f'{html.escape(mod["nombre"].split(" · ")[1])}</a></td></tr>')
        subs = [(i, t) for i, (_, t, _) in enumerate(ARCHIVOS_REQ, 1)] + [(6, "Modelo de casos de uso")]
        if mod["diagramas"]["secuencia"]:
            subs.append((7, "Diagramas de secuencia"))
        if mod["diagramas"]["actividades"]:
            subs.append((8, "Diagramas de actividades"))
        enlaces = " · ".join(f'<a href="#{cod}-{i}">{cod}.{i}</a> {t}' for i, t in subs)
        out.append(f'<tr class="toc-sub"><td></td><td>{enlaces}</td></tr>')
    for num, tit, ancla in [("A", "Reglas de validación y decisiones citadas", "anexo-a"),
                            ("B", "Índice de figuras", "anexo-b"),
                            ("C", "Trazabilidad de las historias de usuario", "anexo-c")]:
        out.append(f'<tr class="toc-cap"><td>Anexo {num}</td><td><a href="#{ancla}">{tit}</a></td></tr>')
    out.append("</tbody></table>")
    return "\n".join(out)


CADENA = """flowchart LR
    RU[Requerimiento de usuario RU] -->|deriva en| RS[Requerimiento de sistema RS]
    RS -->|se expone como| FN[Funcion FN]
    HU[Historia de usuario HU] -->|se realiza con| FN
    FN -->|cumple| RF[Requerimiento funcional RF]
    RN[Regla de negocio RN] -->|restringe| FN
    RNF[Requerimiento no funcional RNF] -->|condiciona| FN
    CU[Caso de uso CU] -->|modela| HU
    SA[Diagramas S y A] -->|detallan| HU"""


def introduccion():
    _lugar[0] = "introducción"
    filas = [
        ("Requerimiento funcional", "RF{nn}", "RF03", "Global, lista de control del sistema", "Visión general, sección III"),
        ("Historia de usuario", "HU-M{mm}-{nn}", "HU-M03-04", "Módulo", "Ficha de cada módulo"),
        ("Criterio de aceptación", "CA{nn}", "CA05", "Dentro de una historia", "Documento de historias de usuario"),
        ("Requerimiento de usuario", "RU-M{mm}-{nn}", "RU-M02-05", "Módulo", "Sección M{mm}.1"),
        ("Requerimiento de sistema", "RS-M{mm}-{nn}", "RS-M03-17", "Módulo", "Sección M{mm}.2"),
        ("Función del módulo", "FN-M{mm}-{nn}", "FN-M03-04", "Módulo; asignado en este documento según el orden de la tabla de funciones", "Sección M{mm}.3"),
        ("Requerimiento no funcional", "RNF-M{mm}-{nn}", "RNF-M05-01", "Módulo; clasificado según ISO/IEC 25010:2023", "Sección M{mm}.4"),
        ("Regla de negocio", "RN-M{mm}-{nn}", "RN-M03-17", "Módulo", "Sección M{mm}.5"),
        ("Regla de validación del ticket", "V{n}", "V1", "Global, cinco reglas", "Anexo A"),
        ("Diagrama de casos de uso", "CU-M{mm}", "CU-M03", "Uno por módulo", "Sección M{mm}.6"),
        ("Caso de uso", "CU-M{mm}-{nn}", "CU-M03-06", "Módulo; el número coincide con el nodo UC{n} del diagrama", "Sección M{mm}.6"),
        ("Diagrama de secuencia", "S-M{mm}-{nn}", "S-M03-04", "Módulo", "Sección M{mm}.7"),
        ("Diagrama de actividades", "A-M{mm}-{nn}", "A-M03-04", "Módulo", "Sección M{mm}.8"),
        ("Decisión de diseño", "D-{nn}", "D-17", "Global", "Anexo A"),
        ("Decisión de reformulación", "DR-{nn}", "DR-10", "Global", "Anexo A"),
    ]
    cuerpo = "".join(
        f"<tr><td><strong>{a}</strong></td><td><code>{b}</code></td><td>{en_linea(c)}</td>"
        f"<td>{d}</td><td>{e}</td></tr>" for a, b, c, d, e in filas)
    return f"""
<div class="seccion" id="intro">
<h2 class="seccion-tit"><span class="num">II</span>Introducción y sistema de codificación</h2>
<h3>Propósito</h3>
<p>Este documento especifica los requerimientos del sistema web inteligente para el control de
inventarios de ingreso de mineral y los modela mediante diagramas de casos de uso, de secuencia y
de actividades. Complementa la especificación de historias de usuario: las historias fijan qué
necesita cada rol; este documento fija cómo el sistema lo satisface, qué reglas respeta y con qué
atributos de calidad.</p>
<h3>Alcance</h3>
<p>Comprende los nueve módulos del sistema, de M01 a M09. Cada módulo se presenta con la misma
estructura de ocho secciones: requerimientos de usuario, de sistema, funcionales y no funcionales,
reglas de negocio, modelo de casos de uso, diagramas de secuencia y diagramas de actividades. Las
notas de implementación, propias del equipo de desarrollo, no forman parte de este documento.</p>
<h3>Sistema de codificación</h3>
<p>Todo elemento del documento lleva un código único que permite citarlo sin ambigüedad. El código
indica el tipo de elemento y el módulo al que pertenece; el correlativo es estable, de modo que un
elemento retirado no libera su número. En la versión digital, cada código citado es un enlace a su
definición.</p>
<table class="codif"><thead><tr><th>Elemento</th><th>Formato</th><th>Ejemplo</th><th>Alcance</th><th>Dónde se define</th></tr></thead>
<tbody>{cuerpo}</tbody></table>
<p class="pendiente">{{mm}} es el número de módulo y {{nn}} el correlativo dentro de él.</p>
<h3>Relación entre los elementos</h3>
<p>Los requerimientos no son listas independientes: cada uno se apoya en otro y la cadena permite
recorrer el sistema desde la necesidad hasta la función que la satisface.</p>
{figura("F-00", "Relación entre los elementos codificados", "Modelo", "", CADENA)}
</div>"""


def vision(modulos, marco):
    _lugar[0] = "visión general"
    rf_mod = {}
    for f in marco["modulos"]:
        for c in re.findall(r"RF\d{2}", f[3]):
            rf_mod.setdefault(c, []).append(f[0])
    rf_filas = "".join(
        f"<tr>{celda_codigo_global(f[0])}<td>{html.escape(f[1])}</td>"
        f"<td>{en_linea(', '.join(rf_mod.get(f[0], [])))}</td></tr>" for f in marco["rf"])
    mod_filas = "".join(
        f'<tr><td class="cod"><span><a class="ref" href="#{f[0]}">{f[0]}</a></span></td>'
        f"<td><strong>{html.escape(f[1])}</strong></td><td>{html.escape(f[2])}</td>"
        f"<td>{en_linea(f[3])}</td></tr>" for f in marco["modulos"])
    rol_filas = "".join(f"<tr><td><strong>{html.escape(f[0])}</strong></td><td>{html.escape(f[1])}</td></tr>"
                        for f in marco["roles"])
    claves = ["HU", "RU", "RS", "FN", "RNF", "RN", "CU", "S", "A"]
    tot = {k: 0 for k in claves}
    filas = []
    for mod in modulos:
        n = contar(mod)
        for k in claves:
            tot[k] += n[k]
        filas.append(f'<tr><td><a class="ref" href="#{mod["cod"]}">{mod["cod"]}</a></td>'
                     + "".join(f"<td class='num'>{n[k]}</td>" for k in claves) + "</tr>")
    filas.append("<tr class='total'><td>Total</td>"
                 + "".join(f"<td class='num'>{tot[k]}</td>" for k in claves) + "</tr>")
    cab = "".join(f"<th class='num'>{k}</th>" for k in claves)
    return f"""
<div class="seccion" id="vision">
<h2 class="seccion-tit"><span class="num">III</span>Visión general del sistema</h2>
<h3>Requerimientos funcionales del sistema</h3>
<p>Los requerimientos funcionales son globales: constituyen la lista de control del sistema y cada
uno tiene un módulo principal responsable.</p>
<table><thead><tr><th style="width:18mm">Código</th><th>Requerimiento funcional</th><th style="width:30mm">Módulo</th></tr></thead>
<tbody>{rf_filas}</tbody></table>
<h3>Módulos del sistema</h3>
<p>Cada módulo existe por una responsabilidad del dominio y se desarrolla en su propio capítulo.</p>
<table><thead><tr><th style="width:15mm">Código</th><th style="width:44mm">Módulo</th><th>Responsabilidad</th><th style="width:30mm">RF</th></tr></thead>
<tbody>{mod_filas}</tbody></table>
<h3>Roles del sistema</h3>
<table><thead><tr><th style="width:44mm">Rol</th><th>Alcance</th></tr></thead><tbody>{rol_filas}</tbody></table>
<h3>Resumen cuantitativo</h3>
<p>Elementos especificados por módulo, según el sistema de codificación de la sección II.</p>
<table class="resumen"><thead><tr><th>Módulo</th>{cab}</tr></thead><tbody>{''.join(filas)}</tbody></table>
</div>""", tot


def celda_codigo_global(cod):
    return celda_codigo(cod)


def anexo_a(marco, decisiones, reformulacion):
    _lugar[0] = "anexo A"
    v = "".join(f"<tr>{celda_codigo(f[0])}<td>{html.escape(f[1])}</td><td>{html.escape(f[2])}</td></tr>"
                for f in marco["v"])
    d = "".join(f"<tr>{celda_codigo(c)}<td>{html.escape(t)}</td><td>{e}</td></tr>" for c, t, e in decisiones)
    dr = "".join(f"<tr>{celda_codigo(c)}<td>{html.escape(t)}</td></tr>" for c, t in reformulacion)
    return f"""
<div class="seccion" id="anexo-a">
<h2 class="seccion-tit"><span class="num">A</span>Reglas de validación y decisiones citadas</h2>
<h3>Reglas de validación del ticket</h3>
<p>Las aplica el módulo M05 en el servidor sobre los datos propuestos, sobre los confirmados y, en el
primer viaje de un vehículo, al registrar el destare.</p>
<table><thead><tr><th style="width:16mm">Código</th><th>Inconsistencia</th><th style="width:34mm">Efecto</th></tr></thead><tbody>{v}</tbody></table>
<h3>Decisiones de diseño</h3>
<table><thead><tr><th style="width:16mm">Código</th><th>Decisión</th><th style="width:22mm">Estado</th></tr></thead><tbody>{d}</tbody></table>
<h3>Decisiones de reformulación</h3>
<table><thead><tr><th style="width:16mm">Código</th><th>Asunto</th></tr></thead><tbody>{dr}</tbody></table>
</div>"""


def anexo_b(modulos):
    filas = []
    for mod in modulos:
        filas.append(f'<tr><td colspan="3" class="grupo">{html.escape(mod["nombre"])}</td></tr>')
        filas.append(f'<tr><td><a class="ref" href="#CU-{mod["cod"]}">CU-{mod["cod"]}</a></td>'
                     f'<td>Diagrama de casos de uso</td><td>Casos de uso</td></tr>')
        for tipo, nombre in (("secuencia", "Secuencia"), ("actividades", "Actividades")):
            for d in mod["diagramas"][tipo]:
                filas.append(f'<tr><td><a class="ref" href="#{d["cod"]}">{d["cod"]}</a></td>'
                             f'<td>{html.escape(d["titulo"])}</td><td>{nombre}</td></tr>')
    return f"""
<div class="seccion" id="anexo-b">
<h2 class="seccion-tit"><span class="num">B</span>Índice de figuras</h2>
<table class="figs"><thead><tr><th style="width:22mm">Código</th><th>Título</th><th style="width:26mm">Tipo</th></tr></thead>
<tbody>{''.join(filas)}</tbody></table>
</div>"""


def anexo_c(modulos):
    _lugar[0] = "anexo C"
    filas = []
    for mod in modulos:
        _, funciones = funciones_de(mod)
        filas.append(f'<tr><td colspan="4" class="grupo">{html.escape(mod["nombre"])}</td></tr>')
        for hu, titulo, _ in mod["historias"]:
            fn = [c for c, f in funciones if hu in " ".join(f)]
            cu = [c["codigo"] for c in mod["casos"] if hu in " ".join(c["fila"])]
            dg = []
            for m2 in modulos:
                for tipo in ("secuencia", "actividades"):
                    dg += [d["cod"] for d in m2["diagramas"][tipo] if hu in d["refs"]]
            filas.append(
                f'<tr><td><a class="ref" href="#{hu}">{hu}</a><div class="tenue">{html.escape(titulo)}</div></td>'
                f'<td>{enlazar(", ".join(sorted(fn))) or "—"}</td><td>{enlazar(", ".join(sorted(cu))) or "—"}</td>'
                f'<td>{enlazar(", ".join(sorted(dg))) or "—"}</td></tr>')
    return f"""
<div class="seccion" id="anexo-c">
<h2 class="seccion-tit"><span class="num">C</span>Trazabilidad de las historias de usuario</h2>
<p>Para cada historia de usuario, las funciones que la realizan, los casos de uso que la representan y
los diagramas de secuencia y de actividades que la detallan. Los diagramas de actividades suelen
referirse a reglas de negocio y no a historias; por eso aparecen aquí solo cuando la citan.</p>
<table class="traza"><thead><tr><th style="width:52mm">Historia de usuario</th><th>Funciones</th>
<th>Casos de uso</th><th>Diagramas</th></tr></thead><tbody>{''.join(filas)}</tbody></table>
</div>"""


ESTILO_EXTRA = f"""
@page {{
  size: A4; margin: 21mm 15mm 19mm 15mm;
  @top-left {{ content: "{CODIGO_DOC} · Requerimientos y modelado del sistema"; font: 7.4pt "Helvetica Neue", Helvetica, Arial; color: #8A7A70; vertical-align: bottom; padding-bottom: 3mm; }}
  @top-right {{ content: "Versión {VERSION}"; font: 7.4pt "Helvetica Neue", Helvetica, Arial; color: #8A7A70; vertical-align: bottom; padding-bottom: 3mm; }}
  @bottom-left {{ content: "Construcción y Minería — Planta de Pillcomarca"; font: 7.4pt "Helvetica Neue", Helvetica, Arial; color: #8A7A70; vertical-align: top; padding-top: 3mm; }}
  @bottom-right {{ content: "Página " counter(page) " de " counter(pages); font: 7.4pt "Helvetica Neue", Helvetica, Arial; color: #4A342A; vertical-align: top; padding-top: 3mm; }}
}}
@page :first {{
  margin: 0;
  @top-left {{ content: none; }} @top-right {{ content: none; }}
  @bottom-left {{ content: none; }} @bottom-right {{ content: none; }}
}}
.portada h1 {{ font-size: 24pt; }}
a.ref {{ color: var(--marron-medio); text-decoration: none; border-bottom: .5pt dotted var(--mostaza); white-space: nowrap; }}
code {{ white-space: nowrap; }}
td.cod {{ white-space: nowrap; width: 1%; }}
td.cod span {{ display: inline-block; font-size: 7.8pt; font-weight: 700; letter-spacing: .03em;
  color: var(--marron); background: var(--mostaza-palido); border: .5pt solid var(--mostaza-claro);
  padding: .6mm 1.6mm; border-radius: 1mm; }}
td.cod span a.ref {{ border: 0; color: var(--marron); }}
table.ficha th {{ width: 46mm; background: var(--marron-palido); color: var(--marron); font-size: 8.6pt; }}
table.ficha td {{ background: #fff !important; }}
h3.sub {{ font-size: 12.4pt; color: var(--marron); margin: 8mm 0 1.5mm; padding-bottom: 1.6mm;
  border-bottom: .8pt solid var(--linea); }}
h3.sub.salto {{ page-break-before: always; margin-top: 0; }}
h3.sub .sub-num {{ display: inline-block; font-size: 8.6pt; font-weight: 700; color: #fff;
  background: var(--marron); padding: .8mm 2.2mm; border-radius: 1mm; margin-right: 3mm; vertical-align: 1.5px; }}
.intro-sub {{ color: var(--tinta-suave); font-style: italic; font-size: 9pt; margin-bottom: 3.5mm; }}
table {{ page-break-inside: auto; }}
tr {{ page-break-inside: avoid; }}
thead {{ display: table-header-group; }}
.fig {{ margin: 4mm 0 8mm; page-break-inside: avoid; border: .5pt solid var(--linea); border-radius: 1.5mm; }}
.fig-cab {{ display: flex; justify-content: space-between; align-items: center;
  background: var(--marron); padding: 1.8mm 3.5mm; border-radius: 1.5mm 1.5mm 0 0; }}
.fig-cod {{ font-weight: 700; color: var(--mostaza-claro); letter-spacing: .08em; font-size: 9pt; }}
.fig-tipo {{ color: #E9DDD2; font-size: 7.6pt; letter-spacing: .14em; text-transform: uppercase; }}
.fig-tit {{ padding: 2.6mm 3.5mm 0; font-weight: 700; color: var(--marron); font-size: 10.6pt; }}
.fig-refs {{ padding: .8mm 3.5mm 0; font-size: 8.2pt; color: var(--tinta-suave); }}
.fig-lienzo {{ padding: 2mm 3mm; text-align: center; }}
.fig-lienzo pre.mermaid {{ margin: 0; background: none; font-size: 0; }}
.fig-lienzo svg {{ max-width: 100% !important; max-height: 222mm; height: auto; }}
.fig-lienzo svg p, .fig-lienzo svg div, .fig-lienzo svg span {{ text-align: center !important; margin: 0; line-height: 1.25; }}
.fig-pie {{ border-top: .5pt solid var(--linea); padding: 1.8mm 3.5mm; font-size: 8pt; color: var(--tinta-suave);
  font-style: italic; background: var(--crema); }}
.fig-nota {{ padding: 2.5mm 3.5mm 1mm; font-size: 9pt; border-top: .5pt solid var(--linea); }}
table.toc td {{ padding: 1.3mm 2.2mm; border-bottom: .3pt solid var(--linea); background: #fff !important; }}
table.toc tr.toc-cap td {{ font-weight: 700; color: var(--marron); padding-top: 2.2mm; }}
table.toc tr.toc-cap td:first-child {{ width: 20mm; color: var(--mostaza); }}
table.toc tr.toc-sub td {{ font-size: 8pt; color: var(--tinta-suave); border-bottom: 0; padding-top: 0; }}
table.toc a {{ color: inherit; text-decoration: none; }}
table.toc tr.toc-sub a {{ color: var(--marron-medio); font-weight: 700; }}
table.resumen td.num, table.resumen th.num {{ text-align: center; }}
table.resumen tr.total td {{ font-weight: 700; background: var(--mostaza-palido) !important; color: var(--marron); }}
td.grupo {{ background: var(--marron-palido) !important; font-weight: 700; color: var(--marron); }}
.tenue {{ font-size: 8pt; color: var(--tinta-suave); }}
table.codif td {{ font-size: 8.4pt; }}
"""

MERMAID_JS = """
<script src="%s"></script>
<script>
mermaid.initialize({
  startOnLoad: false, theme: 'base', securityLevel: 'loose',
  fontFamily: '"Helvetica Neue", Helvetica, Arial, sans-serif',
  themeVariables: {
    primaryColor: '#FBF1D9', primaryBorderColor: '#C08A1E', primaryTextColor: '#2B2320',
    secondaryColor: '#F3EBE4', tertiaryColor: '#FDFAF4', lineColor: '#7A5540', fontSize: '15px',
    actorBkg: '#FBF1D9', actorBorder: '#C08A1E', actorTextColor: '#4A342A', actorLineColor: '#B9A99C',
    signalColor: '#4A342A', signalTextColor: '#2B2320', labelBoxBkgColor: '#FBF1D9',
    labelBoxBorderColor: '#C08A1E', labelTextColor: '#4A342A', loopTextColor: '#4A342A',
    noteBkgColor: '#FBF1D9', noteBorderColor: '#C08A1E', noteTextColor: '#2B2320',
    activationBkgColor: '#E8C766', activationBorderColor: '#C08A1E',
    edgeLabelBackground: '#FFFFFF', clusterBkg: '#FDFAF4', clusterBorder: '#DCCFC2'
  },
  flowchart: { htmlLabels: true, curve: 'basis', useMaxWidth: true, padding: 8, rankSpacing: 26, nodeSpacing: 28, diagramPadding: 4, wrappingWidth: 170 },
  sequence: { useMaxWidth: true, mirrorActors: true, wrap: true, width: 130, actorMargin: 40, messageFontSize: 14, actorFontSize: 14, noteFontSize: 13 }
});
mermaid.run({ querySelector: 'pre.mermaid' })
  .then(() => document.body.setAttribute('data-mermaid', 'ok'))
  .catch(e => { document.body.setAttribute('data-mermaid', 'error'); console.error(e); });
</script>
""" % MERMAID_CDN


def main():
    hoy = date.today().strftime("%d/%m/%Y")
    try:
        commit = subprocess.run(["git", "-C", str(RAIZ), "rev-parse", "--short", "HEAD"],
                                capture_output=True, text=True).stdout.strip() or "—"
    except OSError:
        commit = "—"

    marco = leer_marco()
    decisiones, reformulacion = leer_decisiones()
    modulos = [leer_modulo(s) for s in MODULOS]
    registrar_definiciones(modulos, marco, decisiones, reformulacion)

    intro_html = introduccion()
    vision_html, tot = vision(modulos, marco)
    cuerpo_modulos = "\n".join(render_modulo(m, marco["modulos"]) for m in modulos)
    anexos = anexo_a(marco, decisiones, reformulacion) + anexo_b(modulos) + anexo_c(modulos)

    totales = (f"{tot['HU']} historias de usuario, {tot['RU']} requerimientos de usuario, "
               f"{tot['RS']} de sistema, {tot['FN']} funciones, {tot['RNF']} no funcionales, "
               f"{tot['RN']} reglas de negocio, {tot['CU']} casos de uso y "
               f"{9 + tot['S'] + tot['A']} diagramas")
    control_html = control(hoy, commit, totales).replace("{INDICE}", indice(modulos))

    doc = f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8">
<title>{CODIGO_DOC} — Requerimientos y modelado del sistema</title>
<style>{base.ESTILO}{ESTILO_EXTRA}</style></head><body>
{portada(hoy)}
{control_html}
{intro_html}
{vision_html}
{cuerpo_modulos}
{anexos}
{MERMAID_JS}
</body></html>"""

    salida = RAIZ / "docs" / "03-pruebas" / "_build_req.html"
    salida.write_text(doc, encoding="utf-8")

    rotos = {c: sorted(l) for c, l in citados.items() if c not in definidos}
    print(f"HTML generado: {salida}")
    print(f"Contenido: {totales}")
    if duplicados:
        print("\nCodigos definidos mas de una vez: " + ", ".join(duplicados))
    if rotos:
        print("\nReferencias citadas que no se definen en el documento:")
        for c, lugares in sorted(rotos.items()):
            print(f"  {c}: citado en {', '.join(lugares)}")
    else:
        print("Referencias: todas las citadas se resuelven dentro del documento.")
    print()
    print("Para producir el PDF:")
    print('  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \\')
    print("     --headless --disable-gpu --no-pdf-header-footer --virtual-time-budget=60000 \\")
    print(f'     --print-to-pdf="{RAIZ}/docs/Requerimientos_y_Diagramas.pdf" "file://{salida}"')


if __name__ == "__main__":
    main()
