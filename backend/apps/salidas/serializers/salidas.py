from decimal import Decimal

from rest_framework import serializers

from apps.catalogo.models import Cliente, Producto
from apps.salidas.models import Salida, TipoMovimiento

_CANTIDAD_MINIMA = Decimal("0.01")


class SalidaListSerializer(serializers.ModelSerializer):
    """Salida del listado (HU-M04-03 CA01)."""

    producto_nombre = serializers.CharField(source="producto.nombre", read_only=True)
    cliente_nombre = serializers.CharField(source="cliente.razon_social", read_only=True)

    class Meta:
        model = Salida
        fields = [
            "id", "correlativo", "fecha", "producto", "producto_nombre",
            "cliente", "cliente_nombre", "tipo_movimiento", "cantidad_tn", "estado",
        ]
        read_only_fields = fields


class SalidaDetailSerializer(serializers.ModelSerializer):
    """Salida del detalle. `advertencia_stock` es un atributo transitorio que
    pone `services.salidas.registrar_salida`; en cualquier otra respuesta es
    `None` (HU-M04-01 CA02)."""

    producto_nombre = serializers.CharField(source="producto.nombre", read_only=True)
    cliente_nombre = serializers.CharField(source="cliente.razon_social", read_only=True)
    usuario_registro = serializers.CharField(source="usuario_registro.username", read_only=True)
    advertencia_stock = serializers.CharField(read_only=True, default=None, allow_null=True)

    class Meta:
        model = Salida
        fields = [
            "id", "correlativo", "fecha", "hora_registro",
            "producto", "producto_nombre", "cliente", "cliente_nombre",
            "tipo_movimiento", "cantidad_tn", "motivo", "usuario_registro",
            "estado", "motivo_anulacion", "advertencia_stock",
        ]
        read_only_fields = fields


class SalidaCreateSerializer(serializers.Serializer):
    """HU-M04-01 CA01. Ni `correlativo` ni `hora_registro` se aceptan: los
    asigna el servidor. La obligatoriedad condicional de `cliente` y `motivo`
    **no** se valida aquí (RN-M04-03, RN-M04-04): vive en el modelo y en el
    servicio, para que también la cumpla un alta que no venga del formulario.
    """

    fecha = serializers.DateField()
    producto = serializers.PrimaryKeyRelatedField(queryset=Producto.objects.filter(activo=True))
    cliente = serializers.PrimaryKeyRelatedField(
        queryset=Cliente.objects.filter(activo=True), required=False, allow_null=True
    )
    tipo_movimiento = serializers.ChoiceField(choices=TipoMovimiento.choices)
    # `min_value` rechaza el cero como error de campo; el mensaje literal de
    # HU-M04-01 CA03 lo emite el servicio, que es quien conoce la regla.
    cantidad_tn = serializers.DecimalField(
        max_digits=8, decimal_places=2, min_value=_CANTIDAD_MINIMA
    )
    motivo = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class AnularSalidaSerializer(serializers.Serializer):
    """HU-M04-03 CA03: el motivo vacío se rechaza con el mensaje literal de la
    historia, no con el genérico de un campo requerido — por eso se acepta
    aquí y se valida en `services.salidas.anular_salida`."""

    motivo = serializers.CharField(required=False, allow_blank=True, default="")
