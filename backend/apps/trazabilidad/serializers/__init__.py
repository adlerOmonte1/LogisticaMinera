"""Contrato HTTP de M06. Las estimaciones —toneladas por parte, peso de los
bigbags y la diferencia del resumen— salen señaladas con `es_estimacion`
(RNF-M06-09) y nunca entran en un total (RN-M06-17)."""

from decimal import Decimal

from rest_framework import serializers

from apps.trazabilidad.dominio import NOMBRE_ETAPA, Destino, Ruta
from apps.trazabilidad.models import LoteProceso
from apps.trazabilidad.repositories import LoteRepository
from apps.trazabilidad.services.recorrido import (
    Carga,
    es_tardio,
    pendientes,
    requiere_secado_propio,
    texto_fraccion,
    toneladas,
    toneladas_de,
)


class AbrirLoteSerializer(serializers.Serializer):
    nombre = serializers.CharField(required=False, allow_blank=True, default="")
    tipo_mineral = serializers.IntegerField(required=False, allow_null=True)
    fecha_apertura = serializers.DateField(required=False, allow_null=True)


class MineralSerializer(serializers.Serializer):
    tipo_mineral = serializers.IntegerField()


class AsignarSerializer(serializers.Serializer):
    ingresos = serializers.ListField(child=serializers.IntegerField(), required=False, default=list)
    autorizacion = serializers.CharField(required=False, allow_blank=True, default="")


class BigbagsSerializer(serializers.Serializer):
    parte = serializers.IntegerField(required=False, allow_null=True)
    cantidad = serializers.IntegerField(required=False, allow_null=True)
    recalcular = serializers.BooleanField(required=False, default=False)
    peso_aproximado_tn = serializers.DecimalField(max_digits=6, decimal_places=2, required=False, allow_null=True)


class EtapaSerializer(serializers.Serializer):
    etapa = serializers.ChoiceField(choices=list(NOMBRE_ETAPA), required=False, allow_null=True)
    ruta = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    parte = serializers.IntegerField(required=False, allow_null=True)
    ingreso = serializers.IntegerField(required=False, allow_null=True)
    fecha_hora = serializers.DateTimeField(required=False, allow_null=True)
    horas_molienda = serializers.DecimalField(max_digits=6, decimal_places=2, required=False, allow_null=True)
    observacion = serializers.CharField(required=False, allow_blank=True, default="")
    bigbags = BigbagsSerializer(required=False, allow_null=True)


class FraccionParteSerializer(serializers.Serializer):
    parte = serializers.IntegerField()
    fraccion = serializers.CharField()


class SecadoPropioSerializer(serializers.Serializer):
    fecha_hora = serializers.DateTimeField(required=False, allow_null=True)
    observacion = serializers.CharField(required=False, allow_blank=True, default="")
    fracciones = FraccionParteSerializer(many=True, required=False, default=list)


class ParteEntradaSerializer(serializers.Serializer):
    nombre = serializers.CharField(required=False, allow_blank=True, default="")
    fraccion = serializers.CharField(required=False, allow_blank=True, default="")
    ruta = serializers.CharField(required=False, allow_blank=True, default="")


class DivisionSerializer(serializers.Serializer):
    partes = ParteEntradaSerializer(many=True)


class CierreSerializer(serializers.Serializer):
    destino = serializers.CharField(required=False, allow_blank=True, default="")
    observacion = serializers.CharField(required=False, allow_blank=True, default="")


class LoteListaSerializer(serializers.ModelSerializer):
    tipo_mineral_nombre = serializers.CharField(source="tipo_mineral.nombre", read_only=True)
    ingresos = serializers.IntegerField(source="n_ingresos", read_only=True)
    toneladas = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True, coerce_to_string=True)

    class Meta:
        model = LoteProceso
        fields = ["id", "codigo", "nombre", "estado", "tipo_mineral", "tipo_mineral_nombre", "fecha_apertura",
                  "fecha_inicio_recorrido", "ruta", "destino", "ingresos", "toneladas"]
        read_only_fields = fields


class LoteSerializer(serializers.ModelSerializer):
    """HU-M06-01 CA16: estado, composición por tipo de mineral con los tardíos
    señalados, partes, recorrido, bigbags y el total de toneladas."""

    composicion = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()
    partes = serializers.SerializerMethodField()
    recorrido = serializers.SerializerMethodField()
    bigbags = serializers.SerializerMethodField()
    siguientes = serializers.SerializerMethodField()
    pendientes = serializers.SerializerMethodField()
    destino_texto = serializers.CharField(source="get_destino_display", read_only=True)
    usuario_cierre = serializers.CharField(source="usuario_cierre.username", default=None, read_only=True)

    class Meta:
        model = LoteProceso
        fields = ["id", "codigo", "nombre", "estado", "fecha_apertura", "fecha_inicio_recorrido", "ruta",
                  "destino", "destino_texto", "observacion_cierre", "fecha_cierre", "usuario_cierre",
                  "composicion", "total", "partes", "recorrido", "bigbags", "siguientes", "pendientes"]
        read_only_fields = fields

    def get_composicion(self, lote) -> list[dict]:
        agregados = {a["tipo_mineral"]: a for a in LoteRepository.composicion(lote)}
        grupos = []
        for lm in lote.lista_minerales.all():
            if lm.fecha_retiro is not None:
                continue
            ingresos = [i for i in lote.ingresos.all() if i.tipo_mineral_id == lm.tipo_mineral_id]
            agregado = agregados.get(lm.tipo_mineral_id, {})
            grupos.append({
                "tipo_mineral": {"id": lm.tipo_mineral_id, "codigo": lm.tipo_mineral.codigo,
                                 "nombre": lm.tipo_mineral.nombre},
                "otro_mineral": bool(lm.autorizacion),  # DR-27: «Otro mineral», con su autorización
                "autorizacion": lm.autorizacion or None,
                "ingresos": [{
                    "id": i.pk, "codigo": i.codigo, "fecha_hora_pesaje": i.fecha_hora_pesaje,
                    "peso_neto_tn": None if i.peso_neto_tn is None else str(i.peso_neto_tn),
                    "estado": i.estado, "tardio": es_tardio(i, lote),
                    "secado_propio": requiere_secado_propio(i, lote), "otro_mineral": bool(lm.autorizacion),
                } for i in sorted(ingresos, key=lambda x: x.fecha_hora_pesaje)],
                "cantidad": agregado.get("cantidad", 0),
                "toneladas": str(agregado.get("toneladas") or Decimal("0.00")),
            })
        return grupos

    def get_total(self, lote) -> dict:
        return {"ingresos": sum(1 for i in lote.ingresos.all() if i.estado == "REGISTRADO"),
                "toneladas": str(toneladas(lote))}

    def get_partes(self, lote) -> list[dict]:
        total = toneladas(lote)
        return [{"id": p.pk, "nombre": p.nombre, "fraccion": texto_fraccion(p.fraccion), "ruta": p.ruta,
                 "ruta_texto": Ruta(p.ruta).label, "toneladas_aproximadas": str(toneladas_de(lote, p, total)),
                 "es_estimacion": True} for p in lote.partes.all()]

    def get_recorrido(self, lote) -> list[dict]:
        return [{
            "id": p.pk, "etapa": p.etapa.codigo, "etapa_texto": p.etapa.nombre,
            "carga": Carga(lote, p.parte, p.ingreso_tardio).nombre, "parte": p.parte_id,
            "ingreso_tardio": p.ingreso_tardio_id, "fecha_hora": p.fecha_hora,
            "usuario": p.usuario_registro.username, "horas_molienda": None if p.horas_molienda is None
            else str(p.horas_molienda), "observacion": p.observacion,
        } for p in lote.pasos.all()]

    def get_bigbags(self, lote) -> list[dict]:
        return [{"id": b.pk, "parte": b.parte_id, "cantidad": b.cantidad, "peso_aproximado_tn": str(b.peso_aproximado_tn),
                 "recalculado": b.recalculado, "es_estimacion": True, "fecha_hora": b.fecha_hora}
                for b in lote.bigbags.all()]

    def get_siguientes(self, lote) -> list[dict]:
        """Lo que corresponde registrar en cada carga, para que la interfaz ofrezca
        solo eso (RNF-M06-07)."""
        if lote.estado != LoteProceso.EN_RECORRIDO:
            return []
        cargas = [Carga(lote)] + [Carga(lote, p) for p in lote.partes.all()]
        for i in lote.ingresos.all():
            if i.estado != "ANULADO" and requiere_secado_propio(i, lote):
                cargas.append(Carga(lote, None, i))
                cargas += [Carga(lote, r.parte, i) for r in i.repartos.all()]
        resultado = []
        for c in cargas:
            elegir = c.necesita_ruta() and c.ingreso is None
            etapa = None if elegir else c.siguiente()
            if elegir or etapa:
                resultado.append({"carga": c.nombre, "parte": c.parte.pk if c.parte else None,
                                  "ingreso": c.ingreso.pk if c.ingreso else None, "etapa": etapa,
                                  "elegir_ruta": elegir})
        return resultado

    def get_pendientes(self, lote) -> list[str]:
        return pendientes(lote)


class CatalogosSerializer:
    @staticmethod
    def rutas() -> list[dict]:
        from apps.trazabilidad.dominio import ETAPAS_POR_RUTA  # noqa: PLC0415

        return [{"codigo": r.value, "nombre": r.label, "etapas": list(ETAPAS_POR_RUTA[r])} for r in Ruta]

    @staticmethod
    def destinos() -> list[dict]:
        return [{"codigo": d.value, "nombre": d.label} for d in Destino]
