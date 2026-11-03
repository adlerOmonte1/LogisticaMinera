"""Lado de lectura de M06 (D-09). No escribe."""

from django.db.models import Count, Q, Sum

from apps.ingresos.models import Ingreso
from apps.trazabilidad.models import LoteProceso


class LoteRepository:
    @staticmethod
    def detalle():
        return LoteProceso.objects.select_related("tipo_mineral", "usuario_cierre").prefetch_related(
            "partes", "pasos__etapa", "pasos__usuario_registro", "pasos__parte", "pasos__ingreso_tardio",
            "bigbags", "lista_minerales__tipo_mineral", "ingresos__repartos__parte", "ingresos__tipo_mineral",
        )

    @staticmethod
    def listar(*, estado=None, tipo_mineral=None, desde=None, hasta=None):
        qs = LoteProceso.objects.select_related("tipo_mineral").annotate(
            n_ingresos=Count("ingresos", filter=Q(ingresos__estado=Ingreso.REGISTRADO)),
            toneladas=Sum("ingresos__peso_neto_tn", filter=Q(ingresos__estado=Ingreso.REGISTRADO)),
        )
        if estado:
            qs = qs.filter(estado=estado)
        if tipo_mineral:
            qs = qs.filter(lista_minerales__tipo_mineral_id=tipo_mineral, lista_minerales__fecha_retiro__isnull=True)
        if desde:
            qs = qs.filter(fecha_apertura__gte=desde)
        if hasta:
            qs = qs.filter(fecha_apertura__lte=hasta)
        return qs.distinct().order_by("-fecha_apertura", "-id")

    @staticmethod
    def composicion(lote: LoteProceso) -> list[dict]:
        """Ingresos y toneladas por tipo de mineral en una consulta agregada
        (RNF-M06-02). Los anulados no suman (RN-M06-03)."""
        return list(
            Ingreso.objects.filter(lote=lote, estado=Ingreso.REGISTRADO)
            .values("tipo_mineral")
            .annotate(cantidad=Count("pk"), toneladas=Sum("peso_neto_tn"))
        )

    @staticmethod
    def disponibles(lote: LoteProceso):
        """Ingresos Registrados que pueden entrar al lote: sin lote o en otro que
        no está cerrado (HU-M06-01 CA05 y CA08)."""
        return (
            Ingreso.objects.select_related("vehiculo", "tipo_mineral", "lote")
            .filter(estado=Ingreso.REGISTRADO)
            .exclude(lote=lote)
            .exclude(lote__estado=LoteProceso.CERRADO)
            .order_by("tipo_mineral__nombre", "fecha_hora_pesaje")
        )


__all__ = ["LoteRepository"]
