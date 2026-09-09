"""Puerto de auditoría.

M08-auditoria (RF-12) aún no está implementado — ver `contexto-tesis`, mapa de
módulos. Los servicios que ya deben dejar rastro (M01: inicio de sesión,
rechazos de autorización) dependen de esta abstracción y no de una
implementación concreta (D de SOLID, `solid-proyecto`): cuando M08 exista,
basta con registrar su implementación aquí sin tocar `apps/accounts`.

Mientras tanto, `RegistradorDeEventosPorLog` dejar constancia en el logger
`auditoria` para no perder la traza durante el desarrollo del resto de
módulos.
"""

import logging
from typing import Protocol

logger = logging.getLogger("auditoria")


class RegistradorDeEventos(Protocol):
    def registrar(
        self,
        *,
        evento: str,
        usuario=None,
        ip: str | None = None,
        detalles: dict | None = None,
    ) -> None: ...


class RegistradorDeEventosPorLog:
    """Implementación provisional: escribe el evento en el log del servidor."""

    def registrar(
        self,
        *,
        evento: str,
        usuario=None,
        ip: str | None = None,
        detalles: dict | None = None,
    ) -> None:
        logger.info(
            "evento=%s usuario=%s ip=%s detalles=%s",
            evento,
            getattr(usuario, "username", usuario),
            ip,
            detalles or {},
        )


registrador_por_defecto = RegistradorDeEventosPorLog()
