"""Contrato HTTP de M02: listados de vigentes, alta, edición, desactivación
y el filtro de titularidad que alimenta el indicador I2."""

import pytest

from apps.catalogo.models import Producto, Vehiculo

from .factories import ProductoFactory, TransportistaFactory, VehiculoFactory

pytestmark = pytest.mark.django_db

PRODUCTOS = "/api/v1/catalogo/productos/"
VEHICULOS = "/api/v1/catalogo/vehiculos/"
TRANSPORTISTAS = "/api/v1/catalogo/transportistas/"


def test_hu_m02_01_ca01_crear_producto_activo(api_como, administrativo):
    r = api_como(administrativo).post(
        PRODUCTOS, {"codigo": "SAR", "nombre": "Saranda", "unidad_medida": "TONELADA"}
    )
    assert r.status_code == 201
    assert r.data["activo"] is True
    assert Producto.objects.get(codigo="SAR").unidad_medida == "TONELADA"


def test_hu_m02_01_ca02_codigo_duplicado(api_como, administrativo):
    ProductoFactory(codigo="SAR")
    r = api_como(administrativo).post(PRODUCTOS, {"codigo": "SAR", "nombre": "x"})
    assert r.status_code == 400
    assert r.data["mensaje"] == "El código de producto ya está registrado"


def test_hu_m02_01_ca04_producto_desactivado_no_aparece_en_el_listado(api_como, administrativo):
    ProductoFactory(codigo="ACT")
    ProductoFactory(codigo="INA", activo=False)
    r = api_como(administrativo).get(PRODUCTOS)
    codigos = [p["codigo"] for p in r.data["results"]]
    assert "ACT" in codigos and "INA" not in codigos


def test_los_desactivados_si_aparecen_con_incluir_inactivos(api_como, administrativo):
    ProductoFactory(codigo="INA", activo=False)
    r = api_como(administrativo).get(PRODUCTOS + "?incluir_inactivos=1")
    assert any(p["codigo"] == "INA" for p in r.data["results"])


def test_hu_m02_02_ca02_placa_duplicada(api_como, administrativo):
    VehiculoFactory(placa="ABC-500")
    r = api_como(administrativo).post(
        VEHICULOS, {"placa": "ABC-500", "tipo_titularidad": "PROPIO", "capacidad_tn": "30.00"}
    )
    assert r.status_code == 400
    assert r.data["mensaje"] == "La placa ya está registrada"


def test_hu_m02_02_ca03_externo_sin_transportista(api_como, administrativo):
    r = api_como(administrativo).post(
        VEHICULOS, {"placa": "EXT-501", "tipo_titularidad": "EXTERNO", "capacidad_tn": "30.00"}
    )
    assert r.status_code == 400
    assert r.data["mensaje"] == "Debe indicar el transportista para un vehículo externo"


def test_hu_m02_02_ca05_placa_con_formato_invalido(api_como, administrativo):
    r = api_como(administrativo).post(
        VEHICULOS, {"placa": "1234", "tipo_titularidad": "PROPIO", "capacidad_tn": "30.00"}
    )
    assert r.status_code == 400
    assert r.data["mensaje"] == "El formato de la placa no es válido"


def test_hu_m02_02_ca01_alta_de_vehiculo_propio(api_como, administrativo):
    r = api_como(administrativo).post(
        VEHICULOS, {"placa": "PRO-777", "tipo_titularidad": "PROPIO", "capacidad_tn": "32.50"}
    )
    assert r.status_code == 201
    assert r.data["titularidad"] == "PROPIO"
    assert r.data["transportista"] is None


def test_filtro_titularidad_alimenta_el_indicador_i2(api_como, administrativo):
    t = TransportistaFactory()
    VehiculoFactory(placa="PRO-001", tipo_titularidad=Vehiculo.PROPIO)
    VehiculoFactory(placa="PRO-002", tipo_titularidad=Vehiculo.PROPIO)
    VehiculoFactory(placa="EXT-001", tipo_titularidad=Vehiculo.EXTERNO, transportista=t)

    r = api_como(administrativo).get(VEHICULOS + "?titularidad=PROPIO")
    assert r.data["count"] == 2
    assert all(v["titularidad"] == "PROPIO" for v in r.data["results"])


def test_hu_m02_03_ca03_desactivar_transportista_con_vehiculos(api_como, administrador):
    t = TransportistaFactory()
    VehiculoFactory(placa="EXT-900", tipo_titularidad=Vehiculo.EXTERNO, transportista=t)
    r = api_como(administrador).patch(f"{TRANSPORTISTAS}{t.pk}/desactivar/")
    assert r.status_code == 200
    assert r.data["mensaje"] == "El transportista se desactivó porque tiene vehículos asociados"
    t.refresh_from_db()
    assert t.activo is False


def test_no_existe_borrado_fisico(api_como, administrador):
    p = ProductoFactory()
    r = api_como(administrador).delete(f"{PRODUCTOS}{p.pk}/")
    assert r.status_code == 405
    assert Producto.objects.filter(pk=p.pk).exists()


CLIENTES = "/api/v1/catalogo/clientes/"


def test_hu_m02_01_editar_nombre_de_producto(api_como, administrativo):
    p = ProductoFactory(codigo="ED", nombre="Viejo")
    r = api_como(administrativo).patch(f"{PRODUCTOS}{p.pk}/", {"nombre": "Nuevo"})
    assert r.status_code == 200
    p.refresh_from_db()
    assert p.nombre == "Nuevo"


def test_hu_m02_02_editar_vehiculo_de_propio_a_externo(api_como, administrativo):
    t = TransportistaFactory()
    v = VehiculoFactory(placa="CAM-010", tipo_titularidad=Vehiculo.PROPIO)
    r = api_como(administrativo).patch(
        f"{VEHICULOS}{v.pk}/", {"tipo_titularidad": "EXTERNO", "transportista": t.pk}
    )
    assert r.status_code == 200
    v.refresh_from_db()
    assert v.tipo_titularidad == "EXTERNO" and v.transportista_id == t.pk


def test_hu_m02_03_ca01_crear_transportista(api_como, administrativo):
    r = api_como(administrativo).post(
        TRANSPORTISTAS, {"razon_social": "Transportes Andinos SAC", "ruc": "20123456789"}
    )
    assert r.status_code == 201
    assert r.data["activo"] is True


def test_hu_m02_03_ca02_ruc_invalido(api_como, administrativo):
    r = api_como(administrativo).post(TRANSPORTISTAS, {"razon_social": "X", "ruc": "123"})
    assert r.status_code == 400
    assert r.data["mensaje"] == "El RUC debe tener once dígitos"


def test_hu_m02_04_ca01_crear_cliente(api_como, administrativo):
    r = api_como(administrativo).post(
        CLIENTES, {"razon_social": "Minera Sur SAC", "ruc": "20999888777"}
    )
    assert r.status_code == 201


def test_hu_m02_04_ca02_desactivar_cliente_es_baja_logica(api_como, administrador):
    from apps.catalogo.models import Cliente

    from .factories import ClienteFactory

    c = ClienteFactory()
    r = api_como(administrador).patch(f"{CLIENTES}{c.pk}/desactivar/")
    assert r.status_code == 200
    c.refresh_from_db()
    assert c.activo is False and Cliente.objects.filter(pk=c.pk).exists()
