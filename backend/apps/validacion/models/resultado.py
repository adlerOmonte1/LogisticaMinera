from django.db import models


class ResultadoValidacion(models.Model):
    """Una fila por regla evaluada sobre un ingreso, con su momento y su
    resolución (RN-M05-06, modelo de datos 3.1).

    El detalle conserva los valores que motivaron el incumplimiento: saber que
    V2 falló sirve de poco sin saber qué peso bruto y qué tara se compararon.
    """

    V1, V2, V3, V4, V5 = "V1", "V2", "V3", "V4", "V5"
    REGLAS = [(V1, "V1"), (V2, "V2"), (V3, "V3"), (V4, "V4"), (V5, "V5")]

    PROPUESTA = "PROPUESTA"
    CONFIRMACION = "CONFIRMACION"
    DESTARE = "DESTARE"
    MOMENTOS = [(PROPUESTA, "Propuesta"), (CONFIRMACION, "Confirmación"), (DESTARE, "Destare")]

    NO_APLICA = "NO_APLICA"
    CORREGIDA = "CORREGIDA"
    JUSTIFICADA = "JUSTIFICADA"
    RESOLUCIONES = [(NO_APLICA, "No aplica"), (CORREGIDA, "Corregida"), (JUSTIFICADA, "Justificada")]

    ingreso = models.ForeignKey(
        "ingresos.Ingreso", on_delete=models.PROTECT, related_name="validaciones", verbose_name="Ingreso"
    )
    regla = models.CharField(max_length=2, choices=REGLAS, verbose_name="Regla")
    momento = models.CharField(max_length=12, choices=MOMENTOS, verbose_name="Momento")
    cumple = models.BooleanField(verbose_name="Cumple")
    detalle = models.TextField(blank=True, verbose_name="Detalle")
    resolucion = models.CharField(
        max_length=12, choices=RESOLUCIONES, default=NO_APLICA, verbose_name="Resolución"
    )
    justificacion = models.TextField(blank=True, verbose_name="Justificación")
    fecha_hora = models.DateTimeField(verbose_name="Fecha y hora")

    class Meta:
        db_table = "resultado_validacion"
        verbose_name = "Resultado de validación"
        verbose_name_plural = "Resultados de validación"
        ordering = ["fecha_hora", "id"]
        indexes = [models.Index(fields=["ingreso"], name="idx_resultado_ingreso")]
        constraints = [
            # Solo V1 y V4 admiten justificación, y la justificada la exige.
            models.CheckConstraint(
                check=~models.Q(resolucion="JUSTIFICADA")
                | (models.Q(regla__in=["V1", "V4"]) & ~models.Q(justificacion="")),
                name="ck_resultado_justificacion",
            ),
        ]

    def __str__(self):
        return f"{self.regla} {self.momento} {'cumple' if self.cumple else 'no cumple'}"
