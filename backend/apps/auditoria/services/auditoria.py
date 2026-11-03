"""Único punto de escritura de EVENTO_AUDITORIA (notas de M09, RS-M09-07).

Se invoca dentro de la transacción de la operación que audita: si la operación
falla, el evento tampoco queda. Además del registro en la base, deja una línea
en el logger `auditoria` para seguir los eventos desde la consola en desarrollo.
"""

import logging

from django.utils import timezone

from apps.auditoria.models import EventoAuditoria

logger = logging.getLogger("auditoria")

# RS-M09-16: ningún valor de un evento contiene una contraseña.
_CLAVES_PROHIBIDAS = ("password", "clave", "contrasena", "contraseña")


def _sin_contrasenas(valores: dict | None) -> dict | None:
    if valores is None:
        return None
    return {
        k: v for k, v in valores.items() if not any(p in k.lower() for p in _CLAVES_PROHIBIDAS)
    }


class ServicioAuditoria:
    def registrar(
        self,
        *,
        accion: str,
        entidad: str,
        id_entidad: int | None = None,
        usuario=None,
        ip: str | None = None,
        valores_anteriores: dict | None = None,
        valores_nuevos: dict | None = None,
        motivo: str = "",
        ingresos_relacionados: list[int] | None = None,
    ) -> EventoAuditoria:
        evento = EventoAuditoria.objects.create(
            usuario=usuario if getattr(usuario, "pk", None) else None,
            accion=accion,
            entidad=entidad,
            id_entidad=id_entidad,
            valores_anteriores=_sin_contrasenas(valores_anteriores),
            valores_nuevos=_sin_contrasenas(valores_nuevos),
            motivo=motivo or "",
            fecha_hora=timezone.now(),
            direccion_ip=ip,
            ingresos_relacionados=list(ingresos_relacionados or []),
        )
        logger.info(
            "accion=%s entidad=%s id_entidad=%s usuario=%s ip=%s",
            accion,
            entidad,
            id_entidad,
            getattr(usuario, "username", None),
            ip,
        )
        return evento


servicio_auditoria = ServicioAuditoria()
