"""Controladores de M07 (ARQ-02 §6): solo lectura (RN-M07-09), salvo el evento
de la exportación, que registra M09."""

from django.http import FileResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework.generics import GenericAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.permissions import PuedeConsultar, PuedeExportarListado
from apps.consulta.repositories import ConsultaRepository
from apps.consulta.services import (
    ServicioExportacion,
    avisos,
    cabecera,
    calendario,
    detalle,
    fila,
    inicio,
    leer_filtros,
    mensajes,
    respaldo,
)
from apps.ingresos.models import Ingreso
from common.excepciones import ErrorDeValidacionDeDominio
from common.red import ip_del_cliente


class IngresosView(GenericAPIView):
    """Búsqueda por placa y fecha y listado con filtros: el mismo endpoint
    (HU-M07-01, HU-M07-02)."""

    permission_classes = [IsAuthenticated, PuedeConsultar]
    pagination_class = PageNumberPagination

    @extend_schema(responses=OpenApiTypes.OBJECT)
    def get(self, request):
        filtros, busqueda = leer_filtros(request.query_params, timezone.localdate())
        qs = ConsultaRepository.filtrar(filtros)
        pagina = self.paginate_queryset(qs)
        respuesta = self.get_paginated_response([fila(i) for i in pagina])
        totales = ConsultaRepository.totales(qs)
        respuesta.data["totales"] = totales
        respuesta.data["filtros"] = {"fecha_desde": filtros.desde, "fecha_hasta": filtros.hasta}
        vacio = mensajes.SIN_RESULTADOS_BUSQUEDA if busqueda else mensajes.SIN_RESULTADOS_LISTADO
        respuesta.data["mensaje"] = None if totales["ingresos"] else vacio
        return respuesta


class IngresoDetalleView(GenericAPIView):
    permission_classes = [IsAuthenticated, PuedeConsultar]

    @extend_schema(responses=OpenApiTypes.OBJECT)
    def get(self, request, pk):
        ingreso = get_object_or_404(Ingreso.objects.select_related("vehiculo", "tipo_mineral", "usuario_registro",
                                                                   "lote"), pk=pk)
        if ingreso.lote_id:
            from apps.trazabilidad.repositories import LoteRepository  # noqa: PLC0415

            ingreso.lote = LoteRepository.detalle().get(pk=ingreso.lote_id)
        return Response(detalle(ingreso, request))


class TicketView(GenericAPIView):
    """RN-M07-06: la imagen solo con sesión, nunca desde una ruta pública."""

    permission_classes = [IsAuthenticated, PuedeConsultar]

    @extend_schema(responses=OpenApiTypes.OBJECT)
    def get(self, request, pk):
        ingreso = get_object_or_404(Ingreso, pk=pk)
        estado = respaldo(ingreso)
        if estado["tipo"] != "IMAGEN":
            raise ErrorDeValidacionDeDominio(estado.get("motivo") or estado["mensaje"], codigo=estado["tipo"])
        return FileResponse(ingreso.imagen_ticket.open("rb"))


class ExportarView(GenericAPIView):
    permission_classes = [IsAuthenticated, PuedeExportarListado]

    @extend_schema(responses=OpenApiTypes.OBJECT)
    def get(self, request):
        filtros, _ = leer_filtros(request.query_params, timezone.localdate())
        filas, cantidad = ServicioExportacion().exportar(filtros, request.user, ip=ip_del_cliente(request))
        respuesta = StreamingHttpResponse(filas, content_type="text/csv; charset=utf-8")
        respuesta["Content-Disposition"] = f'attachment; filename="ingresos_{timezone.localdate():%Y%m%d}.csv"'
        respuesta["X-Total-Ingresos"] = str(cantidad)
        return respuesta


class CalendarioView(GenericAPIView):
    permission_classes = [IsAuthenticated, PuedeConsultar]

    @extend_schema(responses=OpenApiTypes.OBJECT)
    def get(self, request):
        hoy = timezone.localdate()
        p = request.query_params
        try:
            anio, mes = int(p.get("anio") or hoy.year), int(p.get("mes") or hoy.month)
        except ValueError:
            raise ErrorDeValidacionDeDominio("Datos inválidos", codigo="ERROR_DE_VALIDACION")
        return Response(calendario(anio, mes, p.get("dia")))


class CabeceraView(GenericAPIView):
    permission_classes = [IsAuthenticated, PuedeConsultar]

    @extend_schema(responses=OpenApiTypes.OBJECT)
    def get(self, request):
        return Response(cabecera(request.query_params.get("q", "")))


class InicioView(GenericAPIView):
    permission_classes = [IsAuthenticated, PuedeConsultar]

    @extend_schema(responses=OpenApiTypes.OBJECT)
    def get(self, request):
        return Response(inicio(request.user, timezone.localdate()))


class AvisosView(GenericAPIView):
    permission_classes = [IsAuthenticated, PuedeConsultar]

    @extend_schema(responses=OpenApiTypes.OBJECT)
    def get(self, request):
        return Response(avisos(request.user, timezone.localdate()))
