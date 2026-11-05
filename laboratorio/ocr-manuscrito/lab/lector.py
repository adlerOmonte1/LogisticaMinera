"""Lector de recortes con TrOCR y armado de los tres campos del ticket.

Cada zona se lee con un alfabeto propio (el peso solo admite dígitos y
separadores; la fecha, solo dígitos), y la confianza de una lectura es la
probabilidad media de sus caracteres, entre 0 y 1 (RN-M04-06).
"""

from dataclasses import dataclass
from decimal import Decimal

import torch
from PIL import Image
from transformers import TrOCRProcessor, VisionEncoderDecoderModel

from lab import normalizacion as N

ALFABETO = {
    "peso": set("0123456789.,:-+ "),
    "dia": set("0123456789. "),
    "mes": set("0123456789. "),
    "anio": set("0123456789. "),
    "placa": set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzáéíóúñÑ0123456789- ."),
}
CAMPOS_ZONA = ("peso", "placa", "dia", "mes", "anio")


@dataclass
class Lectura:
    texto: str
    confianza: float


@dataclass
class Campo:
    valor: str | None
    confianza: float | None


class LectorTrOCR:
    def __init__(self, modelo: str, dispositivo: str | None = None, haces: int = 4):
        self.dispositivo = dispositivo or ("cuda" if torch.cuda.is_available() else "cpu")
        self.procesador = TrOCRProcessor.from_pretrained(modelo)
        self.modelo = VisionEncoderDecoderModel.from_pretrained(modelo).to(self.dispositivo).eval()
        self.haces = haces
        self._permitidos = {c: self._tokens_permitidos(a) for c, a in ALFABETO.items()}

    def _tokens_permitidos(self, alfabeto: set) -> list[int]:
        tok = self.procesador.tokenizer
        especiales = set(tok.all_special_ids)
        ids = []
        for i in range(len(tok)):
            if i in especiales:
                ids.append(i)
                continue
            texto = tok.decode([i])
            if texto and all(ch in alfabeto for ch in texto):
                ids.append(i)
        return ids

    def leer(self, imagenes: list[Image.Image], zona: str) -> list[Lectura]:
        return self._leer(imagenes, [zona] * len(imagenes))

    def leer_zonas(self, recortes: dict[str, Image.Image]) -> dict[str, Lectura]:
        """Las cinco zonas de un ticket en una sola pasada del modelo, cada una con
        su alfabeto: es lo que baja el tiempo por ticket en CPU."""
        zonas = list(recortes)
        return dict(zip(zonas, self._leer([recortes[z] for z in zonas], zonas)))

    @torch.inference_mode()
    def _leer(self, imagenes: list[Image.Image], zonas: list[str]) -> list[Lectura]:
        permitidos = [self._permitidos[z] for z in zonas]
        pixeles = self.procesador(images=[i.convert("RGB") for i in imagenes], return_tensors="pt").pixel_values
        salida = self.modelo.generate(
            pixeles.to(self.dispositivo),
            num_beams=self.haces,
            max_new_tokens=24,
            output_scores=True,
            return_dict_in_generate=True,
            prefix_allowed_tokens_fn=lambda b, _ids: permitidos[b],
        )
        textos = self.procesador.batch_decode(salida.sequences, skip_special_tokens=True)
        puntajes = self.modelo.compute_transition_scores(
            # Con haz, los puntajes ya son log-probabilidades; sin haz son logits y se normalizan.
            salida.sequences, salida.scores, getattr(salida, "beam_indices", None), normalize_logits=self.haces == 1
        )
        # Las posiciones de relleno, después del fin de la lectura, se reconocen por
        # el token de relleno, no por su puntaje: un carácter leído con total
        # seguridad también tiene log-probabilidad 0.
        relleno = self.procesador.tokenizer.pad_token_id
        generados = salida.sequences[:, -puntajes.shape[1]:]
        lecturas = []
        for texto, fila, ids in zip(textos, puntajes, generados):
            # La confianza de la lectura es la de su carácter más dudoso: un solo
            # dígito equivocado basta para que el peso o la placa estén mal.
            validos = (ids != relleno) & torch.isfinite(fila)
            probs = torch.exp(fila[validos])
            conf = float(probs.min()) if len(probs) else 0.0
            lecturas.append(Lectura(texto.strip(), round(min(max(conf, 0.0), 1.0), 3)))
        return lecturas


def armar_campos(lecturas: dict[str, Lectura]) -> dict[str, Campo]:
    """De las cinco lecturas a los tres campos normalizados. Un campo que no
    cumple su regla queda sin valor y sin confianza (RN-M04-03, RN-M04-06)."""
    peso = N.peso_bruto(lecturas["peso"].texto)
    placa = N.placa(lecturas["placa"].texto)
    fecha = N.fecha(N.solo_digitos(lecturas["dia"].texto), N.solo_digitos(lecturas["mes"].texto),
                    N.solo_digitos(lecturas["anio"].texto))
    conf_fecha = min(lecturas[z].confianza for z in ("dia", "mes", "anio"))
    return {
        "PESO_BRUTO": Campo(str(peso) if peso is not None else None, lecturas["peso"].confianza if peso is not None else None),
        "PLACA": Campo(placa, lecturas["placa"].confianza if placa else None),
        "FECHA": Campo(fecha, conf_fecha if fecha else None),
    }


def coincide(campo: str, leido: str | None, verdadero: str) -> bool:
    """Un campo sin valor verdadero (placa escrita como nombre, día tapado) es
    correcto solo si el lector tampoco propone valor."""
    if not verdadero:
        return leido is None
    if leido is None:
        return False
    if campo == "PESO_BRUTO":
        return Decimal(leido) == Decimal(verdadero)
    return leido.upper() == verdadero.upper()
