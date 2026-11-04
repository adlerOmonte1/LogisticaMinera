"""Exportación del listado a CSV (HU-M07-02): UTF-8 con BOM, separador punto y
coma y coma decimal, para que la hoja de cálculo de la planta respete tildes y
columnas (RNF-M07-15). Se escribe por filas, sin cargar el archivo en memoria."""

import csv
import io

from django.utils import timezone

COLUMNAS = ["Código", "Fecha y hora del pesaje", "Placa", "Tipo de vehículo", "Tipo de mineral",
            "Peso bruto (t)", "Tara (t)", "Peso neto (t)", "Estado", "Registró"]


def _decimal(valor) -> str:
    return "" if valor is None else str(valor).replace(".", ",")


def filas(qs):
    buffer = io.StringIO()
    escritor = csv.writer(buffer, delimiter=";")

    def vaciar():
        texto = buffer.getvalue()
        buffer.seek(0)
        buffer.truncate(0)
        return texto

    yield "﻿"
    escritor.writerow(COLUMNAS)
    yield vaciar()
    for i in qs.iterator(chunk_size=500):
        escritor.writerow([
            i.codigo,
            timezone.localtime(i.fecha_hora_pesaje).strftime("%d/%m/%Y %H:%M"),
            i.vehiculo.placa,
            i.vehiculo.get_tipo_titularidad_display(),
            i.tipo_mineral.nombre,
            _decimal(i.peso_bruto_tn),
            _decimal(i.tara_tn),
            _decimal(i.peso_neto_tn),
            i.get_estado_display(),
            i.usuario_registro.username,
        ])
        yield vaciar()
