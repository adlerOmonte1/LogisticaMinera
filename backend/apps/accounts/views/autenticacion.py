"""Controladores HTTP de sesión (RF10). HU-M01-01.

Solo entrada/salida HTTP: validan el cuerpo, delegan en
`services.autenticacion` y traducen el resultado a JSON. Ninguna regla de
negocio vive aquí (solid-proyecto, SRP).
"""

from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.serializers import LoginSerializer, LogoutSerializer
from apps.accounts.services.autenticacion import autenticar, cerrar_sesion
from common.red import ip_del_cliente


def _tokens_para(usuario) -> dict:
    refresh = RefreshToken.for_user(usuario)
    return {"access": str(refresh.access_token), "refresh": str(refresh)}


class LoginView(GenericAPIView):
    """`POST /api/v1/auth/login/` — HU-M01-01."""

    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = LoginSerializer

    def post(self, request):
        entrada = LoginSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)

        usuario = autenticar(
            entrada.validated_data["username"],
            entrada.validated_data["password"],
            ip=ip_del_cliente(request),
        )

        cuerpo = _tokens_para(usuario)
        cuerpo["usuario"] = {
            "id": usuario.pk,
            "username": usuario.username,
            "nombre_completo": usuario.nombre_completo,
            "rol": usuario.rol.nombre,
            "debe_cambiar_clave": usuario.debe_cambiar_clave,
        }
        return Response(cuerpo)


class LogoutView(GenericAPIView):
    """`POST /api/v1/auth/logout/` — HU-M01-01 CA05. Invalida el refresh."""

    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = LogoutSerializer

    def post(self, request):
        entrada = LogoutSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        cerrar_sesion(entrada.validated_data["refresh"], ip=ip_del_cliente(request))
        return Response(status=204)
