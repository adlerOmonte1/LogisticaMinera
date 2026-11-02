"""Adaptador local provisional (D-12): OCR con Tesseract dentro del mismo
backend, sin servicio externo ni credenciales. Es el único archivo que importa
`pytesseract` (RNF-M04-05).

El ticket imprime tres líneas que interesan (DR-09): `FECHA dd/mm/aaaa`,
`PLACA XXX-NNN` y `P. BRUTO 32 500 kg`. El adaptador busca cada una por su
patrón; un campo que no encuentra queda sin valor y sin confianza (RN-M04-03).
"""

import io
import re
from datetime import date
from decimal import Decimal, InvalidOperation

from django.conf import settings

from apps.reconocimiento.dominio import (
    FECHA,
    ILEGIBLE,
    PESO_BRUTO,
    PLACA,
    CampoLeido,
    ResultadoReconocimiento,
)

_PLACA = re.compile(r"\b([A-Z0-9]{3})\s?[-–]\s?([A-Z0-9]{3})\b")
_FECHA = re.compile(r"\b(\d{2})[/.-](\d{2})[/.-](\d{4})\b")
_PESO = re.compile(r"(\d{1,3}(?:[ .,]\d{3})+|\d{4,6})\s*KG", re.IGNORECASE)


class ReconocedorTesseract:
    motor = "tesseract-local"

    def __init__(self):
        import pytesseract  # noqa: PLC0415 — solo este adaptador conoce la librería

        self._ocr = pytesseract
        self.version_motor = str(pytesseract.get_tesseract_version())

    def reconocer(self, imagen: bytes) -> ResultadoReconocimiento:
        from PIL import Image, ImageOps  # noqa: PLC0415

        try:
            figura = ImageOps.grayscale(Image.open(io.BytesIO(imagen)))
        except Exception:
            return ResultadoReconocimiento.fallido(self.motor, self.version_motor, ILEGIBLE)

        datos = self._ocr.image_to_data(
            figura, lang=settings.OCR_IDIOMA, output_type=self._ocr.Output.DICT, timeout=settings.RECONOCIMIENTO_TIEMPO_ESPERA_S
        )
        lineas = self._lineas(datos)
        campos = [self._placa(lineas), self._fecha(lineas), self._peso(lineas)]
        if all(c.valor is None for c in campos):
            return ResultadoReconocimiento.fallido(self.motor, self.version_motor, ILEGIBLE)
        return ResultadoReconocimiento(True, self.motor, self.version_motor, campos)

    @staticmethod
    def _lineas(datos: dict) -> list[tuple[str, float]]:
        """Agrupa las palabras por línea con la confianza media de la línea (0 a 1)."""
        grupos: dict[tuple, list] = {}
        for i, texto in enumerate(datos["text"]):
            texto = (texto or "").strip()
            conf = float(datos["conf"][i])
            if not texto or conf < 0:
                continue
            clave = (datos["block_num"][i], datos["par_num"][i], datos["line_num"][i])
            grupos.setdefault(clave, []).append((texto, conf))
        return [
            (" ".join(t for t, _ in palabras).upper(), sum(c for _, c in palabras) / len(palabras) / 100)
            for palabras in grupos.values()
        ]

    @staticmethod
    def _confianza(valor: float) -> float:
        return round(min(max(valor, 0.0), 1.0), 3)

    def _placa(self, lineas) -> CampoLeido:
        for texto, conf in lineas:
            if "PLACA" in texto:
                m = _PLACA.search(texto.replace("PLACA", ""))
                if m:
                    return CampoLeido(PLACA, f"{m.group(1)}-{m.group(2)}", self._confianza(conf))
        return CampoLeido(PLACA)

    def _fecha(self, lineas) -> CampoLeido:
        for texto, conf in lineas:
            m = _FECHA.search(texto)
            if m:
                try:
                    valor = date(int(m.group(3)), int(m.group(2)), int(m.group(1))).isoformat()
                except ValueError:
                    continue
                return CampoLeido(FECHA, valor, self._confianza(conf))
        return CampoLeido(FECHA)

    def _peso(self, lineas) -> CampoLeido:
        for texto, conf in lineas:
            if "BRUTO" in texto or "KG" in texto:
                m = _PESO.search(texto)
                if m:
                    try:
                        kg = Decimal(re.sub(r"[ .,]", "", m.group(1)))
                    except InvalidOperation:
                        continue
                    toneladas = (kg / 1000).quantize(Decimal("0.01"))
                    return CampoLeido(PESO_BRUTO, str(toneladas), self._confianza(conf))
        return CampoLeido(PESO_BRUTO)
