"""Rutas de M08 (ARQ-02 §6). Se monta en /api/v1/consolidacion/."""

from django.urls import path

from apps.consolidacion.views import ExportarView, MensualView

app_name = "consolidacion"

urlpatterns = [
    path("mensual/", MensualView.as_view(), name="mensual"),
    path("mensual/exportar/", ExportarView.as_view(), name="exportar"),
]
