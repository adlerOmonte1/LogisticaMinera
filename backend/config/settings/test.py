"""Entorno de pruebas automatizadas.

SQLite en memoria: las pruebas no dependen de un PostgreSQL levantado y corren
en cualquier máquina o en integración continua. El comportamiento de dominio
que se verifica (unicidad, FK protegida, transacciones) es idéntico en ambos
motores para lo que cubren estas pruebas.
"""

from .base import *  # noqa: F401,F403

DEBUG = False

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Hashing rápido: las pruebas crean muchos usuarios y no miden criptografía.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
