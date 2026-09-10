from django.db import models


class EntidadCatalogo(models.Model):
    """Base de las cuatro entidades de catálogo (RN-M02-07, RN-M02-08).

    Todas comparten el indicador de vigencia. La baja es siempre lógica: el
    histórico de ingresos y salidas conserva claves foráneas hacia estos
    registros y un borrado físico las rompería.
    """

    activo = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        abstract = True
