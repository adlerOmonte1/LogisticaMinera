"""Manejador uniforme de errores de la API (backend-django, "Contrato de la API").

Toda respuesta de error de la API tiene la forma:

    {"codigo": "...", "mensaje": "...", "detalles": {...}}

`mensaje` coincide literalmente con el criterio de aceptación de la historia
que protege. Las pruebas lo verifican por igualdad exacta.
"""

from rest_framework import exceptions as drf_exceptions
from rest_framework.response import Response
from rest_framework.views import exception_handler as manejador_por_defecto

from common.excepciones import (
    AccionNoAutorizada,
    ConflictoDeConcurrencia,
    ErrorDeDominio,
    ErrorDeValidacionDeDominio,
)
from common.eventos import registrador_por_defecto

_ESTADO_HTTP_POR_EXCEPCION = {
    ErrorDeValidacionDeDominio: 400,
    AccionNoAutorizada: 403,
    ConflictoDeConcurrencia: 409,
}


def _estado_http(exc: ErrorDeDominio) -> int:
    for tipo, estado in _ESTADO_HTTP_POR_EXCEPCION.items():
        if isinstance(exc, tipo):
            return estado
    return 400


def _ip_del_cliente(request) -> str | None:
    if request is None:
        return None
    adelante = request.META.get("HTTP_X_FORWARDED_FOR")
    if adelante:
        return adelante.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def manejador_uniforme(exc, context):
    """Reemplaza a `rest_framework.views.exception_handler` (ver settings)."""
    request = context.get("request")

    if isinstance(exc, ErrorDeDominio):
        if isinstance(exc, AccionNoAutorizada):
            usuario = getattr(request, "user", None)
            usuario = usuario if usuario and usuario.is_authenticated else None
            registrador_por_defecto.registrar(
                evento="ACCESO_RECHAZADO",
                usuario=usuario,
                ip=_ip_del_cliente(request),
                detalles={"ruta": request.path if request else None, **exc.detalles},
            )
        return Response(
            {"codigo": exc.codigo, "mensaje": exc.mensaje, "detalles": exc.detalles},
            status=_estado_http(exc),
        )

    respuesta = manejador_por_defecto(exc, context)
    if respuesta is None:
        return None

    if isinstance(exc, (drf_exceptions.NotAuthenticated, drf_exceptions.AuthenticationFailed)):
        respuesta.data = {"codigo": "NO_AUTENTICADO", "mensaje": "Credenciales inválidas o ausentes", "detalles": {}}
    elif isinstance(exc, drf_exceptions.PermissionDenied):
        respuesta.data = {"codigo": "ACCION_NO_AUTORIZADA", "mensaje": "Acción no autorizada", "detalles": {}}
    elif isinstance(exc, drf_exceptions.ValidationError):
        respuesta.data = {"codigo": "ERROR_DE_VALIDACION", "mensaje": "Datos inválidos", "detalles": respuesta.data}
    else:
        respuesta.data = {"codigo": "ERROR", "mensaje": str(exc), "detalles": {}}

    return respuesta
