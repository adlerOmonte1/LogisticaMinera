"""Filtros de listado del catálogo. La búsqueda exacta por placa es la que usa
el registro de M03 al reconocer el ticket (notas de M02, frontend)."""

import django_filters

from apps.catalogo.models import TipoMineral, Vehiculo


class TipoMineralFilter(django_filters.FilterSet):
    activo = django_filters.BooleanFilter(field_name="activo")
    codigo = django_filters.CharFilter(field_name="codigo", lookup_expr="iexact")

    class Meta:
        model = TipoMineral
        fields = ["activo", "codigo"]


class VehiculoFilter(django_filters.FilterSet):
    titularidad = django_filters.ChoiceFilter(
        field_name="tipo_titularidad", choices=Vehiculo.TITULARIDADES
    )
    activo = django_filters.BooleanFilter(field_name="activo")
    placa = django_filters.CharFilter(field_name="placa", lookup_expr="iexact")

    class Meta:
        model = Vehiculo
        fields = ["titularidad", "activo", "placa"]
