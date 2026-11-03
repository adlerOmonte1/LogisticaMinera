"""Entidades del lote de proceso (modelo de datos 3.1, M06).

`on_delete=PROTECT` en todas las claves foráneas: nada de lo que participa en un
recorrido puede borrarse. Las cifras del lote —toneladas, estimaciones de las
partes y de los bigbags— no se almacenan: se calculan sobre los ingresos al
consultarse (RN-M06-17, RN-M06-24).
"""

from fractions import Fraction

from django.conf import settings
from django.db import models
from django.db.models import Q

from apps.catalogo.models import TipoMineral
from apps.trazabilidad.dominio import ETAPAS, Destino, Ruta


class EtapaProceso(models.Model):
    """Catálogo cerrado de cuatro filas, cargado por migración de datos (RN-M06-09)."""

    codigo = models.CharField(max_length=10, unique=True, choices=[(c, n) for c, n, _ in ETAPAS], editable=False)
    nombre = models.CharField(max_length=50, editable=False)
    orden = models.PositiveSmallIntegerField(editable=False)

    class Meta:
        db_table = "etapa_proceso"
        ordering = ["orden"]

    def __str__(self):
        return self.nombre


class ContadorLote(models.Model):
    """Soporte técnico del código del lote, como el del ingreso (D-02)."""

    anio = models.PositiveIntegerField(unique=True)
    ultimo_valor = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "contador_correlativo_lote"


class LoteProceso(models.Model):
    ABIERTO = "ABIERTO"
    EN_RECORRIDO = "EN_RECORRIDO"
    CERRADO = "CERRADO"
    ESTADOS = [(ABIERTO, "Abierto"), (EN_RECORRIDO, "En recorrido"), (CERRADO, "Cerrado")]

    codigo = models.CharField(max_length=20, unique=True, editable=False)
    nombre = models.CharField(max_length=80, unique=True)  # RN-M06-14
    tipo_mineral = models.ForeignKey(TipoMineral, on_delete=models.PROTECT, related_name="+")
    fecha_apertura = models.DateField()
    fecha_inicio_recorrido = models.DateTimeField(null=True, blank=True, editable=False)
    ruta = models.CharField(max_length=30, choices=Ruta.choices, blank=True)  # sin dividir
    estado = models.CharField(max_length=12, choices=ESTADOS, default=ABIERTO)
    destino = models.CharField(max_length=10, choices=Destino.choices, blank=True)
    observacion_cierre = models.TextField(blank=True)
    fecha_cierre = models.DateTimeField(null=True, blank=True, editable=False)
    usuario_cierre = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT, editable=False, related_name="+"
    )
    usuario_registro = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, editable=False, related_name="+"
    )
    fecha_registro = models.DateTimeField(editable=False)

    class Meta:
        db_table = "lote_proceso"
        ordering = ["-fecha_apertura", "-id"]
        indexes = [models.Index(fields=["estado"], name="idx_lote_estado")]
        constraints = [
            models.UniqueConstraint(models.functions.Lower("nombre"), name="uq_lote_nombre_sin_mayusculas"),
            models.CheckConstraint(
                check=~Q(estado="CERRADO") | (~Q(destino="") & Q(fecha_cierre__isnull=False)),
                name="ck_lote_cerrado_con_destino",
            ),
        ]

    def __str__(self):
        return f"{self.codigo} {self.nombre}"

    @property
    def dividido(self) -> bool:
        return self.partes.exists()


class LoteMineral(models.Model):
    """Lista de tipos que admite el lote (DR-27). Quitar uno es una baja lógica (D-22)."""

    lote = models.ForeignKey(LoteProceso, on_delete=models.PROTECT, related_name="lista_minerales")
    tipo_mineral = models.ForeignKey(TipoMineral, on_delete=models.PROTECT, related_name="+")
    autorizacion = models.TextField(blank=True)
    fecha_hora = models.DateTimeField(editable=False)
    usuario_registro = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, editable=False, related_name="+"
    )
    fecha_retiro = models.DateTimeField(null=True, blank=True, editable=False)
    usuario_retiro = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT, editable=False, related_name="+"
    )

    class Meta:
        db_table = "lote_mineral"
        ordering = ["fecha_hora", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["lote", "tipo_mineral"], condition=Q(fecha_retiro__isnull=True),
                name="uq_lote_mineral_vigente",
            ),
        ]


class _Fraccion(models.Model):
    numerador = models.PositiveSmallIntegerField()
    denominador = models.PositiveSmallIntegerField()

    class Meta:
        abstract = True

    @property
    def fraccion(self) -> Fraction:
        return Fraction(self.numerador, self.denominador)


class ParteLote(_Fraccion):
    """Fracciones como numerador y denominador: con decimales, tres tercios no
    suman la unidad (RNF-M06-11)."""

    lote = models.ForeignKey(LoteProceso, on_delete=models.PROTECT, related_name="partes")
    nombre = models.CharField(max_length=80)
    ruta = models.CharField(max_length=30, choices=Ruta.choices)

    class Meta:
        db_table = "parte_lote"
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(fields=["lote", "nombre"], name="uq_parte_nombre_por_lote"),
            models.CheckConstraint(check=Q(numerador__gt=0) & Q(denominador__gt=0), name="ck_parte_fraccion_positiva"),
        ]

    def __str__(self):
        return self.nombre


class RepartoIngreso(_Fraccion):
    """Porción de un ingreso tardío en una parte de un lote dividido (DR-20)."""

    ingreso = models.ForeignKey("ingresos.Ingreso", on_delete=models.PROTECT, related_name="repartos")
    parte = models.ForeignKey(ParteLote, on_delete=models.PROTECT, related_name="repartos")

    class Meta:
        db_table = "reparto_ingreso"
        indexes = [models.Index(fields=["ingreso"], name="idx_reparto_ingreso")]
        constraints = [models.UniqueConstraint(fields=["ingreso", "parte"], name="uq_reparto_ingreso_parte")]


class PasoEtapa(models.Model):
    """El paso de una carga por una etapa. La carga es el lote —secado común o
    ruta sin dividir—, una parte, el secado propio de un ingreso tardío o la
    porción de ese ingreso en la ruta (D-26). Un solo paso por etapa y carga
    (RN-M06-07): la unicidad trata los nulos como iguales."""

    lote = models.ForeignKey(LoteProceso, on_delete=models.PROTECT, related_name="pasos")
    parte = models.ForeignKey(ParteLote, null=True, blank=True, on_delete=models.PROTECT, related_name="pasos")
    ingreso_tardio = models.ForeignKey(
        "ingresos.Ingreso", null=True, blank=True, on_delete=models.PROTECT, related_name="pasos_propios"
    )
    etapa = models.ForeignKey(EtapaProceso, on_delete=models.PROTECT, related_name="+")
    fecha_hora = models.DateTimeField()
    horas_molienda = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    observacion = models.TextField(blank=True)
    usuario_registro = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, editable=False, related_name="+"
    )
    fecha_registro = models.DateTimeField(editable=False)

    class Meta:
        db_table = "paso_etapa"
        ordering = ["fecha_hora", "id"]
        indexes = [models.Index(fields=["lote"], name="idx_paso_lote")]
        constraints = [
            models.UniqueConstraint(
                fields=["lote", "parte", "ingreso_tardio", "etapa"], nulls_distinct=False,
                name="uq_paso_por_carga_y_etapa",
            ),
            models.CheckConstraint(
                check=Q(horas_molienda__isnull=True) | Q(horas_molienda__gt=0), name="ck_paso_horas_positivas"
            ),
        ]


class Bigbag(models.Model):
    """Registro de un grupo de bigbags. Datos descriptivos, no inventario (DR-15)."""

    lote = models.ForeignKey(LoteProceso, on_delete=models.PROTECT, related_name="bigbags")
    parte = models.ForeignKey(ParteLote, null=True, blank=True, on_delete=models.PROTECT, related_name="bigbags")
    cantidad = models.PositiveIntegerField()
    peso_aproximado_tn = models.DecimalField(max_digits=6, decimal_places=2)
    recalculado = models.BooleanField(default=False)
    fecha_hora = models.DateTimeField(editable=False)
    usuario_registro = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, editable=False, related_name="+"
    )

    class Meta:
        db_table = "bigbag"
        ordering = ["fecha_hora", "id"]
        constraints = [models.CheckConstraint(check=Q(cantidad__gt=0), name="ck_bigbag_cantidad_positiva")]
