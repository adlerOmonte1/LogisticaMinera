"""Consultas de lectura del catálogo. No escriben (solid-proyecto).

Cada repositorio ofrece dos vistas del mismo dato:
- `vigentes()`  -> lo que se ofrece en los formularios operativos (RN-M02-08).
- `todos()`     -> incluye desactivados, para las consultas históricas.
"""

from apps.catalogo.models import Cliente, Producto, Transportista, Vehiculo


class _RepositorioCatalogo:
    modelo = None

    @classmethod
    def vigentes(cls):
        return cls.modelo.objects.filter(activo=True)

    @classmethod
    def todos(cls):
        return cls.modelo.objects.all()

    @classmethod
    def obtener(cls, pk):
        return cls.modelo.objects.filter(pk=pk).first()


class ProductoRepository(_RepositorioCatalogo):
    modelo = Producto

    @staticmethod
    def existe_codigo(codigo, *, excluir_id=None):
        qs = Producto.objects.filter(codigo=codigo)
        if excluir_id is not None:
            qs = qs.exclude(pk=excluir_id)
        return qs.exists()


class TransportistaRepository(_RepositorioCatalogo):
    modelo = Transportista

    @staticmethod
    def tiene_vehiculos(transportista):
        return transportista.vehiculos.exists()


class ClienteRepository(_RepositorioCatalogo):
    modelo = Cliente


class VehiculoRepository(_RepositorioCatalogo):
    modelo = Vehiculo

    @classmethod
    def vigentes(cls):
        return Vehiculo.objects.select_related("transportista").filter(activo=True)

    @classmethod
    def todos(cls):
        return Vehiculo.objects.select_related("transportista").all()

    @staticmethod
    def existe_placa(placa, *, excluir_id=None):
        qs = Vehiculo.objects.filter(placa=placa)
        if excluir_id is not None:
            qs = qs.exclude(pk=excluir_id)
        return qs.exists()
