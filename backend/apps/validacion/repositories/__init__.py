"""Lectura de los resultados de validación de un ingreso. No escribe."""

from apps.validacion.models import ResultadoValidacion


class ResultadoValidacionRepository:
    @staticmethod
    def de_ingreso(id_ingreso: int):
        return ResultadoValidacion.objects.filter(ingreso_id=id_ingreso).order_by("fecha_hora", "id")


__all__ = ["ResultadoValidacionRepository"]
