"""Casos de prueba de HU-M01-03 (gestión de usuarios) y HU-M01-05 (cambio
de contraseña propia)."""

import pytest

from apps.accounts.models import Usuario

from .factories import UsuarioFactory

pytestmark = pytest.mark.django_db
USUARIOS = "/api/v1/usuarios/"
CAMBIAR_CLAVE = "/api/v1/usuarios/cambiar-clave/"


def _payload_nuevo(**cambios):
    base = {
        "username": "jperez",
        "nombres": "Juan",
        "apellidos": "Pérez",
        "password": "clave-segura-12",
        "rol": "SUPERVISOR",
    }
    base.update(cambios)
    return base


def test_ca01_administrador_crea_usuario_en_estado_activo(api_como, administrador):
    respuesta = api_como(administrador).post(USUARIOS, _payload_nuevo())

    assert respuesta.status_code == 201
    creado = Usuario.objects.get(username="jperez")
    assert creado.is_active is True
    assert creado.rol.nombre == "SUPERVISOR"
    assert creado.check_password("clave-segura-12")


def test_ca02_nombre_de_usuario_duplicado_es_rechazado(api_como, administrador):
    UsuarioFactory(username="jperez")

    respuesta = api_como(administrador).post(USUARIOS, _payload_nuevo())

    assert respuesta.status_code == 400
    assert respuesta.data["mensaje"] == "El nombre de usuario ya está registrado"


def test_ca03_desactivar_no_elimina_el_registro(api_como, administrador):
    objetivo = UsuarioFactory()

    respuesta = api_como(administrador).patch(f"{USUARIOS}{objetivo.pk}/desactivar/")

    assert respuesta.status_code == 200
    objetivo.refresh_from_db()
    assert objetivo.is_active is False
    assert Usuario.objects.filter(pk=objetivo.pk).exists()


def test_no_existe_endpoint_delete_de_usuarios(api_como, administrador):
    objetivo = UsuarioFactory()

    respuesta = api_como(administrador).delete(f"{USUARIOS}{objetivo.pk}/")

    assert respuesta.status_code == 405


def test_hu04_editar_datos_de_usuario(api_como, administrador):
    objetivo = UsuarioFactory(nombres="Ana", apellidos="Lopez")

    respuesta = api_como(administrador).patch(
        f"{USUARIOS}{objetivo.pk}/", {"nombres": "Ana María", "apellidos": "López"}
    )

    assert respuesta.status_code == 200
    objetivo.refresh_from_db()
    assert objetivo.nombres == "Ana María"
    assert objetivo.apellidos == "López"


def test_hu04_ca03_cambio_de_rol_queda_persistido(api_como, administrador):
    objetivo = UsuarioFactory()  # SUPERVISOR por defecto

    respuesta = api_como(administrador).patch(
        f"{USUARIOS}{objetivo.pk}/", {"rol": "ADMINISTRATIVO"}
    )

    assert respuesta.status_code == 200
    objetivo.refresh_from_db()
    assert objetivo.rol.nombre == "ADMINISTRATIVO"


def test_hu04_editar_a_un_username_ya_usado_es_rechazado(api_como, administrador):
    UsuarioFactory(username="ocupado")
    objetivo = UsuarioFactory(username="libre")

    respuesta = api_como(administrador).patch(
        f"{USUARIOS}{objetivo.pk}/", {"username": "ocupado"}
    )

    assert respuesta.status_code == 400
    assert respuesta.data["mensaje"] == "El nombre de usuario ya está registrado"


def test_detalle_de_usuario_no_admite_put(api_como, administrador):
    objetivo = UsuarioFactory()

    respuesta = api_como(administrador).put(f"{USUARIOS}{objetivo.pk}/", _payload_nuevo())

    assert respuesta.status_code == 405


def test_hu05_ca01_cambio_de_password_con_datos_validos(api_como, supervisor, password):
    cliente = api_como(supervisor)

    respuesta = cliente.post(
        CAMBIAR_CLAVE,
        {
            "password_actual": password,
            "password_nueva": "nueva-clave-99",
            "password_nueva_confirmacion": "nueva-clave-99",
        },
    )

    assert respuesta.status_code == 204
    supervisor.refresh_from_db()
    assert supervisor.check_password("nueva-clave-99")


def test_hu05_ca02_password_actual_incorrecta(api_como, supervisor):
    respuesta = api_como(supervisor).post(
        CAMBIAR_CLAVE,
        {
            "password_actual": "no-es-la-actual",
            "password_nueva": "nueva-clave-99",
            "password_nueva_confirmacion": "nueva-clave-99",
        },
    )

    assert respuesta.status_code == 400
    assert respuesta.data["mensaje"] == "La contraseña actual no es correcta"


def test_hu05_ca03_password_nueva_demasiado_corta(api_como, supervisor, password):
    respuesta = api_como(supervisor).post(
        CAMBIAR_CLAVE,
        {
            "password_actual": password,
            "password_nueva": "corta",
            "password_nueva_confirmacion": "corta",
        },
    )

    assert respuesta.status_code == 400
    assert respuesta.data["mensaje"] == "La contraseña debe tener al menos ocho caracteres"
