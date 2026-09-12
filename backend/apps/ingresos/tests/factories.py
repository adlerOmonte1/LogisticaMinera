from datetime import date, time
from decimal import Decimal

import factory
from django.utils import timezone

from apps.accounts.tests.factories import UsuarioFactory
from apps.catalogo.tests.factories import ProductoFactory, VehiculoFactory
from apps.ingresos.models import Ingreso


class IngresoFactory(factory.django.DjangoModelFactory):
    """Para pruebas que necesitan un ingreso ya persistido (editar, anular,
    listar). Las pruebas que verifican el alta en sí pasan por
    `services.ingresos.registrar_ingreso`, no por esta factory."""

    class Meta:
        model = Ingreso

    correlativo = factory.Sequence(lambda n: f"ING-2026-{n + 1:05d}")
    fecha_pesaje = date(2026, 3, 15)
    hora_pesaje = time(8, 30)
    hora_registro = factory.LazyFunction(timezone.now)
    vehiculo = factory.SubFactory(VehiculoFactory)
    producto = factory.SubFactory(ProductoFactory)
    peso_bruto_tn = Decimal("32.50")
    tara_tn = Decimal("12.30")
    peso_neto_tn = Decimal("20.20")
    numero_ticket = factory.Sequence(lambda n: f"TCK-{n + 1:04d}")
    usuario_registro = factory.SubFactory(UsuarioFactory)
