"""Rutas de M05 (ARQ-02 §6). Se monta en /api/v1/ingresos/: el resultado de la
validación es un subrecurso del ingreso."""

from django.urls import path

from apps.validacion.views import ValidacionesDeIngresoView

app_name = "validacion"

urlpatterns = [
    path("<int:pk>/validaciones/", ValidacionesDeIngresoView.as_view(), name="validaciones-ingreso"),
]
