from rest_framework import serializers

from apps.catalogo.models import TipoMineral


class TipoMineralSerializer(serializers.ModelSerializer):
    """Salida y listado."""

    class Meta:
        model = TipoMineral
        fields = ["id", "codigo", "nombre", "unidad_medida", "activo"]
        read_only_fields = fields


class TipoMineralCreateSerializer(serializers.Serializer):
    """`desde_registro` marca el alta rápida de M03 (HU-M02-02 CA07): el código
    se vuelve opcional. Los campos vacíos los rechaza el servicio con el mensaje
    de cada criterio."""

    codigo = serializers.CharField(max_length=20, required=False, allow_blank=True, default="")
    nombre = serializers.CharField(max_length=100, required=False, allow_blank=True, default="")
    unidad_medida = serializers.ChoiceField(
        choices=TipoMineral.UNIDADES, default=TipoMineral.TONELADA
    )
    desde_registro = serializers.BooleanField(required=False, default=False)


class TipoMineralUpdateSerializer(serializers.Serializer):
    """Solo el nombre: el código no cambia tras el alta (RN-M02-16)."""

    nombre = serializers.CharField(max_length=100, required=False, allow_blank=True)
