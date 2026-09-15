from rest_framework import serializers

from apps.accounts.models import Rol, Usuario


class UsuarioListSerializer(serializers.ModelSerializer):
    rol = serializers.CharField(source="rol.nombre", read_only=True)

    class Meta:
        model = Usuario
        fields = ["id", "username", "nombres", "apellidos", "rol", "is_active"]


class UsuarioDetailSerializer(serializers.ModelSerializer):
    rol = serializers.CharField(source="rol.nombre", read_only=True)

    class Meta:
        model = Usuario
        fields = ["id", "username", "nombres", "apellidos", "rol", "is_active", "date_joined"]
        read_only_fields = ["id", "is_active", "date_joined"]


def _validar_rol(valor):
    """`valor` llega como el código del choice (p. ej. "SUPERVISOR"); se
    resuelve a la instancia `Rol` aquí para que `services.usuarios` reciba
    siempre el objeto, nunca la cadena (RN-M01-02).

    Los tres roles se siembran en la migración `0002_roles_iniciales`; este
    validador solo lee, nunca crea (solid-proyecto: un serializer no escribe).
    """
    try:
        return Rol.objects.get(nombre=valor)
    except Rol.DoesNotExist as exc:
        raise serializers.ValidationError("Rol no reconocido") from exc


class UsuarioCreateSerializer(serializers.Serializer):
    """HU-M01-03 CA01: nombres, apellidos, nombre de usuario, contraseña y rol."""

    username = serializers.CharField(max_length=50)
    nombres = serializers.CharField(max_length=100)
    apellidos = serializers.CharField(max_length=100)
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    rol = serializers.ChoiceField(choices=Rol.OPCIONES)

    def validate_rol(self, valor):
        return _validar_rol(valor)


class UsuarioUpdateSerializer(serializers.Serializer):
    """HU-M01-04. Todos los campos opcionales: es un `PATCH` parcial."""

    username = serializers.CharField(max_length=50, required=False)
    nombres = serializers.CharField(max_length=100, required=False)
    apellidos = serializers.CharField(max_length=100, required=False)
    rol = serializers.ChoiceField(choices=Rol.OPCIONES, required=False)

    def validate_rol(self, valor):
        return _validar_rol(valor)


class CambiarPasswordSerializer(serializers.Serializer):
    """HU-M01-05 CA01: nueva contraseña repetida dos veces."""

    password_actual = serializers.CharField(write_only=True, trim_whitespace=False)
    password_nueva = serializers.CharField(write_only=True, trim_whitespace=False)
    password_nueva_confirmacion = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, datos):
        if datos["password_nueva"] != datos["password_nueva_confirmacion"]:
            raise serializers.ValidationError(
                {"password_nueva_confirmacion": "Las contraseñas no coinciden"}
            )
        return datos
