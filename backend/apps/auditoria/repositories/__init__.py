"""Lado de lectura de M09 (D-09): el historial de un ingreso y la consulta de la
auditoría. No escribe: la única escritura es `ServicioAuditoria`."""

from django.db.models import Q, TextField
from django.db.models.functions import Cast

from apps.auditoria.models import EventoAuditoria
from common.eventos import Accion

ENTIDAD_INGRESO = "Ingreso"
# Entidad con que M06 registrará sus eventos (F5). Sus eventos llevan los
# ingresos que afectan en `ingresos_relacionados` (RS-M09-13).
ENTIDAD_LOTE = "Lote"


class EventoRepository:
    @staticmethod
    def historial_de_ingreso(id_ingreso: int):
        """RN-M09-07: los eventos del ingreso y los de su lote que lo afectan, del
        primero al más reciente. Nunca los de usuarios, catálogos ni accesos
        rechazados (RS-M09-15): el filtro es del repositorio, no de la interfaz."""
        return (
            EventoAuditoria.objects.select_related("usuario")
            .filter(
                Q(entidad=ENTIDAD_INGRESO, id_entidad=id_ingreso)
                | Q(entidad=ENTIDAD_LOTE, ingresos_relacionados__contains=[id_ingreso])
            )
            .exclude(accion=Accion.ACCESO_RECHAZADO)
            .order_by("fecha_hora", "id")
        )

    @staticmethod
    def consultar(*, usuario: str | None = None, accion: str | None = None, texto: str | None = None):
        """HU-M09-03: filtros combinables, del más reciente al más antiguo.

        `texto` se busca en la referencia —el código del ingreso, la placa, el
        código del mineral, el RUC, el nombre de usuario— y en el detalle: los
        valores y el motivo del evento."""
        qs = EventoAuditoria.objects.select_related("usuario").order_by("-fecha_hora", "-id")
        if usuario:
            por_usuario = Q(usuario__username__iexact=usuario)
            if usuario.isdigit():
                por_usuario |= Q(usuario__pk=int(usuario))
            qs = qs.filter(por_usuario)
        if accion:
            qs = qs.filter(accion=accion.upper())
        if texto:
            texto = texto.strip()
            qs = qs.annotate(
                _anteriores=Cast("valores_anteriores", TextField()),
                _nuevos=Cast("valores_nuevos", TextField()),
            ).filter(
                Q(_anteriores__icontains=texto)
                | Q(_nuevos__icontains=texto)
                | Q(motivo__icontains=texto)
                | Q(entidad__iexact=texto)
                | _por_referencia(texto)
            )
        return qs


def _por_referencia(texto: str) -> Q:
    """Los eventos cuya entidad tiene esa referencia, aunque sus valores no la
    repitan (por ejemplo, la anulación de un ingreso solo guarda el estado)."""
    from apps.accounts.models import Usuario  # noqa: PLC0415
    from apps.catalogo.models import TipoMineral, Transportista, Vehiculo  # noqa: PLC0415
    from apps.ingresos.models import Ingreso  # noqa: PLC0415

    fuentes = {
        "Ingreso": Ingreso.objects.filter(codigo__icontains=texto),
        "Vehiculo": Vehiculo.objects.filter(placa__icontains=texto),
        "TipoMineral": TipoMineral.objects.filter(Q(codigo__iexact=texto) | Q(nombre__icontains=texto)),
        "Transportista": Transportista.objects.filter(Q(ruc__icontains=texto) | Q(razon_social__icontains=texto)),
        "Usuario": Usuario.objects.filter(username__icontains=texto),
    }
    filtro = Q(pk__in=[])
    for entidad, qs in fuentes.items():
        filtro |= Q(entidad=entidad, id_entidad__in=qs.values("pk"))
    # Los eventos de un ingreso también se encuentran por la placa de su vehículo.
    filtro |= Q(entidad="Ingreso", id_entidad__in=Ingreso.objects.filter(vehiculo__placa__icontains=texto).values("pk"))
    return filtro


def referencias(eventos) -> dict[tuple[str, int], str]:
    """Texto legible de cada registro afectado, resuelto en una consulta por
    entidad (sin N+1)."""
    from apps.accounts.models import Usuario  # noqa: PLC0415
    from apps.catalogo.models import TipoMineral, Transportista, Vehiculo  # noqa: PLC0415
    from apps.ingresos.models import Ingreso  # noqa: PLC0415

    campos = {
        "Ingreso": (Ingreso, "codigo"),
        "Vehiculo": (Vehiculo, "placa"),
        "TipoMineral": (TipoMineral, "codigo"),
        "Transportista": (Transportista, "ruc"),
        "Usuario": (Usuario, "username"),
    }
    ids: dict[str, set] = {}
    for e in eventos:
        if e.entidad in campos and e.id_entidad is not None:
            ids.setdefault(e.entidad, set()).add(e.id_entidad)
    resultado = {}
    for entidad, conjunto in ids.items():
        modelo, campo = campos[entidad]
        for pk, valor in modelo.objects.filter(pk__in=conjunto).values_list("pk", campo):
            resultado[(entidad, pk)] = valor
    return resultado


__all__ = ["ENTIDAD_INGRESO", "ENTIDAD_LOTE", "EventoRepository", "referencias"]
