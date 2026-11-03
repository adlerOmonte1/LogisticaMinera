"""Puerto de auditoría (M09).

Los servicios de escritura registran sus eventos a través de este puerto
(`registrador_por_defecto`), que delega en `ServicioAuditoria` de
`apps.auditoria`: el único punto de escritura de EVENTO_AUDITORIA. La delegación
es diferida para que `common` no importe `apps` al cargarse.

`Accion.OPCIONES` es el dominio cerrado del campo `accion` (RS-M09-11).
"""

from typing import Protocol


class Accion:
    """Dominio cerrado del campo `accion` de EVENTO_AUDITORIA (modelo de datos 3.1)."""

    CREAR = "CREAR"
    MODIFICAR = "MODIFICAR"
    ANULAR = "ANULAR"
    RECONOCER = "RECONOCER"
    CORREGIR_DATO = "CORREGIR_DATO"
    EXPORTAR = "EXPORTAR"
    INICIAR_SESION = "INICIAR_SESION"
    CERRAR_SESION = "CERRAR_SESION"
    ACCESO_RECHAZADO = "ACCESO_RECHAZADO"

    OPCIONES = [
        (CREAR, "Crear"),
        (MODIFICAR, "Modificar"),
        (ANULAR, "Anular"),
        (RECONOCER, "Reconocer"),
        (CORREGIR_DATO, "Corregir dato"),
        (EXPORTAR, "Exportar"),
        (INICIAR_SESION, "Iniciar sesión"),
        (CERRAR_SESION, "Cerrar sesión"),
        (ACCESO_RECHAZADO, "Acceso rechazado"),
    ]


def diferencias(antes: dict, despues: dict) -> tuple[dict, dict]:
    """Solo los campos que cambiaron, con su valor anterior y el nuevo (RS-M09-06)."""
    campos = [k for k in despues if antes.get(k) != despues[k]]
    return {k: antes.get(k) for k in campos}, {k: despues[k] for k in campos}


class RegistradorDeEventos(Protocol):
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
    ):
        """Devuelve el evento registrado: la reversión de una corrección lo
        referencia (RN-M03-29)."""


class _RegistradorDiferido:
    """Resuelve `ServicioAuditoria` en el momento de registrar."""

    def registrar(self, **evento):
        from apps.auditoria.services import servicio_auditoria

        return servicio_auditoria.registrar(**evento)


registrador_por_defecto = _RegistradorDiferido()
