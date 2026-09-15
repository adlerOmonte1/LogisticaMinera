from django.db import models

from .base import EntidadCatalogo


class Cliente(EntidadCatalogo):
    """Receptor de producto en una salida por venta (HU-M02-04)."""

    razon_social = models.CharField(max_length=150, verbose_name="Razón social")
    ruc = models.CharField(max_length=11, verbose_name="RUC")

    class Meta:
        db_table = "cliente"
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ["razon_social"]

    def __str__(self):
        return self.razon_social
