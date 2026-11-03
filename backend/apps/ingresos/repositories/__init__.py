"""Lado de lectura de M03 (D-09). No escribe."""

from datetime import date
from decimal import Decimal

from apps.auditoria.models import EventoAuditoria
from apps.ingresos.models import Ingreso
from common.eventos import Accion

CORRECCION = "CORRECCION"
REVERSION = "REVERSION"


class IngresoRepository:
    @staticmethod
    def detalle():
        return Ingreso.objects.select_related("vehiculo", "tipo_mineral", "usuario_registro")

    @staticmethod
    def pendientes_de_destare():
        return (
            Ingreso.objects.select_related("vehiculo", "tipo_mineral")
            .filter(estado=Ingreso.EN_PROCESO)
            .order_by("fecha_hora_pesaje", "id")
        )

    @staticmethod
    def buscar_por_placa_fecha_peso(
        placa: str, fecha: date, peso_bruto_tn: Decimal, *, excluir: int | None = None
    ) -> str | None:
        """Repositorio que V1 recibe inyectado (RN-M05-12, RN-M05-13)."""
        qs = Ingreso.objects.filter(
            vehiculo__placa=placa.strip().upper(),
            fecha_hora_pesaje__date=fecha,
            peso_bruto_tn=peso_bruto_tn,
        ).exclude(estado=Ingreso.ANULADO)
        if excluir is not None:
            qs = qs.exclude(pk=excluir)
        return qs.order_by("id").values_list("codigo", flat=True).first()

    @staticmethod
    def imagen_ya_registrada(ruta: str) -> str | None:
        return Ingreso.objects.filter(imagen_ticket=ruta).values_list("codigo", flat=True).first()


class HistorialIngresoRepository:
    """Lee de M09 lo que M03 necesita: la auditoría es el historial de
    correcciones (notas de M03: no hay tabla de versiones)."""

    @staticmethod
    def correcciones(id_ingreso: int):
        return EventoAuditoria.objects.filter(
            entidad="Ingreso",
            id_entidad=id_ingreso,
            accion=Accion.MODIFICAR,
            valores_nuevos__operacion__in=[CORRECCION, REVERSION],
        ).order_by("id")

    @classmethod
    def ultima_correccion_vigente(cls, id_ingreso: int) -> EventoAuditoria | None:
        """La última corrección que ninguna reversión anuló (RN-M03-28)."""
        eventos = list(cls.correcciones(id_ingreso))
        revertidas = {e.valores_nuevos.get("revierte") for e in eventos if e.valores_nuevos["operacion"] == REVERSION}
        vigentes = [e for e in eventos if e.valores_nuevos["operacion"] == CORRECCION and e.id not in revertidas]
        return vigentes[-1] if vigentes else None

    @staticmethod
    def anulacion(id_ingreso: int) -> EventoAuditoria | None:
        return (
            EventoAuditoria.objects.select_related("usuario")
            .filter(entidad="Ingreso", id_entidad=id_ingreso, accion=Accion.ANULAR)
            .order_by("-id")
            .first()
        )


__all__ = ["CORRECCION", "REVERSION", "HistorialIngresoRepository", "IngresoRepository"]
