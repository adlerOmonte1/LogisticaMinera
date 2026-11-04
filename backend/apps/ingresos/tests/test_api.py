"""Contrato HTTP de M03, un caso por criterio de HU-M03-01 a HU-M03-04. Las
reglas que se prueban mejor sobre el servicio están en `test_servicio.py`."""

from datetime import timedelta
from decimal import Decimal

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

from apps.auditoria.models import EventoAuditoria
from apps.ingresos.models import Ingreso
from apps.reconocimiento.models import ReconocimientoTicket
from apps.validacion.models import ResultadoValidacion

pytestmark = pytest.mark.django_db

INGRESOS = "/api/v1/ingresos/"
BORRADORES = INGRESOS + "borradores/"
DESTARES = INGRESOS + "destares/"
NO_AUTORIZADA = "Acción no autorizada"


def iniciar(api, imagen):
    r = api.post(BORRADORES, {"imagen": imagen}, format="multipart")
    assert r.status_code == 200, r.data
    return r


def confirmar(api, token, ayer, mineral, **cambios):
    datos = {
        "borrador": token,
        "placa": "V2K-841",
        "fecha": ayer.isoformat(),
        "hora": "08:15",
        "peso_bruto_tn": "29.80",
        "tipo_mineral": mineral.pk,
    }
    datos.update(cambios)
    return api.post(INGRESOS, {k: v for k, v in datos.items() if v is not None}, format="json")


@pytest.fixture
def registrar(api_como, ayer, mineral, lectura, vehiculo):
    """Registra un ingreso completo y devuelve su respuesta."""

    def _registrar(usuario, imagen, **cambios):
        api = api_como(usuario)
        token = iniciar(api, imagen).data["borrador"]
        return confirmar(api, token, ayer, mineral, **cambios)

    return _registrar


# HU-M03-01 — Registro de un ingreso a partir del ticket


def test_hu_m03_01_ca01_registro_con_tara_queda_registrado(registrar, supervisor, imagen_png):
    r = registrar(supervisor, imagen_png)
    assert r.status_code == 201, r.data
    assert r.data["mensaje"] == f"Ingreso registrado con el código {r.data['codigo']}"
    assert r.data["estado"] == "REGISTRADO" and r.data["codigo"].startswith("ING-")


def test_hu_m03_01_ca02_sin_imagen_ni_registro_sin_foto(api_como, supervisor, ayer, mineral, vehiculo):
    api = api_como(supervisor)
    sin_borrador = confirmar(api, "", ayer, mineral)
    assert sin_borrador.status_code == 400
    assert sin_borrador.data["mensaje"] == "Debe adjuntar la imagen del ticket de balanza"
    r = api.post(BORRADORES, {}, format="multipart")
    assert r.status_code == 400 and r.data["mensaje"] == "Debe adjuntar la imagen del ticket de balanza"
    alterado = confirmar(api, "borrador-inventado", ayer, mineral)
    assert alterado.data["mensaje"] == "Debe adjuntar la imagen del ticket de balanza"


def test_hu_m03_01_ca03_campos_obligatorios_con_los_que_faltan(api_como, supervisor, ayer, mineral, lectura,
                                                                imagen_png):
    api = api_como(supervisor)
    token = iniciar(api, imagen_png).data["borrador"]
    r = confirmar(api, token, ayer, mineral, placa="", hora=None, tipo_mineral=None)
    assert r.status_code == 400
    assert r.data["mensaje"] == "Debe completar los campos obligatorios"
    assert set(r.data["detalles"]["campos"]) == {"placa", "hora", "tipo_mineral"}
    sin_motivo = api.post(BORRADORES, {"sin_foto": True}, format="multipart")
    assert sin_motivo.status_code == 400 and sin_motivo.data["detalles"]["campos"] == ["motivo_sin_respaldo"]


def test_hu_m03_01_ca04_placa_no_registrada(api_como, supervisor, ayer, mineral, lectura, imagen_png):
    from apps.reconocimiento.dominio import PLACA

    lectura.campos[PLACA] = ("Z9Z-999", 0.9)
    api = api_como(supervisor)
    propuesta = iniciar(api, imagen_png).data
    aviso = "La placa Z9Z-999 no está registrada. Complete los datos del vehículo para continuar"
    assert propuesta["aviso_placa"] == aviso and propuesta["vehiculo"] is None
    r = confirmar(api, propuesta["borrador"], ayer, mineral, placa="Z9Z-999")
    assert r.status_code == 400 and r.data["mensaje"] == aviso
    # Alta en la misma pantalla con el servicio de M02 y el mismo borrador.
    alta = api.post("/api/v1/catalogo/vehiculos/",
                    {"placa": "Z9Z-999", "tipo_titularidad": "PROPIO", "capacidad_tn": "20.00"}, format="json")
    assert alta.status_code == 201
    r = confirmar(api, propuesta["borrador"], ayer, mineral, placa="Z9Z-999")
    assert r.status_code == 201 and r.data["estado"] == "EN_PROCESO"


def test_hu_m03_01_ca05_vehiculo_sin_tara_queda_en_proceso(api_como, supervisor, ayer, mineral, lectura,
                                                           vehiculo_sin_tara, imagen_png):
    api = api_como(supervisor)
    token = iniciar(api, imagen_png).data["borrador"]
    r = confirmar(api, token, ayer, mineral, placa="E4R-208", peso_bruto_tn="40.00")
    assert r.status_code == 201
    assert r.data["mensaje"] == (
        f"Ingreso {r.data['codigo']} registrado en proceso: pendiente del destare del vehículo E4R-208"
    )
    assert r.data["estado"] == "EN_PROCESO" and r.data["peso_neto_tn"] is None and r.data["tara_tn"] is None


def test_hu_m03_01_ca06_bloqueante_o_advertencia_sin_justificar(registrar, supervisor, imagen_png, imagen_jpg):
    r = registrar(supervisor, imagen_png, peso_bruto_tn="11.00")  # V2
    assert r.status_code == 400
    assert r.data["mensaje"] == "Debe corregir o justificar las inconsistencias señaladas"
    assert [i["regla"] for i in r.data["detalles"]["inconsistencias"]] == ["V2"]


def test_hu_m03_01_ca06_dos_advertencias_sin_justificar(registrar, supervisor, imagen_png, imagen_jpg):
    assert registrar(supervisor, imagen_png, peso_bruto_tn="40.00",
                     justificaciones={"V4": "Sobrecarga autorizada"}).status_code == 201
    r = registrar(supervisor, imagen_jpg, peso_bruto_tn="40.00")  # V1 y V4
    assert r.data["mensaje"] == "Debe corregir o justificar las inconsistencias señaladas"
    assert {f["regla"] for f in r.data["detalles"]["justificaciones_faltantes"]} == {"V1", "V4"}


def test_hu_m03_01_ca07_formato_o_tamano_no_admitido(api_como, supervisor, settings):
    api = api_como(supervisor)
    mensaje = "La imagen debe estar en formato JPG o PNG y no superar los 10 MB"
    pdf = SimpleUploadedFile("ticket.pdf", b"%PDF-1.4 documento", content_type="application/pdf")
    r = api.post(BORRADORES, {"imagen": pdf}, format="multipart")
    assert r.status_code == 400 and r.data["mensaje"] == mensaje
    grande = SimpleUploadedFile("ticket.jpg", b"\xff\xd8" + b"0" * (10 * 1024 * 1024), content_type="image/jpeg")
    r = api.post(BORRADORES, {"imagen": grande}, format="multipart")
    assert r.status_code == 400 and r.data["mensaje"] == mensaje


def test_hu_m03_01_ca08_neto_calculado_y_tara_conservada(registrar, supervisor, imagen_png):
    r = registrar(supervisor, imagen_png, peso_bruto_tn="29.80", peso_neto_tn="99.00", tara_tn="1.00")
    assert r.status_code == 201
    assert (r.data["tara_tn"], r.data["peso_neto_tn"]) == ("11.80", "18.00")


def test_hu_m03_01_ca09_tres_marcas_distintas_y_no_editables(registrar, administrativo, api_como, imagen_png):
    r = registrar(administrativo, imagen_png)
    marcas = [r.data["fecha_hora_pesaje"], r.data["hora_inicio_registro"], r.data["hora_fin_registro"]]
    assert len(set(marcas)) == 3
    api = api_como(administrativo)
    c = api.patch(f"{INGRESOS}{r.data['id']}/", {"motivo": "Prueba", "hora_inicio_registro": "2020-01-01T00:00:00Z",
                                                 "hora_fin_registro": "2020-01-01T00:00:00Z"}, format="json")
    assert c.status_code == 400 and c.data["mensaje"] == "No hay cambios que guardar"
    detalle = api.get(f"{INGRESOS}{r.data['id']}/").data
    assert [detalle["hora_inicio_registro"], detalle["hora_fin_registro"]] == marcas[1:]


def test_hu_m03_01_ca10_la_hora_del_pesaje_es_una_propuesta(api_como, supervisor, lectura, imagen_png):
    propuesta = iniciar(api_como(supervisor), imagen_png).data["propuesta"]
    assert propuesta["hora_es_propuesta"] is True
    ahora = timezone.localtime().strftime("%H:%M")
    hace_un_minuto = (timezone.localtime() - timedelta(minutes=1)).strftime("%H:%M")
    assert propuesta["hora"] in (ahora, hace_un_minuto)


def test_hu_m03_01_ca11_imagen_reconocido_confirmado_y_auditoria(registrar, supervisor, imagen_png):
    r = registrar(supervisor, imagen_png, peso_bruto_tn="29.70")
    ingreso = Ingreso.objects.get(pk=r.data["id"])
    assert ingreso.imagen_ticket.name.startswith("tickets/") and r.data["imagen_url"]
    campos = {c.nombre_campo: c for c in ingreso.reconocimiento.campos.all()}
    assert (campos["PESO_BRUTO"].valor_reconocido, campos["PESO_BRUTO"].valor_confirmado) == ("29.80", "29.70")
    acciones = set(EventoAuditoria.objects.filter(entidad="Ingreso", id_entidad=ingreso.pk)
                   .values_list("accion", flat=True))
    assert {"CREAR", "RECONOCER", "CORREGIR_DATO"} <= acciones


def test_hu_m03_01_ca13_vehiculo_dado_de_baja(registrar, supervisor, imagen_png, vehiculo):
    vehiculo.activo = False
    vehiculo.save()
    r = registrar(supervisor, imagen_png)
    assert r.status_code == 400
    assert r.data["mensaje"] == "El vehículo V2K-841 está dado de baja: no puede asociarse a un ingreso"


def test_hu_m03_01_ca14_alta_de_tipo_de_mineral_desde_el_registro(api_como, administrativo, ayer, lectura,
                                                                  vehiculo, imagen_png):
    api = api_como(administrativo)
    propuesta = iniciar(api, imagen_png).data
    assert propuesta["puede_agregar_tipo_mineral"] is True and propuesta["aviso_tipo_mineral"] is None
    nuevo = api.post("/api/v1/catalogo/tipos-mineral/", {"nombre": "Sulfuro fino", "desde_registro": True},
                     format="json")
    assert nuevo.status_code == 201
    r = api.post(INGRESOS, {"borrador": propuesta["borrador"], "placa": "V2K-841", "fecha": ayer.isoformat(),
                            "hora": "07:30", "peso_bruto_tn": "29.80", "tipo_mineral": nuevo.data["id"]},
                 format="json")
    assert r.status_code == 201 and r.data["tipo_mineral_nombre"] == "Sulfuro fino"


def test_hu_m03_01_ca15_el_supervisor_no_agrega_tipos_de_mineral(api_como, supervisor, lectura, imagen_png):
    api = api_como(supervisor)
    propuesta = iniciar(api, imagen_png).data
    assert propuesta["puede_agregar_tipo_mineral"] is False
    assert propuesta["aviso_tipo_mineral"] == "Si no está en la lista, pida a un administrativo que lo registre"
    r = api.post("/api/v1/catalogo/tipos-mineral/", {"nombre": "X", "desde_registro": True}, format="json")
    assert r.status_code == 403


def test_hu_m03_01_ca16_registro_sin_foto(api_como, supervisor, ayer, mineral, vehiculo, lectura):
    api = api_como(supervisor)
    propuesta = api.post(BORRADORES, {"sin_foto": True, "motivo_sin_respaldo": "TICKET_EXTRAVIADO"},
                         format="multipart").data
    assert propuesta["reconocimiento"] is None and propuesta["sin_respaldo_fotografico"] is True
    assert lectura.invocaciones == 0  # HU-M04-01 CA08
    r = confirmar(api, propuesta["borrador"], ayer, mineral)
    assert r.status_code == 201
    ingreso = Ingreso.objects.get(pk=r.data["id"])
    assert ingreso.sin_respaldo_fotografico and not ingreso.imagen_ticket
    assert not ReconocimientoTicket.objects.filter(ingreso=ingreso).exists()


def test_hu_m03_01_ca17_sin_foto_senalado_con_su_motivo(api_como, supervisor, ayer, mineral, vehiculo):
    api = api_como(supervisor)
    token = api.post(BORRADORES, {"sin_foto": True, "motivo_sin_respaldo": "BALANZA_SIN_TICKET"},
                     format="multipart").data["borrador"]
    r = confirmar(api, token, ayer, mineral)
    detalle = api.get(f"{INGRESOS}{r.data['id']}/").data
    assert detalle["sin_respaldo_fotografico"] is True and detalle["imagen_url"] is None
    assert detalle["motivo_sin_respaldo_texto"] == "La balanza no emitió ticket"
    assert detalle["reconocimiento"]["hubo_reconocimiento"] is False


def test_un_borrador_no_registra_dos_ingresos(api_como, supervisor, ayer, mineral, lectura, vehiculo, imagen_png):
    api = api_como(supervisor)
    token = iniciar(api, imagen_png).data["borrador"]
    primero = confirmar(api, token, ayer, mineral)
    segundo = confirmar(api, token, ayer, mineral, hora="09:00")
    assert segundo.status_code == 409
    assert segundo.data["mensaje"] == f"Este borrador ya se registró como el ingreso {primero.data['codigo']}"


def test_el_borrador_de_otro_usuario_no_sirve(api_como, supervisor, administrativo, ayer, mineral, lectura,
                                               vehiculo, imagen_png):
    token = iniciar(api_como(supervisor), imagen_png).data["borrador"]
    r = confirmar(api_como(administrativo), token, ayer, mineral)
    assert r.status_code == 400 and r.data["mensaje"] == "Debe adjuntar la imagen del ticket de balanza"


# HU-M03-02 — Corrección


@pytest.fixture
def ingreso(registrar, supervisor, imagen_png):
    return registrar(supervisor, imagen_png).data


def corregir(api, ingreso, **datos):
    return api.patch(f"{INGRESOS}{ingreso['id']}/", datos, format="json")


def test_hu_m03_02_ca01_correccion_recalcula_el_neto(api_como, administrativo, ingreso):
    r = corregir(api_como(administrativo), ingreso, peso_bruto_tn="29.00", motivo="Lectura equivocada")
    assert r.status_code == 200
    assert r.data["mensaje"] == f"Ingreso {ingreso['codigo']} actualizado"
    assert r.data["peso_neto_tn"] == "17.20"


def test_hu_m03_02_ca02_motivo_obligatorio(api_como, administrativo, ingreso):
    r = corregir(api_como(administrativo), ingreso, peso_bruto_tn="29.00")
    assert r.status_code == 400 and r.data["mensaje"] == "Debe indicar el motivo de la corrección"


def test_hu_m03_02_ca03_regla_incumplida_con_su_mensaje_literal(api_como, administrativo, ingreso):
    r = corregir(api_como(administrativo), ingreso, peso_bruto_tn="10.00", motivo="Error")
    assert r.status_code == 400 and r.data["mensaje"] == "La tara no puede ser mayor o igual que el peso bruto"
    futuro = (timezone.localdate() + timedelta(days=2)).isoformat()
    r = corregir(api_como(administrativo), ingreso, fecha=futuro, motivo="Error")
    assert r.data["mensaje"] == "La fecha del ticket no puede ser posterior a la fecha de registro"


def test_hu_m03_02_ca04_campos_del_servidor_se_ignoran(api_como, administrativo, ingreso):
    r = corregir(api_como(administrativo), ingreso, peso_bruto_tn="29.50", motivo="Ajuste", codigo="X",
                 tara_tn="1.00", peso_neto_tn="5.00", hora_fin_registro="2020-01-01T00:00:00Z")
    assert r.status_code == 200
    assert (r.data["codigo"], r.data["tara_tn"], r.data["peso_neto_tn"]) == (ingreso["codigo"], "11.80", "17.70")
    assert r.data["hora_fin_registro"] == ingreso["hora_fin_registro"]


def test_hu_m03_02_ca05_no_se_corrige_un_anulado(api_como, administrativo, administrador, ingreso):
    api_como(administrador).patch(f"{INGRESOS}{ingreso['id']}/anular/", {"motivo": "Duplicado"}, format="json")
    r = corregir(api_como(administrativo), ingreso, peso_bruto_tn="29.00", motivo="Error")
    assert r.status_code == 409 and r.data["mensaje"] == "No se puede corregir un ingreso anulado"


def test_hu_m03_02_ca06_el_supervisor_no_corrige(api_como, supervisor, ingreso):
    r = corregir(api_como(supervisor), ingreso, peso_bruto_tn="29.00", motivo="Error")
    assert r.status_code == 403 and r.data["mensaje"] == NO_AUTORIZADA


def test_hu_m03_02_ca07_auditoria_con_anterior_nuevo_y_motivo(api_como, administrativo, ingreso):
    corregir(api_como(administrativo), ingreso, peso_bruto_tn="29.00", motivo="Lectura equivocada")
    evento = EventoAuditoria.objects.filter(entidad="Ingreso", id_entidad=ingreso["id"], accion="MODIFICAR").order_by("id").last()
    assert evento.valores_anteriores == {"peso_bruto_tn": "29.80", "peso_neto_tn": "18.00"}
    assert evento.valores_nuevos == {"peso_bruto_tn": "29.00", "peso_neto_tn": "17.20", "operacion": "CORRECCION"}
    assert evento.motivo == "Lectura equivocada" and evento.usuario == administrativo


def test_hu_m03_02_ca08_placa_de_un_vehiculo_sin_tara_vuelve_a_en_proceso(api_como, administrativo, ingreso,
                                                                          vehiculo_sin_tara):
    r = corregir(api_como(administrativo), ingreso, placa="E4R-208", motivo="Placa mal leída")
    assert r.status_code == 200
    assert (r.data["estado"], r.data["tara_tn"], r.data["peso_neto_tn"]) == ("EN_PROCESO", None, None)


def test_hu_m03_02_ca10_sin_cambios(api_como, administrativo, ingreso):
    r = corregir(api_como(administrativo), ingreso, peso_bruto_tn="29.80", placa="V2K-841", motivo="Nada")
    assert r.status_code == 400 and r.data["mensaje"] == "No hay cambios que guardar"


def test_hu_m03_02_ca12_revertir_dos_veces_hacia_atras(api_como, administrativo, ingreso):
    api = api_como(administrativo)
    corregir(api, ingreso, peso_bruto_tn="29.00", motivo="Primera")
    corregir(api, ingreso, peso_bruto_tn="28.50", motivo="Segunda")
    url = f"{INGRESOS}{ingreso['id']}/revertir-correccion/"
    r = api.post(url, {"motivo": "La segunda fue un error"}, format="json")
    assert r.status_code == 200
    assert r.data["mensaje"] == f"Corrección revertida en el ingreso {ingreso['codigo']}"
    assert (r.data["peso_bruto_tn"], r.data["peso_neto_tn"]) == ("29.00", "17.20")
    r = api.post(url, {"motivo": "La primera también"}, format="json")
    assert r.data["peso_bruto_tn"] == "29.80" and r.data["correccion_revertible"] is None


def test_hu_m03_02_ca13_solo_la_ultima_correccion(api_como, administrativo, ingreso):
    api = api_como(administrativo)
    primera = corregir(api, ingreso, peso_bruto_tn="29.00", motivo="Primera").data["correccion_revertible"]
    corregir(api, ingreso, peso_bruto_tn="28.50", motivo="Segunda")
    r = api.post(f"{INGRESOS}{ingreso['id']}/revertir-correccion/", {"motivo": "x", "correccion": primera},
                 format="json")
    assert r.status_code == 409 and r.data["mensaje"] == "Solo puede revertirse la última corrección del ingreso"


def test_hu_m03_02_ca14_la_reversion_se_revalida(api_como, administrativo, registrar, supervisor, ingreso,
                                                imagen_jpg):
    api = api_como(administrativo)
    corregir(api, ingreso, peso_bruto_tn="29.00", motivo="Bruto mal leído")
    # Otro ingreso ocupa ahora la misma placa, fecha y peso que se restauraría.
    otro = registrar(supervisor, imagen_jpg)
    assert otro.status_code == 201
    api = api_como(administrativo)
    url = f"{INGRESOS}{ingreso['id']}/revertir-correccion/"
    r = api.post(url, {"motivo": "Volver al valor del ticket"}, format="json")
    assert r.status_code == 400 and r.data["mensaje"] == "Debe indicar la justificación del posible duplicado"
    r = api.post(url, {"motivo": "Volver", "justificaciones": {"V1": "Dos viajes"}}, format="json")
    assert r.status_code == 200 and r.data["peso_bruto_tn"] == "29.80"


# HU-M03-03 — Anulación


def anular(api, ingreso, motivo="Ingreso duplicado"):
    return api.patch(f"{INGRESOS}{ingreso['id']}/anular/", {"motivo": motivo}, format="json")


def test_hu_m03_03_ca01_anular_con_motivo(api_como, administrador, ingreso):
    r = anular(api_como(administrador), ingreso)
    assert r.status_code == 200 and r.data["mensaje"] == f"Ingreso {ingreso['codigo']} anulado"
    assert r.data["estado"] == "ANULADO"


def test_hu_m03_03_ca02_motivo_obligatorio(api_como, administrador, ingreso):
    r = anular(api_como(administrador), ingreso, motivo=" ")
    assert r.status_code == 400 and r.data["mensaje"] == "Debe indicar el motivo de la anulación"


def test_hu_m03_03_ca03_ya_anulado(api_como, administrador, ingreso):
    api = api_como(administrador)
    anular(api, ingreso)
    r = anular(api, ingreso)
    assert r.status_code == 409 and r.data["mensaje"] == f"El ingreso {ingreso['codigo']} ya fue anulado"


@pytest.mark.parametrize("rol", ["administrativo", "supervisor"])
def test_hu_m03_03_ca04_solo_el_administrador_anula(api_como, request, rol, ingreso):
    r = anular(api_como(request.getfixturevalue(rol)), ingreso)
    assert r.status_code == 403 and r.data["mensaje"] == NO_AUTORIZADA


def test_hu_m03_03_ca05_el_anulado_conserva_datos_imagen_motivo_y_responsable(api_como, administrador, ingreso):
    api = api_como(administrador)
    anular(api, ingreso)
    d = api.get(f"{INGRESOS}{ingreso['id']}/").data
    assert (d["estado"], d["motivo_anulacion"], d["anulado_por"]) == ("ANULADO", "Ingreso duplicado",
                                                                       administrador.username)
    assert d["peso_neto_tn"] == "18.00" and d["imagen_url"]
    imagen = api.get(d["imagen_url"])
    assert imagen.status_code == 200
    imagen.close()


def test_hu_m03_03_ca07_auditoria_de_la_anulacion(api_como, administrador, ingreso):
    anular(api_como(administrador), ingreso)
    evento = EventoAuditoria.objects.get(entidad="Ingreso", id_entidad=ingreso["id"], accion="ANULAR")
    assert evento.motivo == "Ingreso duplicado" and evento.usuario == administrador


# HU-M03-04 — Destare


@pytest.fixture
def en_proceso(api_como, supervisor, ayer, mineral, lectura, vehiculo_sin_tara, imagen_png, imagen_jpg):
    api = api_como(supervisor)
    creados = []
    for imagen, peso, hora in ((imagen_png, "29.00", "07:10"), (imagen_jpg, "28.00", "11:40")):
        token = iniciar(api, imagen).data["borrador"]
        creados.append(confirmar(api, token, ayer, mineral, placa="E4R-208", peso_bruto_tn=peso, hora=hora).data)
    return creados


def destarar(api, vehiculo, **datos):
    return api.post(DESTARES, {"vehiculo": vehiculo.pk, **datos}, format="json")


def test_hu_m03_04_ca01_destare_registrado_con_los_ingresos_completados(api_como, supervisor, en_proceso,
                                                                    vehiculo_sin_tara):
    r = destarar(api_como(supervisor), vehiculo_sin_tara, tara_tn="12.00")
    assert r.status_code == 201 and r.data["mensaje"] == "Destare registrado"
    assert [(i["codigo"], i["peso_neto_tn"], i["estado"]) for i in r.data["ingresos"]] == [
        (en_proceso[0]["codigo"], "17.00", "REGISTRADO"), (en_proceso[1]["codigo"], "16.00", "REGISTRADO")]
    vehiculo_sin_tara.refresh_from_db()
    assert vehiculo_sin_tara.tara_tn == Decimal("12.00") and vehiculo_sin_tara.usuario_destare == supervisor


def test_hu_m03_04_ca07_varios_en_proceso_se_completan_en_la_misma_operacion(api_como, supervisor, en_proceso,
                                                                           vehiculo_sin_tara):
    destarar(api_como(supervisor), vehiculo_sin_tara, tara_tn="12.00")
    assert not Ingreso.objects.filter(vehiculo=vehiculo_sin_tara, estado="EN_PROCESO").exists()
    assert Ingreso.objects.filter(vehiculo=vehiculo_sin_tara, estado="REGISTRADO").count() == 2


def test_hu_m03_04_ca02_tara_obligatoria(api_como, supervisor, en_proceso, vehiculo_sin_tara):
    r = destarar(api_como(supervisor), vehiculo_sin_tara)
    assert r.status_code == 400 and r.data["mensaje"] == "Debe indicar la tara del vehículo"


def test_hu_m03_04_ca03_tara_mayor_o_igual_que_un_bruto(api_como, supervisor, en_proceso, vehiculo_sin_tara):
    r = destarar(api_como(supervisor), vehiculo_sin_tara, tara_tn="28.00")
    assert r.status_code == 400 and r.data["mensaje"] == "La tara no puede ser mayor o igual que el peso bruto"


def test_hu_m03_04_ca04_neto_fuera_de_rango_sin_justificar(api_como, supervisor, en_proceso, vehiculo_sin_tara):
    api = api_como(supervisor)
    r = destarar(api, vehiculo_sin_tara, tara_tn="5.00")  # netos 24 y 23 sobre 17,5 t
    assert r.status_code == 400 and r.data["mensaje"] == "Debe indicar la justificación del peso fuera de rango"
    justificadas = {i["codigo"]: "Sobrecarga verificada" for i in en_proceso}
    assert destarar(api, vehiculo_sin_tara, tara_tn="5.00", justificaciones=justificadas).status_code == 201


def test_hu_m03_04_ca05_vehiculo_con_tara(api_como, supervisor, vehiculo):
    r = destarar(api_como(supervisor), vehiculo, tara_tn="12.00")
    assert r.status_code == 409 and r.data["mensaje"] == "El vehículo V2K-841 ya tiene tara registrada"


def test_hu_m03_04_ca06_lista_de_pendientes(api_como, supervisor, en_proceso):
    r = api_como(supervisor).get(INGRESOS + "?estado=EN_PROCESO")
    assert r.status_code == 200 and r.data["count"] == 2
    fila = r.data["results"][0]
    assert {"codigo", "placa", "fecha_hora_pesaje", "peso_bruto_tn"} <= set(fila)
    assert r.data["vehiculos"] == [{"id": en_proceso[0]["vehiculo"], "placa": "E4R-208", "ingresos": 2}]


def test_hu_m03_04_ca08_auditoria_del_destare(api_como, supervisor, en_proceso, vehiculo_sin_tara):
    destarar(api_como(supervisor), vehiculo_sin_tara, tara_tn="12.00")
    evento = EventoAuditoria.objects.filter(entidad="Vehiculo", id_entidad=vehiculo_sin_tara.pk).order_by("id").last()
    assert evento.valores_nuevos["tara_tn"] == "12.00" and evento.usuario == supervisor
    assert sorted(evento.ingresos_relacionados) == sorted(i["id"] for i in en_proceso)
    assert EventoAuditoria.objects.filter(entidad="Ingreso", valores_nuevos__operacion="DESTARE").count() == 2


def test_hu_m03_04_ca09_fecha_del_destare_futura(api_como, supervisor, en_proceso, vehiculo_sin_tara):
    futura = (timezone.now() + timedelta(hours=2)).isoformat()
    r = destarar(api_como(supervisor), vehiculo_sin_tara, tara_tn="12.00", fecha_destare=futura)
    assert r.status_code == 400
    assert r.data["mensaje"] == "La fecha del destare no puede ser posterior a la fecha actual"


def test_hu_m03_04_ca10_sin_pendientes(api_como, supervisor):
    r = api_como(supervisor).get(INGRESOS + "?estado=EN_PROCESO")
    assert r.data["count"] == 0 and r.data["mensaje"] == "No hay vehículos pendientes de destare"


# Transversales


def test_rn_m03_14_no_existe_borrado(api_como, administrador, ingreso):
    r = api_como(administrador).delete(f"{INGRESOS}{ingreso['id']}/")
    assert r.status_code == 405 and Ingreso.objects.filter(pk=ingreso["id"]).exists()


def test_la_imagen_no_se_entrega_sin_sesion(ingreso):
    from rest_framework.test import APIClient

    assert APIClient().get(f"{INGRESOS}{ingreso['id']}/imagen/").status_code == 401


def test_hu_m05_01_ca08_se_guarda_el_resultado_de_las_cinco_reglas(registrar, supervisor, imagen_png):
    r = registrar(supervisor, imagen_png, peso_bruto_tn="40.00", justificaciones={"V4": "Sobrecarga autorizada"})
    filas = ResultadoValidacion.objects.filter(ingreso_id=r.data["id"], momento="CONFIRMACION")
    assert sorted(f.regla for f in filas) == ["V1", "V2", "V3", "V4", "V5"]
    v4 = filas.get(regla="V4")
    assert (v4.cumple, v4.resolucion, v4.justificacion) == (False, "JUSTIFICADA", "Sobrecarga autorizada")


def test_hu_m05_01_ca03_la_justificacion_queda_junto_al_resultado(api_como, supervisor, registrar, imagen_png):
    r = registrar(supervisor, imagen_png, peso_bruto_tn="40.00", justificaciones={"V4": "Sobrecarga autorizada"})
    d = api_como(supervisor).get(f"{INGRESOS}{r.data['id']}/validaciones/").data
    assert any(f["regla"] == "V4" and f["justificacion"] == "Sobrecarga autorizada" for f in d)


def test_hu_m05_01_ca02_peso_fuera_de_rango_sin_justificar(registrar, supervisor, imagen_png):
    r = registrar(supervisor, imagen_png, peso_bruto_tn="40.00")
    assert r.status_code == 400
    assert r.data["mensaje"] == "Debe indicar la justificación del peso fuera de rango"


def test_hu_m05_01_ca10_posible_duplicado_sin_justificar(registrar, supervisor, nueva_imagen):
    registrar(supervisor, nueva_imagen())
    r = registrar(supervisor, nueva_imagen())
    assert r.status_code == 400 and r.data["mensaje"] == "Debe indicar la justificación del posible duplicado"
    justificado = registrar(supervisor, nueva_imagen(), justificaciones={"V1": "Segundo viaje del día"})
    assert justificado.status_code == 201


def test_hu_m05_01_ca07_peticion_directa_sin_formulario(api_como, supervisor, ayer, mineral, vehiculo):
    api = api_como(supervisor)
    token = api.post(BORRADORES, {"sin_foto": True, "motivo_sin_respaldo": "OTRO"}, format="multipart").data["borrador"]
    for cambios, regla in (({"peso_bruto_tn": "11.00"}, "V2"),
                           ({"fecha": (timezone.localdate() + timedelta(days=1)).isoformat()}, "V5")):
        r = confirmar(api, token, ayer, mineral, **cambios)
        assert r.status_code == 400 and r.data["detalles"]["inconsistencias"][0]["regla"] == regla


def test_hu_m05_01_ca12_sin_foto_se_valida_y_se_guarda_igual(api_como, supervisor, ayer, mineral, vehiculo):
    api = api_como(supervisor)
    token = api.post(BORRADORES, {"sin_foto": True, "motivo_sin_respaldo": "SIN_CAMARA"},
                     format="multipart").data["borrador"]
    r = confirmar(api, token, ayer, mineral)
    assert ResultadoValidacion.objects.filter(ingreso_id=r.data["id"]).count() == 5
    assert not ResultadoValidacion.objects.filter(ingreso_id=r.data["id"], momento="PROPUESTA").exists()


def test_rnf_m05_05_ninguna_regla_se_desactiva_desde_el_cliente(registrar, supervisor, imagen_png):
    r = registrar(supervisor, imagen_png, peso_bruto_tn="11.00", omitir=["V2"], reglas=[], validar=False)
    assert r.status_code == 400 and r.data["detalles"]["inconsistencias"][0]["regla"] == "V2"


def test_un_tipo_de_mineral_desactivado_no_es_elegible(registrar, supervisor, imagen_png, mineral):
    mineral.activo = False
    mineral.save()
    r = registrar(supervisor, imagen_png)
    assert r.status_code == 400 and r.data["detalles"]["campos"] == ["tipo_mineral"]


def test_alta_de_vehiculo_desde_el_registro_por_el_supervisor(api_como, supervisor):
    alta = api_como(supervisor).post("/api/v1/catalogo/vehiculos/",
                                     {"placa": "N3W-100", "tipo_titularidad": "PROPIO", "capacidad_tn": "18"},
                                     format="json")
    assert alta.status_code == 201 and alta.data["pendiente_destare"] is True
