from rest_framework import serializers

from apps.catalogo.models import Transportista


class TransportistaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transportista
        fields = ["id", "razon_social", "ruc", "activo"]
        read_only_fields = fields


class TransportistaCreateSerializer(serializers.Serializer):
    razon_social = serializers.CharField(max_length=150)
    ruc = serializers.CharField(max_length=11)


class TransportistaUpdateSerializer(serializers.Serializer):
    razon_social = serializers.CharField(max_length=150, required=False)
    ruc = serializers.CharField(max_length=11, required=False)
