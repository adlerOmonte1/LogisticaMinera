# Notas de implementación — M07 Consulta de ingresos y respaldo

## Backend (Django)

**App:** `apps/consulta/` — no existe todavía; se crea en la fase de preparación del backend.

### Estructura

```
apps/consulta/
├── repositories/    buscar_por_placa_fecha, listar_con_filtros, obtener_detalle
├── services/        composicion del detalle a partir de los repositorios de M03 a M06
├── serializers/  views/  permissions.py  filters.py  urls.py  tests/
```

Sin `models/` ni `migrations/` (D-10). M07 no aporta ninguna entidad al modelo de datos: todo lo
que expone pertenece a otro módulo. Crear un `models/` vacío invitaría a que alguien agregara aquí
una entidad que debía discutirse primero en el modelo entidad-relación.

### Repositorio de búsqueda

```python
class RepositorioConsulta:
    def buscar_por_placa_fecha(self, placa: str | None, fecha: date | None,
                                fecha_fin: date | None = None) -> QuerySet[Ingreso]:
        qs = Ingreso.objects.select_related("vehiculo", "tipo_mineral")
        if placa:
            qs = qs.filter(vehiculo__placa__icontains=normalizar_placa(placa))
        if fecha:
            qs = qs.filter(fecha_hora_ticket__date__range=(fecha, fecha_fin or fecha))
        return qs.order_by("-fecha_hora_ticket")
```

Decisiones no obvias:

- **`normalizar_placa()` quita guiones y pasa a mayúsculas antes de comparar** (RNF-M07-06). La
  columna en base conserva el formato tal como lo escribió el usuario; la normalización ocurre solo
  en la consulta, nunca al guardar.
- **La búsqueda nunca se ejecuta sin al menos un criterio** (RN-M07-05): el servicio valida esto
  antes de tocar el repositorio, para no depender de que cada llamador recuerde hacerlo.
- **No se excluyen los ingresos anulados del `QuerySet` base.** RN-M07-01 los exige visibles; la
  exclusión ocurre solo en el cálculo del total (ver más abajo), nunca en el listado.

### Composición del detalle

```python
class ServicioConsulta:
    def __init__(self, ingresos, reconocimientos, validaciones, trazabilidad):
        ...

    def componer_detalle(self, id_ingreso):
        ingreso = self.ingresos.obtener(id_ingreso)
        return DetalleIngreso(
            ingreso=ingreso,
            reconocimiento=self.reconocimientos.obtener_por_ingreso(id_ingreso),
            validaciones=self.validaciones.listar_por_ingreso(id_ingreso),
            trazabilidad=self.trazabilidad.obtener_recorrido(ingreso),
        )
```

Los cuatro repositorios se inyectan: M07 no importa modelos de M04, M05 ni M06 directamente, solo
sus interfaces de lectura. Cada uno puede devolver «sin datos» —un reconocimiento inexistente, un
ingreso sin lote— y el servicio lo traduce en el bloque «ausente» que exige RN-M07-08, nunca en un
bloque omitido.

### El total del conjunto filtrado en una sola consulta agregada

```python
def totales(self, filtros) -> TotalesConjunto:
    return (
        self.buscar_con_filtros(filtros)
        .exclude(estado="ANULADO")
        .aggregate(cantidad=Count("id"), toneladas=Sum("peso_neto_tn"))
    )
```

RNF-M07-03 exige que el listado no dependa del número de resultados: el conteo y la suma se calculan
con `aggregate()` sobre el mismo `QuerySet` filtrado, no recorriendo la página en Python. Es el mismo
principio que aplica el total de un lote en M06.

### La imagen del ticket

`GET /.../ticket/` no sirve el archivo directamente desde una ruta de `MEDIA_URL`: pasa por una vista
que comprueba sesión y permiso antes de leer del almacén (RN-M07-06, RNF-M07-05). Si el almacén no
responde, la vista captura el error y devuelve el indicador de «respaldo no disponible» en lugar de
propagar una excepción (RNF-M07-09): el detalle debe seguir mostrándose sin la imagen.

## Frontend (Angular)

**Feature:** `features/consulta/`

- La búsqueda por placa y fecha está en la pantalla inicial tras iniciar sesión (RNF-M07-07), no
  detrás de un menú: es la operación más frecuente del módulo.
- La miniatura de la lista usa una versión reducida de la imagen; la resolución original se pide
  solo al ampliar (RNF-M07-04), con una petición separada a `.../ticket/`.
- El estado anulado se distingue en la lista con una marca visible, sin depender de abrir el
  detalle (RNF-M07-08).
- El detalle es un componente que compone cuatro bloques independientes (`ui/reconocimiento`,
  `ui/validaciones`, `ui/trazabilidad`, `ui/datos-ticket`), cada uno capaz de mostrar su propio
  estado «sin datos». Ninguno asume que los otros existen.

## Riesgo de implementación identificado

**El riesgo principal es que el total del listado deje de coincidir con el de M08.**

Ambos módulos calculan una suma de toneladas sobre el mismo criterio —ingresos no anulados de un
periodo— pero desde repositorios distintos. Si M07 excluyera los anulados con una condición y M08 con
otra ligeramente diferente (por ejemplo, una que compare contra `"ANULADO"` como texto y otra contra
una constante), los dos totales podrían divergir para el mismo mes sin que ninguna prueba aislada de
un módulo lo detecte, porque cada una prueba solo su propio cálculo.

La prueba que sí lo detecta compara, sobre el mismo conjunto de datos sintéticos, el total que
devuelve el listado de M07 para un mes con el total acumulado que devuelve M08 para ese mismo mes, y
exige que coincidan exactamente.

**Riesgo secundario:** que la búsqueda sin criterios se bloquee solo en el frontend. Si la validación
de RN-M07-05 viviera únicamente en el formulario Angular, una petición directa a la API recorrería el
histórico completo sin límite.

## Dependencias

| Depende de | Para |
|---|---|
| M01 | Autenticación y control de acceso a la imagen |
| M02 | La placa y la titularidad del vehículo, usadas como criterios |
| M03 | Los ingresos y sus imágenes |
| M04 | La comparación entre lo reconocido y lo confirmado |
| M05 | El resultado de las validaciones |
| M06 | El recorrido del proceso |

| Es requerido por | Para |
|---|---|
| — | Ningún módulo depende de M07: es un punto final de lectura |

## Pendientes que afectan a este módulo

| Pendiente | Efecto |
|---|---|
| Medio de almacenamiento de las imágenes (D-14) | Define cómo `ServicioConsulta` accede al respaldo y qué errores debe capturar |
| Volumen esperado de ingresos en producción | Condiciona si la estrategia de paginación e índices de RNF-M07-01 y RNF-M07-03 es suficiente |
