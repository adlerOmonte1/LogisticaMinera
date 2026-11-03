"""M07 lee ingresos, lotes, validaciones y eventos de los demás módulos."""

from datetime import datetime, time, timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from apps.catalogo.tests.factories import VehiculoFactory
from apps.ingresos.models import Ingreso
from apps.ingresos.tests.factories import IngresoFactory
from apps.trazabilidad.tests.conftest import *  # noqa: F401,F403

CONSULTA = "/api/v1/consulta/"


@pytest.fixture
def hoy():
    return timezone.localdate()


@pytest.fixture
def crear(mineral, hoy):
    """Ingreso con el día, la hora, la placa y el estado que pida la prueba."""

    def _crear(dia=None, hora=8, placa="V2K-841", estado=Ingreso.REGISTRADO, **kw):
        dia = dia or hoy
        momento = timezone.make_aware(datetime.combine(dia, time(hora, 0)))
        vehiculo = VehiculoFactory(placa=placa)
        datos = dict(vehiculo=vehiculo, tipo_mineral=mineral, fecha_hora_pesaje=momento,
                     hora_inicio_registro=momento + timedelta(minutes=5),
                     hora_fin_registro=momento + timedelta(minutes=6), estado=estado)
        if estado == Ingreso.EN_PROCESO:
            datos.update(tara_tn=None, peso_neto_tn=None)
        if estado == Ingreso.ANULADO:
            datos.update(motivo_anulacion="Duplicado")
        datos.update(kw)
        return IngresoFactory(**datos)

    return _crear


TONELADAS = Decimal("20.20")


@pytest.fixture
def registrar(api_como, ayer, mineral, lectura, vehiculo):
    """Registro completo por la API de M03, con imagen y reconocimiento."""

    def _registrar(usuario, imagen):
        api = api_como(usuario)
        token = api.post("/api/v1/ingresos/borradores/", {"imagen": imagen}, format="multipart").data["borrador"]
        return api.post("/api/v1/ingresos/", {"borrador": token, "placa": "V2K-841", "fecha": ayer.isoformat(),
                                              "hora": "08:15", "peso_bruto_tn": "29.80",
                                              "tipo_mineral": mineral.pk}, format="json")

    return _registrar
