"""Verificaciones de configuración de M04, que Django ejecuta al arrancar y en
`manage.py check`."""

from django.conf import settings
from django.core import checks


@checks.register()
def motor_fijo_en_ventana_controlada(app_configs=None, **kwargs):
    """RN-M04-05: durante la ventana de operación controlada (D-16) el motor y su
    versión no cambian. Un respaldo entre dos motores haría que los ingresos de
    un mismo periodo provinieran de motores distintos."""
    nombres = [n.strip() for n in settings.RECONOCEDOR_ACTIVO.split(",") if n.strip()]
    errores = []
    if settings.RECONOCIMIENTO_VENTANA_CONTROLADA and len(nombres) > 1:
        errores.append(checks.Error(
            f"RECONOCEDOR_ACTIVO={settings.RECONOCEDOR_ACTIVO} combina {len(nombres)} motores durante la "
            "ventana de operación controlada",
            hint="Deje un solo motor en RECONOCEDOR_ACTIVO mientras RECONOCIMIENTO_VENTANA_CONTROLADA esté activa "
                 "(RN-M04-05, D-16).",
            id="reconocimiento.E001",
        ))
    desconocidos = [n for n in nombres if n not in settings.RECONOCEDORES]
    if desconocidos:
        errores.append(checks.Error(
            f"Motor desconocido en RECONOCEDOR_ACTIVO: {', '.join(desconocidos)}",
            hint=f"Disponibles: {', '.join(settings.RECONOCEDORES)}",
            id="reconocimiento.E002",
        ))
    return errores
