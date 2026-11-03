"""Controladores REST de M03 (ARQ-02 §6). Solo traducen HTTP: la lógica vive en
`ServicioIngreso`. M03 no expone un listado general (D-19): el recurso de un
ingreso y la lista de pendientes de destare. Sin `DELETE` (RN-M03-14, D-22)."""

from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.permissions import (
    PuedeAnularIngreso,
    PuedeConsultar,
    PuedeCorregirIngreso,
    PuedeRegistrarDestare,
    PuedeRegistrarIngreso,
)
from apps.ingresos.models import Ingreso
from apps.ingresos.repositories import IngresoRepository
from apps.ingresos.serializers import (
    AnulacionEntradaSerializer,
    BorradorEntradaSerializer,
    CorreccionEntradaSerializer,
    DestareEntradaSerializer,
    IngresoSerializer,
    PendienteDestareSerializer,
    RegistroEntradaSerializer,
    ReversionEntradaSerializer,
)
from apps.ingresos.services import DatosConfirmados, mensajes, servicio_por_defecto
from apps.catalogo.models import Vehiculo
from common.red import ip_del_cliente

_PERMISOS = {
    "list": PuedeConsultar,
    "retrieve": PuedeConsultar,
    "imagen": PuedeConsultar,
    "borradores": PuedeRegistrarIngreso,
    "create": PuedeRegistrarIngreso,
    "partial_update": PuedeCorregirIngreso,
    "revertir_correccion": PuedeCorregirIngreso,
    "anular": PuedeAnularIngreso,
    "destares": PuedeRegistrarDestare,
}


class IngresoViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    http_method_names = ["get", "post", "patch", "head", "options"]
    lookup_value_regex = r"\d+"
    serializer_class = IngresoSerializer
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get_permissions(self):
        return [IsAuthenticated(), _PERMISOS.get(self.action, PuedeConsultar)()]

    def get_queryset(self):
        return IngresoRepository.detalle()

    def _respuesta(self, ingreso, mensaje, status=200):
        ingreso = IngresoRepository.detalle().get(pk=ingreso.pk)
        return Response({"mensaje": mensaje, **IngresoSerializer(ingreso, context={"request": self.request}).data},
                        status=status)

    def list(self, request):
        """Pendientes de destare (HU-M03-04 CA06 y CA10, RNF-M03-15)."""
        pendientes = IngresoRepository.pendientes_de_destare()
        vehiculos = {}
        for i in pendientes:
            v = vehiculos.setdefault(i.vehiculo_id, {"id": i.vehiculo_id, "placa": i.vehiculo.placa, "ingresos": 0})
            v["ingresos"] += 1
        return Response({
            "count": len(pendientes),
            "mensaje": None if pendientes else mensajes.SIN_PENDIENTES,
            "vehiculos": list(vehiculos.values()),
            "results": PendienteDestareSerializer(pendientes, many=True).data,
        })

    @action(detail=False, methods=["post"], parser_classes=[MultiPartParser, FormParser, JSONParser])
    def borradores(self, request):
        entrada = BorradorEntradaSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        d = entrada.validated_data
        propuesta = servicio_por_defecto().iniciar_registro(
            request.user,
            archivo=d.get("imagen"),
            sin_foto=d["sin_foto"],
            motivo=d["motivo_sin_respaldo"] or None,
        )
        return Response(propuesta)

    def create(self, request):
        entrada = RegistroEntradaSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        d = entrada.validated_data
        ingreso = servicio_por_defecto().registrar_ingreso(
            request.user,
            d["borrador"],
            DatosConfirmados(
                placa=d.get("placa"),
                fecha=d.get("fecha"),
                hora=d.get("hora"),
                peso_bruto_tn=d.get("peso_bruto_tn"),
                tipo_mineral=d.get("tipo_mineral"),
                justificaciones=d.get("justificaciones"),
            ),
            ip=ip_del_cliente(request),
        )
        if ingreso.estado == Ingreso.EN_PROCESO:
            mensaje = mensajes.REGISTRADO_EN_PROCESO.format(codigo=ingreso.codigo, placa=ingreso.vehiculo.placa)
        else:
            mensaje = mensajes.REGISTRADO.format(codigo=ingreso.codigo)
        return self._respuesta(ingreso, mensaje, status=201)

    def partial_update(self, request, pk=None):
        ingreso = self.get_object()
        entrada = CorreccionEntradaSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        d = entrada.validated_data
        cambios = {k: d[k] for k in ("placa", "fecha", "hora", "peso_bruto_tn", "tipo_mineral") if d.get(k) is not None}
        ingreso = servicio_por_defecto().corregir_ingreso(
            ingreso.pk, cambios, d["motivo"], request.user,
            justificaciones=d.get("justificaciones"), ip=ip_del_cliente(request),
        )
        return self._respuesta(ingreso, mensajes.ACTUALIZADO.format(codigo=ingreso.codigo))

    @action(detail=True, methods=["post"], url_path="revertir-correccion")
    def revertir_correccion(self, request, pk=None):
        ingreso = self.get_object()
        entrada = ReversionEntradaSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        d = entrada.validated_data
        ingreso = servicio_por_defecto().revertir_correccion(
            ingreso.pk, d["motivo"], request.user, correccion=d.get("correccion"),
            justificaciones=d.get("justificaciones"), ip=ip_del_cliente(request),
        )
        return self._respuesta(ingreso, mensajes.REVERTIDA.format(codigo=ingreso.codigo))

    @action(detail=True, methods=["patch"])
    def anular(self, request, pk=None):
        ingreso = self.get_object()
        entrada = AnulacionEntradaSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        ingreso = servicio_por_defecto().anular_ingreso(
            ingreso.pk, entrada.validated_data["motivo"], request.user, ip=ip_del_cliente(request)
        )
        return self._respuesta(ingreso, mensajes.ANULADO.format(codigo=ingreso.codigo))

    @action(detail=False, methods=["post"])
    def destares(self, request):
        entrada = DestareEntradaSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        d = entrada.validated_data
        get_object_or_404(Vehiculo, pk=d["vehiculo"])
        vehiculo, completados = servicio_por_defecto().registrar_destare(
            d["vehiculo"], d.get("tara_tn"), request.user,
            fecha_destare=d.get("fecha_destare"), justificaciones=d.get("justificaciones"),
            ip=ip_del_cliente(request),
        )
        return Response({
            "mensaje": mensajes.DESTARE_REGISTRADO,
            "vehiculo": {"id": vehiculo.pk, "placa": vehiculo.placa, "tara_tn": str(vehiculo.tara_tn),
                         "fecha_destare": vehiculo.fecha_destare},
            "ingresos": [
                {"id": i.pk, "codigo": i.codigo, "peso_bruto_tn": str(i.peso_bruto_tn),
                 "peso_neto_tn": str(i.peso_neto_tn), "estado": i.estado}
                for i in completados
            ],
        }, status=201)

    @action(detail=True, methods=["get"])
    def imagen(self, request, pk=None):
        """La imagen solo se entrega con sesión (RNF-M03-11): no hay ruta pública."""
        ingreso = self.get_object()
        if not ingreso.imagen_ticket:
            raise Http404
        return FileResponse(ingreso.imagen_ticket.open("rb"))


__all__ = ["IngresoViewSet"]
