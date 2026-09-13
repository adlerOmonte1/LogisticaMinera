"""Casos de uso de M03 (RS-M03-01 a RS-M03-10). HU-M03-01, 02, 03, 06, 07.

No importa nada de `rest_framework`: el dominio del ingreso es independiente
del transporte (D-08, backend-django). La vista traduce las excepciones de
aquí a HTTP a través de `utils.manejador_errores`.
"""

from datetime import datetime
from decimal import Decimal

from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.ingresos.models import Ingreso
from apps.ingresos.repositories import IngresoRepository
from common.correlativo import GeneradorCorrelativo
from common.eventos import Accion, RegistradorDeEventos, registrador_por_defecto
from common.excepciones import ConflictoDeConcurrencia, ErrorDeValidacionDeDominio
from common.stock import ServicioStock, servicio_stock_por_defecto

from .correlativo import generador_por_defecto

# Mensajes literales — coinciden con los criterios de aceptación de HU-M03-01,
# HU-M03-06 y HU-M03-07. Las pruebas los verifican por igualdad exacta.
MENSAJE_TARA_INVALIDA = "La tara no puede ser mayor o igual al peso bruto"
MENSAJE_FECHA_FUTURA = "La fecha y hora de pesaje no pueden ser posteriores a la hora actual"
MENSAJE_MOTIVO_OBLIGATORIO = "Debe indicar el motivo de la anulación"
MENSAJE_INGRESO_ANULADO_EDICION = "No se puede editar un ingreso anulado"
MENSAJE_INGRESO_YA_ANULADO = "El ingreso ya se encuentra anulado"
MENSAJE_CAMPO_NO_EDITABLE = "El campo indicado no es editable"
MENSAJE_CAPTURA_FUTURA = "La hora de captura no puede ser posterior a la hora del servidor"

# RS-M03-10: ninguno de estos campos se acepta en una edición, con
# independencia del rol. `estado` solo cambia vía anulación (D-07).
CAMPOS_PROTEGIDOS = {"correlativo", "hora_registro", "estado", "usuario_registro", "peso_neto_tn"}


def _mensaje_ticket_duplicado(numero_ticket: str, ingreso_existente: Ingreso) -> str:
    return (
        f"El ticket número {numero_ticket} ya fue registrado "
        f"en el ingreso {ingreso_existente.correlativo}"
    )


def _validar_pesos(peso_bruto_tn: Decimal, tara_tn: Decimal) -> None:
    """RN-M03-03."""
    if tara_tn >= peso_bruto_tn:
        raise ErrorDeValidacionDeDominio(MENSAJE_TARA_INVALIDA, codigo="TARA_INVALIDA")


def _validar_fecha_pesaje(fecha_pesaje, hora_pesaje, momento: datetime) -> None:
    """RN-M03-02. La hora de pesaje es local (America/Lima); se compara contra
    `momento`, ya resuelto por el reloj inyectado."""
    pesaje = timezone.make_aware(datetime.combine(fecha_pesaje, hora_pesaje))
    if pesaje > momento:
        raise ErrorDeValidacionDeDominio(MENSAJE_FECHA_FUTURA, codigo="FECHA_PESAJE_FUTURA")


def _validar_ticket_no_duplicado(numero_ticket: str, *, excluir_id=None) -> None:
    """RN-M03-05. HU-M03-01 CA04: 409, con el correlativo del ingreso previo,
    para que el usuario pueda distinguir un duplicado real de un error de
    transcripción."""
    existente = IngresoRepository.obtener_activo_por_ticket(numero_ticket, excluir_id=excluir_id)
    if existente is not None:
        raise ConflictoDeConcurrencia(
            _mensaje_ticket_duplicado(numero_ticket, existente), codigo="TICKET_DUPLICADO"
        )


def verificar_campos_no_editables(datos_crudos: dict) -> None:
    """RS-M03-10, HU-M03-06 CA02: si el cliente intenta enviar `correlativo`
    u `hora_registro`, se rechaza explícitamente — no se ignora en silencio,
    porque un `PATCH` que los ignorara daría la falsa impresión de haberlos
    aceptado."""
    campos_recibidos = CAMPOS_PROTEGIDOS & set(datos_crudos)
    if campos_recibidos:
        raise ErrorDeValidacionDeDominio(MENSAJE_CAMPO_NO_EDITABLE, codigo="CAMPO_NO_EDITABLE")


def _snapshot(ingreso: Ingreso) -> dict:
    """Valores editables actuales, para el registro de auditoría (RS-M03-07)."""
    return {
        "numero_ticket": ingreso.numero_ticket,
        "fecha_pesaje": str(ingreso.fecha_pesaje),
        "hora_pesaje": str(ingreso.hora_pesaje),
        "vehiculo_id": ingreso.vehiculo_id,
        "producto_id": ingreso.producto_id,
        "peso_bruto_tn": str(ingreso.peso_bruto_tn),
        "tara_tn": str(ingreso.tara_tn),
    }


def registrar_ingreso(
    datos: dict,
    usuario,
    *,
    ahora=timezone.now,
    generador: GeneradorCorrelativo = generador_por_defecto,
    servicio_stock: ServicioStock = servicio_stock_por_defecto,
    registrador: RegistradorDeEventos = registrador_por_defecto,
) -> Ingreso:
    """HU-M03-01, HU-M03-02, HU-M03-03.

    `ahora`, `generador` y `servicio_stock` se inyectan (DIP): las pruebas
    sustituyen el reloj para fijar la hora de pesaje límite, y el generador
    y el servicio de stock por dobles deterministas, sin tocar esta función.

    **Este es también el punto de entrada de la cola de M07** (D-08: un
    registro que llega por sincronización se somete a las mismas reglas que
    uno del formulario). Para ello `datos` admite tres claves opcionales:

    - `uuid_local`: identificador de captura del dispositivo (D-02). Si ya
      existe un ingreso con ese uuid, la operación es **idempotente** y
      devuelve el ingreso ya registrado en lugar de duplicarlo: reenviar un
      lote no debe crear dos veces el mismo ingreso.
    - `hora_captura_local`: pasa a ser `hora_registro` (D-03). Si no viene, se
      usa la hora del servidor. La latencia I1 debe medir el tiempo hasta la
      captura, no hasta que hubo señal.
    - `hora_sincronizacion`: momento en que el lote llegó al servidor; solo
      auditoría.
    """
    momento = ahora()

    uuid_local = datos.get("uuid_local")
    if uuid_local is not None:
        ya_registrado = IngresoRepository.obtener_por_uuid_local(uuid_local)
        if ya_registrado is not None:
            return ya_registrado  # HU-M07-04: reenviar la cola no duplica.

    # D-03: para un ingreso capturado sin conexión manda la hora de captura.
    hora_registro = datos.get("hora_captura_local") or momento
    if hora_registro > momento:
        raise ErrorDeValidacionDeDominio(MENSAJE_CAPTURA_FUTURA, codigo="CAPTURA_FUTURA")

    _validar_fecha_pesaje(datos["fecha_pesaje"], datos["hora_pesaje"], hora_registro)
    _validar_pesos(datos["peso_bruto_tn"], datos["tara_tn"])
    _validar_ticket_no_duplicado(datos["numero_ticket"])

    with transaction.atomic():
        ingreso = Ingreso(
            correlativo=generador.siguiente(hora_registro),
            uuid_local=uuid_local,
            fecha_pesaje=datos["fecha_pesaje"],
            hora_pesaje=datos["hora_pesaje"],
            hora_registro=hora_registro,  # D-01, D-03: nunca auto_now_add.
            hora_sincronizacion=datos.get("hora_sincronizacion"),
            vehiculo=datos["vehiculo"],
            producto=datos["producto"],
            peso_bruto_tn=datos["peso_bruto_tn"],
            tara_tn=datos["tara_tn"],
            peso_neto_tn=datos["peso_bruto_tn"] - datos["tara_tn"],  # RN-M03-04: siempre calculado.
            numero_ticket=datos["numero_ticket"],
            usuario_registro=usuario,  # RN-M03-12, RNF-M03-08: atribución permanente.
            capturado_offline=uuid_local is not None,
        )
        ingreso.full_clean(validate_constraints=False)
        try:
            ingreso.save()
        except IntegrityError:
            # Defensa ante las carreras que el chequeo previo no cubre por sí
            # solo: dos altas del mismo ticket —o dos envíos del mismo lote—
            # casi simultáneas. Los constraints de base de datos son quienes
            # realmente lo impiden; aquí solo se traducen.
            if uuid_local is not None:
                ya_registrado = IngresoRepository.obtener_por_uuid_local(uuid_local)
                if ya_registrado is not None:
                    return ya_registrado
            existente = IngresoRepository.obtener_activo_por_ticket(datos["numero_ticket"])
            if existente is not None:
                raise ConflictoDeConcurrencia(
                    _mensaje_ticket_duplicado(datos["numero_ticket"], existente),
                    codigo="TICKET_DUPLICADO",
                ) from None
            raise

        servicio_stock.generar_movimiento_entrada(ingreso)  # RN-M03-08.
        registrador.registrar(
            accion=Accion.CREAR,
            entidad="Ingreso",
            id_entidad=ingreso.pk,
            usuario=usuario,
            valores_nuevos={"correlativo": ingreso.correlativo, **_snapshot(ingreso)},
        )
    return ingreso


def editar_ingreso(
    ingreso: Ingreso,
    datos: dict,
    usuario,
    *,
    ahora=timezone.now,
    servicio_stock: ServicioStock = servicio_stock_por_defecto,
    registrador: RegistradorDeEventos = registrador_por_defecto,
) -> Ingreso:
    """HU-M03-06. `datos` ya pasó por `verificar_campos_no_editables` en la
    vista antes de llegar aquí."""
    if ingreso.estado == Ingreso.ANULADO:
        raise ConflictoDeConcurrencia(MENSAJE_INGRESO_ANULADO_EDICION, codigo="INGRESO_ANULADO")

    valores_anteriores = _snapshot(ingreso)
    ajusta_stock = False

    if "numero_ticket" in datos and datos["numero_ticket"] != ingreso.numero_ticket:
        _validar_ticket_no_duplicado(datos["numero_ticket"], excluir_id=ingreso.pk)
        ingreso.numero_ticket = datos["numero_ticket"]

    if "fecha_pesaje" in datos or "hora_pesaje" in datos:
        nueva_fecha = datos.get("fecha_pesaje", ingreso.fecha_pesaje)
        nueva_hora = datos.get("hora_pesaje", ingreso.hora_pesaje)
        _validar_fecha_pesaje(nueva_fecha, nueva_hora, ahora())
        ingreso.fecha_pesaje = nueva_fecha
        ingreso.hora_pesaje = nueva_hora

    if "vehiculo" in datos:
        ingreso.vehiculo = datos["vehiculo"]

    if "producto" in datos:
        ingreso.producto = datos["producto"]
        ajusta_stock = True

    if "peso_bruto_tn" in datos or "tara_tn" in datos:
        nuevo_bruto = datos.get("peso_bruto_tn", ingreso.peso_bruto_tn)
        nueva_tara = datos.get("tara_tn", ingreso.tara_tn)
        _validar_pesos(nuevo_bruto, nueva_tara)
        ingreso.peso_bruto_tn = nuevo_bruto
        ingreso.tara_tn = nueva_tara
        ingreso.peso_neto_tn = nuevo_bruto - nueva_tara
        ajusta_stock = True

    with transaction.atomic():
        ingreso.full_clean(validate_constraints=False)
        ingreso.save()
        if ajusta_stock:
            # HU-M03-06 CA03: la corrección se expresa como movimiento
            # compensatorio, no mutando el asiento original (RN-M05-09).
            servicio_stock.ajustar_por_edicion(ingreso, valores_anteriores)
        registrador.registrar(
            accion=Accion.MODIFICAR,
            entidad="Ingreso",
            id_entidad=ingreso.pk,
            usuario=usuario,
            valores_anteriores=valores_anteriores,
            valores_nuevos=_snapshot(ingreso),
        )
    return ingreso


def anular_ingreso(
    ingreso: Ingreso,
    motivo: str,
    usuario,
    *,
    servicio_stock: ServicioStock = servicio_stock_por_defecto,
    registrador: RegistradorDeEventos = registrador_por_defecto,
) -> Ingreso:
    """HU-M03-07. No hay operación de eliminación física en ninguna interfaz
    ni endpoint (CA03): esta es la única forma de retirar un ingreso."""
    if ingreso.estado == Ingreso.ANULADO:
        raise ConflictoDeConcurrencia(MENSAJE_INGRESO_YA_ANULADO, codigo="INGRESO_YA_ANULADO")

    motivo = (motivo or "").strip()
    if not motivo:
        raise ErrorDeValidacionDeDominio(MENSAJE_MOTIVO_OBLIGATORIO, codigo="MOTIVO_OBLIGATORIO")

    with transaction.atomic():
        ingreso.estado = Ingreso.ANULADO
        ingreso.motivo_anulacion = motivo
        ingreso.save(update_fields=["estado", "motivo_anulacion"])
        servicio_stock.revertir_movimiento_entrada(ingreso)  # RN-M03-11.
        # HU-M03-07 CA04: el motivo forma parte del rastro, por eso viaja en
        # `valores_nuevos` junto al cambio de estado.
        registrador.registrar(
            accion=Accion.ANULAR,
            entidad="Ingreso",
            id_entidad=ingreso.pk,
            usuario=usuario,
            valores_anteriores={"estado": Ingreso.REGISTRADO},
            valores_nuevos={"estado": Ingreso.ANULADO, "motivo_anulacion": motivo},
        )
    return ingreso
