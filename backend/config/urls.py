"""Contrato de rutas del sistema (ARQ-02 §6).

Una entrada por módulo, con el prefijo /api/v1/. Plural y barra final.
"""

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
    # path("api/v1/auth/", include("apps.accounts.urls")),            # M01
    # path("api/v1/catalogo/", include("apps.catalogo.urls")),        # M02
    # path("api/v1/ingresos/", include("apps.ingresos.urls")),        # M03
    # path("api/v1/salidas/", include("apps.salidas.urls")),          # M04
    # path("api/v1/existencias/", include("apps.existencias.urls")),  # M05
    # path("api/v1/reportes/", include("apps.reportes.urls")),        # M06
    # path("api/v1/sincronizacion/", include("apps.sincronizacion.urls")),  # M07
    # path("api/v1/auditoria/", include("apps.auditoria.urls")),      # M08
    # path("api/v1/busqueda/", include("apps.busqueda.urls")),        # M09
    path("api/v1/esquema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/v1/docs/", SpectacularSwaggerView.as_view(url_name="schema")),
]
