"""Casos de uso de M03: alta, edición y anulación (RS-M03-01 a RS-M03-10)."""

import logging
import uuid
from datetime import date, datetime, time, timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from apps.ingresos.models import Ingreso
from apps.ingresos.services import ingresos as svc
from common.excepciones import ConflictoDeConcurrencia, ErrorDeValidacionDeDominio

from .factories import IngresoFactory

pytestmark = pytest.mark.django_db


class ServicioStockEspia:
    """Doble de prueba: registra las llamadas en vez de escribir en una tabla
    que M05 todavía no crea (solid-proyecto, DIP)."""

    def __init__(self):
        self.generados = []
        self.revertidos = []
        self.ajustados = []

    def generar_movimiento_entrada(self, ingreso):
        self.generados.append(ingreso.pk)

    def revertir_movimiento_entrada(self, ingreso):
        self.revertidos.append(ingreso.pk)

    def ajustar_por_edicion(self, ingreso, valores_anteriores):
        self.ajustados.append(ingreso.pk)


def _reloj_fijo(momento):
    return lambda: momento


def _datos_validos(**cambios):
    base = {
        "fecha_pesaje": date(2026, 3, 15),
        "hora_pesaje": time(8, 30),
        "numero_ticket": "TCK-9001",
        "peso_bruto_tn": Decimal("32.50"),
        "tara_tn": Decimal("12.30"),
    }
    base.update(cambios)
    return base


# --- HU-M03-01, HU-M03-02, HU-M03-03 -----------------------------------


def test_ca01_registra_el_ingreso_y_asigna_correlativo(administrador):
    from apps.catalogo.tests.factories import ProductoFactory, VehiculoFactory

    datos = _datos_validos(vehiculo=VehiculoFactory(), producto=ProductoFactory())
    ingreso = svc.registrar_ingreso(
        datos, administrador, ahora=_reloj_fijo(timezone.make_aware(datetime(2026, 3, 15, 9, 0)))
    )

    assert ingreso.correlativo.startswith("ING-2026-")
    assert ingreso.pk is not None
    assert ingreso.usuario_registro_id == administrador.pk


def test_ca02_peso_neto_lo_calcula_el_servidor_ignorando_cualquier_otro_valor(administrador):
    from apps.catalogo.tests.factories import ProductoFactory, VehiculoFactory

    datos = _datos_validos(vehiculo=VehiculoFactory(), producto=ProductoFactory())
    ingreso = svc.registrar_ingreso(
        datos, administrador, ahora=_reloj_fijo(timezone.make_aware(datetime(2026, 3, 15, 9, 0)))
    )

    assert ingreso.peso_neto_tn == Decimal("20.20")


def test_ca03_tara_mayor_o_igual_al_bruto_es_rechazada(administrador):
    from apps.catalogo.tests.factories import ProductoFactory, VehiculoFactory

    datos = _datos_validos(
        vehiculo=VehiculoFactory(), producto=ProductoFactory(),
        peso_bruto_tn=Decimal("10.00"), tara_tn=Decimal("10.00"),
    )
    with pytest.raises(ErrorDeValidacionDeDominio) as exc:
        svc.registrar_ingreso(
            datos, administrador, ahora=_reloj_fijo(timezone.make_aware(datetime(2026, 3, 15, 9, 0)))
        )
    assert str(exc.value) == "La tara no puede ser mayor o igual al peso bruto"


def test_ca04_ticket_duplicado_devuelve_el_correlativo_del_ingreso_previo(administrador):
    from apps.catalogo.tests.factories import ProductoFactory, VehiculoFactory

    vehiculo, producto = VehiculoFactory(), ProductoFactory()
    reloj = _reloj_fijo(timezone.make_aware(datetime(2026, 3, 15, 9, 0)))
    previo = svc.registrar_ingreso(
        _datos_validos(vehiculo=vehiculo, producto=producto, numero_ticket="TCK-DUP"),
        administrador, ahora=reloj,
    )

    with pytest.raises(ConflictoDeConcurrencia) as exc:
        svc.registrar_ingreso(
            _datos_validos(vehiculo=vehiculo, producto=producto, numero_ticket="TCK-DUP"),
            administrador, ahora=reloj,
        )
    assert str(exc.value) == (
        f"El ticket número TCK-DUP ya fue registrado en el ingreso {previo.correlativo}"
    )


def test_ca05_hora_de_pesaje_y_hora_de_registro_son_campos_independientes(administrador):
    from apps.catalogo.tests.factories import ProductoFactory, VehiculoFactory

    momento = timezone.make_aware(datetime(2026, 3, 15, 14, 0))
    datos = _datos_validos(
        vehiculo=VehiculoFactory(), producto=ProductoFactory(), hora_pesaje=time(8, 30)
    )
    ingreso = svc.registrar_ingreso(datos, administrador, ahora=_reloj_fijo(momento))

    assert ingreso.hora_pesaje == time(8, 30)
    assert ingreso.hora_registro == momento


def test_ca06_fecha_y_hora_de_pesaje_futuras_son_rechazadas(administrador):
    from apps.catalogo.tests.factories import ProductoFactory, VehiculoFactory

    momento = timezone.make_aware(datetime(2026, 3, 15, 9, 0))
    datos = _datos_validos(
        vehiculo=VehiculoFactory(), producto=ProductoFactory(),
        fecha_pesaje=date(2026, 3, 15), hora_pesaje=time(9, 1),
    )
    with pytest.raises(ErrorDeValidacionDeDominio) as exc:
        svc.registrar_ingreso(datos, administrador, ahora=_reloj_fijo(momento))
    assert str(exc.value) == "La fecha y hora de pesaje no pueden ser posteriores a la hora actual"


def test_ca07_genera_movimiento_de_stock_y_evento_de_auditoria(administrador, caplog):
    from apps.catalogo.tests.factories import ProductoFactory, VehiculoFactory

    espia = ServicioStockEspia()
    datos = _datos_validos(vehiculo=VehiculoFactory(), producto=ProductoFactory())

    with caplog.at_level(logging.INFO, logger="auditoria"):
        ingreso = svc.registrar_ingreso(
            datos, administrador,
            ahora=_reloj_fijo(timezone.make_aware(datetime(2026, 3, 15, 9, 0))),
            servicio_stock=espia,
        )

    assert espia.generados == [ingreso.pk]
    assert any(
        "accion=CREAR" in m and "entidad=Ingreso" in m and ingreso.correlativo in m
        for m in caplog.messages
    )


# --- HU-M03-06 -----------------------------------------------------------


def test_verificar_campos_no_editables_rechaza_correlativo_y_hora_registro():
    with pytest.raises(ErrorDeValidacionDeDominio) as exc:
        svc.verificar_campos_no_editables({"correlativo": "ING-2026-99999"})
    assert str(exc.value) == "El campo indicado no es editable"

    with pytest.raises(ErrorDeValidacionDeDominio):
        svc.verificar_campos_no_editables({"hora_registro": "2026-01-01T00:00:00Z"})


def test_verificar_campos_no_editables_acepta_los_campos_permitidos():
    svc.verificar_campos_no_editables({"peso_bruto_tn": "10.00", "numero_ticket": "X"})


def test_ca01_edicion_persiste_cambios_y_registra_valores_anteriores(administrador, caplog):
    ingreso = IngresoFactory(numero_ticket="TCK-ED1")
    with caplog.at_level(logging.INFO, logger="auditoria"):
        editado = svc.editar_ingreso(ingreso, {"numero_ticket": "TCK-ED1-CORREGIDO"}, administrador)

    assert editado.numero_ticket == "TCK-ED1-CORREGIDO"
    assert any(
        "accion=MODIFICAR" in m and "TCK-ED1" in m and "TCK-ED1-CORREGIDO" in m
        for m in caplog.messages
    )


def test_ca03_editar_peso_ajusta_el_movimiento_de_stock(administrador):
    ingreso = IngresoFactory()
    espia = ServicioStockEspia()

    svc.editar_ingreso(
        ingreso, {"peso_bruto_tn": Decimal("40.00"), "tara_tn": Decimal("15.00")},
        administrador, servicio_stock=espia,
    )

    assert espia.ajustados == [ingreso.pk]


def test_ca03_editar_producto_tambien_ajusta_el_stock(administrador):
    from apps.catalogo.tests.factories import ProductoFactory

    ingreso = IngresoFactory()
    espia = ServicioStockEspia()

    svc.editar_ingreso(ingreso, {"producto": ProductoFactory()}, administrador, servicio_stock=espia)

    assert espia.ajustados == [ingreso.pk]


def test_editar_fecha_y_hora_de_pesaje(administrador):
    ingreso = IngresoFactory(fecha_pesaje=date(2026, 3, 1), hora_pesaje=time(7, 0))
    momento = timezone.make_aware(datetime(2026, 3, 10, 12, 0))

    editado = svc.editar_ingreso(
        ingreso, {"fecha_pesaje": date(2026, 3, 9), "hora_pesaje": time(6, 45)},
        administrador, ahora=_reloj_fijo(momento),
    )

    assert editado.fecha_pesaje == date(2026, 3, 9)
    assert editado.hora_pesaje == time(6, 45)


def test_editar_fecha_de_pesaje_futura_es_rechazada(administrador):
    ingreso = IngresoFactory()
    momento = timezone.make_aware(datetime(2026, 3, 10, 12, 0))

    with pytest.raises(ErrorDeValidacionDeDominio):
        svc.editar_ingreso(
            ingreso, {"fecha_pesaje": date(2026, 3, 11)}, administrador, ahora=_reloj_fijo(momento)
        )


def test_editar_vehiculo(administrador):
    from apps.catalogo.tests.factories import VehiculoFactory

    ingreso = IngresoFactory()
    nuevo_vehiculo = VehiculoFactory()

    editado = svc.editar_ingreso(ingreso, {"vehiculo": nuevo_vehiculo}, administrador)

    assert editado.vehiculo_id == nuevo_vehiculo.pk


def test_editar_no_afecta_stock_si_solo_cambia_el_numero_de_ticket(administrador):
    ingreso = IngresoFactory()
    espia = ServicioStockEspia()

    svc.editar_ingreso(ingreso, {"numero_ticket": "TCK-SIN-IMPACTO"}, administrador, servicio_stock=espia)

    assert espia.ajustados == []


def test_ca04_no_se_puede_editar_un_ingreso_anulado(administrador):
    ingreso = IngresoFactory(estado=Ingreso.ANULADO, motivo_anulacion="Error de digitación")

    with pytest.raises(ConflictoDeConcurrencia) as exc:
        svc.editar_ingreso(ingreso, {"numero_ticket": "X"}, administrador)
    assert str(exc.value) == "No se puede editar un ingreso anulado"


def test_editar_el_ticket_a_uno_ya_activo_en_otro_ingreso_es_rechazado(administrador):
    IngresoFactory(numero_ticket="TCK-OCUPADO")
    ingreso = IngresoFactory(numero_ticket="TCK-LIBRE")

    with pytest.raises(ConflictoDeConcurrencia):
        svc.editar_ingreso(ingreso, {"numero_ticket": "TCK-OCUPADO"}, administrador)


# --- HU-M03-07 -----------------------------------------------------------


def test_ca01_anular_cambia_estado_y_revierte_el_stock(administrador):
    ingreso = IngresoFactory()
    espia = ServicioStockEspia()

    anulado = svc.anular_ingreso(ingreso, "Registrado por error", administrador, servicio_stock=espia)

    assert anulado.estado == Ingreso.ANULADO
    assert espia.revertidos == [ingreso.pk]
    assert Ingreso.objects.filter(pk=ingreso.pk).exists()  # nunca se borra


def test_ca02_motivo_vacio_es_rechazado(administrador):
    ingreso = IngresoFactory()
    with pytest.raises(ErrorDeValidacionDeDominio) as exc:
        svc.anular_ingreso(ingreso, "   ", administrador)
    assert str(exc.value) == "Debe indicar el motivo de la anulación"


def test_anular_un_ingreso_ya_anulado_es_rechazado(administrador):
    ingreso = IngresoFactory(estado=Ingreso.ANULADO, motivo_anulacion="Ya anulado antes")
    with pytest.raises(ConflictoDeConcurrencia) as exc:
        svc.anular_ingreso(ingreso, "Otro motivo", administrador)
    assert str(exc.value) == "El ingreso ya se encuentra anulado"


def test_ca04_anular_registra_usuario_motivo_y_fecha_en_auditoria(administrador, caplog):
    ingreso = IngresoFactory()
    with caplog.at_level(logging.INFO, logger="auditoria"):
        svc.anular_ingreso(ingreso, "Duplicado por error de digitación", administrador)

    assert any(
        "accion=ANULAR" in m and administrador.username in m and "Duplicado" in m
        for m in caplog.messages
    )


# --- Punto de entrada de la cola de M07 (D-02, D-03, D-08) ---------------


def _datos_offline(**cambios):
    from apps.catalogo.tests.factories import ProductoFactory, VehiculoFactory

    base = _datos_validos(vehiculo=VehiculoFactory(), producto=ProductoFactory())
    base["uuid_local"] = uuid.uuid4()
    base.update(cambios)
    return base


def test_d03_la_hora_de_captura_local_manda_sobre_la_del_servidor(administrador):
    captura = timezone.make_aware(datetime(2026, 3, 15, 9, 0))
    sincronizacion = timezone.make_aware(datetime(2026, 3, 16, 7, 30))
    datos = _datos_offline(hora_captura_local=captura, hora_sincronizacion=sincronizacion)

    ingreso = svc.registrar_ingreso(datos, administrador, ahora=_reloj_fijo(sincronizacion))

    # I1 mide hasta la captura, no hasta que hubo señal.
    assert ingreso.hora_registro == captura
    assert ingreso.hora_sincronizacion == sincronizacion
    assert ingreso.capturado_offline is True


def test_reenviar_el_mismo_uuid_local_no_duplica_el_ingreso(administrador):
    momento = timezone.make_aware(datetime(2026, 3, 15, 9, 0))
    datos = _datos_offline(hora_captura_local=momento)

    primero = svc.registrar_ingreso(datos, administrador, ahora=_reloj_fijo(momento))
    segundo = svc.registrar_ingreso(datos, administrador, ahora=_reloj_fijo(momento))

    assert primero.pk == segundo.pk
    assert Ingreso.objects.filter(uuid_local=datos["uuid_local"]).count() == 1


def test_una_hora_de_captura_futura_es_rechazada(administrador):
    momento = timezone.make_aware(datetime(2026, 3, 15, 9, 0))
    datos = _datos_offline(hora_captura_local=momento + timedelta(hours=1))

    with pytest.raises(ErrorDeValidacionDeDominio) as exc:
        svc.registrar_ingreso(datos, administrador, ahora=_reloj_fijo(momento))
    assert str(exc.value) == "La hora de captura no puede ser posterior a la hora del servidor"


def test_el_ingreso_en_linea_no_queda_marcado_como_offline(administrador):
    from apps.catalogo.tests.factories import ProductoFactory, VehiculoFactory

    datos = _datos_validos(vehiculo=VehiculoFactory(), producto=ProductoFactory())
    ingreso = svc.registrar_ingreso(
        datos, administrador, ahora=_reloj_fijo(timezone.make_aware(datetime(2026, 3, 15, 9, 0)))
    )

    assert ingreso.capturado_offline is False
    assert ingreso.uuid_local is None
