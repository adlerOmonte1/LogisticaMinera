"""Controlador REST de M04 (RF-05). HU-M04-01, HU-M04-02, HU-M04-03.

Solo entrada/salida HTTP: valida el cuerpo, delega en `services/salidas.py` y
traduce el resultado a JSON. Sin `DELETE` ni `PATCH`: la eliminación física no
existe (RN-M04-07, HU-M04-03 CA04) y el contrato de `funcionales.md` no expone
edición de salidas, de modo que RN-M04-09 se cumple por ausencia de la vía.
"""

from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.salidas.filters import SalidaFilter
from apps.salidas.permissions import PuedeAnularSalida, PuedeRegistrarSalida
from apps.salidas.repositories import SalidaRepository
from apps.salidas.serializers import (
    AnularSalidaSerializer,
    SalidaCreateSerializer,
    SalidaDetailSerializer,
    SalidaListSerializer,
)
from apps.salidas.services.salidas import anular_salida, registrar_salida


class SalidaViewSet(viewsets.ReadOnlyModelViewSet):
    http_method_names = ["get", "post", "head", "options"]
    filter_backends = [DjangoFilterBackend]
    filterset_class = SalidaFilter

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated(), PuedeRegistrarSalida()]
        if self.action == "anular":
            return [IsAuthenticated(), PuedeAnularSalida()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == "create":
            return SalidaCreateSerializer
        if self.action == "anular":
            return AnularSalidaSerializer
        if self.action == "list":
            return SalidaListSerializer
        return SalidaDetailSerializer

    def _tiene_filtro_de_fecha(self) -> bool:
        parametros = self.request.query_params
        return "fecha_desde" in parametros or "fecha_hasta" in parametros

    def get_queryset(self):
        queryset = SalidaRepository.listado_base()
        if self.action == "list" and not self._tiene_filtro_de_fecha():
            # HU-M04-03 CA01: sin filtro de fecha, el mes en curso.
            hoy = timezone.localdate()
            queryset = queryset.filter(fecha__year=hoy.year, fecha__month=hoy.month)
        return queryset

    def create(self, request, *args, **kwargs):
        entrada = self.get_serializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        salida = registrar_salida(entrada.validated_data, request.user)
        return Response(SalidaDetailSerializer(salida).data, status=201)

    @action(detail=True, methods=["post"])
    def anular(self, request, pk=None):
        salida = self.get_object()
        entrada = self.get_serializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        salida = anular_salida(salida, entrada.validated_data["motivo"], request.user)
        return Response(SalidaDetailSerializer(salida).data)
