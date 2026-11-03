"""Revisión de F4 (paso 4.3): cada operación de escritura de F1 a F3 deja su
evento, con el usuario, los valores y el motivo cuando corresponde (HU-M09-01).

Es la defensa que piden las notas de M09 contra el riesgo principal del módulo:
una ruta de escritura que funciona pero no deja rastro. Cada caso ejecuta una
operación por la API y exige exactamente los eventos nuevos esperados."""

from decimal import Decimal

import pytest

from apps.accounts.tests.factories import UsuarioFactory
from apps.auditoria.models import EventoAuditoria
from apps.catalogo.tests.factories import TipoMineralFactory, TransportistaFactory, VehiculoFactory

pytestmark = pytest.mark.django_db
INGRESOS = "/api/v1/ingresos/"


def nuevos(antes: int):
    return list(EventoAuditoria.objects.filter(pk__gt=antes).order_by("id"))


def ultimo_id() -> int:
    return EventoAuditoria.objects.order_by("-id").values_list("id", flat=True).first() or 0


def test_hu_m09_01_ca01_cada_alta_edicion_y_baja_del_catalogo_deja_su_evento(api_como, administrador):
    api = api_como(administrador)
    t = TransportistaFactory()
    v = VehiculoFactory(placa="AUD-001")
    m = TipoMineralFactory(codigo="AUD")
    operaciones = [
        (lambda: api.post("/api/v1/catalogo/vehiculos/", {"placa": "AUD-002", "tipo_titularidad": "PROPIO",
                                                          "capacidad_tn": "18"}, format="json"), "CREAR", "Vehiculo"),
        (lambda: api.patch(f"/api/v1/catalogo/vehiculos/{v.pk}/", {"capacidad_tn": "21.00"}, format="json"),
         "MODIFICAR", "Vehiculo"),
        (lambda: api.patch(f"/api/v1/catalogo/vehiculos/{v.pk}/desactivar/"), "MODIFICAR", "Vehiculo"),
        (lambda: api.patch(f"/api/v1/catalogo/vehiculos/{v.pk}/reactivar/"), "MODIFICAR", "Vehiculo"),
        (lambda: api.patch(f"/api/v1/catalogo/transportistas/{t.pk}/", {"razon_social": "Otra"}, format="json"),
         "MODIFICAR", "Transportista"),
        (lambda: api.patch(f"/api/v1/catalogo/tipos-mineral/{m.pk}/", {"nombre": "Renombrado"}, format="json"),
         "MODIFICAR", "TipoMineral"),
    ]
    for operar, accion, entidad in operaciones:
        antes = ultimo_id()
        assert operar().status_code in (200, 201)
        [evento] = nuevos(antes)
        assert (evento.accion, evento.entidad, evento.usuario) == (accion, entidad, administrador)


def test_hu_m09_01_ca02_la_edicion_guarda_solo_lo_que_cambio_con_ambos_valores(api_como, administrador):
    v = VehiculoFactory(placa="AUD-003", capacidad_tn=Decimal("18.00"))
    antes = ultimo_id()
    api_como(administrador).patch(f"/api/v1/catalogo/vehiculos/{v.pk}/", {"capacidad_tn": "21.00"}, format="json")
    [evento] = nuevos(antes)
    assert evento.valores_anteriores == {"capacidad_tn": "18.00"}
    assert evento.valores_nuevos == {"capacidad_tn": "21.00"}


def test_hu_m09_01_ca03_una_operacion_que_falla_no_deja_evento(api_como, administrativo):
    antes = ultimo_id()
    r = api_como(administrativo).post("/api/v1/catalogo/vehiculos/",
                                      {"placa": "1234", "tipo_titularidad": "PROPIO", "capacidad_tn": "18"},
                                      format="json")
    assert r.status_code == 400 and nuevos(antes) == []


def test_hu_m09_01_ca04_el_acceso_rechazado_queda_con_usuario_y_operacion(api_como, supervisor):
    antes = ultimo_id()
    api_como(supervisor).get("/api/v1/auditoria/")
    [evento] = nuevos(antes)
    assert (evento.accion, evento.usuario) == ("ACCESO_RECHAZADO", supervisor)
    assert evento.valores_nuevos["ruta"] == "/api/v1/auditoria/" and evento.valores_nuevos["metodo"] == "GET"


def test_hu_m09_01_ca05_reconocimiento_y_dato_propuesto_corregido(api_como, supervisor, ayer, mineral, lectura,
                                                                  vehiculo, imagen_png):
    api = api_como(supervisor)
    antes = ultimo_id()
    token = api.post(INGRESOS + "borradores/", {"imagen": imagen_png}, format="multipart").data["borrador"]
    api.post(INGRESOS, {"borrador": token, "placa": "V2K-841", "fecha": ayer.isoformat(), "hora": "08:15",
                        "peso_bruto_tn": "29.70", "tipo_mineral": mineral.pk}, format="json")
    acciones = [e.accion for e in nuevos(antes)]
    assert acciones == ["RECONOCER", "CORREGIR_DATO", "CREAR"]
    corregido = EventoAuditoria.objects.get(pk__gt=antes, accion="CORREGIR_DATO")
    assert (corregido.valores_anteriores, corregido.valores_nuevos) == ({"PESO_BRUTO": "29.80"},
                                                                        {"PESO_BRUTO": "29.70"})


def test_hu_m09_01_ca07_el_motivo_queda_junto_a_los_valores(api_como, administrador):
    v = VehiculoFactory(placa="AUD-004", tara_tn=Decimal("12.00"))
    antes = ultimo_id()
    api_como(administrador).patch(f"/api/v1/catalogo/vehiculos/{v.pk}/tara/",
                                  {"tara_tn": "12.40", "motivo": "Cambio de tolva"}, format="json")
    [evento] = nuevos(antes)
    assert (evento.valores_anteriores, evento.valores_nuevos, evento.motivo) == (
        {"tara_tn": "12.00"}, {"tara_tn": "12.40"}, "Cambio de tolva")


def test_el_registro_sin_foto_se_audita_con_su_motivo(api_como, supervisor, ayer, mineral, vehiculo):
    api = api_como(supervisor)
    token = api.post(INGRESOS + "borradores/", {"sin_foto": True, "motivo_sin_respaldo": "TICKET_EXTRAVIADO"},
                     format="multipart").data["borrador"]
    antes = ultimo_id()
    api.post(INGRESOS, {"borrador": token, "placa": "V2K-841", "fecha": ayer.isoformat(), "hora": "08:15",
                        "peso_bruto_tn": "29.80", "tipo_mineral": mineral.pk}, format="json")
    [evento] = nuevos(antes)
    assert evento.accion == "CREAR" and evento.motivo == "Ticket extraviado o dañado"


def test_rn_m09_01_el_evento_y_la_operacion_ocurren_juntos(api_como, administrador, monkeypatch):
    from apps.auditoria.services import auditoria

    def falla(*args, **kwargs):
        raise RuntimeError("la base rechaza el evento")

    monkeypatch.setattr(auditoria.EventoAuditoria.objects, "create", falla)
    v = VehiculoFactory(placa="AUD-005", capacidad_tn=Decimal("18.00"))
    with pytest.raises(RuntimeError):
        api_como(administrador).patch(f"/api/v1/catalogo/vehiculos/{v.pk}/", {"capacidad_tn": "25.00"},
                                      format="json")
    v.refresh_from_db()
    assert v.capacidad_tn == Decimal("18.00")


def test_rn_m09_03_la_modificacion_guarda_anterior_y_nuevo(api_como, administrador):
    u = UsuarioFactory(nombres="Antes")
    antes = ultimo_id()
    api_como(administrador).patch(f"/api/v1/usuarios/{u.pk}/", {"nombres": "Despues"}, format="json")
    [evento] = nuevos(antes)
    assert (evento.valores_anteriores, evento.valores_nuevos) == ({"nombres": "Antes"}, {"nombres": "Despues"})


def test_rn_m09_04_el_rechazo_se_registra_igual_que_lo_completado(api_como, supervisor, administrativo):
    for usuario, ruta in ((supervisor, "/api/v1/usuarios/"), (administrativo, "/api/v1/auditoria/")):
        antes = ultimo_id()
        api_como(usuario).get(ruta)
        assert [e.accion for e in nuevos(antes)] == ["ACCESO_RECHAZADO"]


def test_rn_m09_05_un_solo_catalogo_de_acciones():
    from common.eventos import Accion

    acciones = {codigo for codigo, _ in Accion.OPCIONES}
    assert set(EventoAuditoria.objects.values_list("accion", flat=True)) <= acciones
    assert EventoAuditoria._meta.get_field("accion").choices == Accion.OPCIONES


def test_rn_m09_06_el_autor_es_quien_opera_no_el_que_indica_el_cliente(api_como, administrador, supervisor):
    v = VehiculoFactory(placa="AUD-006")
    antes = ultimo_id()
    api_como(administrador).patch(f"/api/v1/catalogo/vehiculos/{v.pk}/",
                                  {"capacidad_tn": "22.00", "usuario": supervisor.pk}, format="json")
    [evento] = nuevos(antes)
    assert evento.usuario == administrador


def test_rs_m09_16_ningun_evento_de_f1_a_f3_contiene_una_contrasena(api_como, administrador):
    api = api_como(administrador)
    api.post("/api/v1/usuarios/", {"username": "con.clave", "nombres": "C", "apellidos": "C",
                                   "password": "Clave-Prueba-1", "rol": "SUPERVISOR"}, format="json")
    u = UsuarioFactory()
    temporal = api.post(f"/api/v1/usuarios/{u.pk}/restablecer-clave/").data["clave_temporal"]
    textos = [str(e.valores_anteriores) + str(e.valores_nuevos) + e.motivo for e in EventoAuditoria.objects.all()]
    assert not any("Clave-Prueba-1" in t or temporal in t for t in textos)
    assert not any(k in t.lower() for t in textos for k in ("'password'", "'clave'"))
