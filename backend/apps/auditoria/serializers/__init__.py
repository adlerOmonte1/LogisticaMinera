from rest_framework import serializers

from apps.auditoria.models import EventoAuditoria

_SIN_DETALLE = {"operacion", "revierte"}


class EventoSerializer(serializers.ModelSerializer):
    """Un evento con su detalle de cambio: por campo, el valor anterior y el nuevo
    (HU-M09-02 CA02, HU-M09-03 CA03). La referencia legible llega en el contexto,
    resuelta para toda la página."""

    usuario = serializers.CharField(source="usuario.username", default=None, read_only=True)
    accion_texto = serializers.CharField(source="get_accion_display", read_only=True)
    referencia = serializers.SerializerMethodField()
    operacion = serializers.SerializerMethodField()
    cambios = serializers.SerializerMethodField()

    class Meta:
        model = EventoAuditoria
        fields = [
            "id", "fecha_hora", "accion", "accion_texto", "operacion", "entidad", "id_entidad", "referencia",
            "usuario", "cambios", "valores_anteriores", "valores_nuevos", "motivo", "direccion_ip",
            "ingresos_relacionados",
        ]
        read_only_fields = fields

    def get_referencia(self, evento) -> str | None:
        return self.context.get("referencias", {}).get((evento.entidad, evento.id_entidad))

    def get_operacion(self, evento) -> str | None:
        return (evento.valores_nuevos or {}).get("operacion")

    def get_cambios(self, evento) -> list[dict]:
        anteriores = evento.valores_anteriores or {}
        nuevos = evento.valores_nuevos or {}
        campos = [c for c in dict.fromkeys([*anteriores, *nuevos]) if c not in _SIN_DETALLE]
        return [{"campo": c, "anterior": anteriores.get(c), "nuevo": nuevos.get(c)} for c in campos]


__all__ = ["EventoSerializer"]
