"""Casos de uso de vehículos (RS-M02-02, RS-M02-03, RS-M02-04). HU-M02-02.

Aquí viven RN-M02-02 a RN-M02-05: la unicidad de placa, la titularidad
obligatoria y la coherencia titularidad ↔ transportista.
"""

from apps.catalogo.models import Transportista, Vehiculo
from apps.catalogo.repositories import VehiculoRepository
from common.excepciones import ErrorDeValidacionDeDominio

from ._eventos import registrar_evento
from .validadores import validar_placa

MENSAJE_PLACA_DUPLICADA = "La placa ya está registrada"
MENSAJE_EXTERNO_SIN_TRANSPORTISTA = "Debe indicar el transportista para un vehículo externo"
MENSAJE_TITULARIDAD_INVALIDA = "La titularidad debe ser PROPIO o EXTERNO"


def _resolver_transportista(datos: dict) -> Transportista | None:
    valor = datos.get("transportista")
    if valor in (None, ""):
        return None
    if isinstance(valor, Transportista):
        return valor
    return Transportista.objects.filter(pk=valor).first()


def _validar_coherencia(titularidad: str, transportista: Transportista | None) -> None:
    if titularidad not in (Vehiculo.PROPIO, Vehiculo.EXTERNO):
        raise ErrorDeValidacionDeDominio(MENSAJE_TITULARIDAD_INVALIDA, codigo="TITULARIDAD_INVALIDA")
    if titularidad == Vehiculo.EXTERNO and transportista is None:
        raise ErrorDeValidacionDeDominio(
            MENSAJE_EXTERNO_SIN_TRANSPORTISTA, codigo="EXTERNO_SIN_TRANSPORTISTA"
        )
    # RN-M02-05: un vehículo propio nunca lleva transportista; se ignora el valor
    # recibido en lugar de rechazar, para no penalizar un formulario que dejó el
    # campo con un resto de selección previa.


def crear_vehiculo(datos: dict, usuario) -> Vehiculo:
    placa = validar_placa(datos["placa"])
    if VehiculoRepository.existe_placa(placa):
        raise ErrorDeValidacionDeDominio(MENSAJE_PLACA_DUPLICADA, codigo="PLACA_DUPLICADA")

    titularidad = datos["tipo_titularidad"]
    transportista = _resolver_transportista(datos)
    _validar_coherencia(titularidad, transportista)
    if titularidad == Vehiculo.PROPIO:
        transportista = None

    vehiculo = Vehiculo(
        placa=placa,
        tipo_titularidad=titularidad,
        capacidad_tn=datos["capacidad_tn"],
        transportista=transportista,
    )
    vehiculo.full_clean()
    vehiculo.save()
    registrar_evento("CREADO", "Vehiculo", vehiculo, usuario)
    return vehiculo


def actualizar_vehiculo(vehiculo: Vehiculo, datos: dict, usuario) -> Vehiculo:
    if "placa" in datos:
        placa = validar_placa(datos["placa"])
        if VehiculoRepository.existe_placa(placa, excluir_id=vehiculo.pk):
            raise ErrorDeValidacionDeDominio(MENSAJE_PLACA_DUPLICADA, codigo="PLACA_DUPLICADA")
        vehiculo.placa = placa
    if "capacidad_tn" in datos:
        vehiculo.capacidad_tn = datos["capacidad_tn"]

    titularidad = datos.get("tipo_titularidad", vehiculo.tipo_titularidad)
    transportista = (
        _resolver_transportista(datos) if "transportista" in datos else vehiculo.transportista
    )
    _validar_coherencia(titularidad, transportista)
    vehiculo.tipo_titularidad = titularidad
    vehiculo.transportista = None if titularidad == Vehiculo.PROPIO else transportista

    vehiculo.full_clean()
    vehiculo.save()
    registrar_evento("MODIFICADO", "Vehiculo", vehiculo, usuario)
    return vehiculo


def desactivar_vehiculo(vehiculo: Vehiculo, usuario) -> Vehiculo:
    vehiculo.activo = False
    vehiculo.save(update_fields=["activo"])
    registrar_evento("DESACTIVADO", "Vehiculo", vehiculo, usuario)
    return vehiculo
