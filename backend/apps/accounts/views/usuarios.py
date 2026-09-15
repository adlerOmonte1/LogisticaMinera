from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

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
from apps.accounts.services.usuarios import (
    actualizar_usuario,
    cambiar_password_propia,
    crear_usuario,
    desactivar_usuario,
)


class UsuarioListCreateView(generics.ListCreateAPIView):
    """`GET/POST /api/v1/usuarios/` — HU-M01-03 CA01, CA02, CA04."""

    permission_classes = [IsAuthenticated, PuedeGestionarUsuarios]
    serializer_class = UsuarioListSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = UsuarioFilter

    def get_queryset(self):
        return UsuarioRepository.listar_activos()

    def create(self, request, *args, **kwargs):
        entrada = UsuarioCreateSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        usuario = crear_usuario(entrada.validated_data)
        return Response(UsuarioDetailSerializer(usuario).data, status=201)


class UsuarioDetailView(generics.RetrieveUpdateAPIView):
    """`GET/PATCH /api/v1/usuarios/{id}/` — HU-M01-04. Sin PUT ni DELETE."""

    permission_classes = [IsAuthenticated, PuedeGestionarUsuarios]
    serializer_class = UsuarioDetailSerializer
    http_method_names = ["get", "patch", "head", "options"]

    def get_queryset(self):
        return Usuario.objects.select_related("rol").all()

    def update(self, request, *args, **kwargs):
        usuario = self.get_object()
        entrada = UsuarioUpdateSerializer(data=request.data, partial=True)
        entrada.is_valid(raise_exception=True)
        actualizar_usuario(usuario, entrada.validated_data)
        return Response(UsuarioDetailSerializer(usuario).data)


class UsuarioDesactivarView(APIView):
    """`PATCH /api/v1/usuarios/{id}/desactivar/` — HU-M01-03 CA03. Baja lógica."""

    permission_classes = [IsAuthenticated, PuedeGestionarUsuarios]

    def patch(self, request, pk):
        usuario = get_object_or_404(Usuario.objects.select_related("rol"), pk=pk)
        desactivar_usuario(usuario)
        return Response(UsuarioDetailSerializer(usuario).data)


class CambiarPasswordView(APIView):
    """`POST /api/v1/usuarios/cambiar-clave/` — HU-M01-05. Solo la propia."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        entrada = CambiarPasswordSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        cambiar_password_propia(
            request.user,
            entrada.validated_data["password_actual"],
            entrada.validated_data["password_nueva"],
        )
        return Response(status=204)
