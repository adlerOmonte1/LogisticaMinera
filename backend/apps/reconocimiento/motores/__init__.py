"""Resolución del motor activo desde la configuración (`RECONOCEDOR_ACTIVO`),
nunca por un `if` en el código de negocio (D-12).

Cambiar de motor es añadir su adaptador a `MOTORES` y cambiar la variable de
entorno: M03 no cambia.
"""

from django.conf import settings
from django.utils.module_loading import import_string

MOTORES = {
    "determinista": "apps.reconocimiento.motores.determinista.ReconocedorDeterminista",
    "tesseract": "apps.reconocimiento.motores.tesseract.ReconocedorTesseract",
}


def obtener_reconocedor():
    """Instancia el motor configurado. Si el motor no puede cargarse —la librería
    o el binario no están instalados—, devuelve None y el registro sigue manual
    (RN-M04-07)."""
    try:
        return import_string(MOTORES[settings.RECONOCEDOR_ACTIVO])()
    except Exception:
        return None
