from django.db import models


class ContadorCorrelativo(models.Model):
    """Soporte técnico de D-02. No es una entidad del modelo entidad-relación:
    es el contador que permite que `Ingreso.correlativo` sea único y
    estrictamente creciente bajo concurrencia, con reinicio anual y prefijo
    (`ING-{año}-{cinco dígitos}`, ver `services/correlativo.py` y
    `skills/base-datos-postgresql`).
    """

    anio = models.PositiveIntegerField(unique=True, verbose_name="Año")
    ultimo_valor = models.PositiveIntegerField(default=0, verbose_name="Último valor emitido")

    class Meta:
        db_table = "contador_correlativo_ingreso"
        verbose_name = "Contador de correlativo"
        verbose_name_plural = "Contadores de correlativo"

    def __str__(self):
        return f"{self.anio}: {self.ultimo_valor}"
