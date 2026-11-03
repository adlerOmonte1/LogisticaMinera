"""Reglas V1 a V5 aisladas: sin base de datos ni petición HTTP (RNF-M05-07).
V1 recibe un doble de su repositorio."""

from datetime import datetime, timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from apps.validacion.reglas import DatosTicket, V1Duplicado, V2Tara, V3Placa, V4Capacidad, V5Fecha, reglas_vigentes
from apps.validacion.services import ValidadorConsistencia

AHORA = timezone.make_aware(datetime(2027, 3, 15, 10, 0))


class RepositorioFalso:
    def __init__(self, existentes=None):
        self.existentes = existentes or []  # [(placa, fecha, peso, codigo, id)]
        self.llamadas = []

    def buscar_por_placa_fecha_peso(self, placa, fecha, peso, *, excluir=None):
        self.llamadas.append((placa, fecha, peso, excluir))
        for p, f, w, codigo, ident in self.existentes:
            if (p, f, w) == (placa, fecha, peso) and ident != excluir:
                return codigo
        return None


def datos(**kw):
    base = dict(
        momento_registro=AHORA,
        placa="V2K-841",
        fecha_hora_pesaje=AHORA - timedelta(minutes=30),
        peso_bruto_tn=Decimal("29.80"),
        tara_tn=Decimal("11.80"),
        capacidad_tn=Decimal("18.00"),
    )
    base.update(kw)
    return DatosTicket(**base)


def validador(existentes=None):
    return ValidadorConsistencia(reglas_vigentes(RepositorioFalso(existentes)))


DUPLICADO = [("V2K-841", AHORA.date(), Decimal("29.80"), "ING-2027-00007", 7)]

# Diez inconsistencias sembradas, dos por regla (RNF-M05-02, DR-08).
SEMBRADAS = [
    ("V1", datos(), DUPLICADO),
    ("V1", datos(peso_bruto_tn=Decimal("25.00")), [("V2K-841", AHORA.date(), Decimal("25.00"), "ING-2027-00008", 8)]),
    ("V2", datos(peso_bruto_tn=Decimal("11.80")), None),
    ("V2", datos(peso_bruto_tn=Decimal("1.59"), tara_tn=Decimal("4.00")), None),
    ("V3", datos(placa="1234"), None),
    ("V3", datos(placa="V2K841"), None),
    ("V4", datos(peso_bruto_tn=Decimal("40.00")), None),
    ("V4", datos(peso_bruto_tn=Decimal("29.81")), None),
    ("V5", datos(fecha_hora_pesaje=AHORA + timedelta(minutes=1)), None),
    ("V5", datos(fecha_hora_pesaje=AHORA + timedelta(days=1)), None),
]


@pytest.mark.parametrize("regla,d,existentes", SEMBRADAS)
def test_rn_m05_01_las_diez_inconsistencias_sembradas_se_detectan(regla, d, existentes):
    inconsistentes = [e.regla for e in validador(existentes).validar(d).inconsistencias]
    assert inconsistentes == [regla]


@pytest.mark.parametrize(
    "d",
    [
        datos(),
        datos(placa="C9K-741", peso_bruto_tn=Decimal("27.10"), tara_tn=Decimal("12.10"), capacidad_tn=Decimal("15.00")),
        datos(placa="ABC-123", peso_bruto_tn=Decimal("32.00"), tara_tn=Decimal("12.60"), capacidad_tn=Decimal("20.00")),
        datos(fecha_hora_pesaje=AHORA),
    ],
)
def test_hu_m05_01_ca06_datos_correctos_no_generan_alertas(d):
    assert validador().validar(d).inconsistencias == []  # RNF-M05-03


def test_hu_m05_01_ca01_la_bloqueante_senala_su_campo_con_el_mensaje_literal():
    [e] = validador().validar(datos(placa="12-34")).inconsistencias
    assert (e.regla, e.campo, e.bloqueante) == ("V3", "placa", True)
    assert e.mensaje == "La placa no tiene un formato válido"


def test_hu_m05_01_ca05_informa_todas_las_inconsistencias_no_solo_la_primera():
    d = datos(placa="XX", peso_bruto_tn=Decimal("10.00"), fecha_hora_pesaje=AHORA + timedelta(hours=1))
    assert [e.regla for e in validador().validar(d).inconsistencias] == ["V2", "V3", "V5"]


def test_rn_m05_04_las_cinco_reglas_se_evaluan_siempre():
    d = datos(placa="XX", peso_bruto_tn=Decimal("10.00"))
    assert [e.regla for e in validador().validar(d)] == ["V1", "V2", "V3", "V4", "V5"]


def test_hu_m05_01_ca09_un_campo_vacio_no_se_senala_como_inconsistencia():
    d = DatosTicket(momento_registro=AHORA)
    resultado = validador().validar(d)
    assert resultado.inconsistencias == [] and all(e.omitida for e in resultado)


def test_rn_m05_07_la_regla_sin_sus_datos_se_omite_en_vez_de_fallar():
    resultado = validador().validar(datos(placa=None))
    omitidas = {e.regla for e in resultado if e.omitida}
    assert omitidas == {"V1", "V3", "V4"}


def test_hu_m05_01_ca11_sin_tara_se_omiten_v2_y_v4():
    resultado = validador().validar(datos(tara_tn=None, peso_bruto_tn=Decimal("5.00")))
    assert {e.regla for e in resultado if e.omitida} == {"V2", "V4"}


def test_rn_m05_05_en_el_destare_se_evaluan_solo_las_que_dependen_de_la_tara():
    resultado = validador().validar(datos(), solo_dependientes_de_tara=True)
    assert [e.regla for e in resultado] == ["V2", "V4"]


def test_rn_m05_03_v1_y_v4_no_bloquean_y_exigen_justificacion():
    reglas = {r.codigo: r for r in reglas_vigentes(RepositorioFalso())}
    assert [c for c, r in reglas.items() if not r.bloqueante] == ["V1", "V4"]
    assert reglas["V1"].mensaje_justificacion == "Debe indicar la justificación del posible duplicado"
    assert reglas["V4"].mensaje_justificacion == "Debe indicar la justificación del peso fuera de rango"


def test_rn_m05_02_v2_v3_y_v5_bloquean():
    assert {r.codigo for r in reglas_vigentes(RepositorioFalso()) if r.bloqueante} == {"V2", "V3", "V5"}


def test_hu_m05_01_ca04_corregido_el_dato_la_alerta_desaparece():
    v = validador()
    assert v.validar(datos(placa="V2K841")).inconsistencias
    assert v.validar(datos(placa="V2K-841")).inconsistencias == []


def test_rn_m05_12_v1_compara_por_coincidencia_exacta():
    v = validador(DUPLICADO)
    assert v.validar(datos(peso_bruto_tn=Decimal("29.79"))).inconsistencias == []
    [e] = v.validar(datos()).inconsistencias
    assert e.mensaje == "El ticket parece duplicado: ya existe el ingreso ING-2027-00007 con la misma placa, fecha y peso"


def test_rn_m05_13_en_una_correccion_v1_no_compara_el_ingreso_consigo_mismo():
    assert validador(DUPLICADO).validar(datos(excluir_ingreso=7)).inconsistencias == []


def test_hu_m05_01_ca13_correccion_advierte_solo_frente_a_otro_ingreso():
    otro = DUPLICADO + [("V2K-841", AHORA.date(), Decimal("29.80"), "ING-2027-00009", 9)]
    [e] = validador(otro).validar(datos(excluir_ingreso=7)).inconsistencias
    assert "ING-2027-00009" in e.mensaje


def test_rn_m05_10_v2_y_v4_usan_la_tara_y_capacidad_del_vehiculo_recibido():
    v = validador()
    assert v.validar(datos(tara_tn=Decimal("29.80"))).bloqueantes[0].regla == "V2"
    assert v.validar(datos(capacidad_tn=Decimal("30.00"), peso_bruto_tn=Decimal("40.00"))).inconsistencias == []


def test_rnf_m05_04_mismos_datos_mismo_resultado():
    v = validador(DUPLICADO)
    d = datos(placa="1X", peso_bruto_tn=Decimal("40.00"))
    assert v.validar(d) == v.validar(d)


def test_rn_m05_11_anadir_una_regla_no_cambia_el_validador_ni_las_demas():
    class SinMineralRaro:
        codigo, bloqueante, requiere_tara, campo = "V6", True, False, "placa"
        mensaje, mensaje_justificacion = "Regla nueva", ""

        def datos_completos(self, d):
            return True

        def evaluar(self, d):
            from apps.validacion.reglas import Resultado

            return Resultado(False)

    reglas = reglas_vigentes(RepositorioFalso()) + [SinMineralRaro()]
    assert [e.regla for e in ValidadorConsistencia(reglas).validar(datos()).inconsistencias] == ["V6"]


def test_rn_m05_08_los_mensajes_son_los_literales_de_la_historia():
    mensajes = {r.codigo: r.mensaje for r in reglas_vigentes(RepositorioFalso())}
    assert mensajes == {
        "V1": "El ticket parece duplicado: ya existe el ingreso {codigo} con la misma placa, fecha y peso",
        "V2": "La tara no puede ser mayor o igual que el peso bruto",
        "V3": "La placa no tiene un formato válido",
        "V4": "El peso neto está fuera del rango de carga del vehículo {placa}",
        "V5": "La fecha del ticket no puede ser posterior a la fecha de registro",
    }


def test_rn_m05_09_el_patron_de_v3_viene_de_la_configuracion(settings):
    settings.PATRON_PLACA = r"^[A-Z]{3}-\d{3}$"
    assert V3Placa().evaluar(datos(placa="V2K-841")).cumple is False
    assert V3Placa().evaluar(datos(placa="ABC-123")).cumple is True


def test_el_detalle_conserva_los_valores_que_motivaron_el_incumplimiento():
    r = V2Tara().evaluar(datos(peso_bruto_tn=Decimal("1.59"), tara_tn=Decimal("4.00")))
    assert r.detalle == "tara_tn=4.00 peso_bruto_tn=1.59"
    assert V4Capacidad().evaluar(datos(peso_bruto_tn=Decimal("40.00"))).detalle == "peso_neto_tn=28.20 capacidad_tn=18.00"
    assert "momento_registro" in V5Fecha().evaluar(datos(fecha_hora_pesaje=AHORA + timedelta(1))).detalle
    assert V1Duplicado(RepositorioFalso(DUPLICADO)).evaluar(datos()).marcadores == {"codigo": "ING-2027-00007"}
