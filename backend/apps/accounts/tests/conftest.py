import pytest
from rest_framework.test import APIClient

from apps.accounts.models import Rol

from .factories import PASSWORD_VALIDA, RolFactory, UsuarioFactory


@pytest.fixture
def password():
    return PASSWORD_VALIDA


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
    """Devuelve un cliente autenticado como el usuario dado."""

    def _autenticar(usuario):
        from rest_framework_simplejwt.tokens import RefreshToken

        token = RefreshToken.for_user(usuario).access_token
        api.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        return api

    return _autenticar
