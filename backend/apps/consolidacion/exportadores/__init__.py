"""Exportadores del consolidado: una clase por formato (RN-M08-06, RNF-M08-04).
Añadir un formato es una clase nueva y una entrada en `EXPORTADORES`; ni el
cálculo ni los exportadores existentes cambian."""

from typing import Protocol

from apps.consolidacion.repositories import Consolidado

from .excel import ExportadorExcel


class ExportadorConsolidado(Protocol):
    tipo_contenido: str
    extension: str

    def generar(self, consolidado: Consolidado, generado_en) -> bytes: ...


EXPORTADORES: dict[str, ExportadorConsolidado] = {"xlsx": ExportadorExcel()}

__all__ = ["EXPORTADORES", "ExportadorConsolidado", "ExportadorExcel"]
