from datetime import datetime
from decimal import Decimal

import factory
from django.utils import timezone

from apps.accounts.tests.factories import UsuarioFactory
from apps.catalogo.tests.factories import TipoMineralFactory, VehiculoFactory
from apps.ingresos.models import Ingreso


def _momento(dia, hora, minuto=0):
    return timezone.make_aware(datetime(2027, 3, dia, hora, minuto))


class IngresoFactory(factory.django.DjangoModelFactory):
    """Ingreso Registrado ya persistido, para las pruebas que lo necesitan como
    dato de partida. Las pruebas del alta pasan por el servicio de registro."""

    class Meta:
        model = Ingreso

    codigo = factory.Sequence(lambda n: f"ING-2027-{n + 1:05d}")
    fecha_hora_pesaje = factory.LazyFunction(lambda: _momento(15, 8, 30))
    hora_inicio_registro = factory.LazyFunction(lambda: _momento(15, 8, 35))
    hora_fin_registro = factory.LazyFunction(lambda: _momento(15, 8, 36))
    vehiculo = factory.SubFactory(VehiculoFactory)
    tipo_mineral = factory.SubFactory(TipoMineralFactory)
    peso_bruto_tn = Decimal("32.50")
    tara_tn = Decimal("12.30")
    peso_neto_tn = Decimal("20.20")
    usuario_registro = factory.SubFactory(UsuarioFactory)
    estado = Ingreso.REGISTRADO
    sin_respaldo_fotografico = True
    motivo_sin_respaldo = Ingreso.OTRO
