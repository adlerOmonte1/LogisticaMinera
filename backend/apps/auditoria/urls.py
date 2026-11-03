"""Rutas de M09 (ARQ-02 §6). `urlpatterns` se monta en /api/v1/auditoria/;
`historial` en /api/v1/ingresos/, porque es un subrecurso del ingreso."""

from django.urls import path

from apps.auditoria.views import AuditoriaView, HistorialIngresoView

app_name = "auditoria"

urlpatterns = [
    path("", AuditoriaView.as_view(), name="auditoria"),
]

historial = ([path("<int:pk>/historial/", HistorialIngresoView.as_view(), name="historial-ingreso")], "historial")
