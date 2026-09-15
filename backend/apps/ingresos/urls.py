"""Rutas de M03 (contrato ARQ-02 §6). Se monta en /api/v1/ingresos/."""

from rest_framework.routers import DefaultRouter

from apps.ingresos.views import IngresoViewSet

app_name = "ingresos"

router = DefaultRouter()
router.register(r"", IngresoViewSet, basename="ingreso")

urlpatterns = router.urls
