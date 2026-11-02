"""Persistencia del resultado de la validación (RN-M05-06). Se invoca dentro de
la transacción de M03: un resultado sin ingreso no describe nada."""

from datetime import datetime

from apps.validacion.models import ResultadoValidacion

from .validador import Evaluacion


def _resolucion(cumple: bool, regla: str, justificaciones: dict, fallo_antes: bool) -> tuple[str, str]:
    if not cumple:
        texto = (justificaciones.get(regla) or "").strip()
        return (ResultadoValidacion.JUSTIFICADA, texto) if texto else (ResultadoValidacion.NO_APLICA, "")
    if fallo_antes:
        return ResultadoValidacion.CORREGIDA, ""
    return ResultadoValidacion.NO_APLICA, ""


def registrar_resultados(
    ingreso,
    momento: str,
    evaluaciones: list[Evaluacion],
    *,
    fecha_hora: datetime,
    justificaciones: dict | None = None,
    propuesta: list[dict] | None = None,
) -> list[ResultadoValidacion]:
    """Guarda una fila por regla evaluada. Con `propuesta` —la pasada sobre lo
    que leyó el reconocimiento—, guarda también esas filas, con la resolución
    que tuvo cada incumplimiento al confirmar: corregido o justificado."""
    justificaciones = justificaciones or {}
    finales = {e.regla: e for e in evaluaciones if not e.omitida}
    filas = []
    for previa in propuesta or []:
        final = finales.get(previa["regla"])
        if previa["cumple"]:
            resolucion, texto = ResultadoValidacion.NO_APLICA, ""
        elif final is None:
            resolucion, texto = ResultadoValidacion.NO_APLICA, ""
        else:
            resolucion, texto = _resolucion(final.cumple, previa["regla"], justificaciones, True)
        filas.append(
            ResultadoValidacion(
                ingreso=ingreso, regla=previa["regla"], momento=ResultadoValidacion.PROPUESTA,
                cumple=previa["cumple"], detalle=previa.get("detalle", ""),
                resolucion=resolucion, justificacion=texto, fecha_hora=fecha_hora,
            )
        )
    fallaron_antes = {p["regla"] for p in propuesta or [] if not p["cumple"]}
    for e in finales.values():
        resolucion, texto = _resolucion(e.cumple, e.regla, justificaciones, e.regla in fallaron_antes)
        filas.append(
            ResultadoValidacion(
                ingreso=ingreso, regla=e.regla, momento=momento, cumple=e.cumple, detalle=e.detalle,
                resolucion=resolucion, justificacion=texto, fecha_hora=fecha_hora,
            )
        )
    return ResultadoValidacion.objects.bulk_create(filas)
