#!/usr/bin/env python3
"""Genera el documento de historias de usuario en HTML listo para imprimir a PDF.

Uso:
    python3 scripts/generar_pdf_hu.py [M03-ingresos M04-reconocimiento ...]

Sin argumentos usa MODULOS_VIGENTES. Los modulos que aun no se han reescrito para el
sistema web inteligente no se incluyen: su HU.md pertenece al alcance anterior.

La conversion a PDF se hace despues con Chrome en modo headless; ver el final del archivo.
"""

import html
import re
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

# Modulos ya reescritos. Ampliar conforme avancen las fases 6 y 7 del plan de migracion.
MODULOS_VIGENTES = ["M03-ingresos"]

NOMBRES_MODULO = {
    "M01-autenticacion": "M01 · Autenticación y roles",
    "M02-catalogo": "M02 · Catálogo maestro",
    "M03-ingresos": "M03 · Registro de ingresos",
    "M04-reconocimiento": "M04 · Reconocimiento automático del ticket",
    "M05-validacion": "M05 · Validación automática de consistencia",
    "M06-trazabilidad": "M06 · Trazabilidad del proceso",
    "M07-consulta": "M07 · Consulta de ingresos y respaldo",
    "M08-consolidacion": "M08 · Consolidación de la producción",
    "M09-auditoria": "M09 · Auditoría",
}


# --------------------------------------------------------------------------- markdown


def en_linea(texto):
    """Convierte el marcado en linea de un fragmento de Markdown."""
    t = html.escape(texto)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![\w*])\*([^*]+)\*(?![\w*])", r"<em>\1</em>", t)
    return t


def tabla(lineas):
    """Convierte un bloque de filas Markdown en una tabla HTML."""
    filas = [[c.strip() for c in ln.strip().strip("|").split("|")] for ln in lineas]
    if len(filas) >= 2 and all(set(c) <= set("-: ") for c in filas[1]):
        cabecera, cuerpo = filas[0], filas[2:]
    else:
        cabecera, cuerpo = None, filas
    out = ['<table>']
    if cabecera:
        out.append("<thead><tr>" + "".join(f"<th>{en_linea(c)}</th>" for c in cabecera) + "</tr></thead>")
    out.append("<tbody>")
    for fila in cuerpo:
        out.append("<tr>" + "".join(f"<td>{en_linea(c)}</td>" for c in fila) + "</tr>")
    out.append("</tbody></table>")
    return "\n".join(out)


def bloques(texto):
    """Convierte un subconjunto de Markdown a HTML: parrafos, listas, citas y tablas."""
    salida, buffer_tabla, buffer_lista, buffer_cita, parrafo = [], [], [], [], []

    def cerrar_parrafo():
        if parrafo:
            salida.append(f"<p>{en_linea(' '.join(parrafo))}</p>")
            parrafo.clear()

    def cerrar_tabla():
        if buffer_tabla:
            salida.append(tabla(buffer_tabla))
            buffer_tabla.clear()

    def cerrar_lista():
        if buffer_lista:
            items = "".join(f"<li>{en_linea(i)}</li>" for i in buffer_lista)
            salida.append(f"<ul>{items}</ul>")
            buffer_lista.clear()

    def cerrar_cita():
        if buffer_cita:
            cuerpo = en_linea(" ".join(buffer_cita))
            m = re.match(r"<strong>(CA\d+)\.</strong>\s*(.*)", cuerpo)
            if m:
                salida.append(
                    f'<div class="ca"><span class="ca-id">{m.group(1)}</span>'
                    f'<span class="ca-txt">{m.group(2)}</span></div>'
                )
            else:
                salida.append(f'<blockquote>{cuerpo}</blockquote>')
            buffer_cita.clear()

    def cerrar_todo():
        cerrar_parrafo(); cerrar_tabla(); cerrar_lista(); cerrar_cita()

    for linea in texto.split("\n"):
        ln = linea.rstrip()
        if not ln.strip():
            cerrar_todo()
        elif ln.lstrip().startswith("|"):
            cerrar_parrafo(); cerrar_lista(); cerrar_cita()
            buffer_tabla.append(ln)
        elif ln.startswith(">"):
            cerrar_parrafo(); cerrar_tabla(); cerrar_lista()
            buffer_cita.append(ln.lstrip("> ").rstrip())
        elif re.match(r"^\s*[-*]\s+", ln):
            cerrar_parrafo(); cerrar_tabla(); cerrar_cita()
            buffer_lista.append(re.sub(r"^\s*[-*]\s+", "", ln))
        elif ln.startswith("### "):
            cerrar_todo(); salida.append(f"<h4>{en_linea(ln[4:])}</h4>")
        elif ln.startswith("## "):
            cerrar_todo(); salida.append(f"<h3>{en_linea(ln[3:])}</h3>")
        elif ln.startswith("---"):
            cerrar_todo()
        else:
            cerrar_tabla(); cerrar_lista(); cerrar_cita()
            parrafo.append(ln.strip())

    cerrar_todo()
    return "\n".join(salida)


# --------------------------------------------------------------------------- lectura


def leer_modulo(slug):
    """Extrae la cabecera y las historias del HU.md de un modulo."""
    ruta = RAIZ / "docs" / "modulos" / slug / "HU.md"
    if not ruta.exists():
        return None
    texto = ruta.read_text(encoding="utf-8")

    titulo = re.search(r"^# (.+)$", texto, re.M)
    meta = re.search(r"^\*\*RF asociad[oa]s?:\*\*(.+)$", texto, re.M)
    intro = re.search(r"^> (.+(?:\n> .+)*)$", texto, re.M)

    partes = re.split(r"^## (HU-M\d{2}-\d{2}) — (.+)$", texto, flags=re.M)
    historias = []
    for i in range(1, len(partes), 3):
        historias.append({
            "id": partes[i].strip(),
            "titulo": partes[i + 1].strip(),
            "cuerpo": partes[i + 2],
        })
    return {
        "slug": slug,
        "nombre": NOMBRES_MODULO.get(slug, slug),
        "titulo": titulo.group(1) if titulo else slug,
        "meta": meta.group(1).strip() if meta else "",
        "intro": re.sub(r"\n> ", " ", intro.group(1)).strip() if intro else "",
        "historias": historias,
    }


def leer_indice():
    """Extrae el backlog completo de docs/HistoriasUsuario.md."""
    ruta = RAIZ / "docs" / "HistoriasUsuario.md"
    if not ruta.exists():
        return []
    grupos, actual = [], None
    for linea in ruta.read_text(encoding="utf-8").split("\n"):
        m = re.match(r"^## (M\d{2} — .+)$", linea)
        if m:
            actual = {"modulo": m.group(1), "filas": []}
            grupos.append(actual)
        elif actual is not None and re.match(r"^\| HU-M", linea):
            actual["filas"].append([c.strip() for c in linea.strip().strip("|").split("|")])
    return grupos


# --------------------------------------------------------------------------- render

ESTILO = """
@page { size: A4; margin: 17mm 15mm 18mm 15mm; }
@page :first { margin: 0; }
* { box-sizing: border-box; }
body {
  font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
  font-size: 9.6pt; line-height: 1.52; color: var(--tinta);
  margin: 0; -webkit-print-color-adjust: exact; print-color-adjust: exact;
}
:root {
  --mostaza: #C08A1E; --mostaza-claro: #E8C766; --mostaza-palido: #FBF1D9;
  --marron: #4A342A; --marron-medio: #7A5540; --marron-palido: #F3EBE4;
  --tinta: #2B2320; --tinta-suave: #6A5B52; --linea: #DCCFC2; --crema: #FDFAF4;
}
h1, h2, h3, h4 { font-weight: 700; margin: 0; color: var(--marron); }

/* -------- portada -------- */
.portada {
  height: 297mm; background: var(--marron); color: #fff;
  padding: 34mm 24mm; page-break-after: always; position: relative;
}
.portada .barra { width: 62mm; height: 5mm; background: var(--mostaza); margin-bottom: 16mm; }
.portada .kicker { font-size: 10pt; letter-spacing: .22em; text-transform: uppercase;
  color: var(--mostaza-claro); margin-bottom: 9mm; }
.portada h1 { font-size: 27pt; line-height: 1.24; color: #fff; margin-bottom: 7mm; max-width: 145mm; }
.portada .sub { font-size: 12.5pt; color: #E9DDD2; max-width: 130mm; line-height: 1.55; }
.portada .pie { position: absolute; bottom: 30mm; left: 24mm; right: 24mm;
  border-top: 1px solid rgba(232,199,102,.42); padding-top: 7mm;
  display: flex; gap: 16mm; font-size: 9.2pt; color: #E9DDD2; }
.portada .pie .et { color: var(--mostaza-claro); text-transform: uppercase;
  letter-spacing: .12em; font-size: 7.4pt; display: block; margin-bottom: 1.6mm; }

/* -------- estructura -------- */
.seccion { page-break-before: always; }
h2.seccion-tit {
  font-size: 16.5pt; padding-bottom: 3mm; margin-bottom: 6mm;
  border-bottom: 2.5px solid var(--mostaza);
}
h2.seccion-tit .num {
  display: inline-block; background: var(--mostaza); color: #fff;
  width: 8.5mm; height: 8.5mm; line-height: 8.5mm; text-align: center;
  border-radius: 50%; font-size: 10.5pt; margin-right: 3.5mm; vertical-align: 2px;
}
h3 { font-size: 11.6pt; margin: 6mm 0 2.5mm; color: var(--marron-medio); }
h4 { font-size: 10.2pt; margin: 4.5mm 0 2mm; color: var(--marron-medio); }
p { margin: 0 0 2.8mm; text-align: justify; }
ul { margin: 0 0 3mm; padding-left: 5mm; }
li { margin-bottom: 1.2mm; }
code { font-family: "SF Mono", Menlo, Consolas, monospace; font-size: .87em;
  background: var(--mostaza-palido); padding: .4mm 1.2mm; border-radius: 1mm; color: #7A5510; }
.intro { font-size: 10.4pt; color: var(--tinta-suave); margin-bottom: 6mm; }

/* -------- tablas -------- */
table { width: 100%; border-collapse: collapse; margin: 0 0 4mm; font-size: 8.9pt;
  page-break-inside: avoid; }
th { background: var(--marron); color: #fff; text-align: left; padding: 2mm 2.6mm;
  font-weight: 600; font-size: 8.4pt; letter-spacing: .02em; }
td { padding: 1.9mm 2.6mm; border-bottom: .4pt solid var(--linea); vertical-align: top; }
tbody tr:nth-child(even) td { background: var(--crema); }

/* -------- historia -------- */
.hu { page-break-inside: avoid; margin-bottom: 9mm; }
.hu-cab { background: var(--mostaza-palido); border-left: 4.5px solid var(--mostaza);
  padding: 3.4mm 4mm; margin-bottom: 4mm; }
.hu-id { font-size: 8pt; font-weight: 700; letter-spacing: .13em; color: #8A6410;
  text-transform: uppercase; }
.hu-tit { font-size: 13pt; font-weight: 700; color: var(--marron); margin-top: 1.2mm;
  line-height: 1.3; }
.hu-pri { display: inline-block; margin-top: 2.4mm; font-size: 7.6pt; font-weight: 700;
  letter-spacing: .1em; text-transform: uppercase; padding: 1mm 2.6mm; border-radius: 1mm;
  background: var(--marron); color: var(--mostaza-claro); }
.rotulo { font-size: 8pt; font-weight: 700; letter-spacing: .14em; text-transform: uppercase;
  color: var(--mostaza); margin: 5mm 0 2mm; }
.narrativa { background: var(--marron-palido); border-left: 3px solid var(--marron-medio);
  padding: 3mm 4mm; font-size: 10.4pt; font-style: italic; color: var(--marron);
  margin-bottom: 3.5mm; }
.ca { display: flex; gap: 3mm; margin-bottom: 2.2mm; page-break-inside: avoid; }
.ca-id { flex: 0 0 13mm; font-size: 7.8pt; font-weight: 700; color: #fff;
  background: var(--mostaza); text-align: center; padding: 1.2mm 0; height: fit-content;
  border-radius: 1mm; letter-spacing: .04em; }
.ca-txt { flex: 1; text-align: justify; }
blockquote { margin: 0 0 3mm; padding-left: 3.5mm; border-left: 2.5px solid var(--mostaza-claro);
  color: var(--tinta-suave); }

/* -------- avisos -------- */
.nota { background: var(--crema); border: .5pt solid var(--linea); border-top: 2.5px solid var(--mostaza);
  padding: 3.4mm 4mm; margin-bottom: 5mm; font-size: 9.2pt; }
.nota .t { font-weight: 700; color: var(--marron); margin-bottom: 1.6mm; }
.pendiente { color: var(--tinta-suave); font-size: 9pt; font-style: italic; }
"""


def render_modulo(mod):
    partes = [f'<div class="seccion"><h2 class="seccion-tit">'
              f'<span class="num">{mod["slug"][1:3]}</span>{html.escape(mod["nombre"])}</h2>']
    if mod["meta"]:
        partes.append(f'<p class="intro"><strong>RF asociados:</strong> {en_linea(mod["meta"].lstrip())}</p>')
    if mod["intro"]:
        partes.append(f'<div class="nota"><div class="t">Responsabilidad del módulo</div>'
                      f'{en_linea(mod["intro"])}</div>')

    for h in mod["historias"]:
        cuerpo = h["cuerpo"]
        prioridad = re.search(r"\*\*Prioridad\*\*\s*\|\s*([^|]+)\|", cuerpo)
        prioridad = prioridad.group(1).strip() if prioridad else ""

        def seccion(nombre, hasta):
            patron = rf"\*\*{nombre}\*\*\s*\n(.*?)(?=\n\*\*(?:{hasta})\*\*|\Z)"
            m = re.search(patron, cuerpo, re.S)
            return m.group(1).strip() if m else ""

        historia = seccion("Historia", "Descripción")
        descripcion = seccion("Descripción", "Detalles|Criterios de aceptación")
        detalles = seccion("Detalles", "Criterios de aceptación")
        criterios = seccion("Criterios de aceptación", "$")

        partes.append('<div class="hu">')
        partes.append(f'<div class="hu-cab"><div class="hu-id">{h["id"]}</div>'
                      f'<div class="hu-tit">{html.escape(h["titulo"])}</div>'
                      + (f'<div class="hu-pri">{html.escape(prioridad)}</div>' if prioridad else "")
                      + '</div>')
        if historia:
            partes.append(f'<div class="narrativa">{en_linea(historia)}</div>')
        if descripcion:
            partes.append(bloques(descripcion))
        if detalles:
            partes.append('<div class="rotulo">Detalles</div>')
            partes.append(bloques(detalles))
        if criterios:
            partes.append('<div class="rotulo">Criterios de aceptación</div>')
            partes.append(bloques(criterios))
        partes.append("</div>")

    partes.append("</div>")
    return "\n".join(partes)


def render_indice(grupos, vigentes):
    filas = []
    for g in grupos:
        slug_mod = g["modulo"][:3]
        listo = any(slug_mod == s[:3] for s in vigentes)
        marca = "" if listo else ' <span class="pendiente">— detalle pendiente</span>'
        filas.append(f'<tr><td colspan="4" style="background:var(--marron-palido);'
                     f'font-weight:700;color:var(--marron)">{html.escape(g["modulo"])}{marca}</td></tr>')
        for f in g["filas"]:
            celdas = "".join(f"<td>{en_linea(c)}</td>" for c in f[:4])
            filas.append(f"<tr>{celdas}</tr>")
    return ('<table><thead><tr><th style="width:24mm">Historia</th><th>Título</th>'
            '<th style="width:34mm">Rol</th><th style="width:20mm">Prioridad</th></tr></thead>'
            "<tbody>" + "".join(filas) + "</tbody></table>")


TESIS = """
<div class="seccion">
<h2 class="seccion-tit"><span class="num">II</span>Relación con la investigación</h2>

<p>Esta sección existe solo en este documento de lectura. La documentación técnica del repositorio
describe el sistema y no menciona variables ni indicadores: la correspondencia entre ambos se
registra en la matriz de trazabilidad.</p>

<h3>Las dos variables</h3>
<p>La <strong>variable independiente</strong> es el sistema web inteligente cuyas historias recoge
este documento. Se evalúa una sola vez, después de la implementación, en tres dimensiones:
funcionalidad, capacidad inteligente y usabilidad.</p>
<p>La <strong>variable dependiente</strong> es el control de inventarios de ingreso de mineral, y se
mide por observación directa de cada ingreso, no con consultas al sistema. El sistema no produce el
dato de la medición: produce las condiciones para que el trabajo cambie, y la observación registra
si cambió.</p>

<h3>Qué exige la variable dependiente del sistema</h3>
<table>
<thead><tr><th style="width:52mm">Dimensión</th><th>Qué debe hacer posible el sistema</th></tr></thead>
<tbody>
<tr><td><strong>Oportunidad del registro</strong></td><td>Que el ingreso se registre junto a la
balanza, en el momento, y que queden tres marcas de tiempo independientes: la del ticket, el inicio
del registro y su fin. De ahí la exigencia de que las dos últimas las asigne el servidor y nadie
las edite.</td></tr>
<tr><td><strong>Integridad del registro</strong></td><td>Que los siete datos del ingreso estén
siempre completos y que exista el respaldo fotográfico recuperable. De ahí que la imagen sea
obligatoria y que ningún campo admita quedar vacío al confirmar.</td></tr>
<tr><td><strong>Consolidación de la producción</strong></td><td>Que el total del mes por tipo de
mineral se obtenga a demanda y que cada ingreso pueda vincularse con las etapas del proceso.</td></tr>
</tbody></table>

<h3>Dónde está el componente inteligente</h3>
<p>Dos capacidades distinguen este sistema de un formulario de captura: el
<strong>reconocimiento automático</strong> de los seis datos del ticket a partir de su fotografía, y
la <strong>detección automática de inconsistencias</strong> mediante las cinco reglas de validación.
Ambas se apoyan en una condición que atraviesa todas las historias: el sistema propone, el usuario
confirma, y el valor propuesto y el confirmado se conservan por separado.</p>

<div class="nota"><div class="t">Por qué el peso neto no se calcula</div>
El ticket de balanza ya trae el peso neto impreso. Si el sistema lo calculara como bruto menos tara,
la comparación entre ambos daría siempre cero y un ticket incoherente entraría sin que nadie lo
advirtiera. Registrarlo como dato leído es lo que permite que la regla V1 lo contraste. Es la
decisión de diseño que más probablemente alguien intentará «simplificar» durante la
implementación.</div>
</div>
"""


def referencia():
    return """
<div class="seccion">
<h2 class="seccion-tit"><span class="num">III</span>Referencia</h2>

<h3>Roles del sistema</h3>
<table>
<thead><tr><th style="width:42mm">Rol</th><th>Alcance</th></tr></thead>
<tbody>
<tr><td><strong>Administrador</strong></td><td>Acceso total, incluidos usuarios, catálogos y anulaciones</td></tr>
<tr><td><strong>Administrativo</strong></td><td>Registro, corrección, consultas, consolidación y exportación</td></tr>
<tr><td><strong>Supervisor de planta</strong></td><td>Registro y consulta</td></tr>
</tbody></table>

<h3>Reglas de validación del ticket</h3>
<p>Se aplican dos veces sobre cada ingreso: sobre los datos que propone el reconocimiento y otra vez
sobre los que el usuario confirma. Se ejecutan siempre en el servidor.</p>
<table>
<thead><tr><th style="width:14mm">Regla</th><th>Qué detecta</th><th style="width:38mm">Efecto</th></tr></thead>
<tbody>
<tr><td><strong>V1</strong></td><td>El peso neto no coincide con el peso bruto menos la tara, más allá de la tolerancia</td><td>Bloquea</td></tr>
<tr><td><strong>V2</strong></td><td>La tara es mayor o igual que el peso bruto</td><td>Bloquea</td></tr>
<tr><td><strong>V3</strong></td><td>La placa no tiene un formato válido</td><td>Bloquea</td></tr>
<tr><td><strong>V4</strong></td><td>El peso neto queda fuera del rango de carga del vehículo</td><td>Exige justificación</td></tr>
<tr><td><strong>V5</strong></td><td>La fecha del ticket es posterior a la del registro</td><td>Bloquea</td></tr>
</tbody></table>

<h3>Los siete datos obligatorios del ingreso</h3>
<p>Placa del vehículo · fecha y hora del ticket · peso bruto · tara · peso neto · tipo de mineral ·
tipo de vehículo. Los seis primeros provienen del ticket; el tipo de vehículo se deriva del catálogo
a partir de la placa y no se digita.</p>

<h3>Cómo leer una historia</h3>
<table>
<thead><tr><th style="width:46mm">Elemento</th><th>Qué contiene</th></tr></thead>
<tbody>
<tr><td><strong>Historia</strong></td><td>Quién necesita la capacidad, qué necesita y para qué. Es el enunciado que se acuerda con el usuario</td></tr>
<tr><td><strong>Descripción</strong></td><td>El razonamiento: qué hace el sistema, qué delega y qué restricciones aplica</td></tr>
<tr><td><strong>Detalles</strong></td><td>Los campos, su obligatoriedad y su origen: leído del ticket, elegido, derivado o asignado por el servidor</td></tr>
<tr><td><strong>Criterios de aceptación</strong></td><td>Lo verificable. Cada criterio se convierte en un caso de prueba, y los mensajes entre comillas se comprueban literalmente</td></tr>
</tbody></table>
</div>
"""


def main():
    vigentes = sys.argv[1:] or MODULOS_VIGENTES
    modulos = [m for m in (leer_modulo(s) for s in vigentes) if m]
    total_detalle = sum(len(m["historias"]) for m in modulos)
    grupos = leer_indice()
    total_backlog = sum(len(g["filas"]) for g in grupos)
    hoy = date.today().strftime("%d/%m/%Y")

    pendientes = [NOMBRES_MODULO[s] for s in NOMBRES_MODULO
                  if not any(s[:3] == v[:3] for v in vigentes)]

    doc = f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8">
<title>Historias de usuario — Sistema web inteligente</title>
<style>{ESTILO}</style></head><body>

<div class="portada">
  <div class="barra"></div>
  <div class="kicker">Construcción y Minería · Huánuco</div>
  <h1>Sistema web inteligente para el control de inventarios de ingreso de mineral</h1>
  <div class="sub">Historias de usuario y criterios de aceptación<br>Planta de procesamiento de Pillcomarca</div>
  <div class="pie">
    <div><span class="et">Documento</span>Historias de usuario</div>
    <div><span class="et">Historias en el catálogo</span>{total_backlog} en 9 módulos</div>
    <div><span class="et">Detalladas aquí</span>{total_detalle}</div>
    <div><span class="et">Fecha</span>{hoy}</div>
  </div>
</div>

<div class="seccion">
<h2 class="seccion-tit"><span class="num">I</span>Catálogo de historias</h2>
<p class="intro">El sistema se organiza en nueve módulos, cada uno responsable de una parte acotada
del trabajo de planta. Una historia cubre una capacidad completa: el mantenimiento de un catálogo es
una sola historia con un criterio por operación, y se reserva historia propia para lo que tiene
lógica dedicada, como el reconocimiento del ticket, la validación o la anulación.</p>
{render_indice(grupos, vigentes)}
<div class="nota"><div class="t">Alcance de este documento</div>
Se detallan con sus criterios de aceptación las {total_detalle} historias de
{", ".join(m["nombre"] for m in modulos)}. Las de {", ".join(p.split(" · ")[0] for p in pendientes)}
figuran en el catálogo y se detallarán conforme avance la documentación.</div>
</div>

{TESIS}

{"".join(render_modulo(m) for m in modulos)}

{referencia()}

</body></html>"""

    salida = RAIZ / "docs" / "03-pruebas" / "_build_hu.html"
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(doc, encoding="utf-8")
    print(f"HTML generado: {salida}")
    print(f"Modulos: {', '.join(m['slug'] for m in modulos)} · historias detalladas: {total_detalle}")
    print()
    print("Para producir el PDF:")
    print('  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \\')
    print("     --headless --disable-gpu --no-pdf-header-footer \\")
    print(f'     --print-to-pdf="{RAIZ}/docs/Historias_de_Usuario.pdf" "file://{salida}"')


if __name__ == "__main__":
    main()
