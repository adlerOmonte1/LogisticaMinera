"""Filtros de listado del catálogo.

`titularidad` sobre vehículos no es comodidad: es la consulta que alimenta el
denominador del indicador I2 (cobertura por tipo de vehículo).
"""

import django_filters

from apps.catalogo.models import Producto, Vehiculo


class ProductoFilter(django_filters.FilterSet):
    activo = django_filters.BooleanFilter(field_name="activo")

    class Meta:
        model = Producto
        fields = ["activo"]


class VehiculoFilter(django_filters.FilterSet):
    titularidad = django_filters.ChoiceFilter(
        field_name="tipo_titularidad", choices=Vehiculo.TITULARIDADES
    )
    activo = django_filters.BooleanFilter(field_name="activo")

    class Meta:
        model = Vehiculo
        fields = ["titularidad", "activo"]
