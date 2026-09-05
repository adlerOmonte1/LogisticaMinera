"""Preproducción: servidor de pruebas donde corre JMeter en la semana 8 (ARQ-02 §7).

Existe separado de producción porque las pruebas de carga no pueden ejecutarse contra el entorno
donde se recolecta el postest: alterarían los tiempos de respuesta que sostienen el RNF de
eficiencia de desempeño.
"""

from .base import *  # noqa: F401,F403

DEBUG = False
