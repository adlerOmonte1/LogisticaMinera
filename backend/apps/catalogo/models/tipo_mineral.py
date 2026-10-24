from django.db import models

from .base import EntidadCatalogo


class TipoMineral(EntidadCatalogo):
    """Catálogo único de tipos de mineral (DR-03): clasifica el ingreso al
    registrarlo y agrupa la producción al consolidar.

    RN-M02-06 (código único), RN-M02-10 (la unidad es siempre la tonelada).
    """

    TONELADA = "TONELADA"
    UNIDADES = [(TONELADA, "Tonelada")]

    codigo = models.CharField(max_length=6, unique=True, verbose_name="Código")
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    unidad_medida = models.CharField(
        max_length=10, choices=UNIDADES, default=TONELADA, verbose_name="Unidad de medida"
    )

    class Meta:
        db_table = "tipo_mineral"
        verbose_name = "Tipo de mineral"
        verbose_name_plural = "Tipos de mineral"
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.codigo} — {self.nombre}"
