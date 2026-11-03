"""El borrador del registro: lo que el servidor sabe entre la imagen y la
confirmación (D-25).

No es un ingreso ni se guarda en la base: no tiene código ni figura en ninguna
consulta (A-M03-03). Viaja al cliente firmado por el servidor y vuelve con la
confirmación. La firma impide que el cliente altere lo que solo el servidor
puede afirmar: la hora de inicio del registro (D-01), la imagen recibida, lo
que leyó el motor (RN-M04-10) y la validación de la propuesta. Sin vencimiento:
el borrador se conserva en el dispositivo mientras no hay señal (RNF-M03-05).
"""

from dataclasses import dataclass
from datetime import datetime

from django.core import signing

_SAL = "apps.ingresos.borrador"


@dataclass(frozen=True)
class Borrador:
    usuario: int
    inicio: datetime
    imagen: str | None
    motivo_sin_respaldo: str | None
    reconocimiento: dict | None
    umbral: str | None
    propuesta: list[dict]

    @property
    def sin_foto(self) -> bool:
        return self.imagen is None


def firmar(b: Borrador) -> str:
    return signing.dumps(
        {
            "u": b.usuario,
            "i": b.inicio.isoformat(),
            "img": b.imagen,
            "m": b.motivo_sin_respaldo,
            "r": b.reconocimiento,
            "t": b.umbral,
            "p": b.propuesta,
        },
        salt=_SAL,
        compress=True,
    )


def leer(token: str | None, usuario) -> Borrador | None:
    """None si falta, si la firma no es válida o si es de otro usuario: para el
    registro es lo mismo que no haber adjuntado la imagen (HU-M03-01 CA02)."""
    if not token:
        return None
    try:
        d = signing.loads(token, salt=_SAL)
    except signing.BadSignature:
        return None
    if d.get("u") != usuario.pk:
        return None
    return Borrador(
        usuario=d["u"],
        inicio=datetime.fromisoformat(d["i"]),
        imagen=d["img"],
        motivo_sin_respaldo=d["m"],
        reconocimiento=d["r"],
        umbral=d["t"],
        propuesta=d["p"] or [],
    )
