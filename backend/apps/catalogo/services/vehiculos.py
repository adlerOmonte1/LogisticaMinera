"""Casos de uso de vehículos. HU-M02-01.

RN-M02-01 a RN-M02-05 (placa, titularidad, transportista, capacidad),
RN-M02-11 a RN-M02-13 (tara), RN-M02-14 (el alta desde el registro usa este
mismo servicio) y RN-M02-19 (la reactivación conserva la tara).
"""

from decimal import Decimal

from django.db import transaction

from apps.catalogo.models import Transportista, Vehiculo
from apps.catalogo.models.vehiculo import MENSAJE_PROPIO_CON_TRANSPORTISTA
from apps.catalogo.repositories import VehiculoRepository
from common.excepciones import ConflictoDeConcurrencia, ErrorDeValidacionDeDominio

from ._eventos import cambiar_estado, registrar_creacion, registrar_edicion, registrar_modificacion
from .validadores import validar_placa

MENSAJE_PLACA_DUPLICADA = "La placa ya está registrada"
MENSAJE_EXTERNO_SIN_TRANSPORTISTA = "Debe indicar el transportista para un vehículo externo"
MENSAJE_TITULARIDAD_INVALIDA = "La titularidad debe ser PROPIO o EXTERNO"
MENSAJE_SOLO_ADMINISTRADOR_TARA = "Solo el Administrador puede modificar la tara del vehículo"
MENSAJE_MOTIVO_TARA = "Debe indicar el motivo del cambio de tara"
MENSAJE_SIN_TARA = "El vehículo {placa} aún no tiene tara: se registra en el destare"
MENSAJE_YA_TIENE_TARA = "El vehículo {placa} ya tiene tara registrada"
MENSAJE_DESACTIVADO_CON_INGRESOS = "El vehículo se desactivó porque tiene ingresos registrados"
MENSAJE_DESACTIVADO = "Vehículo desactivado"
MENSAJE_REACTIVADO = "Vehículo reactivado"


def _resolver_transportista(datos: dict) -> Transportista | None:
    valor = datos.get("transportista")
    if valor in (None, ""):
        return None
    if isinstance(valor, Transportista):
        return valor
    # Un transportista desactivado no se ofrece para asociarlo (RN-M02-09).
    return Transportista.objects.filter(pk=valor, activo=True).first()


def _validar_coherencia(titularidad: str, transportista: Transportista | None) -> None:
    if titularidad not in (Vehiculo.PROPIO, Vehiculo.EXTERNO):
        raise ErrorDeValidacionDeDominio(MENSAJE_TITULARIDAD_INVALIDA, codigo="TITULARIDAD_INVALIDA")
    if titularidad == Vehiculo.EXTERNO and transportista is None:
        raise ErrorDeValidacionDeDominio(
            MENSAJE_EXTERNO_SIN_TRANSPORTISTA, codigo="EXTERNO_SIN_TRANSPORTISTA"
        )
    if titularidad == Vehiculo.PROPIO and transportista is not None:
        raise ErrorDeValidacionDeDominio(
            MENSAJE_PROPIO_CON_TRANSPORTISTA, codigo="PROPIO_CON_TRANSPORTISTA"
        )


def crear_vehiculo(datos: dict, usuario) -> Vehiculo:
    """HU-M02-01 CA01 a CA05, CA08 y CA12. Nace sin tara, pendiente de destare."""
    placa = validar_placa(datos["placa"])
    if VehiculoRepository.existe_placa(placa):
        raise ErrorDeValidacionDeDominio(MENSAJE_PLACA_DUPLICADA, codigo="PLACA_DUPLICADA")

    titularidad = datos["tipo_titularidad"]
    transportista = _resolver_transportista(datos)
    _validar_coherencia(titularidad, transportista)

    with transaction.atomic():
        vehiculo = Vehiculo(
            placa=placa,
            tipo_titularidad=titularidad,
            capacidad_tn=datos["capacidad_tn"],
            transportista=transportista,
        )
        vehiculo.full_clean()
        vehiculo.save()
        registrar_creacion(
            "Vehiculo", vehiculo, usuario,
            nuevos={"placa": placa, "titularidad": titularidad, "capacidad_tn": str(vehiculo.capacidad_tn)},
        )
    return vehiculo


def _datos_auditables(vehiculo: Vehiculo) -> dict:
    return {
        "placa": vehiculo.placa,
        "tipo_titularidad": vehiculo.tipo_titularidad,
        "capacidad_tn": str(vehiculo.capacidad_tn),
        "transportista": vehiculo.transportista_id,
    }


def actualizar_vehiculo(vehiculo: Vehiculo, datos: dict, usuario) -> Vehiculo:
    """Datos distintos de la tara: la tara solo cambia por `modificar_tara`."""
    antes = _datos_auditables(vehiculo)
    if "placa" in datos:
        placa = validar_placa(datos["placa"])
        if VehiculoRepository.existe_placa(placa, excluir_id=vehiculo.pk):
            raise ErrorDeValidacionDeDominio(MENSAJE_PLACA_DUPLICADA, codigo="PLACA_DUPLICADA")
        vehiculo.placa = placa
    if "capacidad_tn" in datos:
        vehiculo.capacidad_tn = datos["capacidad_tn"]

    titularidad = datos.get("tipo_titularidad", vehiculo.tipo_titularidad)
    if "transportista" in datos:
        transportista = _resolver_transportista(datos)
    elif titularidad == Vehiculo.PROPIO:
        # Pasar a PROPIO sin indicar transportista suelta el que tenía.
        transportista = None
    else:
        transportista = vehiculo.transportista
    _validar_coherencia(titularidad, transportista)
    vehiculo.tipo_titularidad = titularidad
    vehiculo.transportista = transportista

    with transaction.atomic():
        vehiculo.full_clean()
        vehiculo.save()
        registrar_edicion("Vehiculo", vehiculo, usuario, antes, _datos_auditables(vehiculo))
    return vehiculo


def registrar_tara(vehiculo: Vehiculo, tara_tn: Decimal, fecha_destare, usuario, *,
                   ingresos_relacionados: list[int] | None = None) -> Vehiculo:
    """Primera tara, desde el destare de M03 (RN-M02-11, DR-25). La invoca el
    servicio de ingresos dentro de su transacción."""
    if vehiculo.tara_tn is not None:
        raise ConflictoDeConcurrencia(
            MENSAJE_YA_TIENE_TARA.format(placa=vehiculo.placa), codigo="VEHICULO_CON_TARA"
        )
    vehiculo.tara_tn = tara_tn
    vehiculo.fecha_destare = fecha_destare
    vehiculo.usuario_destare = usuario
    vehiculo.save(update_fields=["tara_tn", "fecha_destare", "usuario_destare"])
    registrar_modificacion(
        "Vehiculo", vehiculo, usuario, anteriores={"tara_tn": None},
        nuevos={"tara_tn": str(tara_tn), "fecha_destare": fecha_destare.isoformat()},
        ingresos_relacionados=ingresos_relacionados,
    )
    return vehiculo


def modificar_tara(vehiculo: Vehiculo, tara_tn: Decimal, motivo: str, usuario) -> Vehiculo:
    """HU-M02-01 CA10 y CA11, RN-M02-12 y RN-M02-13. El permiso lo comprueba la
    vista (solo Administrador, CA09). Los ingresos ya registrados conservan la
    tara que se les aplicó: aquí no se toca ninguno."""
    motivo = (motivo or "").strip()
    if not motivo:
        raise ErrorDeValidacionDeDominio(MENSAJE_MOTIVO_TARA, codigo="MOTIVO_TARA")
    if vehiculo.tara_tn is None:
        raise ConflictoDeConcurrencia(
            MENSAJE_SIN_TARA.format(placa=vehiculo.placa), codigo="VEHICULO_SIN_TARA"
        )
    anterior = vehiculo.tara_tn
    with transaction.atomic():
        vehiculo.tara_tn = tara_tn
        vehiculo.save(update_fields=["tara_tn"])
        registrar_modificacion(
            "Vehiculo", vehiculo, usuario, anteriores={"tara_tn": str(anterior)},
            nuevos={"tara_tn": str(tara_tn)}, motivo=motivo,
        )
    return vehiculo


def desactivar_vehiculo(vehiculo: Vehiculo, usuario) -> Vehiculo:
    """HU-M02-01 CA06. Nunca se elimina (RN-M02-08)."""
    with transaction.atomic():
        cambiar_estado("Vehiculo", vehiculo, usuario, False)
    vehiculo.mensaje = (
        MENSAJE_DESACTIVADO_CON_INGRESOS if vehiculo.ingresos.exists() else MENSAJE_DESACTIVADO
    )
    return vehiculo


def reactivar_vehiculo(vehiculo: Vehiculo, usuario) -> Vehiculo:
    """HU-M02-01 CA13. Conserva su tara (RN-M02-19)."""
    with transaction.atomic():
        cambiar_estado("Vehiculo", vehiculo, usuario, True)
    vehiculo.mensaje = MENSAJE_REACTIVADO
    return vehiculo
