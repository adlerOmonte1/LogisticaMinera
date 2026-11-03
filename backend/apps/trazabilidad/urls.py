"""Rutas de M06 (ARQ-02 §6). `urlpatterns` se monta en /api/v1/; la trazabilidad
de un ingreso, en /api/v1/ingresos/, porque es un subrecurso del ingreso."""

from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.trazabilidad.views import EtapasView, LoteViewSet, RutasView, TrazabilidadIngresoView

app_name = "trazabilidad"

router = DefaultRouter()
router.register("lotes", LoteViewSet, basename="lote")

urlpatterns = router.urls + [
    path("etapas/", EtapasView.as_view(), name="etapas"),
    path("rutas/", RutasView.as_view(), name="rutas"),
]

del_ingreso = (
    [path("<int:pk>/trazabilidad/", TrazabilidadIngresoView.as_view(), name="trazabilidad-ingreso")],
    "trazabilidad_ingreso",
)
