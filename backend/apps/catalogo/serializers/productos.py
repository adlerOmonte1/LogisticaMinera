from rest_framework import serializers

from apps.catalogo.models import Producto


class ProductoSerializer(serializers.ModelSerializer):
    """Salida y listado."""

    class Meta:
        model = Producto
        fields = ["id", "codigo", "nombre", "unidad_medida", "activo"]
        read_only_fields = fields


class ProductoCreateSerializer(serializers.Serializer):
    codigo = serializers.CharField(max_length=20)
    nombre = serializers.CharField(max_length=100)
    unidad_medida = serializers.ChoiceField(
        choices=Producto.UNIDADES, default=Producto.TONELADA
    )


class ProductoUpdateSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=100, required=False)
