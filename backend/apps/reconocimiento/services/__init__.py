"""Casos de uso de M04: reconocer una imagen y persistir el resultado con los
valores confirmados. Ninguno se expone como endpoint de escritura: los invoca
M03 dentro de su flujo (requerimientos funcionales de M04)."""

from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as TiempoAgotado
from datetime import datetime
from decimal import Decimal

from django.conf import settings

from apps.reconocimiento.dominio import (
    CAMPOS,
    MENSAJE_BAJA_CONFIANZA,
    MENSAJE_ILEGIBLE,
    MENSAJE_NO_DISPONIBLE,
    NO_DISPONIBLE,
    ReconocedorTicket,
    ResultadoReconocimiento,
)
from apps.reconocimiento.models import CampoReconocido, ReconocimientoTicket

MOTOR_AUSENTE = "no-disponible"


def umbral_vigente() -> Decimal:
    return Decimal(str(settings.RECONOCIMIENTO_UMBRAL_CONFIANZA))


def reconocer(reconocedor: ReconocedorTicket | None, imagen: bytes) -> ResultadoReconocimiento:
    """Nunca lanza: el fallo del motor, su excepción o su demora se traducen en
    un resultado sin lecturas (RN-M04-07, RNF-M04-02). El registro sigue manual."""
    if reconocedor is None:
        return ResultadoReconocimiento.fallido(MOTOR_AUSENTE, "-", NO_DISPONIBLE)
    motor = getattr(reconocedor, "motor", MOTOR_AUSENTE)
    version = getattr(reconocedor, "version_motor", "-")
    ejecutor = ThreadPoolExecutor(max_workers=1)
    try:
        futuro = ejecutor.submit(reconocedor.reconocer, imagen)
        return futuro.result(timeout=settings.RECONOCIMIENTO_TIEMPO_ESPERA_S)
    except (TiempoAgotado, Exception):
        return ResultadoReconocimiento.fallido(motor, version, NO_DISPONIBLE)
    finally:
        ejecutor.shutdown(wait=False, cancel_futures=True)


def presentar(resultado: ResultadoReconocimiento) -> dict:
    """Propuesta para la pantalla de revisión: cada campo con su confianza y, si
    queda bajo el umbral, su aviso (HU-M04-01 CA01 a CA05). No persiste nada."""
    umbral = umbral_vigente()
    campos = []
    for nombre in CAMPOS:
        c = resultado.campo(nombre)
        dudoso = c.confianza is not None and Decimal(str(c.confianza)) < umbral
        campos.append({
            "nombre": nombre,
            "valor": c.valor,
            "confianza": c.confianza,
            "dudoso": dudoso,
            "aviso": MENSAJE_BAJA_CONFIANZA if dudoso else None,
        })
    aviso = None
    if not resultado.exito:
        aviso = MENSAJE_NO_DISPONIBLE if resultado.causa == NO_DISPONIBLE else MENSAJE_ILEGIBLE
    return {
        "exito": resultado.exito,
        "motor": resultado.motor,
        "version_motor": resultado.version_motor,
        "umbral_confianza": float(umbral),
        "aviso": aviso,
        "campos": campos,
    }


def persistir(ingreso, resultado: ResultadoReconocimiento, confirmados: dict, *, fecha_proceso: datetime,
              umbral: Decimal) -> ReconocimientoTicket:
    """Guarda, dentro de la transacción del registro, lo leído junto a lo
    confirmado (HU-M04-01 CA07). `confirmados`: {nombre_campo: texto}."""
    reconocimiento = ReconocimientoTicket.objects.create(
        ingreso=ingreso,
        motor=resultado.motor,
        version_motor=resultado.version_motor,
        fecha_proceso=fecha_proceso,
        umbral_confianza=umbral,
        exito=resultado.exito,
        causa_fallo=resultado.causa or "",
    )
    CampoReconocido.objects.bulk_create([
        CampoReconocido(
            reconocimiento=reconocimiento,
            nombre_campo=nombre,
            valor_reconocido=resultado.campo(nombre).valor,
            valor_confirmado=confirmados[nombre],
            confianza=None if resultado.campo(nombre).confianza is None
            else Decimal(str(resultado.campo(nombre).confianza)).quantize(Decimal("0.001")),
        )
        for nombre in CAMPOS
    ])
    return reconocimiento


__all__ = ["MOTOR_AUSENTE", "persistir", "presentar", "reconocer", "umbral_vigente"]
