"""Consultas de lectura sobre `Salida`. No escribe (D-09, solid-proyecto)."""

from apps.salidas.models import Salida


class SalidaRepository:
    @staticmethod
    def listado_base():
        return Salida.objects.select_related("producto", "cliente", "usuario_registro")

    @classmethod
    def obtener(cls, pk):
        return cls.listado_base().filter(pk=pk).first()
