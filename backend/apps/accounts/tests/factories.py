import factory

from apps.accounts.models import Rol, Usuario

PASSWORD_VALIDA = "clave-segura-12"


class RolFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Rol
        django_get_or_create = ("nombre",)

    nombre = Rol.SUPERVISOR


class UsuarioFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Usuario

    username = factory.Sequence(lambda n: f"usuario{n}")
    nombres = "Nombre"
    apellidos = "Apellido"
    rol = factory.SubFactory(RolFactory)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        password = kwargs.pop("password", PASSWORD_VALIDA)
        usuario = model_class(*args, **kwargs)
        usuario.set_password(password)
        usuario.save()
        return usuario
