"""Casos de uso de M08: consolidar un mes y exportarlo. Leer no se audita;
exportar sí, con el periodo (RS-M08-10, notas de M08)."""

from datetime import date

from apps.consolidacion.exportadores import EXPORTADORES
from apps.consolidacion.repositories import Consolidado, ConsolidacionRepository, Periodo
from common.eventos import Accion, RegistradorDeEventos, registrador_por_defecto
from common.excepciones import ErrorDeValidacionDeDominio
from common.reloj import Reloj, reloj_del_sistema

SIN_INGRESOS = "No hay ingresos registrados para el periodo indicado"
PERIODO_FUTURO = "No se puede consolidar un periodo futuro"
EN_PROCESO = "Hay {n} ingresos en proceso en el periodo, pendientes del destare"
AL_CORTE = "Total al corte de hoy, {fecha}"  # maqueta: «al corte de hoy» (D-28)


def leer_periodo(anio, mes) -> Periodo:
    try:
        anio, mes = int(anio), int(mes)
        if not 1 <= mes <= 12:
            raise ValueError
    except (TypeError, ValueError):
        raise ErrorDeValidacionDeDominio("Datos inválidos", codigo="ERROR_DE_VALIDACION",
                                         detalles={"periodo": ["Indique el mes (1 a 12) y el año"]})
    return Periodo(anio, mes)


class ServicioConsolidacion:
    def __init__(self, *, reloj: Reloj = reloj_del_sistema, auditoria: RegistradorDeEventos = registrador_por_defecto):
        self.reloj = reloj
        self.auditoria = auditoria

    def _hoy(self) -> date:
        from django.utils import timezone  # noqa: PLC0415

        return timezone.localtime(self.reloj.ahora()).date()

    def consolidar(self, periodo: Periodo) -> tuple[Consolidado, dict]:
        """HU-M08-01. Devuelve el cálculo y los avisos que lo acompañan."""
        hoy = self._hoy()
        if (periodo.anio, periodo.mes) > (hoy.year, hoy.month):  # RN-M08-04
            raise ErrorDeValidacionDeDominio(PERIODO_FUTURO, codigo="PERIODO_FUTURO")
        consolidado = ConsolidacionRepository.calcular(periodo)
        avisos = {
            "mensaje": None if consolidado.filas else SIN_INGRESOS,
            "en_proceso_mensaje": EN_PROCESO.format(n=len(consolidado.en_proceso)) if consolidado.en_proceso else None,
            "al_corte": AL_CORTE.format(fecha=hoy.strftime("%d/%m/%Y"))
            if (periodo.anio, periodo.mes) == (hoy.year, hoy.month) else None,
        }
        return consolidado, avisos

    def exportar(self, periodo: Periodo, usuario, *, formato: str = "xlsx", ip=None):
        """HU-M08-02: el mismo cálculo que la pantalla (RN-M08-05)."""
        consolidado, _ = self.consolidar(periodo)
        if not consolidado.filas:
            raise ErrorDeValidacionDeDominio(SIN_INGRESOS, codigo="SIN_INGRESOS")
        exportador = EXPORTADORES[formato]
        contenido = exportador.generar(consolidado, self.reloj.ahora())
        self.auditoria.registrar(
            accion=Accion.EXPORTAR, entidad="Consolidado", usuario=usuario, ip=ip,
            valores_nuevos={"exportacion": "CONSOLIDADO_MENSUAL", "periodo": f"{periodo.anio}-{periodo.mes:02d}",
                            "formato": formato, "total_toneladas": str(consolidado.total_toneladas),
                            "ingresos": consolidado.total_ingresos},
        )
        return contenido, exportador


__all__ = ["AL_CORTE", "EN_PROCESO", "PERIODO_FUTURO", "SIN_INGRESOS", "ServicioConsolidacion", "leer_periodo"]
