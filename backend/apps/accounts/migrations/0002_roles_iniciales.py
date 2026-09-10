"""Siembra los tres roles del sistema (RN-M01-02, backend-auth-permisos).

Son un catálogo cerrado: Administrador, Administrativo y Supervisor. No se
crean desde la aplicación —los serializers solo los leen—, por eso viven en
una migración de datos y no en un `get_or_create` disperso por el código.
"""

from django.db import migrations

ROLES = ["ADMINISTRADOR", "ADMINISTRATIVO", "SUPERVISOR"]


def crear_roles(apps, schema_editor):
    Rol = apps.get_model("accounts", "Rol")
    for nombre in ROLES:
        Rol.objects.get_or_create(nombre=nombre)


def borrar_roles(apps, schema_editor):
    Rol = apps.get_model("accounts", "Rol")
    Rol.objects.filter(nombre__in=ROLES).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(crear_roles, borrar_roles),
    ]
