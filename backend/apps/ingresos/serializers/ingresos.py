from decimal import Decimal

from rest_framework import serializers

from apps.catalogo.models import Producto, Vehiculo
from apps.ingresos.models import Ingreso

_PESO_MINIMO = Decimal("0.01")


class IngresoListSerializer(serializers.ModelSerializer):
    """Salida del listado (HU-M03-04)."""

    vehiculo_placa = serializers.CharField(source="vehiculo.placa", read_only=True)
    producto_nombre = serializers.CharField(source="producto.nombre", read_only=True)

    class Meta:
        model = Ingreso
        fields = [
            "id", "correlativo", "fecha_pesaje", "hora_pesaje", "numero_ticket",
            "vehiculo", "vehiculo_placa", "producto", "producto_nombre",
            "peso_bruto_tn", "tara_tn", "peso_neto_tn", "estado",
        ]
        read_only_fields = fields


class IngresoDetailSerializer(serializers.ModelSerializer):
    """Salida del detalle (HU-M03-05): todos los campos, incluidas las tres
    marcas temporales y el motivo de anulación cuando corresponde."""

    vehiculo_placa = serializers.CharField(source="vehiculo.placa", read_only=True)
    producto_nombre = serializers.CharField(source="producto.nombre", read_only=True)
    usuario_registro = serializers.CharField(source="usuario_registro.username", read_only=True)

    class Meta:
        model = Ingreso
        fields = [
            "id", "correlativo", "uuid_local", "fecha_pesaje", "hora_pesaje",
            "hora_registro", "hora_sincronizacion",
            "vehiculo", "vehiculo_placa", "producto", "producto_nombre",
            "peso_bruto_tn", "tara_tn", "peso_neto_tn", "numero_ticket",
            "usuario_registro", "capturado_offline", "estado", "motivo_anulacion",
        ]
        read_only_fields = fields


class IngresoCreateSerializer(serializers.Serializer):
    """HU-M03-01 CA01. `peso_neto_tn` no se acepta: lo calcula el servidor
    (RN-M03-04, HU-M03-02 CA03)."""

    fecha_pesaje = serializers.DateField()
    hora_pesaje = serializers.TimeField()
    numero_ticket = serializers.CharField(max_length=20)
    vehiculo = serializers.PrimaryKeyRelatedField(queryset=Vehiculo.objects.filter(activo=True))
    producto = serializers.PrimaryKeyRelatedField(queryset=Producto.objects.filter(activo=True))
    peso_bruto_tn = serializers.DecimalField(max_digits=8, decimal_places=2, min_value=_PESO_MINIMO)
    tara_tn = serializers.DecimalField(max_digits=8, decimal_places=2, min_value=_PESO_MINIMO)


class IngresoUpdateSerializer(serializers.Serializer):
    """HU-M03-06. Todos los campos opcionales: es un `PATCH` parcial. No
    incluye `correlativo` ni `hora_registro`: ver
    `services.ingresos.verificar_campos_no_editables`, que rechaza el intento
    antes de llegar aquí."""

    fecha_pesaje = serializers.DateField(required=False)
    hora_pesaje = serializers.TimeField(required=False)
    numero_ticket = serializers.CharField(max_length=20, required=False)
    vehiculo = serializers.PrimaryKeyRelatedField(
        queryset=Vehiculo.objects.filter(activo=True), required=False
    )
    producto = serializers.PrimaryKeyRelatedField(
        queryset=Producto.objects.filter(activo=True), required=False
    )
    peso_bruto_tn = serializers.DecimalField(
        max_digits=8, decimal_places=2, min_value=_PESO_MINIMO, required=False
    )
    tara_tn = serializers.DecimalField(
        max_digits=8, decimal_places=2, min_value=_PESO_MINIMO, required=False
    )


class AnularIngresoSerializer(serializers.Serializer):
    """HU-M03-07 CA02: el motivo vacío se rechaza con el mensaje literal de
    la historia, no con el genérico de un campo requerido — por eso se acepta
    aquí y se valida en `services.ingresos.anular_ingreso`."""

    motivo = serializers.CharField(required=False, allow_blank=True, default="")
