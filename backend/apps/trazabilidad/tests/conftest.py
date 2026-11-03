"""Las pruebas de M06 componen lotes con ingresos de M03: comparten sus fixtures."""

from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from apps.catalogo.tests.factories import TipoMineralFactory
from apps.ingresos.tests.conftest import *  # noqa: F401,F403
from apps.ingresos.tests.factories import IngresoFactory

LOTES = "/api/v1/lotes/"


@pytest.fixture
def otro_mineral(db):
    return TipoMineralFactory(codigo="MOB", nombre="Mineral óxido tipo B")


@pytest.fixture
def nuevo_ingreso(mineral):
    """Ingreso Registrado de 20,20 t netas del mineral del lote."""

    def _crear(**kw):
        kw.setdefault("tipo_mineral", mineral)
        return IngresoFactory(**kw)

    return _crear


@pytest.fixture
def lotes(api_como, administrativo, supervisor, administrador, mineral):
    """Atajos de la API de lotes, con el rol que corresponde a cada operación."""

    class Lotes:
        def __init__(self):
            self.adm = lambda: api_como(administrativo)
            self.sup = lambda: api_como(supervisor)
            self.admin = lambda: api_como(administrador)

        def abrir(self, nombre="Lote 1", tipo=None, api=None):
            r = (api or self.adm()).post(LOTES, {"nombre": nombre, "tipo_mineral": (tipo or mineral).pk,
                                                 "fecha_apertura": timezone.localdate().isoformat()}, format="json")
            assert r.status_code == 201, r.data
            return r.data

        def asignar(self, lote, *ingresos, autorizacion="", api=None):
            return (api or self.adm()).post(f"{LOTES}{lote['id']}/ingresos/",
                                            {"ingresos": [i.pk for i in ingresos], "autorizacion": autorizacion},
                                            format="json")

        def iniciar(self, lote, api=None):
            return (api or self.adm()).patch(f"{LOTES}{lote['id']}/iniciar-recorrido/")

        def etapa(self, lote, api=None, **datos):
            return (api or self.sup()).post(f"{LOTES}{lote['id']}/etapas/", datos, format="json")

        def dividir(self, lote, partes, api=None):
            return (api or self.adm()).post(f"{LOTES}{lote['id']}/division/", {"partes": partes}, format="json")

        def retirar(self, lote, ingreso, api=None):
            return (api or self.adm()).post(f"{LOTES}{lote['id']}/ingresos/{ingreso.pk}/retirar/")

        def detalle(self, lote, api=None):
            return (api or self.sup()).get(f"{LOTES}{lote['id']}/").data

        def en_recorrido(self, *ingresos, nombre="Lote 1"):
            lote = self.abrir(nombre)
            assert self.asignar(lote, *ingresos).status_code == 200
            assert self.iniciar(lote).status_code == 200
            return lote

        def completo(self, *ingresos, ruta="ZARANDEO_ENSACADO", nombre="Lote 1"):
            """Un lote con secado, ruta y todas sus etapas registradas."""
            lote = self.en_recorrido(*ingresos, nombre=nombre)
            assert self.etapa(lote, etapa="SECADO").status_code == 201
            assert self.etapa(lote, ruta=ruta).status_code == 201
            r = None
            while True:
                siguientes = self.detalle(lote)["siguientes"]
                if not siguientes:
                    return lote
                r = self.etapa(lote, etapa=siguientes[0]["etapa"])
                assert r.status_code == 201, r.data

    return Lotes()


@pytest.fixture
def hace(db):
    return lambda **delta: (timezone.now() - timedelta(**delta)).isoformat()


TONELADAS = Decimal("20.20")
