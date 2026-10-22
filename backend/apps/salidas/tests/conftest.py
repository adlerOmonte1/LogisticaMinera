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
