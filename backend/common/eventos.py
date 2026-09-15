"""Puerto de auditoría.

M08-auditoria (RF-12) aún no está implementado. Los servicios que ya deben
dejar rastro dependen de esta abstracción y no de una implementación concreta
(DIP, solid-proyecto): cuando M08 exista, basta con registrar su
implementación aquí sin tocar el resto de las apps.

## La firma espeja las columnas de EVENTO_AUDITORIA

`accion`, `entidad`, `id_entidad`, `valores_anteriores` y `valores_nuevos` son
columnas del modelo entidad-relación, no claves libres dentro de un
diccionario. Si el puerto las aceptara como texto suelto, M08 tendría que
hacer ingeniería inversa sobre diccionarios con forma distinta en cada módulo
para poder rellenar su propia tabla.

`Accion.OPCIONES` está pensado para usarse tal cual como `choices` del campo
`accion` cuando se escriba el modelo de M08.

Mientras tanto, `RegistradorDeEventosPorLog` deja constancia en el logger
`auditoria` para no perder la traza durante el desarrollo del resto de
módulos.
"""

import logging
from typing import Protocol

logger = logging.getLogger("auditoria")


class Accion:
    """Dominio cerrado del campo `accion` de EVENTO_AUDITORIA.

    `CERRAR_SESION` y `ACCESO_RECHAZADO` amplían el enum original del modelo
    entidad-relación: el primero lo exige RS-M01-08 («inicio de sesión, cierre
    de sesión y cambio de rol»), y el segundo, la regla de
    `backend-auth-permisos` de que toda solicitud rechazada por autorización
    quede registrada.
    """

    CREAR = "CREAR"
    MODIFICAR = "MODIFICAR"
    ANULAR = "ANULAR"
    EXPORTAR = "EXPORTAR"
    INICIAR_SESION = "INICIAR_SESION"
    CERRAR_SESION = "CERRAR_SESION"
    ACCESO_RECHAZADO = "ACCESO_RECHAZADO"

    OPCIONES = [
        (CREAR, "Crear"),
        (MODIFICAR, "Modificar"),
        (ANULAR, "Anular"),
        (EXPORTAR, "Exportar"),
        (INICIAR_SESION, "Iniciar sesión"),
        (CERRAR_SESION, "Cerrar sesión"),
        (ACCESO_RECHAZADO, "Acceso rechazado"),
    ]


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
    ) -> None: ...


class RegistradorDeEventosPorLog:
    """Implementación provisional: escribe el evento en el log del servidor."""

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
    ) -> None:
        logger.info(
            "accion=%s entidad=%s id_entidad=%s usuario=%s ip=%s anteriores=%s nuevos=%s",
            accion,
            entidad,
            id_entidad,
            getattr(usuario, "username", usuario),
            ip,
            valores_anteriores or {},
            valores_nuevos or {},
        )


registrador_por_defecto = RegistradorDeEventosPorLog()
