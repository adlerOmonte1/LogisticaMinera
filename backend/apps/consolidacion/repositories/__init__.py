"""Cálculo agregado de M08 (D-10): sin entidad propia ni acumulado guardado
(RN-M08-02). Usa `Ingreso.objects.computables()`, el mismo criterio del lote,
del listado y del calendario (D-27): un mes tiene un solo total."""

from dataclasses import dataclass, field
from decimal import Decimal

from django.db.models import Count, Sum

from apps.ingresos.models import Ingreso


@dataclass(frozen=True)
class Periodo:
    anio: int
    mes: int


@dataclass
class Consolidado:
    periodo: Periodo
    filas: list[dict] = field(default_factory=list)  # tipo de mineral, ingresos, toneladas
    total_toneladas: Decimal = Decimal("0.00")
    total_ingresos: int = 0
    en_proceso: list[str] = field(default_factory=list)
    anulados: int = 0


class ConsolidacionRepository:
    @staticmethod
    def del_periodo(periodo: Periodo):
        """El mes del ingreso es el de su fecha del pesaje (RN-M08-10)."""
        return Ingreso.objects.filter(fecha_hora_pesaje__year=periodo.anio, fecha_hora_pesaje__month=periodo.mes)

    @classmethod
    def calcular(cls, periodo: Periodo) -> Consolidado:
        """Una consulta agregada por tipo de mineral y dos de conteo (RNF-M08-01).
        Un tipo sin ingresos no aparece (RN-M08-03); el lote no interviene
        (RN-M08-09) y el ingreso sin foto suma como cualquiera (RN-M08-08)."""
        filas = list(
            cls.del_periodo(periodo).computables()
            .values("tipo_mineral_id", "tipo_mineral__codigo", "tipo_mineral__nombre")
            .annotate(ingresos=Count("pk"), toneladas=Sum("peso_neto_tn"))
            .order_by("tipo_mineral__nombre")
        )
        total = sum((f["toneladas"] for f in filas), Decimal("0.00"))
        return Consolidado(
            periodo=periodo,
            filas=[{
                "tipo_mineral": f["tipo_mineral_id"], "codigo": f["tipo_mineral__codigo"],
                "nombre": f["tipo_mineral__nombre"], "ingresos": f["ingresos"], "toneladas": f["toneladas"],
                "participacion": (f["toneladas"] * 100 / total).quantize(Decimal("0.01")) if total else Decimal("0"),
            } for f in filas],
            total_toneladas=total,
            total_ingresos=sum(f["ingresos"] for f in filas),
            en_proceso=list(cls.del_periodo(periodo).filter(estado=Ingreso.EN_PROCESO)
                            .order_by("fecha_hora_pesaje").values_list("codigo", flat=True)),
            anulados=cls.del_periodo(periodo).filter(estado=Ingreso.ANULADO).count(),
        )


__all__ = ["Consolidado", "ConsolidacionRepository", "Periodo"]
