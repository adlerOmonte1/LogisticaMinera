from django.apps import AppConfig


class ReconocimientoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.reconocimiento"
    verbose_name = "M04 — Reconocimiento automático del ticket"

    def ready(self):
        from apps.reconocimiento import checks  # noqa: F401, PLC0415 — registra las verificaciones
