from rest_framework import serializers

from apps.catalogo.models import Cliente


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ["id", "razon_social", "ruc", "activo"]
        read_only_fields = fields


class ClienteCreateSerializer(serializers.Serializer):
    razon_social = serializers.CharField(max_length=150)
    ruc = serializers.CharField(max_length=11)


class ClienteUpdateSerializer(serializers.Serializer):
    razon_social = serializers.CharField(max_length=150, required=False)
    ruc = serializers.CharField(max_length=11, required=False)
