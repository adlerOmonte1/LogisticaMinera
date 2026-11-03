"""Contrato HTTP de M03. Los serializers de entrada solo declaran lo que el
cliente puede enviar: el código, las marcas del servidor, la tara y el peso neto
no figuran, de modo que si llegan se ignoran (HU-M03-02 CA04, RS-M03-12)."""

from decimal import Decimal

from django.urls import reverse
from rest_framework import serializers

from apps.ingresos.models import Ingreso
from apps.ingresos.repositories import HistorialIngresoRepository


class BorradorEntradaSerializer(serializers.Serializer):
    imagen = serializers.FileField(required=False, allow_empty_file=True)
    sin_foto = serializers.BooleanField(required=False, default=False)
    motivo_sin_respaldo = serializers.CharField(required=False, allow_blank=True, default="")


class _CamposCorregiblesSerializer(serializers.Serializer):
    placa = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    fecha = serializers.DateField(required=False, allow_null=True)
    hora = serializers.TimeField(required=False, allow_null=True)
    peso_bruto_tn = serializers.DecimalField(
        max_digits=8, decimal_places=2, min_value=Decimal("0.01"), required=False, allow_null=True
    )
    tipo_mineral = serializers.IntegerField(required=False, allow_null=True)
    justificaciones = serializers.DictField(
        child=serializers.CharField(allow_blank=True), required=False, default=dict
    )


class RegistroEntradaSerializer(_CamposCorregiblesSerializer):
    borrador = serializers.CharField(required=False, allow_blank=True, default="")


class CorreccionEntradaSerializer(_CamposCorregiblesSerializer):
    motivo = serializers.CharField(required=False, allow_blank=True, default="")


class ReversionEntradaSerializer(serializers.Serializer):
    motivo = serializers.CharField(required=False, allow_blank=True, default="")
    correccion = serializers.IntegerField(required=False, allow_null=True)
    justificaciones = serializers.DictField(
        child=serializers.CharField(allow_blank=True), required=False, default=dict
    )


class AnulacionEntradaSerializer(serializers.Serializer):
    motivo = serializers.CharField(required=False, allow_blank=True, default="")


class DestareEntradaSerializer(serializers.Serializer):
    vehiculo = serializers.IntegerField()
    tara_tn = serializers.DecimalField(
        max_digits=8, decimal_places=2, min_value=Decimal("0.01"), required=False, allow_null=True
    )
    fecha_destare = serializers.DateTimeField(required=False, allow_null=True)
    justificaciones = serializers.DictField(
        child=serializers.CharField(allow_blank=True), required=False, default=dict
    )


class IngresoSerializer(serializers.ModelSerializer):
    """Recurso del ingreso (HU-M03-01 CA09 y CA17, HU-M03-03 CA05). Las tres
    marcas de tiempo salen como tres valores distintos y todas son de solo
    lectura. El sin respaldo fotográfico se señala con su motivo."""

    placa = serializers.CharField(source="vehiculo.placa", read_only=True)
    tipo_vehiculo = serializers.CharField(read_only=True)
    tipo_mineral_codigo = serializers.CharField(source="tipo_mineral.codigo", read_only=True)
    tipo_mineral_nombre = serializers.CharField(source="tipo_mineral.nombre", read_only=True)
    motivo_sin_respaldo_texto = serializers.CharField(source="get_motivo_sin_respaldo_display", read_only=True)
    registrado_por = serializers.CharField(source="usuario_registro.username", read_only=True)
    imagen_url = serializers.SerializerMethodField()
    anulado_por = serializers.SerializerMethodField()
    reconocimiento = serializers.SerializerMethodField()
    correccion_revertible = serializers.SerializerMethodField()

    class Meta:
        model = Ingreso
        fields = [
            "id", "codigo", "estado", "placa", "vehiculo", "tipo_vehiculo",
            "tipo_mineral", "tipo_mineral_codigo", "tipo_mineral_nombre",
            "fecha_hora_pesaje", "hora_inicio_registro", "hora_fin_registro",
            "peso_bruto_tn", "tara_tn", "peso_neto_tn",
            "sin_respaldo_fotografico", "motivo_sin_respaldo", "motivo_sin_respaldo_texto", "imagen_url",
            "registrado_por", "motivo_anulacion", "anulado_por", "reconocimiento", "correccion_revertible",
        ]
        read_only_fields = fields

    def get_imagen_url(self, obj) -> str | None:
        if not obj.imagen_ticket:
            return None
        return reverse("ingresos:ingreso-imagen", kwargs={"pk": obj.pk})

    def get_anulado_por(self, obj) -> str | None:
        if obj.estado != Ingreso.ANULADO:
            return None
        evento = HistorialIngresoRepository.anulacion(obj.pk)
        return evento.usuario.username if evento and evento.usuario else None

    def get_reconocimiento(self, obj) -> dict:
        """HU-M04-02 CA03: sin reconocimiento, se dice por qué."""
        rec = getattr(obj, "reconocimiento", None) if hasattr(obj, "reconocimiento") else None
        if rec is None:
            return {"id": None, "hubo_reconocimiento": False,
                    "motivo": "Registrado sin fotografía del ticket" if obj.sin_respaldo_fotografico else None}
        if not rec.exito:
            from apps.reconocimiento.serializers import ReconocimientoSerializer  # noqa: PLC0415

            motivo = ReconocimientoSerializer().get_motivo_fallo(rec)
            return {"id": rec.pk, "hubo_reconocimiento": False, "motivo": motivo}
        return {"id": rec.pk, "hubo_reconocimiento": True, "motivo": None}

    def get_correccion_revertible(self, obj) -> int | None:
        if obj.estado == Ingreso.ANULADO:
            return None
        evento = HistorialIngresoRepository.ultima_correccion_vigente(obj.pk)
        return evento.pk if evento else None


class PendienteDestareSerializer(serializers.ModelSerializer):
    """HU-M03-04 CA06: código, placa, fecha del pesaje y peso bruto."""

    placa = serializers.CharField(source="vehiculo.placa", read_only=True)

    class Meta:
        model = Ingreso
        fields = ["id", "codigo", "vehiculo", "placa", "fecha_hora_pesaje", "peso_bruto_tn"]
        read_only_fields = fields
