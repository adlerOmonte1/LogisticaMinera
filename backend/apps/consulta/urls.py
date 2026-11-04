"""Rutas de M07 (ARQ-02 §6). Se monta en /api/v1/consulta/."""

from django.urls import path

from apps.consulta import views

app_name = "consulta"

urlpatterns = [
    path("ingresos/", views.IngresosView.as_view(), name="ingresos"),
    path("ingresos/exportar/", views.ExportarView.as_view(), name="exportar"),
    path("ingresos/<int:pk>/", views.IngresoDetalleView.as_view(), name="detalle"),
    path("ingresos/<int:pk>/ticket/", views.TicketView.as_view(), name="ticket"),
    path("calendario/", views.CalendarioView.as_view(), name="calendario"),
    path("cabecera/", views.CabeceraView.as_view(), name="cabecera"),
    path("inicio/", views.InicioView.as_view(), name="inicio"),
    path("avisos/", views.AvisosView.as_view(), name="avisos"),
]
