"""Entorno de desarrollo local. Base de datos con datos de prueba."""

from .base import *  # noqa: F401,F403

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# El registro de auditoría (inicio de sesión, rechazos de autorización) se
# emite por el logger "auditoria". Mientras M08 no exista, en desarrollo se
# vuelca a la consola para poder verificarlo desde la ventana de `runserver`.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "consola": {"class": "logging.StreamHandler"},
    },
    "loggers": {
        "auditoria": {"handlers": ["consola"], "level": "INFO", "propagate": False},
    },
}
