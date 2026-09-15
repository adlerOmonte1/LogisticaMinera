from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    """Solo valida presencia de los dos campos. La validez de las
    credenciales la decide `services.autenticacion.autenticar` — no aquí,
    porque RNF-M01-02 exige no revelar cuál de los dos campos falló, y un
    error de serializer por campo lo revelaría."""

    username = serializers.CharField()
    password = serializers.CharField(trim_whitespace=False, style={"input_type": "password"})


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
