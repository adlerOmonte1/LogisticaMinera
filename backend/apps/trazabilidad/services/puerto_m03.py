"""Adaptador del puerto `PuertoLotes` de M03 (RN-M03-25, RN-M03-27). Reemplaza a
`SinLotes` desde F5: la corrección consulta los minerales del lote y la anulación
retira el ingreso del lote que todavía reúne ingresos."""

from apps.ingresos.services.lotes import LoteDelIngreso
from apps.trazabilidad.models import LoteProceso

from .lotes import servicio_lote


class LotesM06:
    def lote_del_ingreso(self, ingreso) -> LoteDelIngreso | None:
        if ingreso.lote_id is None:
            return None
        lote = LoteProceso.objects.prefetch_related("lista_minerales").get(pk=ingreso.lote_id)
        return LoteDelIngreso(
            nombre=lote.nombre,
            minerales=frozenset(lm.tipo_mineral_id for lm in lote.lista_minerales.all() if lm.fecha_retiro is None),
            reune_ingresos=lote.estado == LoteProceso.ABIERTO,
        )

    def retirar(self, ingreso, usuario) -> None:
        servicio_lote.retirar_por_anulacion(ingreso, usuario)
