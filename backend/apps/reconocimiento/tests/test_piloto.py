"""Herramienta del piloto de D-12 (PLAN-02 7.3): mide exactitud por campo,
tiempo y errores que el umbral no habría resaltado."""

from django.core.management import call_command
from django.core.management.base import CommandError
import pytest

from apps.reconocimiento.dominio import FECHA, PESO_BRUTO, PLACA
from apps.reconocimiento.motores.determinista import ReconocedorDeterminista
from apps.reconocimiento.piloto import evaluar, informe


@pytest.fixture
def conjunto(tmp_path):
    (tmp_path / "t1.jpg").write_bytes(b"imagen-1")
    (tmp_path / "t2.jpg").write_bytes(b"imagen-2")
    (tmp_path / "verdad.csv").write_text(
        "archivo;placa;fecha;peso_bruto_tn\nt1.jpg;V2K-841;2026-10-30;29,80\nt2.jpg;C9K-741;2026-10-31;27.10\n",
        encoding="utf-8")
    return tmp_path


def test_el_piloto_mide_exactitud_por_campo_y_errores_confiados(conjunto):
    lector = ReconocedorDeterminista({PLACA: ("V2K-841", 0.95), FECHA: ("2026-10-30", 0.90),
                                      PESO_BRUTO: ("29.80", 0.85)})
    [r] = evaluar({"determinista": lector}, conjunto)
    assert (r.tickets, r.exitos) == (2, 2)
    assert (r.exactitud(PLACA), r.exactitud(FECHA), r.exactitud(PESO_BRUTO)) == (50.0, 50.0, 50.0)
    # En el segundo ticket leyó mal los tres campos con confianza alta: el umbral no los habría resaltado.
    assert r.errores_confiados == {PLACA: 1, FECHA: 1, PESO_BRUTO: 1}
    texto = informe([r], conjunto, 2)
    assert "| determinista | 1.0 | 2/2 | 50.0 % |" in texto and "Utilidad del umbral" in texto


def test_el_motor_que_falla_cuenta_como_sin_exito(conjunto):
    [r] = evaluar({"caido": ReconocedorDeterminista(error=TimeoutError())}, conjunto)
    assert (r.exitos, r.exactitud_global) == (0, 0.0)


def test_el_comando_exige_la_verdad_y_motores_conocidos(tmp_path, conjunto):
    with pytest.raises(CommandError, match="verdad.csv"):
        call_command("piloto_motores", str(tmp_path / "vacia"))
    with pytest.raises(CommandError, match="Motor desconocido"):
        call_command("piloto_motores", str(conjunto), motores="inexistente")


def test_el_comando_escribe_el_informe(conjunto, tmp_path):
    salida = tmp_path / "informe.md"
    call_command("piloto_motores", str(conjunto), motores="determinista", salida=str(salida))
    assert salida.read_text(encoding="utf-8").startswith("# Informe del piloto")
