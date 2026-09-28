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
- **`models/vehiculo.py` conserva `tipo_titularidad` y `capacidad_tn`** y añade `tara_tn`,
  `fecha_destare` y `usuario_destare` (DR-10, D-17), en una migración nueva; cambia el comentario
  que citaba el indicador anterior.
- **`models/transportista.py` sin cambios.**

### Modelo de vehículo

```python
class Vehiculo(models.Model):
    placa = models.CharField(max_length=10, unique=True)
    tipo_titularidad = models.CharField(max_length=10, choices=TITULARIDAD)  # PROPIO / EXTERNO
    capacidad_tn = models.DecimalField(max_digits=6, decimal_places=2)
    tara_tn = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    fecha_destare = models.DateTimeField(null=True, blank=True)
    usuario_destare = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                        on_delete=models.PROTECT, related_name="+")
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
- **`tara_tn` nace nula y no se expone en el serializer de alta ni en el de edición.** La primera
  tara entra solo por `registrar_tara()` del servicio, que invoca el destare de M03 y fija a la vez
  `fecha_destare` y `usuario_destare`. El cambio posterior entra solo por `modificar_tara()`, con
  permiso de Administrador y motivo obligatorio. Si la tara pudiera escribirse por el `PATCH`
  genérico, cualquier edición del vehículo podría cambiar el peso neto de los ingresos siguientes sin
  dejar motivo.
- **El alta desde el registro de ingresos usa el mismo servicio `crear_vehiculo()`.** No existe un
  endpoint abreviado con menos validaciones; la pantalla de M03 llama al mismo recurso.
- **`on_delete=PROTECT` en `transportista`.** Un transportista con vehículos asociados no puede
  eliminarse; solo se desactiva desde el servicio.

## Frontend (Angular)

**Feature:** `features/catalogo/`

- Los formularios de vehículo muestran u ocultan el campo de transportista según la titularidad
  seleccionada, sin recargar la página.
- El selector de tipo de mineral del registro de ingresos consume el endpoint filtrado por vigencia.
  La placa no se elige de una lista: se reconoce del ticket y se busca en el catálogo; si no existe,
  el mismo formulario de vehículo se abre como panel dentro del registro, sin navegar a otra ruta.
- El listado de vehículos distingue los pendientes de destare.
- La tara no aparece en el formulario de edición; el cambio de tara es una acción aparte, visible
  solo para el Administrador, con el motivo como campo obligatorio.

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
| M03 | El vehículo vigente con su titularidad y su tara, el tipo de mineral del ingreso, el alta de un vehículo nuevo y el registro de su primera tara |
| M05 | La tara y la capacidad del vehículo, que contrastan las reglas V2 y V4 |
| M08 | Los tipos de mineral que agrupan el total mensual |

**Riesgo de la tara.** Que la tara termine siendo editable por el mismo camino que la capacidad o la
placa. La prueba que lo detecta envía un `PATCH` genérico con `tara_tn` como Administrativo y espera
que el valor no cambie, y otro como Administrador sin motivo y espera el rechazo.

## Pendientes que afectan a este módulo

| Pendiente | Efecto |
|---|---|
| Valores del catálogo de tipos de mineral, a definir con la empresa (DR-03) | Bloquea la carga inicial de datos, no la estructura del modelo |
| Orden de la fase de limpieza del backend: salidas antes que Cliente | Evita una migración fallida o forzada |
| Carga de la tara de los vehículos que ya operan antes de la puesta en marcha | Sin ella, todos sus primeros ingresos quedarán En proceso hasta un nuevo destare |
