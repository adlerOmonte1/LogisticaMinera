"""Consultas de M09 (ARQ-02 §6). Solo lectura: no hay endpoint que cree,
modifique ni elimine un evento (RN-M09-02, RS-M09-08)."""

from django.shortcuts import get_object_or_404
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.permissions import SOLO_ADMINISTRADOR, PuedeConsultar, PuedeConsultarAuditoria
from apps.auditoria.repositories import EventoRepository, referencias
from apps.auditoria.serializers import EventoSerializer
from apps.ingresos.models import Ingreso

MENSAJE_SIN_EVENTOS = "No hay eventos con estos filtros"


class HistorialIngresoView(GenericAPIView):
    """HU-M09-02: los tres roles, igual para todos (CA04). Cronológico y sin
    filtros: para lo demás está la auditoría del Administrador."""

    permission_classes = [IsAuthenticated, PuedeConsultar]
    serializer_class = EventoSerializer

    def get(self, request, pk):
        ingreso = get_object_or_404(Ingreso, pk=pk)
        eventos = list(EventoRepository.historial_de_ingreso(ingreso.pk))
        datos = EventoSerializer(eventos, many=True, context={"referencias": referencias(eventos)}).data
        return Response({
            "ingreso": ingreso.codigo,
            # CA05: a quien no es Administrador no se le ofrece la auditoría completa.
            "puede_ver_auditoria": request.user.tiene_rol(*SOLO_ADMINISTRADOR),
            "count": len(datos),
            "results": datos,
        })


class AuditoriaView(GenericAPIView):
    """HU-M09-03: solo el Administrador (RN-M09-08)."""

    permission_classes = [IsAuthenticated, PuedeConsultarAuditoria]
    serializer_class = EventoSerializer

    def get(self, request):
        p = request.query_params
        qs = EventoRepository.consultar(usuario=p.get("usuario"), accion=p.get("accion"), texto=p.get("texto"))
        pagina = self.paginate_queryset(qs)
        datos = EventoSerializer(pagina, many=True, context={"referencias": referencias(pagina)}).data
        respuesta = self.get_paginated_response(datos)
        respuesta.data["mensaje"] = None if respuesta.data["count"] else MENSAJE_SIN_EVENTOS  # CA04
        return respuesta


__all__ = ["AuditoriaView", "HistorialIngresoView"]
