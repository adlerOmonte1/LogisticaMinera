"""Producción: entorno donde se recolecta el postest de la tesis.

Todo despliegue posterior al inicio de la ventana de observación debe registrarse: introduce una
amenaza a la validez interna (ARQ-02 §7).
"""

from .base import *  # noqa: F401,F403

DEBUG = False

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
X_FRAME_OPTIONS = "DENY"
