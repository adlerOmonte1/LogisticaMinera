from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.filters import UsuarioFilter
from apps.accounts.models import Usuario
from apps.accounts.permissions import PuedeGestionarUsuarios
from apps.accounts.repositories import UsuarioRepository
from apps.accounts.serializers import (
    CambiarPasswordSerializer,
    UsuarioCreateSerializer,
    UsuarioDetailSerializer,
    UsuarioListSerializer,
    UsuarioUpdateSerializer,
)
from apps.accounts.services import usuarios as servicio

_VERDADERO = {"1", "true", "True", "si", "sí"}


class UsuarioListCreateView(generics.ListCreateAPIView):
    """`GET/POST /api/v1/usuarios/` — HU-M01-02. `?incluir_inactivos=1` muestra
    también los desactivados, para reactivarlos."""

    permission_classes = [IsAuthenticated, PuedeGestionarUsuarios]
    serializer_class = UsuarioListSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = UsuarioFilter

    def get_queryset(self):
        if self.request.query_params.get("incluir_inactivos") in _VERDADERO:
            return UsuarioRepository.listar_todos()
        return UsuarioRepository.listar_activos()

    def create(self, request, *args, **kwargs):
        entrada = UsuarioCreateSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        usuario = servicio.crear_usuario(entrada.validated_data, request.user)
        return Response(UsuarioDetailSerializer(usuario).data, status=201)


class UsuarioDetailView(generics.RetrieveUpdateAPIView):
    """`GET/PATCH /api/v1/usuarios/{id}/` — HU-M01-02. Sin PUT ni DELETE."""

    permission_classes = [IsAuthenticated, PuedeGestionarUsuarios]
    serializer_class = UsuarioDetailSerializer
    http_method_names = ["get", "patch", "head", "options"]

    def get_queryset(self):
        return UsuarioRepository.listar_todos()

    def update(self, request, *args, **kwargs):
        usuario = self.get_object()
        entrada = UsuarioUpdateSerializer(data=request.data, partial=True)
        entrada.is_valid(raise_exception=True)
        servicio.actualizar_usuario(usuario, entrada.validated_data, request.user)
        return Response(UsuarioDetailSerializer(usuario).data)


class _AccionSobreUsuario(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, PuedeGestionarUsuarios]
    serializer_class = UsuarioDetailSerializer

    def _usuario(self, pk):
        return get_object_or_404(Usuario.objects.select_related("rol"), pk=pk)


class UsuarioDesactivarView(_AccionSobreUsuario):
    """`PATCH /api/v1/usuarios/{id}/desactivar/` — HU-M01-02 CA03, CA09."""

    def patch(self, request, pk):
        usuario = servicio.desactivar_usuario(self._usuario(pk), request.user)
        return Response({"mensaje": servicio.MENSAJE_DESACTIVADO, **UsuarioDetailSerializer(usuario).data})


class UsuarioReactivarView(_AccionSobreUsuario):
    """`PATCH /api/v1/usuarios/{id}/reactivar/` — HU-M01-02 CA10."""

    def patch(self, request, pk):
        usuario = servicio.reactivar_usuario(self._usuario(pk), request.user)
        return Response({"mensaje": servicio.MENSAJE_REACTIVADO, **UsuarioDetailSerializer(usuario).data})


class UsuarioRestablecerClaveView(_AccionSobreUsuario):
    """`POST /api/v1/usuarios/{id}/restablecer-clave/` — HU-M01-02 CA08. La
    contraseña temporal viaja solo en esta respuesta."""

    def post(self, request, pk):
        usuario = self._usuario(pk)
        temporal = servicio.restablecer_clave(usuario, request.user)
        return Response({"username": usuario.username, "clave_temporal": temporal})


class CambiarPasswordView(generics.GenericAPIView):
    """`POST /api/v1/usuarios/cambiar-clave/` — HU-M01-02, HU-M01-01 CA09. Solo la propia."""

    permission_classes = [IsAuthenticated]
    serializer_class = CambiarPasswordSerializer

    def post(self, request):
        entrada = CambiarPasswordSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        servicio.cambiar_password_propia(
            request.user,
            entrada.validated_data["password_actual"],
            entrada.validated_data["password_nueva"],
            entrada.validated_data["password_nueva_confirmacion"],
        )
        return Response({"mensaje": servicio.MENSAJE_CLAVE_CAMBIADA})
