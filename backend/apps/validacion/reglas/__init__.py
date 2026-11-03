"""Colección registrada de reglas (RN-M05-11, RNF-M05-06).

Añadir una regla es crear su clase y agregarla a `reglas_vigentes`: ni las
demás reglas ni `ValidadorConsistencia` cambian. Durante la ventana de
operación controlada el conjunto queda congelado (D-16).
"""

from .base import DatosTicket, Regla, Resultado
from .v1_duplicado import RepositorioDuplicados, V1Duplicado
from .v2_tara import V2Tara
from .v3_placa import V3Placa
from .v4_capacidad import V4Capacidad
from .v5_fecha import V5Fecha


def reglas_vigentes(repositorio_duplicados: RepositorioDuplicados) -> list[Regla]:
    return [
        V1Duplicado(repositorio_duplicados),
        V2Tara(),
        V3Placa(),
        V4Capacidad(),
        V5Fecha(),
    ]


__all__ = [
    "DatosTicket", "Regla", "Resultado", "RepositorioDuplicados", "reglas_vigentes",
    "V1Duplicado", "V2Tara", "V3Placa", "V4Capacidad", "V5Fecha",
]
