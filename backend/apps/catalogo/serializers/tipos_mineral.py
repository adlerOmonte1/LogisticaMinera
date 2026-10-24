from rest_framework import serializers

from apps.catalogo.models import TipoMineral


class TipoMineralSerializer(serializers.ModelSerializer):
    """Salida y listado."""

    class Meta:
        model = TipoMineral
        fields = ["id", "codigo", "nombre", "unidad_medida", "activo"]
        read_only_fields = fields


class TipoMineralCreateSerializer(serializers.Serializer):
    codigo = serializers.CharField(max_length=6)
    nombre = serializers.CharField(max_length=100)
    unidad_medida = serializers.ChoiceField(
        choices=TipoMineral.UNIDADES, default=TipoMineral.TONELADA
    )


class TipoMineralUpdateSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=100, required=False)
