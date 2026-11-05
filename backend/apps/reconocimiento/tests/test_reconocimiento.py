"""M04: la interfaz, el fallo del motor, la persistencia separada de lo leído y
lo confirmado, y la consulta comparativa (HU-M04-01, HU-M04-02)."""

import time
from datetime import datetime
from decimal import Decimal

import pytest

from apps.reconocimiento import services
from apps.reconocimiento.dominio import FECHA, ILEGIBLE, NO_DISPONIBLE, PESO_BRUTO, PLACA
from apps.reconocimiento.models import CampoReconocido, ReconocimientoTicket
from apps.reconocimiento.motores.determinista import ReconocedorDeterminista
from apps.reconocimiento.motores.tesseract import ReconocedorTesseract

pytestmark = pytest.mark.django_db

INGRESOS = "/api/v1/ingresos/"
RECONOCIMIENTOS = "/api/v1/reconocimientos/"


def registrar(api, imagen, ayer, mineral, **cambios):
    token = api.post(INGRESOS + "borradores/", {"imagen": imagen}, format="multipart").data["borrador"]
    datos = {"borrador": token, "placa": "V2K-841", "fecha": ayer.isoformat(), "hora": "08:15",
             "peso_bruto_tn": "29.80", "tipo_mineral": mineral.pk, **cambios}
    r = api.post(INGRESOS, datos, format="json")
    assert r.status_code == 201, r.data
    return r.data


def test_hu_m04_01_ca01_tres_campos_con_su_confianza(api_como, supervisor, lectura, vehiculo, imagen_png):
    rec = api_como(supervisor).post(INGRESOS + "borradores/", {"imagen": imagen_png}, format="multipart").data
    campos = {c["nombre"]: c for c in rec["reconocimiento"]["campos"]}
    assert set(campos) == {PLACA, FECHA, PESO_BRUTO}
    assert all(0 <= c["confianza"] <= 1 for c in campos.values())


def test_hu_m04_01_ca02_baja_confianza_se_senala(api_como, supervisor, lectura, vehiculo, imagen_png):
    rec = api_como(supervisor).post(INGRESOS + "borradores/", {"imagen": imagen_png}, format="multipart").data
    peso = next(c for c in rec["reconocimiento"]["campos"] if c["nombre"] == PESO_BRUTO)
    assert peso["dudoso"] is True and peso["aviso"] == "Verifique este dato: lectura con baja confianza"


def test_hu_m04_01_ca03_campo_sin_lectura_queda_vacio(api_como, supervisor, lectura, vehiculo, imagen_png):
    lectura.campos[PESO_BRUTO] = (None, None)
    rec = api_como(supervisor).post(INGRESOS + "borradores/", {"imagen": imagen_png}, format="multipart").data
    peso = next(c for c in rec["reconocimiento"]["campos"] if c["nombre"] == PESO_BRUTO)
    assert (peso["valor"], peso["confianza"]) == (None, None)
    assert rec["propuesta"]["peso_bruto_tn"] is None


def test_hu_m04_01_ca04_ticket_ilegible_permite_continuar(api_como, supervisor, lectura, imagen_png):
    lectura.exito, lectura.causa = False, ILEGIBLE
    r = api_como(supervisor).post(INGRESOS + "borradores/", {"imagen": imagen_png}, format="multipart")
    assert r.status_code == 200 and r.data["borrador"]
    assert r.data["reconocimiento"]["aviso"] == (
        "No fue posible leer el ticket. Tome una nueva fotografía o ingrese los datos manualmente")


def test_hu_m04_01_ca05_motor_que_falla_o_no_responde(settings):
    mensaje = "El reconocimiento no está disponible. Puede ingresar los datos manualmente"
    caido = services.reconocer(ReconocedorDeterminista(error=ConnectionError("sin red")), b"img")
    assert (caido.exito, caido.causa) == (False, NO_DISPONIBLE)
    assert services.presentar(caido)["aviso"] == mensaje

    class Lento(ReconocedorDeterminista):
        def reconocer(self, imagen):
            time.sleep(2)
            return super().reconocer(imagen)

    settings.RECONOCIMIENTO_TIEMPO_ESPERA_S = 0.2
    assert services.reconocer(Lento(), b"img").causa == NO_DISPONIBLE
    assert services.reconocer(None, b"img").causa == NO_DISPONIBLE


def test_rn_m04_07_el_fallo_del_motor_no_impide_registrar(api_como, supervisor, lectura, vehiculo, ayer, mineral,
                                                          imagen_png):
    lectura.error = TimeoutError()
    ingreso = registrar(api_como(supervisor), imagen_png, ayer, mineral)
    rec = ReconocimientoTicket.objects.get(ingreso_id=ingreso["id"])
    assert (rec.exito, rec.causa_fallo) == (False, NO_DISPONIBLE)
    assert not rec.campos.exclude(valor_reconocido__isnull=True).exists()


def test_hu_m04_01_ca07_leido_confirmado_confianza_motor_y_version(api_como, supervisor, lectura,
                                                                              vehiculo, ayer, mineral, imagen_png):
    ingreso = registrar(api_como(supervisor), imagen_png, ayer, mineral, peso_bruto_tn="29.70")
    rec = ReconocimientoTicket.objects.get(ingreso_id=ingreso["id"])
    assert (rec.motor, rec.version_motor, rec.umbral_confianza) == ("determinista", "1.0", Decimal("0.80"))
    peso = rec.campos.get(nombre_campo=PESO_BRUTO)
    assert (peso.valor_reconocido, peso.valor_confirmado, peso.confianza) == ("29.80", "29.70", Decimal("0.620"))


def test_hu_m04_01_ca08_sin_foto_no_se_invoca_el_reconocimiento(api_como, supervisor, lectura, vehiculo, ayer,
                                                                  mineral):
    api = api_como(supervisor)
    token = api.post(INGRESOS + "borradores/", {"sin_foto": True, "motivo_sin_respaldo": "OTRO"},
                     format="multipart").data["borrador"]
    r = api.post(INGRESOS, {"borrador": token, "placa": "V2K-841", "fecha": ayer.isoformat(), "hora": "08:00",
                            "peso_bruto_tn": "29.80", "tipo_mineral": mineral.pk}, format="json")
    assert lectura.invocaciones == 0 and not ReconocimientoTicket.objects.filter(ingreso_id=r.data["id"]).exists()


def test_rn_m04_01_el_resultado_es_una_propuesta(api_como, supervisor, lectura, imagen_png):
    api_como(supervisor).post(INGRESOS + "borradores/", {"imagen": imagen_png}, format="multipart")
    assert not ReconocimientoTicket.objects.exists()


def test_rn_m04_03_sin_lectura_el_campo_queda_vacio(api_como, supervisor, lectura, vehiculo, ayer,
                                                                   mineral, imagen_png):
    lectura.campos[FECHA] = (None, None)
    ingreso = registrar(api_como(supervisor), imagen_png, ayer, mineral)
    fecha = CampoReconocido.objects.get(reconocimiento__ingreso_id=ingreso["id"], nombre_campo=FECHA)
    assert fecha.valor_reconocido is None and fecha.confianza is None and fecha.valor_confirmado


def test_rn_m04_04_el_motor_y_su_version_vienen_del_adaptador_configurado(settings):
    from apps.reconocimiento import motores

    settings.RECONOCEDOR_ACTIVO = "determinista"
    r = services.reconocer(motores.obtener_reconocedor(), b"img")
    assert (r.motor, r.version_motor) == ("determinista", "1.0")


def test_rn_m04_08_el_servicio_de_registro_no_importa_ningun_motor():
    from pathlib import Path

    fuente = (Path(__file__).resolve().parents[2] / "ingresos" / "services" / "registro.py").read_text()
    assert "motores" not in fuente and "tesseract" not in fuente.lower()


def test_rn_m04_09_un_reconocimiento_por_ingreso():
    assert ReconocimientoTicket._meta.get_field("ingreso").one_to_one


def test_rn_m04_10_corregido_se_deriva_y_no_se_acepta_del_cliente(api_como, supervisor, lectura, vehiculo, ayer,
                                                                  mineral, imagen_png):
    ingreso = registrar(api_como(supervisor), imagen_png, ayer, mineral, fue_corregido=False,
                        peso_bruto_tn="29.70")
    peso = CampoReconocido.objects.get(reconocimiento__ingreso_id=ingreso["id"], nombre_campo=PESO_BRUTO)
    assert peso.fue_corregido is True
    assert "fue_corregido" not in [f.name for f in CampoReconocido._meta.get_fields()]


# HU-M04-02 — Consulta


@pytest.fixture
def reconocido(api_como, supervisor, lectura, vehiculo, ayer, mineral, imagen_png):
    ingreso = registrar(api_como(supervisor), imagen_png, ayer, mineral, placa="V2K-841", peso_bruto_tn="29.70")
    return ReconocimientoTicket.objects.get(ingreso_id=ingreso["id"])


def test_hu_m04_02_ca01_comparacion_campo_a_campo(api_como, administrativo, reconocido):
    d = api_como(administrativo).get(f"{RECONOCIMIENTOS}{reconocido.pk}/").data
    campos = {c["nombre_campo"]: c for c in d["campos"]}
    assert campos[PESO_BRUTO]["fue_corregido"] is True and campos[PLACA]["fue_corregido"] is False
    assert {"valor_reconocido", "valor_confirmado", "confianza"} <= set(campos[PLACA])


def test_hu_m04_02_ca02_el_campo_corregido_se_senala(api_como, administrativo, reconocido):
    campos = api_como(administrativo).get(f"{RECONOCIMIENTOS}{reconocido.pk}/").data["campos"]
    assert [c["nombre_campo"] for c in campos if c["fue_corregido"]] == [PESO_BRUTO]


def test_rn_m04_02_lo_leido_y_lo_confirmado_son_columnas_distintas():
    nombres = {f.name for f in CampoReconocido._meta.get_fields()}
    assert {"valor_reconocido", "valor_confirmado"} <= nombres


def test_rn_m04_05_el_motor_no_se_elige_por_ingreso_sino_por_configuracion(api_como, supervisor, lectura,
                                                                           vehiculo, ayer, mineral, nueva_imagen):
    api = api_como(supervisor)
    registrar(api, nueva_imagen(), ayer, mineral, hora="07:00")
    registrar(api, nueva_imagen(), ayer, mineral, hora="07:30", peso_bruto_tn="28.00")
    assert set(ReconocimientoTicket.objects.values_list("motor", "version_motor")) == {("determinista", "1.0")}


def test_rn_m04_06_la_confianza_esta_entre_cero_y_uno_y_no_se_inventa():
    from django.db import IntegrityError

    rec = ReconocimientoTicket.objects.create(
        ingreso=__import__("apps.ingresos.tests.factories", fromlist=["IngresoFactory"]).IngresoFactory(),
        motor="m", version_motor="1", fecha_proceso=datetime.now().astimezone(), umbral_confianza=Decimal("0.80"))
    with pytest.raises(IntegrityError):
        CampoReconocido.objects.create(reconocimiento=rec, nombre_campo=PLACA, valor_reconocido=None,
                                       valor_confirmado="ABC-123", confianza=Decimal("0"))


def test_rn_m04_11_el_sin_foto_no_hereda_lecturas_de_otro_ingreso(api_como, supervisor, lectura, vehiculo, ayer,
                                                                  mineral, imagen_png):
    api = api_como(supervisor)
    registrar(api, imagen_png, ayer, mineral)
    token = api.post(INGRESOS + "borradores/", {"sin_foto": True, "motivo_sin_respaldo": "OTRO"},
                     format="multipart").data["borrador"]
    r = api.post(INGRESOS, {"borrador": token, "placa": "V2K-841", "fecha": ayer.isoformat(), "hora": "09:00",
                            "peso_bruto_tn": "28.00", "tipo_mineral": mineral.pk}, format="json")
    assert r.status_code == 201
    assert ReconocimientoTicket.objects.count() == 1 and r.data["reconocimiento"]["id"] is None


def test_hu_m04_02_ca03_sin_reconocimiento_se_indica_el_motivo(api_como, supervisor, lectura, vehiculo, ayer,
                                                               mineral, imagen_png):
    lectura.exito, lectura.causa = False, ILEGIBLE
    api = api_como(supervisor)
    ingreso = registrar(api, imagen_png, ayer, mineral)
    d = api.get(f"{INGRESOS}{ingreso['id']}/").data["reconocimiento"]
    assert d["hubo_reconocimiento"] is False and d["motivo"].startswith("No fue posible leer el ticket")


def test_hu_m04_02_ca04_el_supervisor_consulta_en_solo_lectura(api_como, supervisor, reconocido):
    api = api_como(supervisor)
    d = api.get(f"{RECONOCIMIENTOS}{reconocido.pk}/").data
    assert d["puede_corregir_ingreso"] is False
    assert api.patch(f"{RECONOCIMIENTOS}{reconocido.pk}/", {}, format="json").status_code == 405


def test_hu_m04_02_ca05_motor_y_version(api_como, administrador, reconocido):
    d = api_como(administrador).get(f"{RECONOCIMIENTOS}{reconocido.pk}/").data
    assert (d["motor"], d["version_motor"]) == ("determinista", "1.0")


def test_hu_m04_02_ca06_sin_sesion_401(reconocido):
    from rest_framework.test import APIClient

    r = APIClient().get(f"{RECONOCIMIENTOS}{reconocido.pk}/")
    assert r.status_code == 401 and "campos" not in r.data


def test_listado_filtra_los_corregidos(api_como, administrativo, reconocido):
    api = api_como(administrativo)
    assert api.get(RECONOCIMIENTOS + "?corregidos=1").data["count"] == 1
    assert api.get(RECONOCIMIENTOS + "?corregidos=0").data["count"] == 0
    assert api.get(RECONOCIMIENTOS + "?motor=otro").data["count"] == 0


# Adaptador local: el análisis del texto, sin el binario de Tesseract.


def _datos_ocr(lineas):
    d = {k: [] for k in ("text", "conf", "block_num", "par_num", "line_num")}
    for n, (texto, conf) in enumerate(lineas):
        for palabra in texto.split():
            d["text"].append(palabra)
            d["conf"].append(conf)
            d["block_num"].append(1)
            d["par_num"].append(1)
            d["line_num"].append(n)
    return d


def test_el_adaptador_local_interpreta_el_ticket_de_la_balanza_dr_09():
    """El ticket trae `Peso:` sin unidad, `Placa:` y la fecha en tres casillas bajo
    `DIA MES AÑO`, con el año en dos dígitos (DR-09)."""
    adaptador = ReconocedorTesseract.__new__(ReconocedorTesseract)
    lineas = adaptador._lineas(_datos_ocr([("BALANZA", 90), ("Peso: 13.400 Placa: A5S-939", 70),
                                           ("DIA MES AÑO", 95), ("15 07 26", 85)]))
    assert adaptador._placa(lineas).valor == "A5S-939"
    assert adaptador._fecha(lineas).valor == "2026-07-15"
    peso = adaptador._peso(lineas)
    assert (peso.valor, peso.confianza) == ("13.40", 0.7)
    assert adaptador._placa(adaptador._lineas(_datos_ocr([("NADA", 50)]))).valor is None


def test_el_adaptador_local_toma_el_peso_bruto_de_una_linea_con_calculo_de_tara():
    adaptador = ReconocedorTesseract.__new__(ReconocedorTesseract)
    lineas = adaptador._lineas(_datos_ocr([("Peso: 16.650 - 55.080", 80), ("Placa: Viscacho", 80)]))
    assert adaptador._peso(lineas).valor == "55.08"
    assert adaptador._placa(lineas).valor is None  # un apodo no es placa (RN-M04-03)


def test_fecha_proceso_se_guarda(reconocido):
    assert isinstance(reconocido.fecha_proceso, datetime)
