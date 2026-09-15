from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models

from .rol import Rol


class UsuarioManager(BaseUserManager):
    """`create_user`/`create_superuser` son obligatorios en un modelo de
    usuario personalizado (AbstractBaseUser no trae uno por defecto).

    La creación operativa de usuarios (HU-M01-03) no pasa por aquí: la hace
    `apps.accounts.services.usuarios.crear_usuario`, que además aplica las
    reglas de negocio (RN-M01-01, 02, 04). Este manager solo cubre lo mínimo
    que Django necesita para `createsuperuser` y para las fixtures de prueba.
    """

    use_in_migrations = True

    def _crear_usuario(self, username, password, **extra_campos):
        if not username:
            raise ValueError("El nombre de usuario es obligatorio")
        usuario = self.model(username=username, **extra_campos)
        usuario.set_password(password)
        usuario.save(using=self._db)
        return usuario

    def create_user(self, username, password=None, **extra_campos):
        extra_campos.setdefault("is_staff", False)
        extra_campos.setdefault("is_superuser", False)
        return self._crear_usuario(username, password, **extra_campos)

    def create_superuser(self, username, password=None, **extra_campos):
        extra_campos.setdefault("is_staff", True)
        extra_campos.setdefault("is_superuser", True)
        if extra_campos.get("rol_id") is None and extra_campos.get("rol") is None:
            rol_administrador, _ = Rol.objects.get_or_create(nombre=Rol.ADMINISTRADOR)
            extra_campos["rol"] = rol_administrador
        return self._crear_usuario(username, password, **extra_campos)


class Usuario(AbstractBaseUser, PermissionsMixin):
    """RS-M01-01, RS-M01-02, RS-M01-07. Invariantes de la entidad (RN-M01-*).

    `is_active` es el campo que usa el framework de autenticación de Django
    (`ModelBackend`, el panel de administración); es la misma noción que la
    documentación llama "activo" — no se duplica.
    """

    username = models.CharField(max_length=50, unique=True, verbose_name="Nombre de usuario")
    nombres = models.CharField(max_length=100, verbose_name="Nombres")
    apellidos = models.CharField(max_length=100, verbose_name="Apellidos")
    rol = models.ForeignKey(
        Rol,
        on_delete=models.PROTECT,  # RN-M01-02: todo usuario pertenece a exactamente un rol
        related_name="usuarios",
        verbose_name="Rol",
    )

    is_active = models.BooleanField(default=True, verbose_name="Activo")
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    # RN-M01-07: el contador se reinicia solo tras un acceso exitoso o
    # transcurrido el bloqueo. Ninguno de los dos campos es editable desde un
    # serializer: los asigna exclusivamente el servicio de autenticación.
    intentos_fallidos = models.PositiveSmallIntegerField(default=0, editable=False)
    bloqueado_hasta = models.DateTimeField(null=True, blank=True, editable=False)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["nombres", "apellidos"]

    objects = UsuarioManager()

    class Meta:
        db_table = "usuario"
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ["username"]

    def __str__(self):
        return f"{self.nombres} {self.apellidos} ({self.username})"

    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}".strip()

    def tiene_rol(self, *nombres_de_rol):
        return self.rol_id is not None and self.rol.nombre in nombres_de_rol
