"""Adaptador local de referencia (D-12): OCR con Tesseract dentro del mismo
backend, sin servicio externo ni credenciales. Es el único archivo que importa
`pytesseract` (RNF-M04-05).

El ticket de la Balanza (DR-09) trae tres datos que interesan, escritos a mano
junto a etiquetas impresas: `Peso: 13.400`, `Placa: A5S-939` y la fecha en tres
casillas bajo `DIA MES AÑO`. El adaptador busca cada etiqueta y normaliza lo que
sigue con las reglas comunes; un campo que no encuentra queda sin valor y sin
confianza (RN-M04-03). Tesseract lee bien lo impreso y mal lo manuscrito: sirve
como línea base del piloto, no como motor de operación.
"""

import io
import re

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

    @staticmethod
    def _despues_de(etiqueta: str, texto: str) -> str | None:
        m = re.search(rf"{etiqueta}\s*:?\s*(.*)", texto)
        return m.group(1) if m else None

    def _placa(self, lineas) -> CampoLeido:
        for texto, conf in lineas:
            resto = self._despues_de("PLACA", texto)
            if resto is not None and (valor := N.placa(resto)):
                return CampoLeido(PLACA, valor, self._confianza(conf))
        return CampoLeido(PLACA)

    def _peso(self, lineas) -> CampoLeido:
        for texto, conf in lineas:
            resto = self._despues_de("PESO", texto)
            if resto is not None:
                # La placa puede quedar en la misma línea: el peso termina donde ella empieza.
                resto = resto.split("PLACA")[0]
                if (valor := N.peso_bruto(resto)) is not None:
                    return CampoLeido(PESO_BRUTO, str(valor), self._confianza(conf))
        return CampoLeido(PESO_BRUTO)

    def _fecha(self, lineas) -> CampoLeido:
        """Las casillas quedan en la línea siguiente a la cabecera `DIA MES AÑO`."""
        for i, (texto, _conf) in enumerate(lineas[:-1]):
            if "DIA" in texto and "MES" in texto:
                siguiente, conf = lineas[i + 1]
                numeros = re.findall(r"\d{1,4}", siguiente)
                if len(numeros) >= 3 and (valor := N.fecha(*numeros[:3])):
                    return CampoLeido(FECHA, valor, self._confianza(conf))
        return CampoLeido(FECHA)
