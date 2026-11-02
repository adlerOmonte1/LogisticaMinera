"""HU-M01-02 — Gestión de usuarios. Una prueba por criterio de aceptación."""

import pytest

from apps.accounts.models import Usuario
from apps.auditoria.models import EventoAuditoria
from common.eventos import Accion

from .factories import UsuarioFactory

pytestmark = pytest.mark.django_db
USUARIOS = "/api/v1/usuarios/"
CAMBIAR = "/api/v1/usuarios/cambiar-clave/"


def _alta(**extra):
    datos = {"username": "nuevo", "nombres": "Ana", "apellidos": "Ruiz", "password": "clave-segura-1", "rol": "SUPERVISOR"}
    datos.update(extra)
    return datos


def test_hu_m01_02_ca01_el_administrador_crea_un_usuario_activo(api_como, administrador):
    r = api_como(administrador).post(USUARIOS, _alta())

    assert r.status_code == 201
    assert Usuario.objects.get(username="nuevo").is_active
    assert EventoAuditoria.objects.filter(accion=Accion.CREAR, entidad="Usuario").exists()


def test_hu_m01_02_ca02_nombre_de_usuario_duplicado(api_como, administrador):
    UsuarioFactory(username="nuevo")

    r = api_como(administrador).post(USUARIOS, _alta())

    assert r.status_code == 400
    assert r.data["mensaje"] == "El nombre de usuario ya está registrado"


def test_hu_m01_02_ca03_desactivar_es_baja_logica(api_como, administrador):
    u = UsuarioFactory()

    r = api_como(administrador).patch(f"{USUARIOS}{u.pk}/desactivar/")
    borrado = api_como(administrador).delete(f"{USUARIOS}{u.pk}/")

    assert r.status_code == 200
    assert r.data["mensaje"] == "Usuario desactivado"
    assert borrado.status_code == 405
    u.refresh_from_db()
    assert u.is_active is False


@pytest.mark.parametrize("rol", ["administrativo", "supervisor"])
def test_hu_m01_02_ca04_otro_rol_no_gestiona_usuarios(request, api_como, rol):
    r = api_como(request.getfixturevalue(rol)).get(USUARIOS)

    assert r.status_code == 403
    assert r.data["mensaje"] == "Acción no autorizada"


def test_hu_m01_02_ca05_cambio_de_la_propia_contrasena(api_como, supervisor, password):
    r = api_como(supervisor).post(
        CAMBIAR, {"password_actual": password, "password_nueva": "otra-clave-9", "password_nueva_confirmacion": "otra-clave-9"}
    )

    assert r.status_code == 200
    assert r.data["mensaje"] == "Contraseña cambiada. Inicie sesión nuevamente"
    supervisor.refresh_from_db()
    assert supervisor.check_password("otra-clave-9")


def test_hu_m01_02_ca06_contrasena_actual_incorrecta(api_como, supervisor):
    r = api_como(supervisor).post(
        CAMBIAR, {"password_actual": "mala", "password_nueva": "otra-clave-9", "password_nueva_confirmacion": "otra-clave-9"}
    )

    assert r.status_code == 400
    assert r.data["mensaje"] == "La contraseña actual no es correcta"


def test_hu_m01_02_ca07_contrasena_nueva_corta(api_como, supervisor, password):
    r = api_como(supervisor).post(
        CAMBIAR, {"password_actual": password, "password_nueva": "corta", "password_nueva_confirmacion": "corta"}
    )

    assert r.status_code == 400
    assert r.data["mensaje"] == "La contraseña debe tener al menos ocho caracteres"


def test_hu_m01_02_ca08_restablecer_genera_una_temporal_de_un_solo_uso(api_como, administrador):
    u = UsuarioFactory()

    r = api_como(administrador).post(f"{USUARIOS}{u.pk}/restablecer-clave/")

    assert r.status_code == 200
    temporal = r.data["clave_temporal"]
    assert len(temporal) >= 8
    u.refresh_from_db()
    assert u.debe_cambiar_clave and u.check_password(temporal)
    evento = EventoAuditoria.objects.get(entidad="Usuario", id_entidad=u.pk, accion=Accion.MODIFICAR)
    assert temporal not in str(evento.valores_nuevos) and temporal not in evento.motivo


def test_hu_m01_02_ca09_no_desactiva_su_propia_cuenta(api_como, administrador):
    r = api_como(administrador).patch(f"{USUARIOS}{administrador.pk}/desactivar/")

    assert r.status_code == 400
    assert r.data["mensaje"] == "No puede desactivar su propia cuenta"


def test_hu_m01_02_ca10_reactivar_conserva_el_rol(api_como, administrador):
    u = UsuarioFactory(is_active=False)

    listado = api_como(administrador).get(f"{USUARIOS}?incluir_inactivos=1")
    r = api_como(administrador).patch(f"{USUARIOS}{u.pk}/reactivar/")

    assert any(x["id"] == u.pk for x in listado.data["results"])
    assert r.status_code == 200
    assert r.data["mensaje"] == "Usuario reactivado"
    assert r.data["rol"] == u.rol.nombre
    u.refresh_from_db()
    assert u.is_active


def test_hu_m01_02_ca11_las_contrasenas_no_coinciden(api_como, supervisor, password):
    r = api_como(supervisor).post(
        CAMBIAR, {"password_actual": password, "password_nueva": "otra-clave-9", "password_nueva_confirmacion": "distinta-9"}
    )

    assert r.status_code == 400
    assert r.data["mensaje"] == "Las contraseñas no coinciden"


def test_rn_m01_01_nombre_de_usuario_unico(api_como, administrador):
    UsuarioFactory(username="repetido")
    u = UsuarioFactory()

    r = api_como(administrador).patch(f"{USUARIOS}{u.pk}/", {"username": "repetido"})

    assert r.status_code == 400


def test_rn_m01_03_ningun_usuario_se_elimina(api_como, administrador):
    u = UsuarioFactory()
    api_como(administrador).patch(f"{USUARIOS}{u.pk}/desactivar/")

    assert Usuario.objects.filter(pk=u.pk).exists()


def test_rn_m01_04_contrasena_minima_al_crear(api_como, administrador):
    r = api_como(administrador).post(USUARIOS, _alta(password="corta"))

    assert r.status_code == 400
    assert r.data["mensaje"] == "La contraseña debe tener al menos ocho caracteres"


def test_rn_m01_08_cambiar_la_propia_contrasena_exige_la_actual(api_como, supervisor):
    r = api_como(supervisor).post(
        CAMBIAR, {"password_actual": "", "password_nueva": "otra-clave-9", "password_nueva_confirmacion": "otra-clave-9"}
    )

    assert r.status_code == 400


def test_rn_m01_02_todo_usuario_tiene_un_rol(api_como, administrador):
    r = api_como(administrador).post(USUARIOS, _alta(rol="INEXISTENTE"))

    assert r.status_code == 400


def test_rn_m01_11_solo_el_administrador_restablece_y_la_temporal_se_cambia(api_como, administrativo, api):
    u = UsuarioFactory()

    rechazo = api_como(administrativo).post(f"{USUARIOS}{u.pk}/restablecer-clave/")

    assert rechazo.status_code == 403
    u.refresh_from_db()
    assert u.debe_cambiar_clave is False


def test_rn_m01_12_nadie_desactiva_su_propia_cuenta(administrador):
    from apps.accounts.services.usuarios import desactivar_usuario
    from common.excepciones import ErrorDeValidacionDeDominio

    with pytest.raises(ErrorDeValidacionDeDominio):
        desactivar_usuario(administrador, administrador)
    administrador.refresh_from_db()
    assert administrador.is_active
