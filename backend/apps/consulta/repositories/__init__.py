"""Consultas de M07 (D-10): lectura sobre INGRESO, sin entidad propia. Los
totales usan `Ingreso.objects.computables()`, el mismo criterio del lote y de
la consolidación (RN-M07-02, RN-M07-12)."""

from dataclasses import dataclass
from datetime import date

from django.db.models import Count, F, Q, Sum, Value
from django.db.models.functions import Replace, TruncDate
from django.utils import timezone

from apps.ingresos.models import Ingreso


def normalizar_placa(texto: str) -> str:
    """RNF-M07-06: sin mayúsculas, guiones ni espacios."""
    return "".join(c for c in (texto or "").upper() if c.isalnum())


@dataclass
class Filtros:
    placa: str | None = None
    desde: date | None = None
    hasta: date | None = None
    tipo_mineral: int | None = None
    vehiculo: int | None = None
    titularidad: str | None = None
    estado: str | None = None
    texto: str | None = None  # placa o código (HU-M07-02 CA10)


class ConsultaRepository:
    @staticmethod
    def base():
        # La placa se guarda con guion; se compara sin él (RNF-M07-06).
        return Ingreso.objects.select_related("vehiculo", "tipo_mineral", "usuario_registro").annotate(
            _placa=Replace(F("vehiculo__placa"), Value("-"), Value(""))
        )

    @classmethod
    def filtrar(cls, f: Filtros):
        qs = cls.base()
        if f.placa:
            qs = qs.filter(_placa__icontains=normalizar_placa(f.placa))
        if f.desde:
            qs = qs.filter(fecha_hora_pesaje__date__gte=f.desde)
        if f.hasta:
            qs = qs.filter(fecha_hora_pesaje__date__lte=f.hasta)
        if f.tipo_mineral:
            qs = qs.filter(tipo_mineral_id=f.tipo_mineral)
        if f.vehiculo:
            qs = qs.filter(vehiculo_id=f.vehiculo)
        if f.titularidad:
            qs = qs.filter(vehiculo__tipo_titularidad=f.titularidad.upper())
        if f.estado:
            qs = qs.filter(estado=f.estado.upper())
        if f.texto:
            qs = qs.filter(Q(_placa__icontains=normalizar_placa(f.texto)) | Q(codigo__icontains=f.texto.strip()))
        # Los anulados no se excluyen: aparecen señalados (RN-M07-01).
        return qs.order_by("-fecha_hora_pesaje", "-id")

    @staticmethod
    def totales(qs) -> dict:
        """Una consulta agregada (RNF-M07-03): el número del conjunto y la suma de
        los computables."""
        datos = qs.order_by().aggregate(
            ingresos=Count("pk"),
            registrados=Count("pk", filter=Q(estado=Ingreso.REGISTRADO)),
            en_proceso=Count("pk", filter=Q(estado=Ingreso.EN_PROCESO)),
            anulados=Count("pk", filter=Q(estado=Ingreso.ANULADO)),
        )
        toneladas = qs.order_by().filter(pk__in=Ingreso.objects.computables().values("pk")).aggregate(
            t=Sum("peso_neto_tn"))["t"]
        return {**datos, "toneladas": str(toneladas if toneladas is not None else "0.00")}

    @staticmethod
    def por_dia(desde: date, hasta: date) -> dict:
        """Llegadas y toneladas por día del pesaje, en la zona de la planta
        (RN-M07-11), en una consulta agregada (RNF-M07-10)."""
        filas = (
            Ingreso.objects.filter(fecha_hora_pesaje__date__gte=desde, fecha_hora_pesaje__date__lte=hasta)
            .annotate(dia=TruncDate("fecha_hora_pesaje", tzinfo=timezone.get_current_timezone()))
            .values("dia")
            .annotate(
                ingresos=Count("pk", filter=~Q(estado=Ingreso.ANULADO)),
                toneladas=Sum("peso_neto_tn", filter=Q(estado=Ingreso.REGISTRADO)),
                en_proceso=Count("pk", filter=Q(estado=Ingreso.EN_PROCESO)),
                anulados=Count("pk", filter=Q(estado=Ingreso.ANULADO)),
            )
            .order_by("dia")
        )
        return {f["dia"]: f for f in filas}


__all__ = ["ConsultaRepository", "Filtros", "normalizar_placa"]
