from django.db import models

from apps.accounts.models import Usuario
from apps.catalogo.models import Producto, Vehiculo


class Ingreso(models.Model):
    """Unidad de registro del sistema (RS-M03-01 a RS-M03-10).

    `hora_pesaje` la ingresa el usuario desde el ticket; `hora_registro` la
    asigna el servicio, nunca `auto_now_add` (D-01, D-03): para un ingreso
    capturado sin conexión el valor correcto es la hora de captura local, no
    la de inserción en la base. `correlativo` lo asigna
    `services/correlativo.py` dentro de una transacción con bloqueo (D-02).

    Los índices de `idx_ingreso_correlativo` e `idx_ingreso_vehiculo` del
    modelo ER ya quedan cubiertos por `unique=True` en `correlativo` y por el
    índice implícito de la FK `vehiculo`; no se duplican aquí.
    """

    REGISTRADO = "REGISTRADO"
    ANULADO = "ANULADO"
    ESTADOS = [(REGISTRADO, "Registrado"), (ANULADO, "Anulado")]

    correlativo = models.CharField(
        max_length=20, unique=True, editable=False, verbose_name="Correlativo"
    )
    uuid_local = models.UUIDField(
        null=True, blank=True, unique=True, verbose_name="Identificador local"
    )
    fecha_pesaje = models.DateField(verbose_name="Fecha de pesaje")
    hora_pesaje = models.TimeField(verbose_name="Hora de pesaje")
    hora_registro = models.DateTimeField(editable=False, verbose_name="Hora de registro")
    hora_sincronizacion = models.DateTimeField(
        null=True, blank=True, verbose_name="Hora de sincronización"
    )
    vehiculo = models.ForeignKey(
        Vehiculo, on_delete=models.PROTECT, related_name="ingresos", verbose_name="Vehículo"
    )
    producto = models.ForeignKey(
        Producto, on_delete=models.PROTECT, related_name="ingresos", verbose_name="Producto"
    )
    peso_bruto_tn = models.DecimalField(
        max_digits=8, decimal_places=2, verbose_name="Peso bruto (tn)"
    )
    tara_tn = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Tara (tn)")
    peso_neto_tn = models.DecimalField(
        max_digits=8, decimal_places=2, editable=False, verbose_name="Peso neto (tn)"
    )
    numero_ticket = models.CharField(max_length=20, verbose_name="Número de ticket")
    usuario_registro = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        editable=False,
        related_name="ingresos_registrados",
        verbose_name="Registrado por",
    )
    capturado_offline = models.BooleanField(default=False, verbose_name="Capturado sin conexión")
    estado = models.CharField(
        max_length=10, choices=ESTADOS, default=REGISTRADO, verbose_name="Estado"
    )
    motivo_anulacion = models.TextField(
        null=True, blank=True, verbose_name="Motivo de anulación"
    )

    class Meta:
        db_table = "ingreso"
        verbose_name = "Ingreso"
        verbose_name_plural = "Ingresos"
        ordering = ["-fecha_pesaje", "-hora_pesaje"]
        indexes = [
            # I5, I6: consolidados y búsqueda por fecha y producto.
            models.Index(fields=["fecha_pesaje", "producto"], name="idx_ingreso_fecha_producto"),
        ]
        constraints = [
            # RN-M03-05: el ticket es único solo entre los ingresos no anulados.
            models.UniqueConstraint(
                fields=["numero_ticket"],
                condition=models.Q(estado="REGISTRADO"),
                name="uq_ingreso_ticket_no_anulado",
            ),
            # RN-M03-03, salvaguarda de dominio además del mensaje de servicio.
            models.CheckConstraint(
                check=models.Q(tara_tn__lt=models.F("peso_bruto_tn")),
                name="ck_ingreso_tara_menor_bruto",
            ),
            models.CheckConstraint(
                check=models.Q(peso_bruto_tn__gt=0) & models.Q(tara_tn__gt=0),
                name="ck_ingreso_pesos_positivos",
            ),
        ]

    def __str__(self):
        return f"{self.correlativo} — {self.numero_ticket}"
