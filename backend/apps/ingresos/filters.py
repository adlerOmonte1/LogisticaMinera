"""Filtros del listado de ingresos (RS-M03-06, requerimientos/funcionales.md).

`titularidad` no es un atributo del ingreso sino del vehículo asociado; es la
consulta directa que alimenta el indicador I2.
"""

import django_filters

from apps.catalogo.models import Vehiculo
from apps.ingresos.models import Ingreso


class IngresoFilter(django_filters.FilterSet):
    fecha_desde = django_filters.DateFilter(field_name="fecha_pesaje", lookup_expr="gte")
    fecha_hasta = django_filters.DateFilter(field_name="fecha_pesaje", lookup_expr="lte")
    titularidad = django_filters.ChoiceFilter(
        field_name="vehiculo__tipo_titularidad", choices=Vehiculo.TITULARIDADES
    )
    # M07 declara este filtro sobre el endpoint de M03 (HU-M07-05).
    capturado_offline = django_filters.BooleanFilter(field_name="capturado_offline")

    class Meta:
        model = Ingreso
        fields = [
            "producto", "vehiculo", "estado",
            "fecha_desde", "fecha_hasta", "titularidad", "capturado_offline",
        ]
