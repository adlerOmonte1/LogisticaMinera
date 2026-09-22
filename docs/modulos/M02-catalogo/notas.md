# Notas de implementación — M02 Catálogo maestro

## Backend (Django)

**App:** `apps/catalogo/` — implementada y con pruebas. Ajustes pendientes de esta reformulación,
sin recrear la app:

- **Retirar `models/cliente.py`, su serializer, su servicio, su vista, sus rutas, su factory y sus
  pruebas.** `CLIENTE` pertenecía al alcance de salidas y ventas, retirado por la reformulación.
  Requiere una migración nueva que elimine la tabla; no se edita `0001_initial`.
- **Renombrar `models/producto.py` a `models/tipo_mineral.py`** (DR-03): mismo mecanismo, catálogo
  único usado al registrar el ingreso y al consolidar. El campo `nombre` pasa de valores fijos
  (Saranda, Molido) a los que defina la empresa.
- **`models/vehiculo.py` conserva `tipo_titularidad` y `capacidad_tn`** sin cambios de estructura;
  cambia el comentario que citaba el indicador anterior.
- **`models/transportista.py` sin cambios.**

### Modelo de vehículo

```python
class Vehiculo(models.Model):
    placa = models.CharField(max_length=10, unique=True)
    tipo_titularidad = models.CharField(max_length=10, choices=TITULARIDAD)  # PROPIO / EXTERNO
    capacidad_tn = models.DecimalField(max_digits=6, decimal_places=2)
    transportista = models.ForeignKey(Transportista, null=True, blank=True,
                                      on_delete=models.PROTECT)
    activo = models.BooleanField(default=True)
```

Decisiones no obvias:

- **`capacidad_tn` no es un dato decorativo.** Es el valor que la regla V4 de M05 lee para decidir
  si un peso neto está fuera de rango. Un vehículo con capacidad mal cargada —cero, o una unidad
  distinta de toneladas— produciría falsos positivos o falsos negativos en esa regla sin que M02
  tenga forma de saberlo: la responsabilidad de que el dato sea correcto es de quien lo registra
  aquí, no de quien lo consume en M05.
- **`transportista` admite nulo solo cuando `tipo_titularidad` es `PROPIO`.** La invariante se
  aplica en `clean()` del modelo, no únicamente en el serializer, para que también la respete
  cualquier carga por script o por el admin.
- **`on_delete=PROTECT` en `transportista`.** Un transportista con vehículos asociados no puede
  eliminarse; solo se desactiva desde el servicio.

## Frontend (Angular)

**Feature:** `features/catalogo/`

- Los formularios de vehículo muestran u ocultan el campo de transportista según la titularidad
  seleccionada, sin recargar la página.
- Los selectores de placa y tipo de mineral en el formulario de registro de ingresos consumen estos
  mismos endpoints filtrados por vigencia; no hay una copia local del catálogo.

## Riesgo de implementación identificado

**El riesgo principal es que la migración que retira `Cliente` arrastre datos que otro módulo
todavía referencia.**

Si `apps/salidas` no se hubiera retirado antes de esta migración, `Cliente` tendría una clave
foránea activa desde `Salida` y la migración fallaría o, peor, se forzaría con `CASCADE` sin que
nadie lo advirtiera. Por eso el orden de la fase de limpieza del backend importa: primero se retira
`apps/salidas` por completo, y solo entonces se elimina `Cliente` de `apps/catalogo`.

**Riesgo secundario:** renombrar `Producto` a `TipoMineral` sin renombrar también sus referencias en
`apps/ingresos` (el campo `producto` de `Ingreso`) dejaría el código en un estado mixto donde el
modelo se llama de una forma y las variables de otra, lo que dificulta encontrar todas las
referencias en una búsqueda posterior.

## Dependencias

| Es requerido por | Para |
|---|---|
| M03 | El vehículo vigente, su titularidad y el tipo de mineral del ingreso |
| M05 | La capacidad del vehículo, que contrasta la regla V4 |
| M08 | Los tipos de mineral que agrupan el total mensual |

## Pendientes que afectan a este módulo

| Pendiente | Efecto |
|---|---|
| Valores del catálogo de tipos de mineral, a definir con la empresa (DR-03) | Bloquea la carga inicial de datos, no la estructura del modelo |
| Orden de la fase de limpieza del backend: salidas antes que Cliente | Evita una migración fallida o forzada |
