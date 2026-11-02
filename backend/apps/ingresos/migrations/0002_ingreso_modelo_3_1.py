"""`Ingreso` según el modelo de datos 3.1.

Retira los campos del diseño anterior —número de ticket (DR-12), captura sin
conexión (DR-01) y la fecha y la hora del pesaje separadas— e incorpora las tres
marcas de tiempo de D-01, el tipo de mineral (DR-03), la tara y el peso neto
nulos mientras el ingreso está En proceso (D-17) y el registro sin foto (DR-13).

Las filas existentes, solo de desarrollo, conservan sus datos: la fecha y la hora
del pesaje se unen en `fecha_hora_pesaje`, y `hora_registro` pasa a ser el inicio
y el fin del registro, porque el diseño anterior no los distinguía.

**No es reversible**: los campos retirados no existen en la línea base 2.1 y no
hay de dónde reconstruirlos.
"""

import datetime

import django.db.models.deletion
from django.db import migrations, models
from django.utils import timezone


def unir_marcas_de_tiempo(apps, schema_editor):
    Ingreso = apps.get_model("ingresos", "Ingreso")
    for ingreso in Ingreso.objects.all():
        pesaje = datetime.datetime.combine(ingreso.fecha_pesaje, ingreso.hora_pesaje)
        ingreso.fecha_hora_pesaje = timezone.make_aware(pesaje)
        ingreso.hora_inicio_registro = ingreso.hora_registro
        ingreso.hora_fin_registro = ingreso.hora_registro
        ingreso.save(
            update_fields=["fecha_hora_pesaje", "hora_inicio_registro", "hora_fin_registro"]
        )


class Migration(migrations.Migration):

    dependencies = [
        ("catalogo", "0003_producto_a_tipo_mineral"),
        ("ingresos", "0001_initial"),
    ]

    operations = [
        migrations.RemoveConstraint(model_name="ingreso", name="uq_ingreso_ticket_no_anulado"),
        migrations.RemoveConstraint(model_name="ingreso", name="ck_ingreso_tara_menor_bruto"),
        migrations.RemoveConstraint(model_name="ingreso", name="ck_ingreso_pesos_positivos"),
        migrations.RemoveIndex(model_name="ingreso", name="idx_ingreso_fecha_producto"),
        migrations.RenameField(model_name="ingreso", old_name="correlativo", new_name="codigo"),
        migrations.RenameField(model_name="ingreso", old_name="producto", new_name="tipo_mineral"),
        migrations.AddField(
            model_name="ingreso",
            name="fecha_hora_pesaje",
            field=models.DateTimeField(null=True, verbose_name="Fecha y hora del pesaje"),
        ),
        migrations.AddField(
            model_name="ingreso",
            name="hora_inicio_registro",
            field=models.DateTimeField(null=True, editable=False, verbose_name="Inicio del registro"),
        ),
        migrations.AddField(
            model_name="ingreso",
            name="hora_fin_registro",
            field=models.DateTimeField(null=True, editable=False, verbose_name="Fin del registro"),
        ),
        migrations.RunPython(unir_marcas_de_tiempo),
        migrations.RemoveField(model_name="ingreso", name="fecha_pesaje"),
        migrations.RemoveField(model_name="ingreso", name="hora_pesaje"),
        migrations.RemoveField(model_name="ingreso", name="hora_registro"),
        migrations.RemoveField(model_name="ingreso", name="hora_sincronizacion"),
        migrations.RemoveField(model_name="ingreso", name="uuid_local"),
        migrations.RemoveField(model_name="ingreso", name="numero_ticket"),
        migrations.RemoveField(model_name="ingreso", name="capturado_offline"),
        migrations.AlterField(
            model_name="ingreso",
            name="fecha_hora_pesaje",
            field=models.DateTimeField(verbose_name="Fecha y hora del pesaje"),
        ),
        migrations.AlterField(
            model_name="ingreso",
            name="hora_inicio_registro",
            field=models.DateTimeField(editable=False, verbose_name="Inicio del registro"),
        ),
        migrations.AlterField(
            model_name="ingreso",
            name="hora_fin_registro",
            field=models.DateTimeField(editable=False, verbose_name="Fin del registro"),
        ),
        migrations.AddField(
            model_name="ingreso",
            name="imagen_ticket",
            field=models.ImageField(
                blank=True, null=True, upload_to="tickets/%Y/%m/", verbose_name="Imagen del ticket"
            ),
        ),
        migrations.AddField(
            model_name="ingreso",
            name="sin_respaldo_fotografico",
            field=models.BooleanField(
                default=False, editable=False, verbose_name="Sin respaldo fotográfico"
            ),
        ),
        migrations.AddField(
            model_name="ingreso",
            name="motivo_sin_respaldo",
            field=models.CharField(
                blank=True, editable=False, max_length=60, verbose_name="Motivo del registro sin foto"
            ),
        ),
        migrations.AlterField(
            model_name="ingreso",
            name="codigo",
            field=models.CharField(editable=False, max_length=20, unique=True, verbose_name="Código"),
        ),
        migrations.AlterField(
            model_name="ingreso",
            name="tipo_mineral",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="ingresos",
                to="catalogo.tipomineral",
                verbose_name="Tipo de mineral",
            ),
        ),
        migrations.AlterField(
            model_name="ingreso",
            name="tara_tn",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=8, null=True, verbose_name="Tara aplicada (tn)"
            ),
        ),
        migrations.AlterField(
            model_name="ingreso",
            name="peso_neto_tn",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                editable=False,
                max_digits=8,
                null=True,
                verbose_name="Peso neto (tn)",
            ),
        ),
        migrations.AlterField(
            model_name="ingreso",
            name="estado",
            field=models.CharField(
                choices=[
                    ("EN_PROCESO", "En proceso"),
                    ("REGISTRADO", "Registrado"),
                    ("ANULADO", "Anulado"),
                ],
                max_length=12,
                verbose_name="Estado",
            ),
        ),
        migrations.AlterModelOptions(
            name="ingreso",
            options={
                "ordering": ["-fecha_hora_pesaje"],
                "verbose_name": "Ingreso",
                "verbose_name_plural": "Ingresos",
            },
        ),
        migrations.AddIndex(
            model_name="ingreso",
            index=models.Index(fields=["vehiculo", "fecha_hora_pesaje"], name="idx_ingreso_vehiculo_fecha"),
        ),
        migrations.AddIndex(
            model_name="ingreso",
            index=models.Index(fields=["fecha_hora_pesaje", "tipo_mineral"], name="idx_ingreso_fecha_mineral"),
        ),
        migrations.AddIndex(
            model_name="ingreso",
            index=models.Index(fields=["estado"], name="idx_ingreso_estado"),
        ),
        migrations.AddConstraint(
            model_name="ingreso",
            constraint=models.CheckConstraint(
                check=models.Q(("peso_bruto_tn__gt", 0))
                & (models.Q(("tara_tn__isnull", True)) | models.Q(("tara_tn__gt", 0))),
                name="ck_ingreso_pesos_positivos",
            ),
        ),
        migrations.AddConstraint(
            model_name="ingreso",
            constraint=models.CheckConstraint(
                check=models.Q(("tara_tn__isnull", True))
                | models.Q(("tara_tn__lt", models.F("peso_bruto_tn"))),
                name="ck_ingreso_tara_menor_bruto",
            ),
        ),
    ]
