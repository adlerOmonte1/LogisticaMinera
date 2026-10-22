#!/usr/bin/env python3
"""Convierte un documento Markdown de docs/ en PDF, con Chromium sin interfaz.

Uso:
    python3 scripts/md_a_pdf.py docs/REVISION_TECNICA_V2.md [salida.pdf]

Requiere el paquete `markdown` (pip install markdown) y Chrome o Chromium. El
navegador se toma de la variable CHROME o de las rutas habituales. Sin salida
explícita, el PDF queda junto al Markdown con el mismo nombre.

Pensado para documentos de texto y tablas. Los diagramas Mermaid de los módulos
tienen su propio generador (generar_pdf_requerimientos.py).
"""

import html
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

import markdown

NAVEGADORES = [
    os.environ.get("CHROME", ""),
    "chromium", "chromium-browser", "google-chrome",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    *sorted(str(p) for p in Path("/opt/pw-browsers").glob("chromium-*/chrome-linux*/chrome")),
]

ESTILO = """
@page { size: A4; margin: 18mm 16mm; }
body { font: 10pt/1.45 "DejaVu Sans", Arial, sans-serif; color: #222; }
h1 { font-size: 17pt; border-bottom: 2px solid #4a3b2a; padding-bottom: 4px; }
h2 { font-size: 13pt; margin-top: 22px; color: #4a3b2a; page-break-after: avoid; }
h3 { font-size: 11pt; page-break-after: avoid; }
table { border-collapse: collapse; width: 100%; margin: 8px 0; font-size: 8.5pt; }
th, td { border: 1px solid #bbb; padding: 4px 6px; vertical-align: top; text-align: left; }
th { background: #efe9e1; }
tr { page-break-inside: avoid; }
code { font-size: 8.5pt; background: #f3f3f3; padding: 0 2px; }
hr { border: 0; border-top: 1px solid #ccc; }
.pie { color: #777; font-size: 8pt; margin-top: 24px; }
"""


def navegador():
    for candidato in NAVEGADORES:
        if candidato and (shutil.which(candidato) or Path(candidato).exists()):
            return shutil.which(candidato) or candidato
    sys.exit("No se encontró Chrome ni Chromium. Defina la variable CHROME.")


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    origen = Path(sys.argv[1]).resolve()
    destino = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else origen.with_suffix(".pdf")

    cuerpo = markdown.markdown(origen.read_text(encoding="utf-8"), extensions=["tables", "sane_lists"])
    documento = (
        f'<!doctype html><html lang="es"><head><meta charset="utf-8">'
        f"<title>{html.escape(origen.stem)}</title><style>{ESTILO}</style></head><body>{cuerpo}"
        f'<p class="pie">Generado desde {html.escape(origen.name)} el {date.today():%d/%m/%Y}.</p></body></html>'
    )
    with tempfile.NamedTemporaryFile("w", suffix=".html", encoding="utf-8", delete=False) as tmp:
        tmp.write(documento)
    try:
        subprocess.run(
            [navegador(), "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
             f"--print-to-pdf={destino}", f"file://{tmp.name}"],
            check=True, capture_output=True,
        )
    finally:
        os.unlink(tmp.name)
    print(f"PDF generado: {destino}")


if __name__ == "__main__":
    main()
