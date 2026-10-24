"""Comando de datos de prueba del entorno local (PLAN-02 §4.6)."""

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import override_settings

from apps.accounts.management.commands.cargar_datos_prueba import CLAVE_PRUEBA, USUARIOS_PRUEBA
from apps.accounts.models import Usuario

pytestmark = pytest.mark.django_db


@override_settings(DEBUG=True)
def test_crea_una_cuenta_activa_por_rol():
    call_command("cargar_datos_prueba")

    for username, _, _, rol in USUARIOS_PRUEBA:
        usuario = Usuario.objects.get(username=username)
        assert usuario.rol.nombre == rol
        assert usuario.is_active
        assert usuario.check_password(CLAVE_PRUEBA)


@override_settings(DEBUG=True)
def test_es_idempotente_y_restablece_el_estado_inicial():
    call_command("cargar_datos_prueba")
    supervisor = Usuario.objects.get(username="supervisor.prueba")
    supervisor.is_active = False
    supervisor.intentos_fallidos = 5
    supervisor.set_password("otra-clave-cualquiera")
    supervisor.save()

    call_command("cargar_datos_prueba")

    supervisor.refresh_from_db()
    assert Usuario.objects.filter(username__endswith=".prueba").count() == 3
    assert supervisor.is_active and supervisor.intentos_fallidos == 0
    assert supervisor.check_password(CLAVE_PRUEBA)


@override_settings(DEBUG=False)
def test_se_niega_a_correr_sin_debug():
    with pytest.raises(CommandError):
        call_command("cargar_datos_prueba")
    assert not Usuario.objects.filter(username__endswith=".prueba").exists()
