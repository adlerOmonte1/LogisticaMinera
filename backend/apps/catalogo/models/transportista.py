from django.db import models

from .base import EntidadCatalogo


class Transportista(EntidadCatalogo):
    """Empresa de transporte de un vehículo EXTERNO (RN-M02-04)."""

    razon_social = models.CharField(max_length=150, verbose_name="Razón social")
    ruc = models.CharField(max_length=11, verbose_name="RUC")

    class Meta:
        db_table = "transportista"
        verbose_name = "Transportista"
        verbose_name_plural = "Transportistas"
        ordering = ["razon_social"]

    def __str__(self):
        return self.razon_social
