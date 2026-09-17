"""Filtros del listado de salidas (HU-M04-02 CA04, HU-M04-03 CA01)."""

import django_filters

from apps.salidas.models import Salida


class SalidaFilter(django_filters.FilterSet):
    fecha_desde = django_filters.DateFilter(field_name="fecha", lookup_expr="gte")
    fecha_hasta = django_filters.DateFilter(field_name="fecha", lookup_expr="lte")

    class Meta:
        model = Salida
        fields = [
            "producto", "cliente", "tipo_movimiento", "estado",
            "fecha_desde", "fecha_hasta",
        ]
