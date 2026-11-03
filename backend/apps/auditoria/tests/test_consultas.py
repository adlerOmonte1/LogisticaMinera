"""Historial de un ingreso (HU-M09-02) y consulta de la auditoría (HU-M09-03)."""

import pytest
from rest_framework.test import APIClient

from apps.auditoria.models import EventoAuditoria
from apps.auditoria.services import servicio_auditoria
from common.eventos import Accion

pytestmark = pytest.mark.django_db

INGRESOS = "/api/v1/ingresos/"
AUDITORIA = "/api/v1/auditoria/"


@pytest.fixture
def ingreso(api_como, supervisor, administrativo, ayer, mineral, lectura, vehiculo, imagen_png):
    """Un ingreso registrado y corregido una vez, con su historial."""
    api = api_como(supervisor)
    token = api.post(INGRESOS + "borradores/", {"imagen": imagen_png}, format="multipart").data["borrador"]
    r = api.post(INGRESOS, {"borrador": token, "placa": "V2K-841", "fecha": ayer.isoformat(), "hora": "08:15",
                            "peso_bruto_tn": "29.80", "tipo_mineral": mineral.pk}, format="json")
    api_como(administrativo).patch(f"{INGRESOS}{r.data['id']}/",
                                   {"peso_bruto_tn": "29.00", "motivo": "Lectura equivocada"}, format="json")
    return r.data


def historial(api, ingreso):
    return api.get(f"{INGRESOS}{ingreso['id']}/historial/")


# HU-M09-02 — Historial de un ingreso


def test_hu_m09_02_ca01_cronologico_con_su_autor(api_como, supervisor, administrativo, ingreso):
    d = historial(api_como(supervisor), ingreso).data
    assert [e["accion"] for e in d["results"]] == ["RECONOCER", "CREAR", "MODIFICAR"]
    assert [e["usuario"] for e in d["results"]] == [supervisor.username, supervisor.username,
                                                     administrativo.username]
    fechas = [e["fecha_hora"] for e in d["results"]]
    assert fechas == sorted(fechas)


def test_hu_m09_02_ca02_modificacion_con_anterior_nuevo_y_motivo(api_como, supervisor, ingreso):
    correccion = historial(api_como(supervisor), ingreso).data["results"][-1]
    assert correccion["operacion"] == "CORRECCION" and correccion["motivo"] == "Lectura equivocada"
    assert {"campo": "peso_bruto_tn", "anterior": "29.80", "nuevo": "29.00"} in correccion["cambios"]
    assert all(c["campo"] != "operacion" for c in correccion["cambios"])


def test_hu_m09_02_ca03_incluye_los_eventos_de_su_lote(api_como, supervisor, administrativo, ingreso):
    # M06 se construye en F5; su evento se registra por el mismo servicio, con
    # los ingresos que afecta (RS-M09-13). Aquí se registra uno equivalente.
    servicio_auditoria.registrar(accion=Accion.MODIFICAR, entidad="Lote", id_entidad=12, usuario=administrativo,
                                 valores_nuevos={"etapa": "SECADO"}, ingresos_relacionados=[ingreso["id"]])
    servicio_auditoria.registrar(accion=Accion.MODIFICAR, entidad="Lote", id_entidad=13, usuario=administrativo,
                                 valores_nuevos={"etapa": "SECADO"}, ingresos_relacionados=[999999])
    eventos = historial(api_como(supervisor), ingreso).data["results"]
    lote = [e for e in eventos if e["entidad"] == "Lote"]
    assert len(lote) == 1 and lote[0]["id_entidad"] == 12


@pytest.mark.parametrize("rol", ["supervisor", "administrativo", "administrador"])
def test_hu_m09_02_ca04_el_historial_es_igual_para_los_tres_roles(api_como, request, rol, ingreso):
    d = historial(api_como(request.getfixturevalue(rol)), ingreso).data
    assert d["count"] == 3 and d["ingreso"] == ingreso["codigo"]


def test_hu_m09_02_ca05_sin_acceso_a_la_auditoria_si_no_es_administrador(api_como, supervisor, administrador,
                                                                        ingreso):
    assert historial(api_como(supervisor), ingreso).data["puede_ver_auditoria"] is False
    assert historial(api_como(administrador), ingreso).data["puede_ver_auditoria"] is True


def test_rn_m09_07_el_historial_excluye_usuarios_catalogos_y_accesos(api_como, supervisor, administrador, ingreso,
                                                                     vehiculo):
    api_como(supervisor).patch(f"{INGRESOS}{ingreso['id']}/anular/", {"motivo": "x"}, format="json")  # 403
    api_como(administrador).patch(f"/api/v1/catalogo/vehiculos/{vehiculo.pk}/", {"capacidad_tn": "19.00"},
                                  format="json")
    entidades = {e["entidad"] for e in historial(api_como(supervisor), ingreso).data["results"]}
    acciones = {e["accion"] for e in historial(api_como(supervisor), ingreso).data["results"]}
    assert entidades == {"Ingreso"} and "ACCESO_RECHAZADO" not in acciones


# HU-M09-03 — Consulta de la auditoría


def test_hu_m09_03_ca01_del_mas_reciente_con_entidad_referencia_y_autor(api_como, administrador, ingreso):
    d = api_como(administrador).get(AUDITORIA).data
    ids = [e["id"] for e in d["results"]]
    assert ids == sorted(ids, reverse=True)
    del_ingreso = next(e for e in d["results"] if e["entidad"] == "Ingreso")
    assert del_ingreso["referencia"] == ingreso["codigo"] and del_ingreso["usuario"]


def test_hu_m09_03_ca02_filtros_combinados(api_como, administrador, administrativo, ingreso):
    api = api_como(administrador)
    d = api.get(AUDITORIA, {"usuario": administrativo.username, "accion": "MODIFICAR",
                            "texto": ingreso["codigo"]}).data
    assert d["count"] == 1 and d["results"][0]["motivo"] == "Lectura equivocada"
    por_placa = api.get(AUDITORIA, {"texto": "V2K-841", "accion": "CREAR"}).data
    assert any(e["referencia"] == ingreso["codigo"] for e in por_placa["results"])


def test_hu_m09_03_ca03_modificacion_con_ambos_valores_y_motivo(api_como, administrador, ingreso):
    d = api_como(administrador).get(AUDITORIA, {"accion": "MODIFICAR", "texto": ingreso["codigo"]}).data
    evento = d["results"][0]
    assert {"campo": "peso_neto_tn", "anterior": "18.00", "nuevo": "17.20"} in evento["cambios"]
    assert evento["motivo"] == "Lectura equivocada"


def test_hu_m09_03_ca04_sin_resultados(api_como, administrador, ingreso):
    d = api_como(administrador).get(AUDITORIA, {"texto": "NO-EXISTE-123"}).data
    assert d["count"] == 0 and d["mensaje"] == "No hay eventos con estos filtros"


@pytest.mark.parametrize("rol", ["administrativo", "supervisor"])
def test_hu_m09_03_ca05_solo_el_administrador(api_como, request, rol):
    r = api_como(request.getfixturevalue(rol)).get(AUDITORIA)
    assert r.status_code == 403 and r.data["mensaje"] == "Acción no autorizada"


def test_rn_m09_08_la_auditoria_incluye_accesos_rechazados_y_usuarios(api_como, supervisor, administrador):
    api_como(supervisor).get(AUDITORIA)  # queda como acceso rechazado
    api_como(administrador).post("/api/v1/usuarios/", {"username": "nuevo.usuario", "nombres": "N",
                                                         "apellidos": "U", "password": "Clave-Prueba-1",
                                                         "rol": "SUPERVISOR"}, format="json")
    entidades = {(e["accion"], e["entidad"]) for e in api_como(administrador).get(AUDITORIA).data["results"]}
    assert ("ACCESO_RECHAZADO", "Autorizacion") in entidades and ("CREAR", "Usuario") in entidades


def test_rn_m09_02_ningun_endpoint_modifica_ni_elimina_eventos(api_como, administrador, ingreso):
    api = api_como(administrador)
    evento = EventoAuditoria.objects.order_by("id").first()
    for metodo in (api.post, api.put, api.patch, api.delete):
        assert metodo(AUDITORIA, {}, format="json").status_code == 405
    assert api.delete(f"{AUDITORIA}{evento.pk}/").status_code == 404
    assert EventoAuditoria.objects.filter(pk=evento.pk).exists()


def test_la_consulta_sin_sesion_responde_401():
    assert APIClient().get(AUDITORIA).status_code == 401
