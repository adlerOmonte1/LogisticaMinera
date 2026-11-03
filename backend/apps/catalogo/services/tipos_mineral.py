"""Casos de uso del catálogo de tipos de mineral. HU-M02-02.

RN-M02-06 y RN-M02-16 (código único, de 2 a 6 letras o números, inmutable),
RN-M02-15 (nombre único sin distinguir mayúsculas), RN-M02-17 (alta desde el
registro con código generado) y RN-M02-19 (reactivación).
"""

import re
import unicodedata

from django.db import transaction

from apps.catalogo.models import TipoMineral
from apps.catalogo.repositories import TipoMineralRepository
from common.excepciones import ErrorDeValidacionDeDominio

from ._eventos import cambiar_estado, registrar_creacion, registrar_edicion

MENSAJE_CODIGO_DUPLICADO = "El código ya está registrado"
MENSAJE_CODIGO_INVALIDO = "El código debe tener de 2 a 6 letras o números"
MENSAJE_NOMBRE_DUPLICADO = "Ya existe un tipo de mineral con ese nombre"
MENSAJE_NOMBRE_OBLIGATORIO = "Debe indicar el nombre del tipo de mineral"
MENSAJE_CAMPOS_OBLIGATORIOS = "Debe completar los campos obligatorios"
MENSAJE_DESACTIVADO_CON_INGRESOS = "El tipo de mineral se desactivó porque tiene ingresos registrados"
# Sin un mensaje propio en el criterio, la baja y la reactivación usan el
# genérico de la maqueta.
MENSAJE_DESACTIVADO = "Cambios guardados"
MENSAJE_REACTIVADO = "Cambios guardados"

_CODIGO = re.compile(r"^[A-Z0-9]{2,6}$")
_PALABRAS_VACIAS = {"DE", "DEL", "LA", "EL", "TIPO", "Y"}


def _sin_tildes(texto: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn")


def generar_codigo(nombre: str) -> str:
    """Iniciales de las palabras significativas del nombre, completadas y
    numeradas hasta no repetirse (RN-M02-17)."""
    palabras = [p for p in re.split(r"[^A-Z0-9]+", _sin_tildes(nombre).upper()) if p]
    utiles = [p for p in palabras if p not in _PALABRAS_VACIAS] or palabras or ["MIN"]
    base = "".join(p[0] for p in utiles)[:4]
    if len(base) < 2:
        base = (utiles[0] + "XX")[:3]
    codigo, n = base, 1
    while TipoMineralRepository.existe_codigo(codigo):
        n += 1
        codigo = f"{base[:6 - len(str(n))]}{n}"
    return codigo


def _validar_nombre(nombre: str, *, excluir_id=None) -> str:
    nombre = (nombre or "").strip()
    if not nombre:
        raise ErrorDeValidacionDeDominio(MENSAJE_NOMBRE_OBLIGATORIO, codigo="NOMBRE_OBLIGATORIO")
    if TipoMineralRepository.existe_nombre(nombre, excluir_id=excluir_id):
        raise ErrorDeValidacionDeDominio(MENSAJE_NOMBRE_DUPLICADO, codigo="NOMBRE_DUPLICADO")
    return nombre


def crear_tipo_mineral(datos: dict, usuario, *, desde_registro: bool | None = None) -> TipoMineral:
    """HU-M02-02 CA01, CA02, CA05 a CA08. Desde el registro el código es
    opcional y, si falta, lo genera el sistema."""
    if desde_registro is None:
        desde_registro = bool(datos.get("desde_registro"))
    nombre = _validar_nombre(datos.get("nombre"))
    codigo = (datos.get("codigo") or "").strip().upper()
    if not codigo:
        if not desde_registro:
            raise ErrorDeValidacionDeDominio(MENSAJE_CAMPOS_OBLIGATORIOS, codigo="CAMPOS_OBLIGATORIOS")
        codigo = generar_codigo(nombre)
    if not _CODIGO.match(codigo):
        raise ErrorDeValidacionDeDominio(MENSAJE_CODIGO_INVALIDO, codigo="CODIGO_INVALIDO")
    if TipoMineralRepository.existe_codigo(codigo):
        raise ErrorDeValidacionDeDominio(MENSAJE_CODIGO_DUPLICADO, codigo="CODIGO_DUPLICADO")

    with transaction.atomic():
        tipo = TipoMineral(
            codigo=codigo, nombre=nombre,
            unidad_medida=datos.get("unidad_medida", TipoMineral.TONELADA),
        )
        tipo.full_clean()
        tipo.save()
        registrar_creacion(
            "TipoMineral", tipo, usuario,
            nuevos={"codigo": codigo, "nombre": nombre, "desde_registro": desde_registro},
        )
    return tipo


def actualizar_tipo_mineral(tipo: TipoMineral, datos: dict, usuario) -> TipoMineral:
    """El código no se modifica tras el alta (RN-M02-16): solo el nombre."""
    anterior = tipo.nombre
    if "nombre" in datos:
        tipo.nombre = _validar_nombre(datos["nombre"], excluir_id=tipo.pk)
    with transaction.atomic():
        tipo.full_clean()
        tipo.save()
        registrar_edicion("TipoMineral", tipo, usuario, {"nombre": anterior}, {"nombre": tipo.nombre})
    return tipo


def desactivar_tipo_mineral(tipo: TipoMineral, usuario) -> TipoMineral:
    """HU-M02-02 CA03. Nunca se elimina (RN-M02-08)."""
    with transaction.atomic():
        cambiar_estado("TipoMineral", tipo, usuario, False)
    tipo.mensaje = MENSAJE_DESACTIVADO_CON_INGRESOS if tipo.ingresos.exists() else MENSAJE_DESACTIVADO
    return tipo


def reactivar_tipo_mineral(tipo: TipoMineral, usuario) -> TipoMineral:
    """HU-M02-02 CA09."""
    with transaction.atomic():
        cambiar_estado("TipoMineral", tipo, usuario, True)
    tipo.mensaje = MENSAJE_REACTIVADO
    return tipo
