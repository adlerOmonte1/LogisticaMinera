from django.core.exceptions import ValidationError
from django.db import models

from apps.accounts.models import Usuario
from apps.catalogo.models import Cliente, Producto

# Mensajes literales — coinciden con los criterios de aceptación de
# HU-M04-01 CA03/CA04 y HU-M04-02 CA02. Las pruebas los verifican por
# igualdad exacta; si cambian aquí, cambian también en el HU.md del módulo.
MENSAJE_CANTIDAD_INVALIDA = "La cantidad debe ser mayor que cero"
MENSAJE_VENTA_SIN_CLIENTE = "Debe indicar el cliente para una salida por venta"
MENSAJE_MERMA_SIN_MOTIVO = "Debe indicar el motivo de la merma"


class TipoMovimiento(models.TextChoices):
    """Dominio cerrado de RN-M04-02. Los tres restan del stock; la distinción
    existe para poder interpretar el indicador I4: una desviación explicada
    por mermas registradas es distinta de una sin explicación."""

    VENTA = "VENTA", "Venta"
    TRASLADO_INTERNO = "TRASLADO_INTERNO", "Traslado interno"
    MERMA = "MERMA", "Merma"


class Salida(models.Model):
    """Despacho o baja de producto (RS-M04-01 a RS-M04-07).

    `hora_registro` la asigna el servicio, nunca `auto_now_add`: mismo criterio
    que en M03 (D-01). `correlativo` lo asigna `services/correlativo.py` con la
    serie `SAL`, independiente de la de ingresos por construcción (D-13,
    RN-M04-10).

    La validación condicional —cliente si VENTA, motivo si MERMA— vive en
    `clean()` y no en el serializer, porque debe aplicarse a cualquier origen
    del dato (notas.md del módulo, D-08).
    """

    REGISTRADO = "REGISTRADO"
    ANULADO = "ANULADO"
    ESTADOS = [(REGISTRADO, "Registrado"), (ANULADO, "Anulado")]

    correlativo = models.CharField(
        max_length=20, unique=True, editable=False, verbose_name="Correlativo"
    )
    fecha = models.DateField(verbose_name="Fecha")
    hora_registro = models.DateTimeField(editable=False, verbose_name="Hora de registro")
    producto = models.ForeignKey(
        Producto, on_delete=models.PROTECT, related_name="salidas", verbose_name="Producto"
    )
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="salidas",
        verbose_name="Cliente",
    )
    tipo_movimiento = models.CharField(
        max_length=20, choices=TipoMovimiento.choices, verbose_name="Tipo de movimiento"
    )
    cantidad_tn = models.DecimalField(
        max_digits=8, decimal_places=2, verbose_name="Cantidad (tn)"
    )
    motivo = models.TextField(
        null=True, blank=True, verbose_name="Motivo"
    )  # obligatorio si MERMA (RN-M04-04)
    usuario_registro = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        editable=False,
        related_name="salidas_registradas",
        verbose_name="Registrado por",
    )
    estado = models.CharField(
        max_length=10, choices=ESTADOS, default=REGISTRADO, verbose_name="Estado"
    )
    motivo_anulacion = models.TextField(
        null=True, blank=True, verbose_name="Motivo de anulación"
    )

    class Meta:
        db_table = "salida"
        verbose_name = "Salida"
        verbose_name_plural = "Salidas"
        ordering = ["-fecha", "-hora_registro"]
        indexes = [
            # Consolidado de despachos del periodo (M06) y listado filtrado
            # de HU-M04-03 CA01.
            models.Index(fields=["fecha", "producto"], name="idx_salida_fecha_producto"),
        ]
        constraints = [
            # RN-M04-01.
            models.CheckConstraint(
                check=models.Q(cantidad_tn__gt=0),
                name="ck_salida_cantidad_positiva",
            ),
            # RN-M04-03: una venta sin cliente no debe poder existir en la base,
            # ni siquiera creada por una migración de datos o por el panel de
            # administración.
            models.CheckConstraint(
                check=~models.Q(tipo_movimiento=TipoMovimiento.VENTA)
                | models.Q(cliente__isnull=False),
                name="ck_salida_venta_con_cliente",
            ),
            # RN-M04-04.
            models.CheckConstraint(
                check=~models.Q(tipo_movimiento=TipoMovimiento.MERMA)
                | (models.Q(motivo__isnull=False) & ~models.Q(motivo="")),
                name="ck_salida_merma_con_motivo",
            ),
        ]

    def __str__(self):
        return f"{self.correlativo} — {self.get_tipo_movimiento_display()}"

    def clean(self):
        """Salvaguarda de dominio: RN-M04-01, RN-M04-03 y RN-M04-04. El
        servicio las comprueba antes para devolver el mensaje de la historia;
        esto protege cualquier otro origen del dato."""
        super().clean()
        if self.cantidad_tn is not None and self.cantidad_tn <= 0:
            raise ValidationError({"cantidad_tn": MENSAJE_CANTIDAD_INVALIDA})
        if self.tipo_movimiento == TipoMovimiento.VENTA and self.cliente_id is None:
            raise ValidationError({"cliente": MENSAJE_VENTA_SIN_CLIENTE})
        if self.tipo_movimiento == TipoMovimiento.MERMA and not (self.motivo or "").strip():
            raise ValidationError({"motivo": MENSAJE_MERMA_SIN_MOTIVO})
