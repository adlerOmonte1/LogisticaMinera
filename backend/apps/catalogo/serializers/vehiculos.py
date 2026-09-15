from decimal import Decimal

from rest_framework import serializers

from apps.catalogo.models import Vehiculo


class VehiculoSerializer(serializers.ModelSerializer):
    titularidad = serializers.CharField(source="tipo_titularidad", read_only=True)
    transportista = serializers.PrimaryKeyRelatedField(read_only=True)
    transportista_nombre = serializers.CharField(
        source="transportista.razon_social", read_only=True, default=None
    )

    class Meta:
        model = Vehiculo
        fields = [
            "id", "placa", "titularidad", "capacidad_tn",
            "transportista", "transportista_nombre", "activo",
        ]
        read_only_fields = fields


class VehiculoCreateSerializer(serializers.Serializer):
    placa = serializers.CharField(max_length=10)
    tipo_titularidad = serializers.ChoiceField(choices=Vehiculo.TITULARIDADES)
    capacidad_tn = serializers.DecimalField(max_digits=6, decimal_places=2, min_value=Decimal('0.01'))
    transportista = serializers.IntegerField(required=False, allow_null=True)


class VehiculoUpdateSerializer(serializers.Serializer):
    placa = serializers.CharField(max_length=10, required=False)
    tipo_titularidad = serializers.ChoiceField(choices=Vehiculo.TITULARIDADES, required=False)
    capacidad_tn = serializers.DecimalField(
        max_digits=6, decimal_places=2, min_value=Decimal('0.01'), required=False
    )
    transportista = serializers.IntegerField(required=False, allow_null=True)
