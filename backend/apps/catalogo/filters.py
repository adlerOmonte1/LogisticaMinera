"""Filtros de listado del catálogo."""

import django_filters

from apps.catalogo.models import TipoMineral, Vehiculo


class TipoMineralFilter(django_filters.FilterSet):
    activo = django_filters.BooleanFilter(field_name="activo")

    class Meta:
        model = TipoMineral
        fields = ["activo"]


class VehiculoFilter(django_filters.FilterSet):
    titularidad = django_filters.ChoiceFilter(
        field_name="tipo_titularidad", choices=Vehiculo.TITULARIDADES
    )
    activo = django_filters.BooleanFilter(field_name="activo")

    class Meta:
        model = Vehiculo
        fields = ["titularidad", "activo"]
