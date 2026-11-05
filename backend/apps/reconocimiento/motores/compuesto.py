"""Motor compuesto: varios motores detrás de una sola `ReconocedorTicket`.

El registro de ingresos sigue viendo un solo motor (D-12). Cada resultado
conserva el motor y la versión que realmente leyeron el ticket (RN-M04-04).
Una política distinta —por ejemplo, consultar un segundo motor solo cuando un
campo sale con confianza baja— es otra clase con la misma interfaz, que se
elige en `RECONOCIMIENTO_COMPOSICION` sin modificar esta.
"""

from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as TiempoAgotado

from django.conf import settings

from apps.reconocimiento.dominio import ILEGIBLE, NO_DISPONIBLE, ResultadoReconocimiento


class ReconocedorConRespaldo:
    """Lee con el primer motor; si no está disponible (falla, no responde a
    tiempo o no hay conexión), con el siguiente. Un ticket ilegible no pasa al
    siguiente: el motor sí respondió."""

    version_motor = "-"

    def __init__(self, miembros: list[tuple[str, object]]):
        self.miembros = miembros
        self.motor = ("respaldo:" + "+".join(n for n, _ in miembros))[:50]

    def _tiempo(self, nombre: str) -> float:
        propio = settings.RECONOCIMIENTO_TIEMPO_POR_MOTOR.get(nombre)
        return float(propio) if propio else settings.RECONOCIMIENTO_TIEMPO_ESPERA_S / len(self.miembros)

    def reconocer(self, imagen: bytes) -> ResultadoReconocimiento:
        for nombre, motor in self.miembros:
            ejecutor = ThreadPoolExecutor(max_workers=1)
            try:
                resultado = ejecutor.submit(motor.reconocer, imagen).result(timeout=self._tiempo(nombre))
            except (TiempoAgotado, Exception):
                continue
            finally:
                ejecutor.shutdown(wait=False, cancel_futures=True)
            if resultado.exito or resultado.causa == ILEGIBLE:
                return resultado
        return ResultadoReconocimiento.fallido(self.motor, self.version_motor, NO_DISPONIBLE)
