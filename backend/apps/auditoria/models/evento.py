from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex
from django.db import models

from apps.accounts.models import Usuario
from common.eventos import Accion


class EventoAuditoria(models.Model):
    """Quién hizo qué y cuándo sobre cada entidad (modelo de datos 3.1, M09).

    Solo lo escribe `ServicioAuditoria`, dentro de la transacción de la operación
    que describe (RN-M09-01). No tiene operación de modificación ni de borrado
    (RS-M09-08). `usuario` es nulo en un acceso rechazado sin sesión.
    """

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        null=True,
        editable=False,
        related_name="eventos",
        verbose_name="Usuario",
    )
    accion = models.CharField(max_length=30, choices=Accion.OPCIONES, editable=False)
    entidad = models.CharField(max_length=50, editable=False)
    id_entidad = models.BigIntegerField(null=True, editable=False)
    valores_anteriores = models.JSONField(null=True, editable=False)
    valores_nuevos = models.JSONField(null=True, editable=False)
    motivo = models.TextField(blank=True, editable=False)
    fecha_hora = models.DateTimeField(editable=False)
    direccion_ip = models.CharField(max_length=45, null=True, editable=False)
    ingresos_relacionados = ArrayField(
        models.BigIntegerField(), default=list, blank=True, editable=False
    )

    class Meta:
        db_table = "evento_auditoria"
        verbose_name = "Evento de auditoría"
        verbose_name_plural = "Eventos de auditoría"
        ordering = ["-fecha_hora", "-id"]
        indexes = [
            models.Index(fields=["entidad", "id_entidad"], name="idx_evento_entidad"),
            GinIndex(fields=["ingresos_relacionados"], name="idx_evento_ingresos"),
        ]

    def __str__(self):
        return f"{self.fecha_hora:%Y-%m-%d %H:%M} {self.accion} {self.entidad} {self.id_entidad}"
