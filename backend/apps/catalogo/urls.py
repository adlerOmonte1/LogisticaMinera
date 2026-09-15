"""Rutas de M02 (contrato ARQ-02 §6). Se monta en /api/v1/catalogo/."""

from rest_framework.routers import DefaultRouter

from apps.catalogo.views import (
    ClienteViewSet,
    ProductoViewSet,
    TransportistaViewSet,
    VehiculoViewSet,
)

app_name = "catalogo"

router = DefaultRouter()
router.register("productos", ProductoViewSet, basename="producto")
router.register("vehiculos", VehiculoViewSet, basename="vehiculo")
router.register("transportistas", TransportistaViewSet, basename="transportista")
router.register("clientes", ClienteViewSet, basename="cliente")

urlpatterns = router.urls
