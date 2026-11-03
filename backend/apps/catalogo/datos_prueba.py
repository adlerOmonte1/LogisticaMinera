"""Catálogo provisional del entorno local, tomado de la maqueta (PLAN-02 §4.6).

**Provisional**: los tipos de mineral y las taras reales los entrega la empresa
en la semana 2 (DR-03, ACTA-01 §4.3). Hasta entonces se cargan los de
`Mockup/index.html`, para que la colección de Postman y la interfaz trabajen
sobre los mismos datos. Al recibir los valores reales se reemplaza este archivo;
el código de negocio no cambia.

Cada ejecución devuelve estas filas a su estado inicial —datos, vigencia y
tara—, porque la colección de Postman las consulta. Las entidades que la
colección crea por su cuenta no se tocan.
"""

from decimal import Decimal

from django.utils import timezone

from apps.catalogo.models import TipoMineral, Transportista, Vehiculo

TIPOS_MINERAL = [
    ("MOA", "Mineral óxido Pingüino", True),
    ("MOB", "Mineral óxido tipo B", True),
    ("MOC", "Mineral óxido tipo C", False),
]
TRANSPORTISTAS = [
    ("T1", "Transportes Huallaga", "20604123457"),
    ("T2", "Servicios Mineros Pillco", "20611890231"),
    ("T3", "Logística Andina del Centro", "20487654321"),
]
# placa, titularidad, transportista, capacidad, tara (None: pendiente de destare), activo.
# En la maqueta las taras las registró el Supervisor de planta en el destare.
VEHICULOS = [
    ("V2K-841", Vehiculo.PROPIO, None, "18.00", "11.80", True),
    ("A7M-309", Vehiculo.PROPIO, None, "16.00", "11.20", True),
    ("B5A-812", Vehiculo.EXTERNO, "T1", "20.00", "12.60", True),
    ("C9K-741", Vehiculo.EXTERNO, "T2", "15.00", "12.10", True),
    ("D3P-552", Vehiculo.EXTERNO, "T1", "17.00", "12.30", False),
    ("E4R-208", Vehiculo.PROPIO, None, "17.50", None, True),
    ("F7T-615", Vehiculo.EXTERNO, "T1", "19.00", "12.80", True),
]


def cargar(usuario_destare) -> list[str]:
    """Crea o restablece el catálogo provisional. Lo invoca `cargar_datos_prueba`."""
    lineas = []
    for codigo, nombre, activo in TIPOS_MINERAL:
        TipoMineral.objects.update_or_create(
            codigo=codigo, defaults={"nombre": nombre, "activo": activo}
        )
    lineas.append(f"Tipos de mineral: {len(TIPOS_MINERAL)}")

    por_clave = {}
    for clave, razon_social, ruc in TRANSPORTISTAS:
        por_clave[clave], _ = Transportista.objects.update_or_create(
            ruc=ruc, defaults={"razon_social": razon_social, "activo": True}
        )
    lineas.append(f"Transportistas: {len(TRANSPORTISTAS)}")

    ahora = timezone.now()
    for placa, titularidad, transportista, capacidad, tara, activo in VEHICULOS:
        Vehiculo.objects.update_or_create(
            placa=placa,
            defaults={
                "tipo_titularidad": titularidad,
                "transportista": por_clave.get(transportista),
                "capacidad_tn": Decimal(capacidad),
                "tara_tn": Decimal(tara) if tara else None,
                "fecha_destare": ahora if tara else None,
                "usuario_destare": usuario_destare if tara else None,
                "activo": activo,
            },
        )
    lineas.append(f"Vehículos: {len(VEHICULOS)} (uno pendiente de destare)")
    return lineas
