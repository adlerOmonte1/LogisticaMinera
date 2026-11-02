from django.db import models


class EntidadCatalogo(models.Model):
    """Base de las entidades de catálogo (RN-M02-08, RN-M02-09).

    Todas comparten el indicador de vigencia. La baja es siempre lógica: el
    histórico de ingresos conserva claves foráneas hacia estos registros y un
    borrado físico las rompería.
    """

    activo = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        abstract = True
