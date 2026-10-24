import factory

from apps.catalogo.models import TipoMineral, Transportista, Vehiculo


class TipoMineralFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TipoMineral
        django_get_or_create = ("codigo",)

    codigo = factory.Sequence(lambda n: f"M{n:03d}")
    nombre = factory.Sequence(lambda n: f"Mineral {n}")
    unidad_medida = TipoMineral.TONELADA


class TransportistaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Transportista

    razon_social = factory.Sequence(lambda n: f"Transportes {n} SAC")
    ruc = factory.Sequence(lambda n: f"20{n:09d}")


class VehiculoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Vehiculo
        django_get_or_create = ("placa",)

    placa = factory.Sequence(lambda n: f"ABC-{n:03d}")
    tipo_titularidad = Vehiculo.PROPIO
    capacidad_tn = "30.00"
    transportista = None
