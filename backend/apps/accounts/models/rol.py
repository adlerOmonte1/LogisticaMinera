from django.db import models


class Rol(models.Model):
    """Entidad ROL, con FK desde USUARIO (backend-auth-permisos, "Los tres roles").

    Son exactamente tres. No se modela como campo de texto libre ni como
    grupos de Django sin respaldo en el modelo ER: las historias de usuario
    de M01 y el resto de módulos están escritas sobre estos tres nombres.
    """

    ADMINISTRADOR = "ADMINISTRADOR"
    ADMINISTRATIVO = "ADMINISTRATIVO"
    SUPERVISOR = "SUPERVISOR"

    OPCIONES = [
        (ADMINISTRADOR, "Administrador"),
        (ADMINISTRATIVO, "Administrativo"),
        (SUPERVISOR, "Supervisor"),
    ]

    nombre = models.CharField(max_length=20, unique=True, choices=OPCIONES)

    class Meta:
        db_table = "rol"
        verbose_name = "Rol"
        verbose_name_plural = "Roles"
        ordering = ["nombre"]

    def __str__(self):
        return self.get_nombre_display()
