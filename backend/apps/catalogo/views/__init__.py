"""Controladores REST del catálogo (M02). HU-M02-01 a HU-M02-03.

Un `ViewSet` por entidad, todos con la misma forma: listar (vigentes por
defecto), crear, editar y desactivar. Sin `DELETE`: la baja es siempre lógica
(RN-M02-08). La lógica de negocio vive en `services/`; aquí solo se traduce
HTTP.
"""

from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.catalogo.filters import TipoMineralFilter, VehiculoFilter
from apps.catalogo.permissions import PuedeGestionarCatalogo
from apps.catalogo.repositories import (
    TipoMineralRepository,
    TransportistaRepository,
    VehiculoRepository,
)
from apps.catalogo.serializers import (
    TipoMineralCreateSerializer,
    TipoMineralSerializer,
    TipoMineralUpdateSerializer,
    TransportistaCreateSerializer,
    TransportistaSerializer,
    TransportistaUpdateSerializer,
    VehiculoCreateSerializer,
    VehiculoSerializer,
    VehiculoUpdateSerializer,
)
from apps.catalogo.services import tipos_mineral, transportistas, vehiculos

_VERDADERO = {"1", "true", "True", "si", "sí"}


class CatalogoViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """Compuesto por mixins explícitos, sin `DestroyModelMixin` (ISP,
    solid-proyecto): la clase no ofrece la capacidad de borrar, en vez de
    ofrecerla y bloquearla después. `http_method_names` queda solo para
    excluir `PUT` — `update()` siempre trata la edición como parcial."""

    http_method_names = ["get", "post", "patch", "head", "options"]
    permission_classes = [IsAuthenticated, PuedeGestionarCatalogo]

    repositorio = None
    serializer_salida = None
    serializer_alta = None
    serializer_edicion = None
    fn_crear = None
    fn_actualizar = None
    fn_desactivar = None

    def get_queryset(self):
        incluir_inactivos = self.request.query_params.get("incluir_inactivos") in _VERDADERO
        return self.repositorio.todos() if incluir_inactivos else self.repositorio.vigentes()

    def get_serializer_class(self):
        if self.action == "create":
            return self.serializer_alta
        if self.action in ("update", "partial_update"):
            return self.serializer_edicion
        return self.serializer_salida

    def create(self, request, *args, **kwargs):
        entrada = self.get_serializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        obj = self.fn_crear(entrada.validated_data, request.user)
        return Response(self.serializer_salida(obj).data, status=201)

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        entrada = self.get_serializer(data=request.data, partial=True)
        entrada.is_valid(raise_exception=True)
        obj = self.fn_actualizar(obj, entrada.validated_data, request.user)
        return Response(self.serializer_salida(obj).data)

    @action(detail=True, methods=["patch"])
    def desactivar(self, request, pk=None):
        obj = self.get_object()
        resultado = self.fn_desactivar(obj, request.user)
        cuerpo = self.serializer_salida(resultado).data
        mensaje = getattr(resultado, "mensaje", None)
        if mensaje:
            cuerpo = {"mensaje": mensaje, **cuerpo}
        return Response(cuerpo)


class TipoMineralViewSet(CatalogoViewSet):
    repositorio = TipoMineralRepository
    serializer_salida = TipoMineralSerializer
    serializer_alta = TipoMineralCreateSerializer
    serializer_edicion = TipoMineralUpdateSerializer
    filterset_class = TipoMineralFilter
    fn_crear = staticmethod(tipos_mineral.crear_tipo_mineral)
    fn_actualizar = staticmethod(tipos_mineral.actualizar_tipo_mineral)
    fn_desactivar = staticmethod(tipos_mineral.desactivar_tipo_mineral)


class VehiculoViewSet(CatalogoViewSet):
    repositorio = VehiculoRepository
    serializer_salida = VehiculoSerializer
    serializer_alta = VehiculoCreateSerializer
    serializer_edicion = VehiculoUpdateSerializer
    filterset_class = VehiculoFilter
    fn_crear = staticmethod(vehiculos.crear_vehiculo)
    fn_actualizar = staticmethod(vehiculos.actualizar_vehiculo)
    fn_desactivar = staticmethod(vehiculos.desactivar_vehiculo)


class TransportistaViewSet(CatalogoViewSet):
    repositorio = TransportistaRepository
    serializer_salida = TransportistaSerializer
    serializer_alta = TransportistaCreateSerializer
    serializer_edicion = TransportistaUpdateSerializer
    fn_crear = staticmethod(transportistas.crear_transportista)
    fn_actualizar = staticmethod(transportistas.actualizar_transportista)
    fn_desactivar = staticmethod(transportistas.desactivar_transportista)


__all__ = ["TipoMineralViewSet", "VehiculoViewSet", "TransportistaViewSet"]
