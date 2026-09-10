"""Contrato de rutas del sistema (ARQ-02 §6).

Una entrada por módulo, con el prefijo /api/v1/. Plural y barra final.
"""

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("apps.accounts.urls")),                   # M01
    path("api/v1/catalogo/", include("apps.catalogo.urls")),          # M02
    path("api/v1/esquema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/v1/docs/", SpectacularSwaggerView.as_view(url_name="schema")),
]
