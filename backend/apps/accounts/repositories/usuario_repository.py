"""Consultas de lectura sobre `Usuario`. No escribe (solid-proyecto: "Lectura
y escritura separadas").
"""

from apps.accounts.models import Usuario


class UsuarioRepository:
    @staticmethod
    def listar_activos():
        return Usuario.objects.select_related("rol").filter(is_active=True)

    @staticmethod
    def obtener_por_id(usuario_id):
        return Usuario.objects.select_related("rol").filter(pk=usuario_id).first()

    @staticmethod
    def obtener_por_username(username):
        return Usuario.objects.select_related("rol").filter(username=username).first()

    @staticmethod
    def existe_username(username, *, excluir_id=None):
        qs = Usuario.objects.filter(username=username)
        if excluir_id is not None:
            qs = qs.exclude(pk=excluir_id)
        return qs.exists()
