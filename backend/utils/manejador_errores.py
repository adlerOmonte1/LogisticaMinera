from rest_framework import exceptions as drf_exceptions
from rest_framework.response import Response
from rest_framework.views import exception_handler as manejador_por_defecto

from common.excepciones import (
    AccionNoAutorizada,
    AutenticacionFallida,
    ConflictoDeConcurrencia,
    CuentaBloqueadaTemporalmente,
    ErrorDeDominio,
    ErrorDeValidacionDeDominio,
)
from common.eventos import Accion, registrador_por_defecto
from common.red import ip_del_cliente

_ESTADO_HTTP_POR_EXCEPCION = {
    ErrorDeValidacionDeDominio: 400,
    AutenticacionFallida: 401,
    AccionNoAutorizada: 403,
    ConflictoDeConcurrencia: 409,
    CuentaBloqueadaTemporalmente: 423,
}


def _estado_http(exc: ErrorDeDominio) -> int:
    for tipo, estado in _ESTADO_HTTP_POR_EXCEPCION.items():
        if isinstance(exc, tipo):
            return estado
    return 400


def manejador_uniforme(exc, context):
    """Reemplaza a `rest_framework.views.exception_handler` (ver settings)."""
    request = context.get("request")

    if isinstance(exc, ErrorDeDominio):
        if isinstance(exc, AccionNoAutorizada):
            usuario = getattr(request, "user", None)
            usuario = usuario if usuario and usuario.is_authenticated else None
            registrador_por_defecto.registrar(
                accion=Accion.ACCESO_RECHAZADO,
                entidad="Autorizacion",
                usuario=usuario,
                ip=ip_del_cliente(request),
                valores_nuevos={
                    "ruta": request.path if request else None,
                    "metodo": request.method if request else None,
                    **exc.detalles,
                },
            )
        return Response(
            {"codigo": exc.codigo, "mensaje": exc.mensaje, "detalles": exc.detalles},
            status=_estado_http(exc),
        )

    respuesta = manejador_por_defecto(exc, context)
    if respuesta is None:
        return None

    codigo_propio = getattr(exc, "codigo_uniforme", None)
    if codigo_propio:
        # Rechazos con mensaje literal de un criterio: sesión expirada (HU-M01-01
        # CA06) y contraseña temporal pendiente (HU-M01-01 CA09).
        respuesta.data = {"codigo": codigo_propio, "mensaje": str(exc.detail), "detalles": {}}
    elif isinstance(exc, (drf_exceptions.NotAuthenticated, drf_exceptions.AuthenticationFailed)):
        respuesta.data = {"codigo": "NO_AUTENTICADO", "mensaje": "Credenciales inválidas o ausentes", "detalles": {}}
    elif isinstance(exc, drf_exceptions.PermissionDenied):
        respuesta.data = {"codigo": "ACCION_NO_AUTORIZADA", "mensaje": "Acción no autorizada", "detalles": {}}
    elif isinstance(exc, drf_exceptions.ValidationError):
        respuesta.data = {"codigo": "ERROR_DE_VALIDACION", "mensaje": "Datos inválidos", "detalles": respuesta.data}
    else:
        respuesta.data = {"codigo": "ERROR", "mensaje": str(exc), "detalles": {}}

    return respuesta
