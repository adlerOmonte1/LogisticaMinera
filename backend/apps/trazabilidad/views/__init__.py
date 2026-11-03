"""Controladores REST de M06 (ARQ-02 §6). Solo traducen HTTP: la lógica vive en
`ServicioLote`. Ninguna operación usa `DELETE` (D-22)."""

from django.shortcuts import get_object_or_404
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.permissions import (
    PuedeCerrarLote,
    PuedeComponerLote,
    PuedeConsultar,
    PuedeRegistrarEtapa,
)
from apps.catalogo.models import TipoMineral
from apps.ingresos.models import Ingreso
from apps.trazabilidad.dominio import Destino
from apps.trazabilidad.models import EtapaProceso, LoteProceso
from apps.trazabilidad.repositories import LoteRepository
from apps.trazabilidad.serializers import (
    AbrirLoteSerializer,
    AsignarSerializer,
    BigbagsSerializer,
    CatalogosSerializer,
    CierreSerializer,
    DivisionSerializer,
    EtapaSerializer,
    LoteListaSerializer,
    LoteSerializer,
    MineralSerializer,
    SecadoPropioSerializer,
)
from apps.trazabilidad.services import mensajes as m
from apps.trazabilidad.services import servicio_lote
from apps.trazabilidad.services.recorrido import resumen, trazabilidad

_PERMISOS = {
    "list": PuedeConsultar, "retrieve": PuedeConsultar, "resumen": PuedeConsultar,
    "create": PuedeComponerLote, "minerales": PuedeComponerLote, "quitar_mineral": PuedeComponerLote,
    "ingresos": PuedeComponerLote, "retirar": PuedeComponerLote, "iniciar_recorrido": PuedeComponerLote,
    "division": PuedeComponerLote,
    "etapas": PuedeRegistrarEtapa, "secado": PuedeRegistrarEtapa, "bigbags": PuedeRegistrarEtapa,
    "cerrar": PuedeCerrarLote,
}


class LoteViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    http_method_names = ["get", "post", "patch", "head", "options"]
    lookup_value_regex = r"\d+"

    def get_permissions(self):
        accion = self.action
        if accion == "ingresos" and self.request.method == "GET":
            accion = "retrieve"  # consultar lo disponible para asignar es una consulta
        return [IsAuthenticated(), _PERMISOS.get(accion, PuedeConsultar)()]

    def get_queryset(self):
        if self.action == "list":
            p = self.request.query_params
            return LoteRepository.listar(estado=p.get("estado"), tipo_mineral=p.get("tipo_mineral"),
                                         desde=p.get("desde"), hasta=p.get("hasta"))
        return LoteRepository.detalle()

    def get_serializer_class(self):
        return LoteListaSerializer if self.action == "list" else LoteSerializer

    def _detalle(self, id_lote, mensaje=None, status=200, **extra):
        lote = LoteRepository.detalle().get(pk=id_lote)
        return Response({"mensaje": mensaje, **extra, **LoteSerializer(lote).data}, status=status)

    def create(self, request):
        entrada = AbrirLoteSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        lote = servicio_lote.abrir(entrada.validated_data, request.user)
        return self._detalle(lote.pk, m.LOTE_ABIERTO.format(nombre=lote.nombre), status=201)

    @action(detail=True, methods=["post"])
    def minerales(self, request, pk=None):
        entrada = MineralSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        get_object_or_404(LoteProceso, pk=pk)
        servicio_lote.agregar_mineral(pk, entrada.validated_data["tipo_mineral"], request.user)
        nombre = TipoMineral.objects.get(pk=entrada.validated_data["tipo_mineral"]).nombre
        return self._detalle(pk, m.MINERAL_AGREGADO.format(mineral=nombre))

    @action(detail=True, methods=["post"], url_path=r"minerales/(?P<id_tipo>\d+)/quitar")
    def quitar_mineral(self, request, pk=None, id_tipo=None):
        get_object_or_404(LoteProceso, pk=pk)
        tipo = servicio_lote.quitar_mineral(pk, id_tipo, request.user)
        return self._detalle(pk, m.MINERAL_QUITADO.format(mineral=tipo.nombre))

    @action(detail=True, methods=["get", "post"])
    def ingresos(self, request, pk=None):
        lote = get_object_or_404(LoteProceso, pk=pk)
        if request.method == "GET":
            return Response(self._disponibles(lote))
        entrada = AsignarSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        servicio_lote.asignar(pk, entrada.validated_data["ingresos"], request.user,
                              autorizacion=entrada.validated_data["autorizacion"])
        return self._detalle(pk)

    @staticmethod
    def _disponibles(lote) -> dict:
        """HU-M06-01 CA05: los del mineral del lote aparte; los de otro tipo,
        agrupados en «Agregar de otro tipo de mineral»."""
        vigentes = {lm.tipo_mineral_id for lm in lote.lista_minerales.all() if lm.fecha_retiro is None}

        def fila(i):
            return {"id": i.pk, "codigo": i.codigo, "placa": i.vehiculo.placa,
                    "fecha_hora_pesaje": i.fecha_hora_pesaje, "peso_neto_tn": str(i.peso_neto_tn),
                    "lote_actual": i.lote.codigo if i.lote else None}

        del_lote, otros = [], {}
        for i in LoteRepository.disponibles(lote):
            if i.tipo_mineral_id in vigentes:
                del_lote.append(fila(i))
            else:
                grupo = otros.setdefault(i.tipo_mineral_id, {"tipo_mineral": {
                    "id": i.tipo_mineral_id, "codigo": i.tipo_mineral.codigo, "nombre": i.tipo_mineral.nombre},
                    "ingresos": []})
                grupo["ingresos"].append(fila(i))
        return {"ingresos": del_lote, "otros_minerales": list(otros.values())}

    @action(detail=True, methods=["post"], url_path=r"ingresos/(?P<id_ingreso>\d+)/retirar")
    def retirar(self, request, pk=None, id_ingreso=None):
        get_object_or_404(Ingreso, pk=id_ingreso, lote_id=pk)
        servicio_lote.retirar(pk, id_ingreso, request.user)
        return self._detalle(pk, m.INGRESO_RETIRADO)

    @action(detail=True, methods=["patch"], url_path="iniciar-recorrido")
    def iniciar_recorrido(self, request, pk=None):
        get_object_or_404(LoteProceso, pk=pk)
        lote = servicio_lote.iniciar_recorrido(pk, request.user)
        return self._detalle(pk, m.RECORRIDO_INICIADO.format(nombre=lote.nombre))

    @action(detail=True, methods=["post"])
    def etapas(self, request, pk=None):
        get_object_or_404(LoteProceso, pk=pk)
        entrada = EtapaSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        paso, carga, calculado = servicio_lote.registrar_etapa(pk, entrada.validated_data, request.user)
        return self._detalle(pk, m.ETAPA_REGISTRADA.format(etapa=paso.etapa.nombre, nombre=carga.nombre),
                             status=201, paso={"id": paso.pk, "etapa": paso.etapa.codigo, "carga": carga.nombre,
                                               **calculado})

    @action(detail=True, methods=["post"], url_path=r"ingresos/(?P<id_ingreso>\d+)/secado")
    def secado(self, request, pk=None, id_ingreso=None):
        ingreso = get_object_or_404(Ingreso, pk=id_ingreso, lote_id=pk)
        entrada = SecadoPropioSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        servicio_lote.registrar_secado_propio(pk, ingreso.pk, entrada.validated_data, request.user)
        return self._detalle(pk, m.SECADO_PROPIO.format(codigo=ingreso.codigo), status=201)

    @action(detail=True, methods=["post"])
    def bigbags(self, request, pk=None):
        get_object_or_404(LoteProceso, pk=pk)
        entrada = BigbagsSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        registro = servicio_lote.asociar_bigbags(pk, entrada.validated_data, request.user)
        return self._detalle(pk, m.BIGBAGS_ASOCIADOS.format(cantidad=registro["cantidad"]), status=201,
                             registro=registro)

    @action(detail=True, methods=["post"])
    def division(self, request, pk=None):
        get_object_or_404(LoteProceso, pk=pk)
        entrada = DivisionSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        partes = servicio_lote.dividir(pk, entrada.validated_data["partes"], request.user)
        return self._detalle(pk, m.LOTE_DIVIDIDO.format(n=len(partes)), status=201)

    @action(detail=True, methods=["get"])
    def resumen(self, request, pk=None):
        """HU-M06-05 CA06: el resumen que se confirma antes de cerrar."""
        return Response(resumen(LoteRepository.detalle().get(pk=get_object_or_404(LoteProceso, pk=pk).pk)))

    @action(detail=True, methods=["patch"])
    def cerrar(self, request, pk=None):
        get_object_or_404(LoteProceso, pk=pk)
        entrada = CierreSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        lote = servicio_lote.cerrar(pk, entrada.validated_data["destino"] or None, request.user,
                                    observacion=entrada.validated_data["observacion"])
        return self._detalle(pk, m.LOTE_CERRADO_CON_DESTINO.format(
            nombre=lote.nombre, destino=Destino(lote.destino).label.lower()))


class TrazabilidadIngresoView(GenericAPIView):
    """HU-M06-03: los tres roles."""

    permission_classes = [IsAuthenticated, PuedeConsultar]

    @extend_schema(responses=OpenApiTypes.OBJECT)
    def get(self, request, pk):
        ingreso = get_object_or_404(Ingreso.objects.select_related("lote"), pk=pk)
        if ingreso.lote_id:
            ingreso.lote = LoteRepository.detalle().get(pk=ingreso.lote_id)
        return Response(trazabilidad(ingreso))


class EtapasView(GenericAPIView):
    permission_classes = [IsAuthenticated, PuedeConsultar]

    @extend_schema(responses=OpenApiTypes.OBJECT)
    def get(self, request):
        return Response([{"codigo": e.codigo, "nombre": e.nombre, "orden": e.orden}
                         for e in EtapaProceso.objects.order_by("orden")])


class RutasView(GenericAPIView):
    permission_classes = [IsAuthenticated, PuedeConsultar]

    @extend_schema(responses=OpenApiTypes.OBJECT)
    def get(self, request):
        return Response({"rutas": CatalogosSerializer.rutas(), "destinos": CatalogosSerializer.destinos()})


__all__ = ["EtapasView", "LoteViewSet", "RutasView", "TrazabilidadIngresoView"]
