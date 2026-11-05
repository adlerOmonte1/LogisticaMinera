"""`python manage.py piloto_motores CARPETA [--motores tesseract,otro] [--salida informe.md]`

Ejecuta el piloto de D-12 sobre un conjunto de tickets con su verdad. Solo lee:
no registra ingresos ni reconocimientos.
"""

from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.reconocimiento.motores import crear
from apps.reconocimiento.piloto import evaluar, informe, leer_conjunto


class Command(BaseCommand):
    help = "Compara los motores de reconocimiento sobre un conjunto de tickets reales (D-12)."

    def add_arguments(self, parser):
        parser.add_argument("carpeta")
        parser.add_argument("--motores", default="tesseract")
        parser.add_argument("--salida")

    def handle(self, carpeta, motores, salida=None, **opciones):
        carpeta = Path(carpeta)
        if not (carpeta / "verdad.csv").exists():
            raise CommandError(f"Falta {carpeta / 'verdad.csv'} (archivo;placa;fecha;peso_bruto_tn)")
        elegidos = {}
        for nombre in [m.strip() for m in motores.split(",") if m.strip()]:
            if nombre not in settings.RECONOCEDORES:
                raise CommandError(f"Motor desconocido: {nombre}. Disponibles: {', '.join(settings.RECONOCEDORES)}")
            try:
                elegidos[nombre] = crear(nombre)
            except Exception as exc:
                raise CommandError(f"No se pudo cargar el motor {nombre}: {exc}")
        resultados = evaluar(elegidos, carpeta)
        texto = informe(resultados, carpeta, len(leer_conjunto(carpeta)))
        if salida:
            Path(salida).write_text(texto, encoding="utf-8")
        self.stdout.write(texto)
