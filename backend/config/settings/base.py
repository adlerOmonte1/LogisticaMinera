"""Configuración común a todos los entornos.

No leer variables sensibles fuera de `env`: el entorno debe ser reproducible desde `.env.example`.
"""

from datetime import timedelta
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env(
    DEBUG=(bool, False),
    JWT_ACCESS_MINUTES=(int, 30),
    JWT_REFRESH_DAYS=(int, 7),
)
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("DJANGO_SECRET_KEY")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])

# --- Aplicaciones -----------------------------------------------------------

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework_simplejwt",
    "django_filters",
    "corsheaders",
    "drf_spectacular",
    "rest_framework_simplejwt.token_blacklist",  # HU-M01-02: invalidación de refresh en logout
]

# Una app por módulo (ARQ-01). El orden espeja el código del módulo.
LOCAL_APPS = [
    "apps.accounts",        # M01 Autenticación y roles
    "apps.catalogo",        # M02 Catálogo maestro
    "apps.ingresos",        # M03 Registro de ingresos
    "apps.reconocimiento",  # M04 Reconocimiento automático del ticket
    "apps.validacion",      # M05 Validación automática de consistencia
    "apps.trazabilidad",    # M06 Trazabilidad del proceso
    "apps.consulta",        # M07 Consulta de ingresos y respaldo — app de lectura (D-10)
    "apps.consolidacion",   # M08 Consolidación de la producción — app de lectura (D-10)
    "apps.auditoria",       # M09 Auditoría
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# --- Base de datos ----------------------------------------------------------

DATABASES = {"default": env.db("DATABASE_URL")}

# Fijado antes del primer `migrate` (cambiarlo después obliga a recrear la base).
AUTH_USER_MODEL = "accounts.Usuario"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- Localización -----------------------------------------------------------
# America/Lima no es cosmético: las tres marcas de tiempo del ingreso (D-01) se
# comparan entre sí y con la hora real de la planta. Un desfase de zona horaria
# las desalinea sin que ninguna prueba lo note.

LANGUAGE_CODE = "es-pe"
TIME_ZONE = "America/Lima"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Imágenes del ticket ------------------------------------------------------
# Se guardan por la API de almacenamiento de Django (D-18). Provisionalmente en
# el volumen `media` del mismo backend (D-14); cambiar de medio es cambiar
# `STORAGES`, no el código. MEDIA_URL no se publica: la imagen solo se entrega
# por la vista de M07 que comprueba la sesión (RN-M07-06).
MEDIA_ROOT = env.path("MEDIA_ROOT", default=BASE_DIR / "media")
MEDIA_URL = "media/"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}

# RS-M03-01: imagen JPG o PNG de hasta 10 MB. Nginx debe admitir el mismo límite
# (skill despliegue-docker).
TAMANO_MAXIMO_IMAGEN_TICKET = 10 * 1024 * 1024

# --- API --------------------------------------------------------------------

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "apps.accounts.autenticacion.AutenticacionJWT",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
    "PAGE_SIZE": 25,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    # Provisional: se reemplaza por utils.paginacion.PaginacionEstandar al escribir utils/.
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "EXCEPTION_HANDLER": "utils.manejador_errores.manejador_uniforme",
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=env("JWT_ACCESS_MINUTES")),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=env("JWT_REFRESH_DAYS")),
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Sistema web inteligente para el control de inventarios de ingreso de mineral",
    "DESCRIPTION": "API REST — módulos M01 a M09 (línea base 2.1)",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])

# Patrón de placa vehicular (D-24). Lo usan el alta de vehículos de M02 y la
# regla V3 de M05; se cambia por configuración, no en el código (RNF-M05-08).
PATRON_PLACA = env("PATRON_PLACA", default=r"^[A-Z0-9]{3}-[A-Z0-9]{3}$")

# --- Reconocimiento del ticket (M04) -----------------------------------------
# Catálogo de motores (D-12, RNF-M04-05): nombre -> adaptador. Agregar un motor
# es escribir su adaptador en `apps/reconocimiento/motores/` y sumar aquí una
# línea; el registro de ingresos no cambia.
RECONOCEDORES = {
    "determinista": "apps.reconocimiento.motores.determinista.ReconocedorDeterminista",
    "tesseract": "apps.reconocimiento.motores.tesseract.ReconocedorTesseract",
    "trocr": "apps.reconocimiento.motores.trocr_local.ReconocedorTrOCR",
}
# Motor activo: un nombre, o varios separados por coma en orden de respaldo
# («nube,trocr»): si el primero no está disponible, lee el siguiente. Las pruebas
# usan el determinista.
RECONOCEDOR_ACTIVO = env("RECONOCEDOR_ACTIVO", default="tesseract")
RECONOCIMIENTO_COMPOSICION = "apps.reconocimiento.motores.compuesto.ReconocedorConRespaldo"
# Ventana de operación controlada (D-16): el motor y su versión quedan fijos
# (RN-M04-05). Con esta marca, la verificación de Django rechaza más de un motor.
RECONOCIMIENTO_VENTANA_CONTROLADA = env.bool("RECONOCIMIENTO_VENTANA_CONTROLADA", default=False)
RECONOCIMIENTO_UMBRAL_CONFIANZA = env.float("RECONOCIMIENTO_UMBRAL_CONFIANZA", default=0.80)
RECONOCIMIENTO_TIEMPO_ESPERA_S = env.int("RECONOCIMIENTO_TIEMPO_ESPERA_S", default=10)
# Tiempo de cada motor dentro de un respaldo; el que no figura recibe una parte
# igual del tiempo total.
RECONOCIMIENTO_TIEMPO_POR_MOTOR = env.dict("RECONOCIMIENTO_TIEMPO_POR_MOTOR", cast={"value": float}, default={})
OCR_IDIOMA = env("OCR_IDIOMA", default="eng")

# Modelo local entrenado (laboratorio/ocr-manuscrito). No se versiona en git: se
# provisiona con `manage.py obtener_modelo` y se verifica por su hash (RN-M04-04).
TROCR_MODELO_DIR = env.path("TROCR_MODELO_DIR", default=BASE_DIR / "modelos" / "trocr-ticket-v1")
TROCR_MODELO_SHA256 = env("TROCR_MODELO_SHA256", default="35598224867a")
TROCR_HACES = env.int("TROCR_HACES", default=1)
TROCR_HILOS = env.int("TROCR_HILOS", default=0)
