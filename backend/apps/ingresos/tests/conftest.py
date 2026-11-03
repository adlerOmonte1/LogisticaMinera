import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import Rol
from apps.accounts.tests.factories import RolFactory, UsuarioFactory


@pytest.fixture
def api():
    return APIClient()


@pytest.fixture
def administrador(db):
    return UsuarioFactory(rol=RolFactory(nombre=Rol.ADMINISTRADOR))


@pytest.fixture
def administrativo(db):
    return UsuarioFactory(rol=RolFactory(nombre=Rol.ADMINISTRATIVO))


@pytest.fixture
def supervisor(db):
    return UsuarioFactory(rol=RolFactory(nombre=Rol.SUPERVISOR))


@pytest.fixture
def api_como(api):
    def _autenticar(usuario):
        token = RefreshToken.for_user(usuario).access_token
        api.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        return api

    return _autenticar


# --- Registro de ingresos (F3) -------------------------------------------------

import io  # noqa: E402
from datetime import timedelta  # noqa: E402
from decimal import Decimal  # noqa: E402

from django.core.files.uploadedfile import SimpleUploadedFile  # noqa: E402
from django.utils import timezone  # noqa: E402
from PIL import Image  # noqa: E402

from apps.catalogo.tests.factories import TipoMineralFactory, VehiculoFactory  # noqa: E402
from apps.reconocimiento import motores  # noqa: E402
from apps.reconocimiento.dominio import FECHA, PESO_BRUTO, PLACA  # noqa: E402
from apps.reconocimiento.motores.determinista import ReconocedorDeterminista  # noqa: E402


def _imagen(formato="PNG", nombre="ticket.png"):
    buffer = io.BytesIO()
    Image.new("RGB", (40, 60), "white").save(buffer, format=formato)
    return SimpleUploadedFile(nombre, buffer.getvalue(), content_type=f"image/{formato.lower()}")


@pytest.fixture
def nueva_imagen():
    """Un archivo nuevo por envío: el cliente de pruebas lee el archivo al subirlo."""
    return _imagen


@pytest.fixture
def imagen_png():
    return _imagen()


@pytest.fixture
def imagen_jpg():
    return _imagen("JPEG", "ticket.jpg")


@pytest.fixture(autouse=True)
def almacen_temporal(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path / "media"


@pytest.fixture
def ayer():
    """Fecha del pesaje en el pasado, para no chocar con V5 a medianoche."""
    return timezone.localdate() - timedelta(days=1)


@pytest.fixture
def vehiculo(db):
    return VehiculoFactory(placa="V2K-841", capacidad_tn=Decimal("18.00"), tara_tn=Decimal("11.80"))


@pytest.fixture
def vehiculo_sin_tara(db):
    return VehiculoFactory(placa="E4R-208", capacidad_tn=Decimal("17.50"))


@pytest.fixture
def mineral(db):
    return TipoMineralFactory(codigo="MOA", nombre="Mineral óxido Pingüino")


@pytest.fixture
def lectura(monkeypatch, ayer):
    """Fija lo que «lee» el motor: por defecto, el ticket de V2K-841 de ayer
    con 29,80 t. Devuelve el reconocedor para cambiarlo en cada prueba."""
    reconocedor = ReconocedorDeterminista(
        {PLACA: ("V2K-841", 0.97), FECHA: (ayer.isoformat(), 0.95), PESO_BRUTO: ("29.80", 0.62)}
    )
    monkeypatch.setattr(motores, "obtener_reconocedor", lambda: reconocedor)
    return reconocedor
