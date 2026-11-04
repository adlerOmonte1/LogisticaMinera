"""Controladores de M08 (ARQ-02 §6): Administrativo y Administrador
(PuedeConsolidar)."""

from django.http import HttpResponse
from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.permissions import PuedeConsolidar
from apps.consolidacion.services import ServicioConsolidacion, leer_periodo
from common.red import ip_del_cliente


def _periodo(request):
    hoy = timezone.localdate()
    return leer_periodo(request.query_params.get("anio", hoy.year), request.query_params.get("mes", hoy.month))


class MensualView(GenericAPIView):
    permission_classes = [IsAuthenticated, PuedeConsolidar]

    @extend_schema(responses=OpenApiTypes.OBJECT)
    def get(self, request):
        consolidado, avisos = ServicioConsolidacion().consolidar(_periodo(request))
        return Response({
            "anio": consolidado.periodo.anio, "mes": consolidado.periodo.mes,
            "tipos_mineral": [{**f, "toneladas": str(f["toneladas"]), "participacion": str(f["participacion"])}
                              for f in consolidado.filas],
            "total_toneladas": str(consolidado.total_toneladas),
            "total_ingresos": consolidado.total_ingresos,
            "en_proceso": {"cantidad": len(consolidado.en_proceso), "codigos": consolidado.en_proceso},
            "anulados_excluidos": consolidado.anulados,
            **avisos,
        })


class ExportarView(GenericAPIView):
    permission_classes = [IsAuthenticated, PuedeConsolidar]

    @extend_schema(responses=OpenApiTypes.OBJECT)
    def get(self, request):
        periodo = _periodo(request)
        contenido, exportador = ServicioConsolidacion().exportar(periodo, request.user, ip=ip_del_cliente(request))
        respuesta = HttpResponse(contenido, content_type=exportador.tipo_contenido)
        nombre = f"consolidado_{periodo.anio}_{periodo.mes:02d}.{exportador.extension}"
        respuesta["Content-Disposition"] = f'attachment; filename="{nombre}"'
        return respuesta


__all__ = ["ExportarView", "MensualView"]
