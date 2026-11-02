"""Entorno de pruebas automatizadas.

Con `TEST_DATABASE_URL` definida, las pruebas corren sobre esa base; la
integración continua la apunta a PostgreSQL 16, el motor de producción. El
modelo de la versión 2 usa funciones que SQLite no tiene —arreglos, unicidad
condicional y `select_for_update`—, y una prueba que pasa en SQLite no
garantiza nada sobre ellas.

Sin la variable, se usa la misma base de `DATABASE_URL` (pytest-django crea
su propia base `test_*`). Ya no hay alternativa en SQLite: la auditoría usa
arreglos de PostgreSQL. Lo más simple es correr las pruebas dentro del Compose:
`docker compose exec backend pytest`.
"""

from .base import *  # noqa: F401,F403
from .base import env

DEBUG = False

DATABASES = {
    "default": env.db("TEST_DATABASE_URL", default=env("DATABASE_URL")),
}

# Hashing rápido: las pruebas crean muchos usuarios y no miden criptografía.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# Las pruebas no dependen de un motor real (D-12): cada una fija lo que «lee».
RECONOCEDOR_ACTIVO = "determinista"
