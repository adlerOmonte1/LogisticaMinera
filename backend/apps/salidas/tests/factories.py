from datetime import date
from decimal import Decimal

import factory
from django.utils import timezone

from apps.accounts.tests.factories import UsuarioFactory
from apps.catalogo.tests.factories import ClienteFactory, ProductoFactory
from apps.salidas.models import Salida, TipoMovimiento


class SalidaFactory(factory.django.DjangoModelFactory):
    """Para pruebas que necesitan una salida ya persistida. Las que verifican
    el alta en sí pasarán por `services.salidas.registrar_salida`, no por esta
    factory."""

    class Meta:
        model = Salida

    correlativo = factory.Sequence(lambda n: f"SAL-2026-{n + 1:05d}")
    fecha = date(2026, 5, 10)
    hora_registro = factory.LazyFunction(timezone.now)
    producto = factory.SubFactory(ProductoFactory)
    cliente = factory.SubFactory(ClienteFactory)
    tipo_movimiento = TipoMovimiento.VENTA
    cantidad_tn = Decimal("15.00")
    usuario_registro = factory.SubFactory(UsuarioFactory)
