"""Controlador REST de M03 (RF-01, RF-02, RF-09). HU-M03-01 a HU-M03-07.

Solo entrada/salida HTTP: valida el cuerpo, delega en `services/ingresos.py`
y traduce el resultado a JSON. Sin `DELETE` (RN-M03-09, HU-M03-07 CA03).
"""

from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.ingresos.filters import IngresoFilter
from apps.ingresos.permissions import PuedeEditarOAnularIngreso
from apps.ingresos.repositories import IngresoRepository
from apps.ingresos.serializers import (
    AnularIngresoSerializer,
    IngresoCreateSerializer,
    IngresoDetailSerializer,
    IngresoListSerializer,
    IngresoUpdateSerializer,
)
from apps.ingresos.services.ingresos import (
    anular_ingreso,
    editar_ingreso,
    registrar_ingreso,
    verificar_campos_no_editables,
)


class IngresoViewSet(viewsets.ModelViewSet):
    http_method_names = ["get", "post", "patch", "head", "options"]
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngresoFilter

    def get_permissions(self):
        if self.action in ("update", "partial_update", "anular"):
            return [IsAuthenticated(), PuedeEditarOAnularIngreso()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == "create":
            return IngresoCreateSerializer
        if self.action in ("update", "partial_update"):
            return IngresoUpdateSerializer
        if self.action == "anular":
            return AnularIngresoSerializer
        if self.action == "list":
            return IngresoListSerializer
        return IngresoDetailSerializer

    def _tiene_filtro_de_fecha(self) -> bool:
        parametros = self.request.query_params
        return "fecha_desde" in parametros or "fecha_hasta" in parametros

    def get_queryset(self):
        queryset = IngresoRepository.listado_base()
        if self.action == "list" and not self._tiene_filtro_de_fecha():
            # HU-M03-04 CA01: sin filtro de fecha, el mes en curso.
            hoy = timezone.localdate()
            queryset = queryset.filter(fecha_pesaje__year=hoy.year, fecha_pesaje__month=hoy.month)
        return queryset

    def create(self, request, *args, **kwargs):
        entrada = self.get_serializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        ingreso = registrar_ingreso(entrada.validated_data, request.user)
        return Response(IngresoDetailSerializer(ingreso).data, status=201)

    def update(self, request, *args, **kwargs):
        ingreso = self.get_object()
        verificar_campos_no_editables(request.data)
        entrada = self.get_serializer(data=request.data, partial=True)
        entrada.is_valid(raise_exception=True)
        ingreso = editar_ingreso(ingreso, entrada.validated_data, request.user)
        return Response(IngresoDetailSerializer(ingreso).data)

    @action(detail=True, methods=["post"])
    def anular(self, request, pk=None):
        ingreso = self.get_object()
        entrada = self.get_serializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        ingreso = anular_ingreso(ingreso, entrada.validated_data["motivo"], request.user)
        return Response(IngresoDetailSerializer(ingreso).data)
