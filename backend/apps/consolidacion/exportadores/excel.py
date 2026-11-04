"""Exportador XLSX del consolidado (HU-M08-02). Es el único archivo que importa
openpyxl. Escribe los mismos valores que la pantalla, sin redondear de otra
forma (RN-M08-05, riesgo secundario de las notas de M08)."""

import io
from decimal import Decimal

from django.utils import timezone
from openpyxl import Workbook
from openpyxl.styles import Font

from apps.consolidacion.repositories import Consolidado

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre",
         "noviembre", "diciembre"]
FORMATO_TONELADAS = "#,##0.00"


class ExportadorExcel:
    tipo_contenido = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    extension = "xlsx"

    def generar(self, consolidado: Consolidado, generado_en) -> bytes:
        libro = Workbook()
        hoja = libro.active
        hoja.title = "Consolidado"
        p = consolidado.periodo
        hoja.append(["Total acumulado mensual por tipo de mineral"])
        hoja["A1"].font = Font(bold=True, size=13)
        hoja.append(["Periodo", f"{MESES[p.mes - 1]} {p.anio}"])
        hoja.append(["Generado", timezone.localtime(generado_en).strftime("%d/%m/%Y %H:%M")])
        hoja.append([])
        hoja.append(["Código", "Tipo de mineral", "Ingresos", "Toneladas netas", "Participación (%)"])
        for celda in hoja[5]:
            celda.font = Font(bold=True)
        for f in consolidado.filas:
            hoja.append([f["codigo"], f["nombre"], f["ingresos"], f["toneladas"], f["participacion"]])
        hoja.append(["", "Total", consolidado.total_ingresos, consolidado.total_toneladas, Decimal("100.00")])
        for fila in hoja.iter_rows(min_row=6, min_col=4, max_col=5):
            for celda in fila:
                celda.number_format = FORMATO_TONELADAS
        hoja.append([])
        # RN-M08-07: el archivo también avisa que el total no es definitivo.
        hoja.append(["En proceso", len(consolidado.en_proceso), ", ".join(consolidado.en_proceso)])
        hoja.append(["Anulados excluidos", consolidado.anulados])
        for columna, ancho in zip("ABCDE", (12, 32, 10, 16, 18)):
            hoja.column_dimensions[columna].width = ancho
        salida = io.BytesIO()
        libro.save(salida)
        return salida.getvalue()
