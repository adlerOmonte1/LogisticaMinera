"""Consulta de las validaciones de un ingreso (HU-M05-01, DR-31): los tres
roles, solo lectura. La validación no tiene endpoint de escritura propio: ocurre
dentro del registro de M03."""

from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import PuedeConsultar
from apps.ingresos.models import Ingreso
from apps.validacion.repositories import ResultadoValidacionRepository
from apps.validacion.serializers import ResultadoValidacionSerializer


class ValidacionesDeIngresoView(ListAPIView):
    permission_classes = [IsAuthenticated, PuedeConsultar]
    serializer_class = ResultadoValidacionSerializer
    pagination_class = None

    def get_queryset(self):
        ingreso = get_object_or_404(Ingreso, pk=self.kwargs["pk"])
        return ResultadoValidacionRepository.de_ingreso(ingreso.pk)


__all__ = ["ValidacionesDeIngresoView"]
