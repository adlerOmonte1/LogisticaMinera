"""Excepciones de dominio.

`models.py` y `services.py` de cualquier app lanzan estas excepciones, nunca
`rest_framework.exceptions.*`: el dominio no importa nada del transporte HTTP
(backend-django, "Excepciones de dominio"). La capa HTTP las traduce a código
de estado mediante `utils.manejador_errores.manejador_uniforme`.
"""


class ErrorDeDominio(Exception):
    """Base de toda excepción de dominio. No se lanza directamente."""

    codigo = "ERROR_DE_DOMINIO"

    def __init__(self, mensaje, *, codigo=None, detalles=None):
        self.mensaje = mensaje
        if codigo is not None:
            self.codigo = codigo
        self.detalles = detalles or {}
        super().__init__(mensaje)


class ErrorDeValidacionDeDominio(ErrorDeDominio):
    """Una regla de negocio (RN-*) se violó. Se traduce a HTTP 400."""

    codigo = "ERROR_DE_VALIDACION"


class AccionNoAutorizada(ErrorDeDominio):
    """El rol del solicitante no habilita la operación. Se traduce a HTTP 403.

    Todo lugar que lance esta excepción debe hacerlo con el mensaje literal
    "Acción no autorizada" (backend-auth-permisos) y queda registrado en
    auditoría por el manejador uniforme.
    """

    codigo = "ACCION_NO_AUTORIZADA"


class ConflictoDeConcurrencia(ErrorDeDominio):
    """Dos operaciones concurrentes chocan sobre el mismo recurso. HTTP 409."""

    codigo = "CONFLICTO_DE_CONCURRENCIA"
