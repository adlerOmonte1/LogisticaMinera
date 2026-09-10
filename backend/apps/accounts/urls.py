"""Rutas de M01 (contrato de ARQ-02 §6 y requerimientos/funcionales.md).

Se monta en `/api/v1/` (config/urls.py). Plural y barra final; las acciones
no CRUD van como sub-ruta (`.../desactivar/`).
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from apps.accounts.views import (
    CambiarPasswordView,
    LoginView,
    LogoutView,
    UsuarioDesactivarView,
    UsuarioDetailView,
    UsuarioListCreateView,
)

app_name = "accounts"

urlpatterns = [
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="refresh"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("usuarios/", UsuarioListCreateView.as_view(), name="usuarios"),
    path("usuarios/cambiar-clave/", CambiarPasswordView.as_view(), name="cambiar-clave"),
    path("usuarios/<int:pk>/", UsuarioDetailView.as_view(), name="usuario-detalle"),
    path("usuarios/<int:pk>/desactivar/", UsuarioDesactivarView.as_view(), name="usuario-desactivar"),
]
