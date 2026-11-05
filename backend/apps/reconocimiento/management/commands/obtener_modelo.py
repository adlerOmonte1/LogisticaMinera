"""`python manage.py obtener_modelo (--desde RUTA | --url URL) [--destino CARPETA]`

Provisiona el modelo local entrenado (motor `trocr`) en `TROCR_MODELO_DIR`. El
modelo no se versiona en git: pesa más de un gigabyte y aprendió de tickets con
datos personales. Se reparte como un paquete .zip por un almacenamiento privado,
o se copia desde la carpeta del laboratorio.

Antes de instalarlo verifica que el paquete esté completo y que sus pesos
correspondan al hash configurado (`TROCR_MODELO_SHA256`), para que todos los
equipos lean con el mismo motor y la misma versión (RN-M04-04).
"""

import shutil
import tempfile
import urllib.request
import zipfile
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.reconocimiento.motores.trocr_local import _sha256, version_desde

ARCHIVOS = ("VERSION", "config.json", "model.safetensors", "plantilla.json", "referencia.png")


def _carpeta_del_modelo(raiz: Path) -> Path:
    """La carpeta que contiene `VERSION`, esté en la raíz del paquete o un nivel abajo."""
    for candidata in [raiz, *[p for p in raiz.iterdir() if p.is_dir()]]:
        if (candidata / "VERSION").exists():
            return candidata
    raise CommandError("El paquete no contiene un modelo: falta el archivo VERSION")


class Command(BaseCommand):
    help = "Provisiona y verifica el modelo local entrenado del ticket (motor trocr)."

    def add_arguments(self, parser):
        origen = parser.add_mutually_exclusive_group(required=True)
        origen.add_argument("--desde", help="carpeta del modelo o paquete .zip")
        origen.add_argument("--url", help="enlace privado a un paquete .zip")
        parser.add_argument("--destino", default=str(settings.TROCR_MODELO_DIR))
        parser.add_argument("--sha256", default=settings.TROCR_MODELO_SHA256,
                            help="prefijo del hash de model.safetensors (por omisión, TROCR_MODELO_SHA256)")

    def handle(self, desde=None, url=None, destino=None, sha256=None, **opciones):
        destino = Path(destino)
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            if url:
                self.stdout.write(f"Descargando {url.split('?')[0]} …")
                paquete = tmp / "modelo.zip"
                urllib.request.urlretrieve(url, paquete)  # noqa: S310 — enlace indicado por el administrador
                desde = paquete
            origen = Path(desde)
            if origen.is_file():
                if not zipfile.is_zipfile(origen):
                    raise CommandError(f"{origen} no es un paquete .zip")
                with zipfile.ZipFile(origen) as z:
                    z.extractall(tmp / "extraido")
                origen = _carpeta_del_modelo(tmp / "extraido")
            elif not origen.is_dir():
                raise CommandError(f"No existe {origen}")

            faltan = [a for a in ARCHIVOS if not (origen / a).exists()]
            if faltan:
                raise CommandError(f"Al modelo le faltan: {', '.join(faltan)}")
            version = version_desde((origen / "VERSION").read_text(encoding="utf-8"))
            huella = _sha256(origen / "model.safetensors")
            if sha256 and not huella.startswith(sha256):
                raise CommandError(f"El hash de los pesos ({huella[:12]}) no coincide con {sha256}")

            destino.parent.mkdir(parents=True, exist_ok=True)
            provisional = destino.with_name(destino.name + ".nuevo")
            shutil.rmtree(provisional, ignore_errors=True)
            shutil.copytree(origen, provisional)
            shutil.rmtree(destino, ignore_errors=True)
            provisional.rename(destino)
        self.stdout.write(self.style.SUCCESS(f"Modelo trocr-ticket {version} instalado en {destino}"))
