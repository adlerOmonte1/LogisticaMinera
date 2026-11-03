from decimal import Decimal

from rest_framework import serializers

from apps.reconocimiento.dominio import MENSAJE_ILEGIBLE, MENSAJE_NO_DISPONIBLE, NO_DISPONIBLE
from apps.reconocimiento.models import CampoReconocido, ReconocimientoTicket


class CampoReconocidoSerializer(serializers.ModelSerializer):
    fue_corregido = serializers.BooleanField(read_only=True)
    dudoso = serializers.SerializerMethodField()

    class Meta:
        model = CampoReconocido
        fields = ["nombre_campo", "valor_reconocido", "valor_confirmado", "confianza", "fue_corregido", "dudoso"]
        read_only_fields = fields

    def get_dudoso(self, campo) -> bool:
        umbral = campo.reconocimiento.umbral_confianza
        return campo.confianza is not None and Decimal(campo.confianza) < umbral


class ReconocimientoSerializer(serializers.ModelSerializer):
    """Comparación campo a campo (HU-M04-02). Solo lectura para los tres roles;
    `puede_corregir_ingreso` le dice a la interfaz si ofrecer la corrección, que
    es de M03 (CA04)."""

    codigo_ingreso = serializers.CharField(source="ingreso.codigo", read_only=True)
    campos = CampoReconocidoSerializer(many=True, read_only=True)
    motivo_fallo = serializers.SerializerMethodField()
    puede_corregir_ingreso = serializers.SerializerMethodField()

    class Meta:
        model = ReconocimientoTicket
        fields = [
            "id", "ingreso", "codigo_ingreso", "motor", "version_motor", "fecha_proceso",
            "umbral_confianza", "exito", "causa_fallo", "motivo_fallo", "campos", "puede_corregir_ingreso",
        ]
        read_only_fields = fields

    def get_motivo_fallo(self, obj) -> str | None:
        if obj.exito:
            return None
        return MENSAJE_NO_DISPONIBLE if obj.causa_fallo == NO_DISPONIBLE else MENSAJE_ILEGIBLE

    def get_puede_corregir_ingreso(self, obj) -> bool:
        from apps.accounts.permissions import GESTION  # noqa: PLC0415

        usuario = self.context["request"].user
        return usuario.tiene_rol(*GESTION)


__all__ = ["CampoReconocidoSerializer", "ReconocimientoSerializer"]
