from django.db import models

from apps.accounts.models import Usuario
from apps.catalogo.models import TipoMineral, Vehiculo


class IngresoQuerySet(models.QuerySet):
    def computables(self):
        """Los ingresos que suman toneladas: solo los Registrados. Es el único
        criterio del sistema para cualquier total —lote, listado, calendario,
        inicio y consolidado (RN-M07-02, RN-M07-12)—: «distinto de anulado»
        sumaría los En proceso, que no tienen peso neto (notas de M07)."""
        return self.filter(estado=Ingreso.REGISTRADO)


class Ingreso(models.Model):
    """Unidad de registro del sistema: un volquete que entrega mineral en planta,
    con su respaldo y las tres marcas de tiempo que describen cómo se registró
    (modelo de datos 3.1).

    - D-01: `fecha_hora_pesaje`, `hora_inicio_registro` y `hora_fin_registro` son
      independientes. Las dos últimas las asigna el servidor y nadie las edita.
    - D-02: `codigo` lo asigna `services/correlativo.py` dentro de una transacción
      con bloqueo. Es el único identificador del ingreso (DR-12).
    - D-17: el peso neto lo calcula el servidor como bruto menos la tara del
      vehículo, y el ingreso conserva la tara aplicada. Ambos quedan nulos
      mientras el ingreso está En proceso, a la espera del destare.
    - D-18: la imagen se guarda por el almacenamiento de Django; falta solo en el
      registro sin foto, que lleva su marca y su motivo (DR-13).
    """

    # Lista cerrada de motivos del registro sin foto (RN-M03-21, HU-M03-01).
    TICKET_EXTRAVIADO = "TICKET_EXTRAVIADO"
    SIN_CAMARA = "SIN_CAMARA"
    BALANZA_SIN_TICKET = "BALANZA_SIN_TICKET"
    OTRO = "OTRO"
    MOTIVOS_SIN_FOTO = [
        (TICKET_EXTRAVIADO, "Ticket extraviado o dañado"),
        (SIN_CAMARA, "Sin cámara o sin señal en el punto de pesaje"),
        (BALANZA_SIN_TICKET, "La balanza no emitió ticket"),
        (OTRO, "Otro"),
    ]

    EN_PROCESO = "EN_PROCESO"
    REGISTRADO = "REGISTRADO"
    ANULADO = "ANULADO"
    ESTADOS = [(EN_PROCESO, "En proceso"), (REGISTRADO, "Registrado"), (ANULADO, "Anulado")]

    codigo = models.CharField(max_length=20, unique=True, editable=False, verbose_name="Código")
    imagen_ticket = models.ImageField(
        upload_to="tickets/%Y/%m/", null=True, blank=True, verbose_name="Imagen del ticket"
    )
    sin_respaldo_fotografico = models.BooleanField(
        default=False, editable=False, verbose_name="Sin respaldo fotográfico"
    )
    motivo_sin_respaldo = models.CharField(
        max_length=60,
        choices=MOTIVOS_SIN_FOTO,
        blank=True,
        editable=False,
        verbose_name="Motivo del registro sin foto",
    )
    fecha_hora_pesaje = models.DateTimeField(verbose_name="Fecha y hora del pesaje")
    hora_inicio_registro = models.DateTimeField(
        editable=False, verbose_name="Inicio del registro"
    )
    hora_fin_registro = models.DateTimeField(editable=False, verbose_name="Fin del registro")
    vehiculo = models.ForeignKey(
        Vehiculo, on_delete=models.PROTECT, related_name="ingresos", verbose_name="Vehículo"
    )
    tipo_mineral = models.ForeignKey(
        TipoMineral,
        on_delete=models.PROTECT,
        related_name="ingresos",
        verbose_name="Tipo de mineral",
    )
    peso_bruto_tn = models.DecimalField(
        max_digits=8, decimal_places=2, verbose_name="Peso bruto (tn)"
    )
    tara_tn = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        editable=False,
        verbose_name="Tara aplicada (tn)",
    )
    peso_neto_tn = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        editable=False,
        verbose_name="Peso neto (tn)",
    )
    usuario_registro = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        editable=False,
        related_name="ingresos_registrados",
        verbose_name="Registrado por",
    )
    estado = models.CharField(max_length=12, choices=ESTADOS, verbose_name="Estado")
    motivo_anulacion = models.TextField(
        null=True, blank=True, verbose_name="Motivo de anulación"
    )
    # M06 escribe estos dos campos a través de su servicio: un ingreso pertenece
    # a un lote como máximo (RN-M06-01). La fecha de asignación distingue el
    # ingreso tardío y si llegó antes o después del secado del lote (D-26).
    lote = models.ForeignKey(
        "trazabilidad.LoteProceso",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        editable=False,
        related_name="ingresos",
        verbose_name="Lote de proceso",
    )
    fecha_asignacion_lote = models.DateTimeField(
        null=True, blank=True, editable=False, verbose_name="Asignación al lote"
    )

    objects = IngresoQuerySet.as_manager()

    class Meta:
        db_table = "ingreso"
        verbose_name = "Ingreso"
        verbose_name_plural = "Ingresos"
        ordering = ["-fecha_hora_pesaje"]
        indexes = [
            # Consulta por placa y fecha (M07) y búsqueda de un posible duplicado (V1).
            models.Index(fields=["vehiculo", "fecha_hora_pesaje"], name="idx_ingreso_vehiculo_fecha"),
            # Total acumulado mensual por tipo de mineral (M08).
            models.Index(fields=["fecha_hora_pesaje", "tipo_mineral"], name="idx_ingreso_fecha_mineral"),
            # Excluir anulados y En proceso de todo total.
            models.Index(fields=["estado"], name="idx_ingreso_estado"),
            # Composición de un lote y recorrido de un ingreso (M06).
            models.Index(fields=["lote"], name="idx_ingreso_lote"),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(peso_bruto_tn__gt=0)
                & (models.Q(tara_tn__isnull=True) | models.Q(tara_tn__gt=0)),
                name="ck_ingreso_pesos_positivos",
            ),
            # V2 como salvaguarda de base, además del mensaje del validador.
            models.CheckConstraint(
                check=models.Q(tara_tn__isnull=True) | models.Q(tara_tn__lt=models.F("peso_bruto_tn")),
                name="ck_ingreso_tara_menor_bruto",
            ),
            # D-17: el neto es exactamente bruto menos la tara aplicada.
            models.CheckConstraint(
                check=models.Q(peso_neto_tn__isnull=True)
                | models.Q(peso_neto_tn=models.F("peso_bruto_tn") - models.F("tara_tn")),
                name="ck_ingreso_neto_calculado",
            ),
            # RN-M03-17: En proceso sin tara ni neto; Registrado con ambos.
            models.CheckConstraint(
                check=models.Q(estado="ANULADO")
                | models.Q(estado="EN_PROCESO", tara_tn__isnull=True, peso_neto_tn__isnull=True)
                | models.Q(estado="REGISTRADO", tara_tn__isnull=False, peso_neto_tn__isnull=False),
                name="ck_ingreso_estado_y_pesos",
            ),
            # DR-13: exactamente una de dos cosas, la imagen o la marca con su motivo.
            models.CheckConstraint(
                check=(
                    models.Q(sin_respaldo_fotografico=False, imagen_ticket__isnull=False)
                    & ~models.Q(imagen_ticket="")
                    & models.Q(motivo_sin_respaldo="")
                )
                | (
                    models.Q(sin_respaldo_fotografico=True)
                    & ~models.Q(motivo_sin_respaldo="")
                    & (models.Q(imagen_ticket__isnull=True) | models.Q(imagen_ticket=""))
                ),
                name="ck_ingreso_respaldo",
            ),
            # D-07: la anulación lleva su motivo.
            models.CheckConstraint(
                check=~models.Q(estado="ANULADO")
                | (models.Q(motivo_anulacion__isnull=False) & ~models.Q(motivo_anulacion="")),
                name="ck_ingreso_anulacion_motivo",
            ),
        ]

    def __str__(self):
        return self.codigo

    @property
    def tipo_vehiculo(self) -> str:
        """Derivado de la titularidad del catálogo, no editable (RS-M03-06)."""
        return self.vehiculo.tipo_titularidad
