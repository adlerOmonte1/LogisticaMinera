"""Resolución del motor activo desde la configuración (`RECONOCEDOR_ACTIVO`),
nunca por un `if` en el código de negocio (D-12).

El catálogo de motores vive en `settings.RECONOCEDORES`: agregar uno es escribir
su adaptador y sumar una línea de configuración. Ni este módulo ni el registro
de ingresos cambian (RNF-M04-05).
"""

import logging
import threading

from django.conf import settings
from django.utils.module_loading import import_string

log = logging.getLogger(__name__)
_instancias: dict[tuple, object] = {}
_cerrojo = threading.Lock()


def nombres_activos() -> list[str]:
    return [n.strip() for n in settings.RECONOCEDOR_ACTIVO.split(",") if n.strip()]


def crear(nombre: str):
    """Instancia un motor del catálogo. Lanza si no existe o no puede cargarse."""
    return import_string(settings.RECONOCEDORES[nombre])()


def _construir(nombres: list[str]):
    if len(nombres) == 1:
        return crear(nombres[0])
    miembros = []
    for nombre in nombres:
        try:
            miembros.append((nombre, crear(nombre)))
        except Exception:
            log.warning("El motor %s no pudo cargarse y queda fuera del respaldo", nombre, exc_info=True)
    if not miembros:
        raise RuntimeError("Ningún motor del respaldo pudo cargarse")
    return import_string(settings.RECONOCIMIENTO_COMPOSICION)(miembros)


def obtener_reconocedor():
    """El motor configurado, creado una sola vez por proceso: un modelo local
    pesa más de un gigabyte y no puede cargarse en cada registro. Si el motor no
    puede cargarse —la librería, el binario o el modelo faltan—, devuelve None y
    el registro sigue manual (RN-M04-07); el fallo no se guarda, y el siguiente
    registro vuelve a intentarlo."""
    clave = tuple(nombres_activos())
    if clave in _instancias:
        return _instancias[clave]
    with _cerrojo:
        if clave not in _instancias:
            try:
                _instancias[clave] = _construir(list(clave))
            except Exception:
                log.warning("El motor %s no está disponible", ",".join(clave), exc_info=True)
                return None
    return _instancias[clave]
