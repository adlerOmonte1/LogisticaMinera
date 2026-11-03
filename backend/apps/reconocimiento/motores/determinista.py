"""Adaptador determinista: devuelve siempre el resultado con que se construye.
Lo usan las pruebas automatizadas (D-12) y no lee la imagen."""

from apps.reconocimiento.dominio import CAMPOS, CampoLeido, ResultadoReconocimiento


class ReconocedorDeterminista:
    motor = "determinista"
    version_motor = "1.0"

    def __init__(self, campos: dict | None = None, *, exito: bool = True, causa: str | None = None,
                 error: Exception | None = None):
        """`campos`: {nombre: (valor, confianza)}. `error` simula un motor que falla."""
        self.campos = campos or {}
        self.exito = exito
        self.causa = causa
        self.error = error
        self.invocaciones = 0

    def reconocer(self, imagen: bytes) -> ResultadoReconocimiento:
        self.invocaciones += 1
        if self.error is not None:
            raise self.error
        if not self.exito:
            return ResultadoReconocimiento.fallido(self.motor, self.version_motor, self.causa)
        leidos = []
        for nombre in CAMPOS:
            valor, confianza = self.campos.get(nombre, (None, None))
            leidos.append(CampoLeido(nombre, valor, confianza))
        return ResultadoReconocimiento(True, self.motor, self.version_motor, leidos)
