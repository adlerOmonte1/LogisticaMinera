import django_filters

from apps.accounts.models import Rol, Usuario


class UsuarioFilter(django_filters.FilterSet):
    """`GET /api/v1/usuarios/?rol=SUPERVISOR` — soporte para la pantalla de
    gestión de usuarios (HU-M01-03), no alimenta ningún indicador operativo."""

    rol = django_filters.ChoiceFilter(field_name="rol__nombre", choices=Rol.OPCIONES)

    class Meta:
        model = Usuario
        fields = ["rol"]
