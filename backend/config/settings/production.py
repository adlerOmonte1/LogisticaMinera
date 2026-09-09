"""Producción: entorno sobre el que se miden los indicadores operativos del sistema.

Todo despliegue posterior al inicio del periodo de medición debe registrarse: introduce un cambio
no controlado en las condiciones de medición (ARQ-02 §7).
"""

from .base import *  # noqa: F401,F403

DEBUG = False

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
X_FRAME_OPTIONS = "DENY"
