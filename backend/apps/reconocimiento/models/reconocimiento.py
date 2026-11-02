from django.db import models

from apps.reconocimiento.dominio import FECHA, ILEGIBLE, NO_DISPONIBLE, PESO_BRUTO, PLACA


class ReconocimientoTicket(models.Model):
    """Lo que el motor leyó de un ticket, frente a lo que confirmó la persona
    (D-13). Un ingreso con foto tiene uno; el registrado sin foto, ninguno
    (RN-M04-09, RN-M04-11).

    `OneToOneField` con `CASCADE`: el reconocimiento no es un registro del
    negocio sino un detalle del ingreso, y una lectura sin ingreso no describe
    nada (notas de M04). Como el ingreso nunca se borra (D-07), la cascada no se
    ejerce en la operación.

    `causa_fallo` distingue la imagen ilegible del motor no disponible cuando no
    hubo éxito, para que la consulta muestre el motivo (HU-M04-02 CA03, D-25).
    """

    CAUSAS = [(ILEGIBLE, "Imagen ilegible"), (NO_DISPONIBLE, "Reconocimiento no disponible")]

    ingreso = models.OneToOneField(
        "ingresos.Ingreso", on_delete=models.CASCADE, related_name="reconocimiento", verbose_name="Ingreso"
    )
    motor = models.CharField(max_length=50, editable=False, verbose_name="Motor")
    version_motor = models.CharField(max_length=30, editable=False, verbose_name="Versión del motor")
    fecha_proceso = models.DateTimeField(editable=False, verbose_name="Fecha de proceso")
    umbral_confianza = models.DecimalField(
        max_digits=3, decimal_places=2, editable=False, verbose_name="Umbral de confianza"
    )
    exito = models.BooleanField(default=True, verbose_name="Éxito")
    causa_fallo = models.CharField(
        max_length=15, choices=CAUSAS, blank=True, editable=False, verbose_name="Causa del fallo"
    )

    class Meta:
        db_table = "reconocimiento_ticket"
        verbose_name = "Reconocimiento del ticket"
        verbose_name_plural = "Reconocimientos del ticket"
        ordering = ["-fecha_proceso"]

    def __str__(self):
        return f"{self.motor} {self.version_motor} · ingreso {self.ingreso_id}"


class CampoReconocido(models.Model):
    """Un campo del ticket: lo leído y lo confirmado, siempre separados
    (RN-M04-02). `valor_reconocido` y `confianza` son nulos si no hubo lectura;
    nunca cadena vacía ni cero en su lugar (RN-M04-03, RN-M04-06). Los valores
    se guardan como texto: convertirlos perdería la lectura mal formada."""

    CAMPOS = [(PLACA, "Placa"), (FECHA, "Fecha"), (PESO_BRUTO, "Peso bruto")]

    reconocimiento = models.ForeignKey(
        ReconocimientoTicket, on_delete=models.CASCADE, related_name="campos", verbose_name="Reconocimiento"
    )
    nombre_campo = models.CharField(max_length=12, choices=CAMPOS, verbose_name="Campo")
    valor_reconocido = models.CharField(max_length=50, null=True, blank=True, verbose_name="Valor reconocido")
    valor_confirmado = models.CharField(max_length=50, verbose_name="Valor confirmado")
    confianza = models.DecimalField(
        max_digits=4, decimal_places=3, null=True, blank=True, verbose_name="Confianza"
    )

    class Meta:
        db_table = "campo_reconocido"
        verbose_name = "Campo reconocido"
        verbose_name_plural = "Campos reconocidos"
        ordering = ["id"]
        indexes = [models.Index(fields=["reconocimiento"], name="idx_campo_reconocimiento")]
        constraints = [
            models.UniqueConstraint(fields=["reconocimiento", "nombre_campo"], name="uq_campo_por_reconocimiento"),
            models.CheckConstraint(
                check=models.Q(confianza__isnull=True) | (models.Q(confianza__gte=0) & models.Q(confianza__lte=1)),
                name="ck_campo_confianza_0_1",
            ),
            # Sin lectura no hay confianza, y sin confianza no hay lectura.
            models.CheckConstraint(
                check=models.Q(valor_reconocido__isnull=True, confianza__isnull=True)
                | models.Q(valor_reconocido__isnull=False, confianza__isnull=False),
                name="ck_campo_lectura_y_confianza",
            ),
        ]

    @property
    def fue_corregido(self) -> bool:
        """Derivado, nunca escrito por el cliente (RN-M04-10)."""
        return self.valor_reconocido != self.valor_confirmado

    def __str__(self):
        return f"{self.nombre_campo}: {self.valor_reconocido} → {self.valor_confirmado}"
