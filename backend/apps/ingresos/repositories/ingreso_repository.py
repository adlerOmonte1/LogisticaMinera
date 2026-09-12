"""Consultas de lectura sobre `Ingreso`. No escribe (D-09, solid-proyecto)."""

from apps.ingresos.models import Ingreso


class IngresoRepository:
    @staticmethod
    def listado_base():
        return Ingreso.objects.select_related(
            "vehiculo", "vehiculo__transportista", "producto", "usuario_registro"
        )

    @classmethod
    def obtener(cls, pk):
        return cls.listado_base().filter(pk=pk).first()

    @staticmethod
    def obtener_activo_por_ticket(numero_ticket, *, excluir_id=None):
        """Ingreso no anulado con ese número de ticket, o `None` (RN-M03-05)."""
        qs = Ingreso.objects.filter(numero_ticket=numero_ticket, estado=Ingreso.REGISTRADO)
        if excluir_id is not None:
            qs = qs.exclude(pk=excluir_id)
        return qs.first()
