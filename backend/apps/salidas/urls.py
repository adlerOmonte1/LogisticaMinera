"""Rutas de M04 (contrato ARQ-02 §6). Se monta en /api/v1/salidas/."""

from rest_framework.routers import DefaultRouter

from apps.salidas.views import SalidaViewSet

app_name = "salidas"

router = DefaultRouter()
router.register(r"", SalidaViewSet, basename="salida")

urlpatterns = router.urls
