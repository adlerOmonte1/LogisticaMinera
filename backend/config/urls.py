"""Contrato de rutas del sistema (ARQ-02 §6).

Una entrada por módulo, con el prefijo /api/v1/. Plural y barra final.
"""

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from apps.auditoria.urls import historial

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("apps.accounts.urls")),                   # M01
    path("api/v1/catalogo/", include("apps.catalogo.urls")),          # M02
    path("api/v1/ingresos/", include("apps.validacion.urls")),        # M05, subrecurso del ingreso
    path("api/v1/ingresos/", include(historial)),                     # M09, historial del ingreso
    path("api/v1/ingresos/", include("apps.ingresos.urls")),          # M03
    path("api/v1/reconocimientos/", include("apps.reconocimiento.urls")),  # M04
    path("api/v1/auditoria/", include("apps.auditoria.urls")),        # M09
    path("api/v1/esquema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/v1/docs/", SpectacularSwaggerView.as_view(url_name="schema")),
]
