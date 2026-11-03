"""`ValidadorConsistencia`: recorre la colección de reglas sin nombrar ninguna
(RN-M05-11) y devuelve el resultado de todas, nunca una excepción: la primera
inconsistencia no interrumpe la evaluación (RN-M05-04). Quien decide si la
operación continúa es M03.
"""

from dataclasses import dataclass

from apps.validacion.reglas import DatosTicket, Regla


@dataclass(frozen=True)
class Evaluacion:
    """Resultado de una regla sobre unos datos. `omitida` si le faltaban datos
    (RN-M05-07) o si dependía de una tara que el vehículo aún no tiene."""

    regla: str
    campo: str
    bloqueante: bool
    omitida: bool
    cumple: bool
    mensaje: str = ""
    mensaje_justificacion: str = ""
    detalle: str = ""

    @property
    def inconsistente(self) -> bool:
        return not self.omitida and not self.cumple

    def como_dict(self) -> dict:
        return {
            "regla": self.regla,
            "campo": self.campo,
            "mensaje": self.mensaje,
            "bloqueante": self.bloqueante,
            "exige_justificacion": not self.bloqueante,
        }


class ResultadoValidacionDatos(list):
    """Lista de evaluaciones con las consultas que M03 necesita para decidir."""

    @property
    def evaluadas(self) -> list[Evaluacion]:
        return [e for e in self if not e.omitida]

    @property
    def inconsistencias(self) -> list[Evaluacion]:
        return [e for e in self if e.inconsistente]

    @property
    def bloqueantes(self) -> list[Evaluacion]:
        return [e for e in self.inconsistencias if e.bloqueante]

    def advertencias_sin_justificar(self, justificaciones: dict) -> list[Evaluacion]:
        return [
            e
            for e in self.inconsistencias
            if not e.bloqueante and not (justificaciones.get(e.regla) or "").strip()
        ]


class ValidadorConsistencia:
    def __init__(self, reglas: list[Regla]):
        self._reglas = list(reglas)

    def validar(self, datos: DatosTicket, *, solo_dependientes_de_tara: bool = False) -> ResultadoValidacionDatos:
        """`solo_dependientes_de_tara` es la pasada del destare (RN-M05-05): las
        reglas que en el primer viaje se omitieron por falta de tara."""
        resultado = ResultadoValidacionDatos()
        for regla in self._reglas:
            if solo_dependientes_de_tara and not regla.requiere_tara:
                continue
            base = {
                "regla": regla.codigo,
                "campo": regla.campo,
                "bloqueante": regla.bloqueante,
                "mensaje_justificacion": regla.mensaje_justificacion,
            }
            if not regla.datos_completos(datos):
                resultado.append(Evaluacion(**base, omitida=True, cumple=True))
                continue
            r = regla.evaluar(datos)
            resultado.append(
                Evaluacion(
                    **base,
                    omitida=False,
                    cumple=r.cumple,
                    mensaje="" if r.cumple else regla.mensaje.format(**r.marcadores),
                    detalle=r.detalle,
                )
            )
        return resultado
