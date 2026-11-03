"""Carga del catálogo cerrado de etapas (RN-M06-09). No se administra: una etapa
nueva se decide expresamente y entra por otra migración."""

from django.db import migrations

from apps.trazabilidad.dominio import ETAPAS


def cargar(apps, schema_editor):
    EtapaProceso = apps.get_model("trazabilidad", "EtapaProceso")
    for codigo, nombre, orden in ETAPAS:
        EtapaProceso.objects.update_or_create(codigo=codigo, defaults={"nombre": nombre, "orden": orden})


class Migration(migrations.Migration):
    dependencies = [("trazabilidad", "0001_lote_proceso")]

    operations = [migrations.RunPython(cargar, migrations.RunPython.noop)]
