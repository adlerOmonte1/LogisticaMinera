"""ServicioAuditoria, el único punto de escritura de los eventos (M09)."""

import pytest

from apps.accounts.tests.factories import UsuarioFactory
from apps.auditoria.models import EventoAuditoria
from apps.auditoria.services import servicio_auditoria
from common.eventos import Accion

pytestmark = pytest.mark.django_db


def test_registra_el_evento_con_su_autor_y_su_momento():
    u = UsuarioFactory()
    evento = servicio_auditoria.registrar(
        accion=Accion.MODIFICAR, entidad="Usuario", id_entidad=u.pk, usuario=u,
        valores_anteriores={"activo": True}, valores_nuevos={"activo": False}, motivo="Prueba",
    )

    guardado = EventoAuditoria.objects.get(pk=evento.pk)
    assert guardado.usuario == u and guardado.fecha_hora is not None
    assert guardado.valores_anteriores == {"activo": True}


def test_ningun_evento_guarda_una_contrasena():
    evento = servicio_auditoria.registrar(
        accion=Accion.MODIFICAR, entidad="Usuario", valores_nuevos={"password": "x", "clave_temporal": "y", "rol": "SUPERVISOR"},
    )

    assert evento.valores_nuevos == {"rol": "SUPERVISOR"}
