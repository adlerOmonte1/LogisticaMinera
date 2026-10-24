"""Carga los datos de prueba del entorno local (PLAN-02 §4.6).

Crea las tres cuentas de prueba, una por rol, con las credenciales del entorno
local de Postman (`postman/entornos/local.postman_environment.json`). Si ya
existen, las devuelve a su estado inicial —activas, con su rol, su clave y sin
bloqueo—, porque la colección de Postman desactiva, bloquea y cambia claves de
otras cuentas, pero se ejecuta siempre desde estas tres.

Se niega a correr con `DEBUG` desactivado: sus claves están en el repositorio y
estas cuentas nunca deben existir en preproducción ni en producción.
"""

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.accounts.models import Rol, Usuario

# Credenciales solo para el entorno local; coinciden con el entorno de Postman.
CLAVE_PRUEBA = "Prueba-Local-2027"
USUARIOS_PRUEBA = [
    ("admin.prueba", "Administrador", "De prueba", Rol.ADMINISTRADOR),
    ("administrativo.prueba", "Administrativo", "De prueba", Rol.ADMINISTRATIVO),
    ("supervisor.prueba", "Supervisor", "De prueba", Rol.SUPERVISOR),
]


class Command(BaseCommand):
    help = "Crea o restablece los datos de prueba del entorno local (solo con DEBUG activo)."

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError(
                "Los datos de prueba solo se cargan con DEBUG activo: "
                "sus credenciales están en el repositorio."
            )
        with transaction.atomic():
            for username, nombres, apellidos, rol in USUARIOS_PRUEBA:
                usuario, creado = Usuario.objects.get_or_create(
                    username=username,
                    defaults={
                        "nombres": nombres,
                        "apellidos": apellidos,
                        "rol": Rol.objects.get(nombre=rol),
                    },
                )
                usuario.rol = Rol.objects.get(nombre=rol)
                usuario.is_active = True
                usuario.intentos_fallidos = 0
                usuario.bloqueado_hasta = None
                usuario.set_password(CLAVE_PRUEBA)
                usuario.save()
                self.stdout.write(f"{'Creado' if creado else 'Restablecido'}: {username} ({rol})")
