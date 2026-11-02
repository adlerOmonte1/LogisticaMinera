"""Reloj inyectable (notas de M03).

Las marcas de tiempo son el corazón del registro: una prueba que no puede fijar
«ahora» no puede verificar que el inicio y el fin del registro midan momentos
distintos (D-01). Los servicios reciben un `Reloj`; en producción es el del
sistema y en las pruebas uno fijo que se adelanta a voluntad.
"""

from datetime import datetime, timedelta
from typing import Protocol

from django.utils import timezone


class Reloj(Protocol):
    def ahora(self) -> datetime: ...


class RelojDelSistema:
    def ahora(self) -> datetime:
        return timezone.now()


class RelojFijo:
    """Solo para pruebas: devuelve siempre el mismo instante hasta que se adelanta."""

    def __init__(self, instante: datetime):
        self.instante = instante

    def ahora(self) -> datetime:
        return self.instante

    def adelantar(self, **delta) -> None:
        self.instante += timedelta(**delta)


reloj_del_sistema = RelojDelSistema()
