"""Adaptador del modelo local entrenado (D-12): TrOCR ajustado con tickets reales
de la Balanza en `laboratorio/ocr-manuscrito`. Corre dentro del backend, sin
servicio externo ni costo por ticket. Es el único archivo que importa `torch` y
`transformers` (RNF-M04-05).

Cadena: localizar el ticket, recortar las cinco zonas manuscritas, leer cada una
con su alfabeto y normalizar los tres campos con las reglas comunes. La
confianza de un campo es la probabilidad de su carácter más dudoso, de 0 a 1
(RN-M04-06).
"""

import hashlib
import re
from pathlib import Path

from django.conf import settings

from apps.reconocimiento.dominio import (
    FECHA,
    ILEGIBLE,
    PESO_BRUTO,
    PLACA,
    CampoLeido,
    ResultadoReconocimiento,
)
from apps.reconocimiento.motores.comun import normalizacion as N

ALFABETO = {
    "peso": set("0123456789.,:-+ "),
    "dia": set("0123456789. "),
    "mes": set("0123456789. "),
    "anio": set("0123456789. "),
    "placa": set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzáéíóúñÑ0123456789- ."),
}


def version_desde(texto: str) -> str:
    """`trocr-ticket-v1+sha256:35598224867a` -> `v1-35598224867a`: cabe en los 30
    caracteres de `version_motor` y conserva el hash que identifica los pesos."""
    m = re.search(r"-(v\d+)\+sha256:([0-9a-f]{12})", texto.strip())
    if not m:
        raise ValueError(f"VERSION del modelo con formato inesperado: {texto!r}")
    return f"{m.group(1)}-{m.group(2)}"


def _sha256(archivo: Path) -> str:
    h = hashlib.sha256()
    with open(archivo, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


class ReconocedorTrOCR:
    motor = "trocr-ticket"

    def __init__(self, carpeta: Path | None = None):
        import torch  # noqa: PLC0415 — solo este adaptador conoce la librería
        from transformers import TrOCRProcessor, VisionEncoderDecoderModel  # noqa: PLC0415

        from apps.reconocimiento.motores.comun.ticket_balanza import TicketBalanza  # noqa: PLC0415

        carpeta = Path(carpeta or settings.TROCR_MODELO_DIR)
        self.version_motor = version_desde((carpeta / "VERSION").read_text(encoding="utf-8"))
        esperado = settings.TROCR_MODELO_SHA256
        if esperado and not _sha256(carpeta / "model.safetensors").startswith(esperado):
            raise ValueError(f"Los pesos de {carpeta} no corresponden al hash {esperado} (RN-M04-04)")
        if settings.TROCR_HILOS:
            torch.set_num_threads(settings.TROCR_HILOS)
        self._torch = torch
        self.ticket = TicketBalanza(carpeta)
        self.procesador = TrOCRProcessor.from_pretrained(carpeta)
        self.modelo = VisionEncoderDecoderModel.from_pretrained(carpeta).eval()
        self.haces = settings.TROCR_HACES
        self._permitidos = {z: self._tokens_permitidos(a) for z, a in ALFABETO.items()}

    def _tokens_permitidos(self, alfabeto: set) -> list[int]:
        tok = self.procesador.tokenizer
        especiales = set(tok.all_special_ids)
        return [i for i in range(len(tok))
                if i in especiales or ((t := tok.decode([i])) and all(c in alfabeto for c in t))]

    def _leer(self, imagen, zona: str) -> tuple[str, float]:
        from PIL import Image  # noqa: PLC0415

        torch = self._torch
        permitidos = self._permitidos[zona]
        with torch.inference_mode():
            pixeles = self.procesador(images=[Image.fromarray(imagen)], return_tensors="pt").pixel_values
            salida = self.modelo.generate(
                pixeles, num_beams=self.haces, max_new_tokens=24, output_scores=True,
                return_dict_in_generate=True, prefix_allowed_tokens_fn=lambda _b, _ids: permitidos,
            )
            puntajes = self.modelo.compute_transition_scores(
                salida.sequences, salida.scores, getattr(salida, "beam_indices", None),
                normalize_logits=self.haces == 1,
            )[0]
        texto = self.procesador.batch_decode(salida.sequences, skip_special_tokens=True)[0].strip()
        # El relleno tras el fin de la lectura se reconoce por su token, no por su
        # puntaje: un carácter leído con total seguridad también puntúa 0.
        ids = salida.sequences[0, -puntajes.shape[0]:]
        validos = (ids != self.procesador.tokenizer.pad_token_id) & torch.isfinite(puntajes)
        probs = torch.exp(puntajes[validos])
        return texto, round(min(max(float(probs.min()) if len(probs) else 0.0, 0.0), 1.0), 3)

    def reconocer(self, imagen: bytes) -> ResultadoReconocimiento:
        zonas = self.ticket.zonas_de(imagen)
        if zonas is None:
            return ResultadoReconocimiento.fallido(self.motor, self.version_motor, ILEGIBLE)
        leido = {z: self._leer(img, z) for z, img in zonas.items()}

        peso = N.peso_bruto(leido["peso"][0])
        placa = N.placa(leido["placa"][0])
        fecha = N.fecha(leido["dia"][0], leido["mes"][0], leido["anio"][0])
        campos = [
            CampoLeido(PLACA, placa, leido["placa"][1]) if placa else CampoLeido(PLACA),
            CampoLeido(FECHA, fecha, min(leido[z][1] for z in ("dia", "mes", "anio"))) if fecha else CampoLeido(FECHA),
            CampoLeido(PESO_BRUTO, str(peso), leido["peso"][1]) if peso is not None else CampoLeido(PESO_BRUTO),
        ]
        if all(c.valor is None for c in campos):
            return ResultadoReconocimiento.fallido(self.motor, self.version_motor, ILEGIBLE)
        return ResultadoReconocimiento(True, self.motor, self.version_motor, campos)
