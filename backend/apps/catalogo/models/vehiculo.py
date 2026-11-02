from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from .base import EntidadCatalogo
from .transportista import Transportista

MENSAJE_EXTERNO_SIN_TRANSPORTISTA = "Debe indicar el transportista para un vehículo externo"
MENSAJE_PROPIO_CON_TRANSPORTISTA = "Un vehículo propio no lleva transportista asociado"


class Vehiculo(EntidadCatalogo):
    """Volquete que ingresa a planta.

    RN-M02-01 (placa única), RN-M02-02 (titularidad obligatoria y cerrada),
    RN-M02-03 / RN-M02-04 (coherencia titularidad ↔ transportista),
    RN-M02-05 (capacidad positiva). La tara nace nula y se registra en el destare
    del primer viaje, con su fecha y su usuario (RN-M02-11, DR-10, DR-25).

    El índice sobre `tipo_titularidad` sostiene el filtro por titularidad del
    catálogo.
    """

    PROPIO = "PROPIO"
    EXTERNO = "EXTERNO"
    TITULARIDADES = [(PROPIO, "Propio"), (EXTERNO, "Externo")]

    placa = models.CharField(max_length=10, unique=True, verbose_name="Placa")
    tipo_titularidad = models.CharField(
        max_length=10, choices=TITULARIDADES, verbose_name="Titularidad"
    )
    capacidad_tn = models.DecimalField(
        max_digits=6, decimal_places=2, verbose_name="Capacidad (tn)"
    )
    transportista = models.ForeignKey(
        Transportista,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="vehiculos",
        verbose_name="Transportista",
    )
    tara_tn = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True, editable=False, verbose_name="Tara (tn)"
    )
    fecha_destare = models.DateTimeField(
        null=True, blank=True, editable=False, verbose_name="Fecha del destare"
    )
    usuario_destare = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        editable=False,
        related_name="+",
        verbose_name="Registró la tara",
    )

    class Meta:
        db_table = "vehiculo"
        verbose_name = "Vehículo"
        verbose_name_plural = "Vehículos"
        ordering = ["placa"]
        indexes = [models.Index(fields=["tipo_titularidad"], name="idx_vehiculo_titularidad")]

    def __str__(self):
        return f"{self.placa} ({self.get_tipo_titularidad_display()})"

    @property
    def pendiente_destare(self) -> bool:
        return self.tara_tn is None

    def clean(self):
        """Salvaguarda de dominio: RN-M02-04 y RN-M02-05. El servicio ya las
        comprueba; esto protege el alta por el panel de administración o por
        una migración de datos."""
        super().clean()
        if self.tipo_titularidad == self.EXTERNO and self.transportista_id is None:
            raise ValidationError({"transportista": MENSAJE_EXTERNO_SIN_TRANSPORTISTA})
        if self.tipo_titularidad == self.PROPIO and self.transportista_id is not None:
            raise ValidationError({"transportista": MENSAJE_PROPIO_CON_TRANSPORTISTA})
