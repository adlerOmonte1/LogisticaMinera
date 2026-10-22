from django.db import models


class ContadorCorrelativo(models.Model):
    """Serie de correlativos de M04 (D-13, RN-M04-10).

    Tabla propia del módulo: la independencia frente a la serie de ingresos se
    consigue por construcción, no por convención — no existe una fila
    compartida del año donde las dos series pudieran solaparse.

    No es una entidad del modelo entidad-relación (D-10): es la
    infraestructura que hace que `Salida.correlativo` sea único y creciente
    bajo concurrencia. La mecánica vive en `common/correlativo.py`.
    """

    anio = models.PositiveIntegerField(unique=True, verbose_name="Año")
    ultimo_valor = models.PositiveIntegerField(default=0, verbose_name="Último valor emitido")

    class Meta:
        db_table = "contador_correlativo_salida"
        verbose_name = "Contador de correlativo de salidas"
        verbose_name_plural = "Contadores de correlativo de salidas"

    def __str__(self):
        return f"{self.anio}: {self.ultimo_valor}"
