"""Autenticación JWT del sistema (HU-M01-01, HU-M01-03).

Extiende la de SimpleJWT en tres puntos:

- El usuario se lee de la base en cada solicitud, así que un cambio de rol se
  aplica en la siguiente acción y no al expirar el token (HU-M01-03 CA03).
- Un token vencido responde con el mensaje literal de HU-M01-01 CA06. El access
  dura `JWT_ACCESS_MINUTES`, que es la ventana de inactividad: el cliente solo
  lo renueva mientras el usuario trabaja.
- Una cuenta con `debe_cambiar_clave` solo puede cambiar su contraseña o cerrar
  sesión (RS-M01-13, HU-M01-01 CA09).
"""

from rest_framework import exceptions, status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken

MENSAJE_SESION_EXPIRADA = "Su sesión ha expirado. Ingrese nuevamente"
MENSAJE_CLAVE_TEMPORAL = "Debe cambiar la contraseña temporal antes de continuar"

RUTAS_CON_CLAVE_TEMPORAL = {"cambiar-clave", "logout"}


class SesionExpirada(exceptions.AuthenticationFailed):
    codigo_uniforme = "SESION_EXPIRADA"
    default_detail = MENSAJE_SESION_EXPIRADA


class ClaveTemporalPendiente(exceptions.APIException):
    status_code = status.HTTP_403_FORBIDDEN
    codigo_uniforme = "CLAVE_TEMPORAL_PENDIENTE"
    default_detail = MENSAJE_CLAVE_TEMPORAL


class AutenticacionJWT(JWTAuthentication):
    def get_validated_token(self, raw_token):
        try:
            return super().get_validated_token(raw_token)
        except InvalidToken as exc:
            if "expir" in str(exc.detail).lower():
                raise SesionExpirada() from exc
            raise

    def authenticate(self, request):
        resultado = super().authenticate(request)
        if resultado is None:
            return None
        usuario, token = resultado
        if usuario.debe_cambiar_clave:
            ruta = getattr(request._request.resolver_match, "url_name", None)
            if ruta not in RUTAS_CON_CLAVE_TEMPORAL:
                raise ClaveTemporalPendiente()
        return usuario, token
