"""M04: catálogo de motores por configuración, motor creado una vez, respaldo
entre motores, motor fijo en la ventana controlada (RN-M04-05) y reglas comunes
de normalización del ticket de la Balanza (DR-09). Ninguna prueba carga un
modelo real (RNF-M04-06)."""

import time
from decimal import Decimal

import pytest

from apps.reconocimiento import checks, motores
from apps.reconocimiento.dominio import FECHA, ILEGIBLE, NO_DISPONIBLE, PESO_BRUTO, PLACA
from apps.reconocimiento.motores.comun import normalizacion as N
from apps.reconocimiento.motores.compuesto import ReconocedorConRespaldo
from apps.reconocimiento.motores.determinista import ReconocedorDeterminista
from apps.reconocimiento.motores.trocr_local import version_desde


@pytest.fixture(autouse=True)
def _sin_instancias(monkeypatch):
    monkeypatch.setattr(motores, "_instancias", {})


# Catálogo y creación


def test_el_motor_se_crea_una_sola_vez_por_proceso(settings):
    settings.RECONOCEDOR_ACTIVO = "determinista"
    assert motores.obtener_reconocedor() is motores.obtener_reconocedor()


def test_agregar_un_motor_es_sumarlo_al_catalogo_sin_tocar_el_codigo(settings):
    settings.RECONOCEDORES = {**settings.RECONOCEDORES,
                              "otro": "apps.reconocimiento.motores.determinista.ReconocedorDeterminista"}
    settings.RECONOCEDOR_ACTIVO = "otro"
    assert isinstance(motores.obtener_reconocedor(), ReconocedorDeterminista)


def test_un_motor_que_no_carga_deja_el_registro_manual_y_se_reintenta(settings):
    settings.RECONOCEDORES = {**settings.RECONOCEDORES, "roto": "apps.no.existe.Motor"}
    settings.RECONOCEDOR_ACTIVO = "roto"
    assert motores.obtener_reconocedor() is None
    assert motores._instancias == {}  # el fallo no se guarda


def test_varios_motores_forman_un_respaldo_y_el_que_no_carga_queda_fuera(settings):
    settings.RECONOCEDORES = {**settings.RECONOCEDORES, "roto": "apps.no.existe.Motor"}
    settings.RECONOCEDOR_ACTIVO = "roto,determinista"
    r = motores.obtener_reconocedor()
    assert isinstance(r, ReconocedorConRespaldo)
    assert [n for n, _ in r.miembros] == ["determinista"]


# Respaldo


def _lectura():
    return {PLACA: ("A5S-939", 0.9), FECHA: ("2026-07-15", 0.9), PESO_BRUTO: ("13.40", 0.9)}


def test_si_el_primero_no_esta_disponible_lee_el_siguiente():
    caido = ReconocedorDeterminista(exito=False, causa=NO_DISPONIBLE)
    caido.motor = "nube"
    r = ReconocedorConRespaldo([("nube", caido), ("local", ReconocedorDeterminista(_lectura()))]).reconocer(b"img")
    assert r.exito and r.motor == "determinista"  # el resultado lleva el motor que leyó (RN-M04-04)


def test_si_el_primero_falla_o_no_responde_a_tiempo_lee_el_siguiente(settings):
    settings.RECONOCIMIENTO_TIEMPO_POR_MOTOR = {"lento": 0.05}

    class Lento:
        motor, version_motor = "lento", "1"

        def reconocer(self, imagen):
            time.sleep(1)

    local = ReconocedorDeterminista(_lectura())
    assert ReconocedorConRespaldo([("lento", Lento()), ("local", local)]).reconocer(b"img").exito
    error = ReconocedorDeterminista(error=ConnectionError("sin red"))
    assert ReconocedorConRespaldo([("nube", error), ("local", local)]).reconocer(b"img").exito


def test_un_ticket_ilegible_no_pasa_al_siguiente_motor():
    ilegible = ReconocedorDeterminista(exito=False, causa=ILEGIBLE)
    local = ReconocedorDeterminista(_lectura())
    r = ReconocedorConRespaldo([("nube", ilegible), ("local", local)]).reconocer(b"img")
    assert r.causa == ILEGIBLE and local.invocaciones == 0


def test_si_ninguno_esta_disponible_el_resultado_es_no_disponible():
    caido = ReconocedorDeterminista(exito=False, causa=NO_DISPONIBLE)
    r = ReconocedorConRespaldo([("a", caido), ("b", caido)]).reconocer(b"img")
    assert (r.exito, r.causa, r.motor) == (False, NO_DISPONIBLE, "respaldo:a+b")


# RN-M04-05: un solo motor en la ventana de operación controlada


def test_rn_m04_05_la_ventana_controlada_rechaza_un_respaldo(settings):
    settings.RECONOCIMIENTO_VENTANA_CONTROLADA = True
    settings.RECONOCEDOR_ACTIVO = "trocr,tesseract"
    assert [e.id for e in checks.motor_fijo_en_ventana_controlada()] == ["reconocimiento.E001"]
    settings.RECONOCEDOR_ACTIVO = "trocr"
    assert checks.motor_fijo_en_ventana_controlada() == []


def test_un_motor_fuera_del_catalogo_se_informa_al_arrancar(settings):
    settings.RECONOCEDOR_ACTIVO = "inexistente"
    assert [e.id for e in checks.motor_fijo_en_ventana_controlada()] == ["reconocimiento.E002"]


# Versión del modelo local


def test_la_version_del_modelo_cabe_en_version_motor_y_conserva_el_hash():
    from apps.reconocimiento.models import ReconocimientoTicket

    v = version_desde("trocr-ticket-v1+sha256:35598224867a\n")
    assert v == "v1-35598224867a"
    assert len(v) <= ReconocimientoTicket._meta.get_field("version_motor").max_length
    with pytest.raises(ValueError):
        version_desde("sin formato")


# Reglas comunes del ticket de la Balanza (DR-09)


@pytest.mark.parametrize("escrito, toneladas", [
    ("13.400", "13.40"), ("13.4", "13.40"), ("13,4", "13.40"), ("13. 400", "13.40"),
    ("20410", "20.41"), ("15 720", "15.72"),
    ("16.650 - 55.080", "55.08"), ("17.010 - 56.660", "56.66"), ("16.690+58.370", "58.37"),
])
def test_el_peso_se_propone_en_toneladas_con_dos_decimales(escrito, toneladas):
    assert N.peso_bruto(escrito) == Decimal(toneladas)


def test_un_peso_sin_numero_valido_queda_sin_lectura():
    assert N.peso_bruto("") is None and N.peso_bruto("134") is None


@pytest.mark.parametrize("escrito, placa", [
    ("TAJ 869", "TAJ-869"), ("F3P-878 Azul", "F3P-878"), ("CAB 891 AZUL", "CAB-891"), ("A5S-93O", "A5S-930"),
    ("Viscacho", None), ("Edison", None), ("Neron Jhon", None), ("", None),
])
def test_la_placa_cumple_el_formato_y_un_nombre_no_es_placa(escrito, placa):
    assert N.placa(escrito) == placa


@pytest.mark.parametrize("dia, mes, anio, fecha", [
    ("4", "8", "25", "2025-08-04"), ("31", "07", "26.", "2026-07-31"), ("15", "07", "2026", "2026-07-15"),
    ("31", "02", "26", None), ("17", "0", "25", None), ("", "08", "26", None), ("16", "08", "", None),
])
def test_la_fecha_se_arma_con_las_tres_casillas(dia, mes, anio, fecha):
    assert N.fecha(dia, mes, anio) == fecha


def test_el_piloto_cuenta_como_acierto_no_leer_un_campo_sin_valor_verdadero():
    from apps.reconocimiento.piloto import _coincide

    assert _coincide(PLACA, None, "") and not _coincide(PLACA, "D8Q-030", "")
    assert not _coincide(PLACA, None, "TAJ-869")
