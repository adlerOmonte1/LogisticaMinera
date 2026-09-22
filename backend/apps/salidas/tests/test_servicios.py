"""Casos de uso de M04: alta y anulación (HU-M04-01, HU-M04-02, HU-M04-03).

Las dependencias se inyectan; ninguna prueba necesita M05 ni M08 implementados.
"""

from datetime import date, datetime
from decimal import Decimal

import pytest
from django.utils import timezone

from apps.catalogo.tests.factories import ClienteFactory, ProductoFactory
from apps.salidas.models import Salida, TipoMovimiento
from apps.salidas.services.salidas import (
    MENSAJE_MOTIVO_ANULACION_OBLIGATORIO,
    MENSAJE_SALIDA_YA_ANULADA,
    anular_salida,
    registrar_salida,
)
from common.eventos import Accion
from common.excepciones import ConflictoDeConcurrencia, ErrorDeValidacionDeDominio

from .dobles import GeneradorFijo, RegistradorEspia, ServicioStockEspia
from .factories import SalidaFactory

pytestmark = pytest.mark.django_db


def _datos(**cambios):
    base = {
        "fecha": date(2026, 5, 10),
        "producto": ProductoFactory(),
        "cliente": ClienteFactory(),
        "tipo_movimiento": TipoMovimiento.VENTA,
        "cantidad_tn": Decimal("15.00"),
        "motivo": None,
    }
    base.update(cambios)
    return base


def _reloj(momento=datetime(2026, 5, 10, 9, 30)):
    return lambda: timezone.make_aware(momento)


# --- HU-M04-01 CA01: alta de una salida por venta ------------------------


def test_hu_m04_01_ca01_registra_la_salida_con_correlativo_y_movimiento(administrativo):
    stock, registrador = ServicioStockEspia(), RegistradorEspia()

    salida = registrar_salida(
        _datos(),
        administrativo,
        ahora=_reloj(),
        generador=GeneradorFijo(),
        servicio_stock=stock,
        registrador=registrador,
    )

    assert salida.correlativo == "SAL-2026-00001"
    assert salida.estado == Salida.REGISTRADO
    assert salida.usuario_registro == administrativo
    assert stock.salidas_generadas == [salida]  # RN-M04-05: exactamente uno.


def test_la_hora_de_registro_la_fija_el_reloj_inyectado(administrativo):
    """D-01: `hora_registro` la asigna el servicio, no `auto_now_add`; por eso
    se puede fijar en la prueba."""
    salida = registrar_salida(
        _datos(),
        administrativo,
        ahora=_reloj(datetime(2026, 5, 10, 9, 30)),
        generador=GeneradorFijo(),
        servicio_stock=ServicioStockEspia(),
        registrador=RegistradorEspia(),
    )

    assert salida.hora_registro == timezone.make_aware(datetime(2026, 5, 10, 9, 30))


def test_hu_m04_01_ca05_el_alta_queda_en_auditoria(administrativo):
    registrador = RegistradorEspia()

    salida = registrar_salida(
        _datos(),
        administrativo,
        ahora=_reloj(),
        generador=GeneradorFijo(),
        servicio_stock=ServicioStockEspia(),
        registrador=registrador,
    )

    assert len(registrador.eventos) == 1
    evento = registrador.eventos[0]
    assert evento["accion"] == Accion.CREAR
    assert evento["entidad"] == "Salida"
    assert evento["id_entidad"] == salida.pk
    assert evento["usuario"] == administrativo


# --- RN-M04-01, RN-M04-03, RN-M04-04: validación con mensaje literal -----


@pytest.mark.parametrize("cantidad", [Decimal("0.00"), Decimal("-3.00")])
def test_hu_m04_01_ca03_cantidad_no_positiva(administrativo, cantidad):
    with pytest.raises(ErrorDeValidacionDeDominio) as exc:
        registrar_salida(_datos(cantidad_tn=cantidad), administrativo)
    assert exc.value.mensaje == "La cantidad debe ser mayor que cero"


def test_hu_m04_01_ca04_venta_sin_cliente(administrativo):
    with pytest.raises(ErrorDeValidacionDeDominio) as exc:
        registrar_salida(_datos(cliente=None), administrativo)
    assert exc.value.mensaje == "Debe indicar el cliente para una salida por venta"


def test_hu_m04_02_ca02_merma_sin_motivo(administrativo):
    with pytest.raises(ErrorDeValidacionDeDominio) as exc:
        registrar_salida(
            _datos(tipo_movimiento=TipoMovimiento.MERMA, cliente=None), administrativo
        )
    assert exc.value.mensaje == "Debe indicar el motivo de la merma"


def test_hu_m04_02_ca01_el_traslado_interno_no_exige_cliente(administrativo):
    salida = registrar_salida(
        _datos(tipo_movimiento=TipoMovimiento.TRASLADO_INTERNO, cliente=None),
        administrativo,
        ahora=_reloj(),
        generador=GeneradorFijo(),
        servicio_stock=ServicioStockEspia(),
        registrador=RegistradorEspia(),
    )

    assert salida.cliente is None


def test_hu_m04_02_ca03_todos_los_tipos_generan_movimiento(administrativo):
    """El movimiento se genera sea cual sea el tipo; el tipo de origen queda
    identificado en la propia salida."""
    for indice, (tipo, extra) in enumerate(
        [
            (TipoMovimiento.VENTA, {}),
            (TipoMovimiento.TRASLADO_INTERNO, {"cliente": None}),
            (TipoMovimiento.MERMA, {"cliente": None, "motivo": "Humedad"}),
        ]
    ):
        stock = ServicioStockEspia()
        salida = registrar_salida(
            _datos(tipo_movimiento=tipo, **extra),
            administrativo,
            ahora=_reloj(),
            generador=GeneradorFijo(f"SAL-2026-{indice + 10:05d}"),
            servicio_stock=stock,
            registrador=RegistradorEspia(),
        )
        assert [s.tipo_movimiento for s in stock.salidas_generadas] == [tipo]
        assert salida.tipo_movimiento == tipo


# --- RN-M04-06: el stock insuficiente advierte, no bloquea ---------------


def test_rn_m04_06_el_stock_insuficiente_advierte_pero_registra(administrativo):
    """HU-M04-01 CA02. Si esta prueba empieza a fallar porque el servicio
    lanza una excepción, alguien convirtió la advertencia en un bloqueo y
    rompió RN-M04-06 a propósito."""
    stock = ServicioStockEspia(saldo=Decimal("10.00"))

    salida = registrar_salida(
        _datos(cantidad_tn=Decimal("15.00")),
        administrativo,
        ahora=_reloj(),
        generador=GeneradorFijo(),
        servicio_stock=stock,
        registrador=RegistradorEspia(),
    )

    assert salida.pk is not None
    assert salida.advertencia_stock == (
        "La cantidad supera el stock disponible (10.00 tn). ¿Desea continuar?"
    )


def test_no_hay_advertencia_cuando_el_saldo_alcanza(administrativo):
    salida = registrar_salida(
        _datos(cantidad_tn=Decimal("5.00")),
        administrativo,
        ahora=_reloj(),
        generador=GeneradorFijo(),
        servicio_stock=ServicioStockEspia(saldo=Decimal("10.00")),
        registrador=RegistradorEspia(),
    )

    assert salida.advertencia_stock is None


def test_sin_saldo_conocido_no_se_advierte(administrativo):
    """Mientras M05 no exista el saldo es `None` —«no se sabe»—, distinto de
    cero: advertir siempre sería ruido."""
    salida = registrar_salida(
        _datos(),
        administrativo,
        ahora=_reloj(),
        generador=GeneradorFijo(),
        servicio_stock=ServicioStockEspia(saldo=None),
        registrador=RegistradorEspia(),
    )

    assert salida.advertencia_stock is None


# --- HU-M04-03: anulación -------------------------------------------------


def test_hu_m04_03_ca02_anular_cambia_el_estado_y_revierte_el_movimiento(administrativo):
    salida = SalidaFactory()
    stock, registrador = ServicioStockEspia(), RegistradorEspia()

    anulada = anular_salida(
        salida, "Despacho no realizado", administrativo,
        servicio_stock=stock, registrador=registrador,
    )

    anulada.refresh_from_db()
    assert anulada.estado == Salida.ANULADO
    assert anulada.motivo_anulacion == "Despacho no realizado"
    assert stock.salidas_revertidas == [salida]  # RN-M04-08.
    assert registrador.eventos[0]["accion"] == Accion.ANULAR


@pytest.mark.parametrize("motivo", ["", "   ", None])
def test_hu_m04_03_ca03_anular_sin_motivo(administrativo, motivo):
    with pytest.raises(ErrorDeValidacionDeDominio) as exc:
        anular_salida(SalidaFactory(), motivo, administrativo)
    assert exc.value.mensaje == MENSAJE_MOTIVO_ANULACION_OBLIGATORIO


def test_no_se_anula_dos_veces(administrativo):
    salida = SalidaFactory(estado=Salida.ANULADO, motivo_anulacion="Ya anulada")

    with pytest.raises(ConflictoDeConcurrencia) as exc:
        anular_salida(salida, "Otro motivo", administrativo)
    assert exc.value.mensaje == MENSAJE_SALIDA_YA_ANULADA
