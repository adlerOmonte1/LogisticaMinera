"""Consulta del dato reconocido frente al confirmado (HU-M04-02). Los tres roles
(DR-31); solo lectura. El reconocimiento no se expone como endpoint propio de
escritura: lo invoca M03 (requerimientos funcionales de M04)."""

from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import PuedeConsultar
from apps.reconocimiento.repositories import ReconocimientoRepository
from apps.reconocimiento.serializers import ReconocimientoSerializer

_VERDADERO = {"1", "true", "si", "sí"}


class ReconocimientoViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated, PuedeConsultar]
    serializer_class = ReconocimientoSerializer

    def get_queryset(self):
        if self.action != "list":
            return ReconocimientoRepository.base()
        p = self.request.query_params
        corregidos = p.get("corregidos")
        return ReconocimientoRepository.listar(
            desde=p.get("desde"),
            hasta=p.get("hasta"),
            motor=p.get("motor"),
            corregidos=None if corregidos is None else corregidos.lower() in _VERDADERO,
        )


__all__ = ["ReconocimientoViewSet"]
