from django.db import models

from .base import EntidadCatalogo


class Producto(EntidadCatalogo):
    """RN-M02-01 (código único), RN-M02-09 (unidad siempre tonelada)."""

    TONELADA = "TONELADA"
    UNIDADES = [(TONELADA, "Tonelada")]

    codigo = models.CharField(max_length=20, unique=True, verbose_name="Código")
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    unidad_medida = models.CharField(
        max_length=10, choices=UNIDADES, default=TONELADA, verbose_name="Unidad de medida"
    )

    class Meta:
        db_table = "producto"
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.codigo} — {self.nombre}"
