"""Contrato de M04 con el resto del sistema (D-12, notas de M04).

`ReconocedorTicket` es el único punto de acoplamiento entre el registro y el
motor. M03 recibe un `ResultadoReconocimiento` y no sabe qué motor lo produjo.
"""

from dataclasses import asdict, dataclass, field
from typing import Protocol

PLACA = "PLACA"
FECHA = "FECHA"
PESO_BRUTO = "PESO_BRUTO"
CAMPOS = (PLACA, FECHA, PESO_BRUTO)

ILEGIBLE = "ILEGIBLE"
NO_DISPONIBLE = "NO_DISPONIBLE"

MENSAJE_ILEGIBLE = "No fue posible leer el ticket. Tome una nueva fotografía o ingrese los datos manualmente"
MENSAJE_NO_DISPONIBLE = "El reconocimiento no está disponible. Puede ingresar los datos manualmente"
MENSAJE_BAJA_CONFIANZA = "Verifique este dato: lectura con baja confianza"


@dataclass(frozen=True)
class CampoLeido:
    """`valor` y `confianza` son None si no hubo lectura: nunca cadena vacía ni
    cero en su lugar (RN-M04-03, RN-M04-06). El valor llega normalizado como
    texto: placa en mayúsculas, fecha ISO y peso bruto en toneladas."""

    nombre: str
    valor: str | None = None
    confianza: float | None = None


@dataclass(frozen=True)
class ResultadoReconocimiento:
    exito: bool
    motor: str
    version_motor: str
    campos: list[CampoLeido] = field(default_factory=list)
    causa: str | None = None  # ILEGIBLE o NO_DISPONIBLE cuando no hubo éxito

    def campo(self, nombre: str) -> CampoLeido:
        for c in self.campos:
            if c.nombre == nombre:
                return c
        return CampoLeido(nombre)

    def como_dict(self) -> dict:
        return {
            "exito": self.exito,
            "motor": self.motor,
            "version_motor": self.version_motor,
            "causa": self.causa,
            "campos": [asdict(self.campo(n)) for n in CAMPOS],
        }

    @classmethod
    def desde_dict(cls, datos: dict) -> "ResultadoReconocimiento":
        return cls(
            exito=datos["exito"],
            motor=datos["motor"],
            version_motor=datos["version_motor"],
            causa=datos.get("causa"),
            campos=[CampoLeido(**c) for c in datos["campos"]],
        )

    @classmethod
    def fallido(cls, motor: str, version: str, causa: str) -> "ResultadoReconocimiento":
        return cls(False, motor, version, [CampoLeido(n) for n in CAMPOS], causa)


class ReconocedorTicket(Protocol):
    motor: str
    version_motor: str

    def reconocer(self, imagen: bytes) -> ResultadoReconocimiento: ...
