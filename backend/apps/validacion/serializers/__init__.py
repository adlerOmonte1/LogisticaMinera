from rest_framework import serializers

from apps.validacion.models import ResultadoValidacion


class ResultadoValidacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResultadoValidacion
        fields = ["id", "regla", "momento", "cumple", "detalle", "resolucion", "justificacion", "fecha_hora"]
        read_only_fields = fields


__all__ = ["ResultadoValidacionSerializer"]
