"""Rutas de M04 (ARQ-02 §6). Se monta en /api/v1/reconocimientos/."""

from rest_framework.routers import DefaultRouter

from apps.reconocimiento.views import ReconocimientoViewSet

app_name = "reconocimiento"

router = DefaultRouter()
router.register("", ReconocimientoViewSet, basename="reconocimiento")

urlpatterns = router.urls
