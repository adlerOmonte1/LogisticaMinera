# Notas de implementación — M02 Catálogo maestro

## Backend (Django)

**App:** `apps/catalogo/` — implementada y con pruebas. El retiro de `Cliente` y el cambio de
`Producto` a `TipoMineral` son tareas de la preparación del repositorio y figuran en
`../../01-plan/PLAN_DE_TRABAJO.md` §8. Lo que este módulo exige del modelo, una vez hecha esa
preparación:

- **`TipoMineral`** (DR-03) con `codigo` único de dos a seis caracteres, no editable tras el alta, y
  `nombre` único sin distinguir mayúsculas (RN-M02-15, RN-M02-16). El servicio `crear_tipo_mineral()`
  genera el código cuando no se indica y es el mismo que invoca el registro de M03.
- **`Vehiculo`** conserva `tipo_titularidad` y `capacidad_tn` y añade `tara_tn`, `fecha_destare` y
  `usuario_destare` (DR-10, D-17), en una migración nueva.
- **`Transportista`** con `ruc` único (RN-M02-18).

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

**El riesgo principal es que el alta desde el registro se implemente como un camino abreviado con
menos controles que el catálogo.**

La pantalla de registro necesita dar de alta un vehículo o un tipo de mineral sin salir de ella, y es
tentador resolverlo con un endpoint propio de M03 que cree la entidad con los datos mínimos. Ese
atajo permitiría placas duplicadas, vehículos externos sin transportista o nombres de mineral
repetidos. La defensa es que M03 invoque los mismos servicios `crear_vehiculo()` y
`crear_tipo_mineral()` de M02, y que las pruebas del alta desde el registro reutilicen los casos de
rechazo del alta desde el catálogo.

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
| Valores del catálogo de tipos de mineral, a definir con la empresa (DR-03) | Bloquea la carga inicial de datos, no la estructura del modelo; el alta desde el registro reduce el bloqueo |
| Preparación del repositorio (`PLAN_DE_TRABAJO.md` §8): cambio de `Producto` a `TipoMineral`. El retiro de `Cliente` ya se hizo (migración `0002_retira_cliente`) | El modelo descrito en estas notas supone esa preparación hecha |
| Carga de la tara de los vehículos que ya operan antes de la puesta en marcha | Sin ella, todos sus primeros ingresos quedarán En proceso hasta un nuevo destare |
