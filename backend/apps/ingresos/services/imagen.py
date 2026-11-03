"""Imagen del ticket (RS-M03-01, RNF-M03-01): JPG o PNG de hasta 10 MB.

Se comprueba el contenido con Pillow, no la extensión ni el tipo que declara el
cliente. Se guarda por la API de almacenamiento de Django (D-18) antes de abrir
la transacción del registro, porque el sistema de archivos no participa del
`rollback`: una imagen huérfana se limpia; un ingreso sin imagen, no (notas de M03).
"""

import io
import uuid

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from PIL import Image, UnidentifiedImageError

from common.excepciones import ErrorDeValidacionDeDominio

from . import mensajes

_FORMATOS = {"JPEG": "jpg", "PNG": "png"}


def leer_y_validar(archivo) -> tuple[bytes, str]:
    if archivo.size > settings.TAMANO_MAXIMO_IMAGEN_TICKET:
        raise ErrorDeValidacionDeDominio(mensajes.IMAGEN_INVALIDA, codigo="IMAGEN_INVALIDA")
    contenido = archivo.read()
    try:
        figura = Image.open(io.BytesIO(contenido))
        formato = figura.format
        figura.verify()
    except (UnidentifiedImageError, OSError, SyntaxError, ValueError):
        formato = None
    if formato not in _FORMATOS:
        raise ErrorDeValidacionDeDominio(mensajes.IMAGEN_INVALIDA, codigo="IMAGEN_INVALIDA")
    return contenido, _FORMATOS[formato]


def guardar(contenido: bytes, extension: str, momento) -> str:
    ruta = f"tickets/{momento:%Y/%m}/{uuid.uuid4().hex}.{extension}"
    return default_storage.save(ruta, ContentFile(contenido))
