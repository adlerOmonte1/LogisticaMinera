"""Casos de uso de M04 (RS-M04-01 a RS-M04-07). HU-M04-01, 02, 03.

No importa nada de `rest_framework`: el dominio de la salida es independiente
del transporte (D-08, solid-proyecto). La vista traduce las excepciones de
aquí a HTTP a través de `utils.manejador_errores`.
"""

from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apps.salidas.models import Salida, TipoMovimiento
from apps.salidas.models.salida import (
    MENSAJE_CANTIDAD_INVALIDA,
    MENSAJE_MERMA_SIN_MOTIVO,
    MENSAJE_VENTA_SIN_CLIENTE,
)
from common.correlativo import GeneradorCorrelativo
from common.eventos import Accion, RegistradorDeEventos, registrador_por_defecto
from common.excepciones import ConflictoDeConcurrencia, ErrorDeValidacionDeDominio
from common.stock import ServicioStock, servicio_stock_por_defecto

from .correlativo import generador_por_defecto

# Mensajes literales — coinciden con los criterios de aceptación de HU-M04-01
# y HU-M04-03. Las pruebas los verifican por igualdad exacta.
MENSAJE_MOTIVO_ANULACION_OBLIGATORIO = "Debe indicar el motivo de la anulación"
MENSAJE_SALIDA_YA_ANULADA = "La salida ya se encuentra anulada"


def mensaje_stock_insuficiente(saldo: Decimal) -> str:
    """HU-M04-01 CA02, literal de la historia."""
    return f"La cantidad supera el stock disponible ({saldo} tn). ¿Desea continuar?"


def _validar_datos(datos: dict) -> None:
    """RN-M04-01, RN-M04-03 y RN-M04-04 con el mensaje de la historia. El
    modelo las vuelve a comprobar en `clean()` y la base de datos en sus
    `CheckConstraint`: aquí se validan antes solo para poder devolver el texto
    exacto del criterio de aceptación."""
    if datos["cantidad_tn"] <= 0:
        raise ErrorDeValidacionDeDominio(MENSAJE_CANTIDAD_INVALIDA, codigo="CANTIDAD_INVALIDA")
    if datos["tipo_movimiento"] == TipoMovimiento.VENTA and datos.get("cliente") is None:
        raise ErrorDeValidacionDeDominio(MENSAJE_VENTA_SIN_CLIENTE, codigo="VENTA_SIN_CLIENTE")
    if datos["tipo_movimiento"] == TipoMovimiento.MERMA and not (
        datos.get("motivo") or ""
    ).strip():
        raise ErrorDeValidacionDeDominio(MENSAJE_MERMA_SIN_MOTIVO, codigo="MERMA_SIN_MOTIVO")


def _advertencia_por_saldo(datos: dict, servicio_stock: ServicioStock) -> str | None:
    """RS-M04-04 y RN-M04-06: consulta el saldo y **advierte**, sin impedir la
    operación. Que esto devuelva un texto y no lance una excepción es
    deliberado: bloquear una salida real porque la estimación no la respalda
    invitaría a registrar ingresos ficticios, contaminando la variable que el
    sistema busca reducir (nota de `reglas_negocio.md`). Si alguien convierte
    esta función en una validación bloqueante, rompe el diseño.

    `None` del servicio de stock significa «no se sabe» —M05 aún no
    existe—, y no se advierte: una advertencia sin saldo real sería ruido."""
    saldo = servicio_stock.saldo_actual(datos["producto"])
    if saldo is None or datos["cantidad_tn"] <= saldo:
        return None
    return mensaje_stock_insuficiente(saldo)


def _snapshot(salida: Salida) -> dict:
    """Valores de la salida para el registro de auditoría (HU-M04-01 CA05)."""
    return {
        "fecha": str(salida.fecha),
        "producto_id": salida.producto_id,
        "cliente_id": salida.cliente_id,
        "tipo_movimiento": salida.tipo_movimiento,
        "cantidad_tn": str(salida.cantidad_tn),
        "motivo": salida.motivo,
    }


def registrar_salida(
    datos: dict,
    usuario,
    *,
    ahora=timezone.now,
    generador: GeneradorCorrelativo = generador_por_defecto,
    servicio_stock: ServicioStock = servicio_stock_por_defecto,
    registrador: RegistradorDeEventos = registrador_por_defecto,
) -> Salida:
    """HU-M04-01, HU-M04-02.

    `ahora`, `generador`, `servicio_stock` y `registrador` se inyectan (DIP):
    las pruebas los sustituyen por dobles deterministas sin tocar esta
    función, y M05 y M08 se enchufan después sin modificarla (OCP).

    Devuelve la salida con el atributo transitorio `advertencia_stock`: el
    texto de HU-M04-01 CA02 cuando la cantidad supera el saldo estimado, o
    `None`. No se persiste — es información de la respuesta, no del asiento.
    """
    _validar_datos(datos)
    advertencia = _advertencia_por_saldo(datos, servicio_stock)
    momento = ahora()

    # RN-M04-05 y RN-M04-08: correlativo, persistencia, movimiento de stock y
    # evento de auditoría ocurren juntos o no ocurre ninguno.
    with transaction.atomic():
        salida = Salida(
            correlativo=generador.siguiente(momento),  # RN-M04-10: serie SAL.
            fecha=datos["fecha"],
            hora_registro=momento,  # D-01: nunca auto_now_add.
            producto=datos["producto"],
            cliente=datos.get("cliente"),
            tipo_movimiento=datos["tipo_movimiento"],
            cantidad_tn=datos["cantidad_tn"],
            motivo=datos.get("motivo") or None,
            usuario_registro=usuario,  # HU-M04-01 CA05: atribución permanente.
        )
        salida.full_clean(validate_constraints=False)
        salida.save()

        servicio_stock.generar_movimiento_salida(salida)  # RN-M04-05.
        registrador.registrar(
            accion=Accion.CREAR,
            entidad="Salida",
            id_entidad=salida.pk,
            usuario=usuario,
            valores_nuevos={"correlativo": salida.correlativo, **_snapshot(salida)},
        )

    salida.advertencia_stock = advertencia
    return salida


def anular_salida(
    salida: Salida,
    motivo: str,
    usuario,
    *,
    servicio_stock: ServicioStock = servicio_stock_por_defecto,
    registrador: RegistradorDeEventos = registrador_por_defecto,
) -> Salida:
    """HU-M04-03 CA02 y CA03. No existe eliminación física en ninguna
    interfaz ni endpoint (RN-M04-07, RS-M04-07): esta es la única forma de
    retirar una salida.

    La reversión de stock no crea un movimiento de cantidad negativa, sino uno
    de tipo ENTRADA que referencia a esta salida (notas.md del módulo): las
    cantidades siempre positivas y el signo en el tipo evitan errores de signo
    en los agregados de M06.
    """
    if salida.estado == Salida.ANULADO:
        raise ConflictoDeConcurrencia(MENSAJE_SALIDA_YA_ANULADA, codigo="SALIDA_YA_ANULADA")

    motivo = (motivo or "").strip()
    if not motivo:
        raise ErrorDeValidacionDeDominio(
            MENSAJE_MOTIVO_ANULACION_OBLIGATORIO, codigo="MOTIVO_OBLIGATORIO"
        )

    with transaction.atomic():
        salida.estado = Salida.ANULADO
        salida.motivo_anulacion = motivo
        salida.save(update_fields=["estado", "motivo_anulacion"])
        servicio_stock.revertir_movimiento_salida(salida)  # RN-M04-08.
        registrador.registrar(
            accion=Accion.ANULAR,
            entidad="Salida",
            id_entidad=salida.pk,
            usuario=usuario,
            valores_anteriores={"estado": Salida.REGISTRADO},
            valores_nuevos={"estado": Salida.ANULADO, "motivo_anulacion": motivo},
        )
    return salida
