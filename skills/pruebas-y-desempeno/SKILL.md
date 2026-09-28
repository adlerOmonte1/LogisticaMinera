---
name: pruebas-y-desempeno
description: Escribe las pruebas del sistema web inteligente de ingreso de mineral — pruebas unitarias y de integración con pytest-django derivadas de los criterios de aceptación, el conjunto de prueba de reconocimiento (ERA) y validación (TDI), y el protocolo de rendimiento en preproducción. Úsala al escribir o revisar pruebas, al preparar el plan de pruebas o el acta, y cuando se mencionen tests, cobertura, casos de prueba CP, rendimiento o el conjunto de tickets de prueba.
---

# Pruebas y desempeño

Carga antes `contexto-tesis`. Fuente: los `no_funcionales.md` de cada módulo y
`docs/03-pruebas/plan_de_pruebas.md`.

Las pruebas de este proyecto protegen el código y, además, son el mecanismo con el que se ejecutan
los diez casos de la lista de control y el conjunto de prueba de la capacidad inteligente
(`plan_de_pruebas.md`), entregables de la semana de estabilización.

## Herramientas fijadas

`pytest` + `pytest-django` + `coverage.py` para funcionales. La herramienta de prueba de rendimiento
en preproducción se define al llegar a esa fase (`plan_de_pruebas.md` §1); no es una herramienta
específica de la investigación, sino evidencia técnica de los RNF de tiempo de respuesta.

## Cada criterio de aceptación es un caso de prueba

Nomenclatura: `CP-HU-M{nn}-{nn}-{nn}`, uno por criterio. La cadena de trazabilidad completa es:

```
RF -> Módulo -> HU -> Caso de prueba -> Commit
```

Estructura de una prueba, espejo del criterio:

```python
def test_ca02_tara_mayor_o_igual_que_bruto_es_rechazada(...):
    # Dado que la tara del vehiculo es mayor o igual que el peso bruto (V2)
    # cuando el usuario intenta confirmar
    # entonces el sistema rechaza mostrando "La tara no puede ser mayor o igual que el peso bruto"
```

**El mensaje se verifica por igualdad exacta**, no con `in` ni con una expresión regular laxa. Los
criterios de aceptación fijan el texto literal precisamente para que la prueba pueda compararlo así.
Si una prueba falla porque el texto cambió, la respuesta correcta es revisar cuál de los dos está
mal —historia o código—, nunca relajar la comparación.

## Qué se prueba en cada capa

| Capa | Qué se prueba | Con qué |
|---|---|---|
| `models/` | Cada RN del módulo, incluidos los límites | Pruebas unitarias, sin base cuando se pueda |
| `services/` de M03 | El caso de uso completo, con sus dependencias sustituidas | `ReconocedorTicket`, `ValidadorConsistencia`, generador de código y reloj deterministas |
| `reglas/` de M05 | Cada regla V1 a V5, aislada | Datos de entrada concretos, sin base de datos ni petición HTTP |
| `repositories/` de M07 y M08 | Búsquedas, filtros y totales agregados | Datos de prueba con fechas y periodos explícitos, `assertNumQueries` |
| `views/` | Códigos HTTP, cuerpo de error uniforme, permisos por rol | Cliente de API |
| Angular | Captura de imagen, pantalla de confirmación, validaciones de formulario, borrador local | Pruebas de componente |

La inyección de dependencias que exige `solid-proyecto` existe para esto: un servicio que llama a
`timezone.now()` internamente **no se puede probar** controlando el instante exacto de las tres
marcas de tiempo del ingreso. Inyecta el reloj, el generador de código, el reconocedor y el
validador.

## Pruebas obligatorias por su consecuencia sobre el sistema

Estas no son opcionales aunque el tiempo apriete; cada una protege una garantía del dominio,
verificable por observación directa aunque no aparezca aquí como indicador de la tesis:

| Prueba | Protege |
|---|---|
| `fecha_hora_pesaje`, `hora_inicio_registro` y `hora_fin_registro` se persisten como tres valores distintos, y los dos últimos no se pueden editar | Integridad del registro |
| Un valor propuesto por el reconocimiento no se persiste hasta la confirmación del usuario | D-13 |
| `valor_reconocido` y `valor_confirmado` se guardan en columnas separadas, no se sobrescriben | Evidencia de si el reconocimiento funciona |
| El peso neto lo calcula el servidor como bruto menos la tara aplicada, se ignora si llega en la petición, y no cambia al modificar después la tara del vehículo | RN-M03-04, RN-M02-13 |
| Un ingreso de un vehículo sin tara queda En proceso, sin neto, y el destare lo pasa a Registrado | RN-M03-17 a RN-M03-20 |
| Dos confirmaciones simultáneas no producen el mismo código | Identidad única del ingreso |
| Las cinco reglas V1 a V5 se evalúan siempre, aunque la primera ya haya fallado | RN-M05-04 |
| Una petición directa a la API, sin pasar por el formulario, es rechazada igual que una del formulario | D-08 |
| El total mensual considera solo los ingresos Registrados —excluye anulados y En proceso— y coincide entre la consulta y la exportación | RN-M08-01, RN-M08-05 |
| El registro de una etapa fuera de orden es rechazado | RN-M06-06 |
| Cada operación restringida rechaza al rol no autorizado desde el servidor, y queda registrada en auditoría | D-08, RN-M09-04 |

## Conjunto de prueba de reconocimiento y validación (ERA, TDI)

No son pruebas unitarias: son un protocolo sobre un conjunto fijo de tickets reales, descrito en
`docs/03-pruebas/plan_de_pruebas.md` §4.

- **ERA** se mide comparando, campo por campo, el valor reconocido contra el valor real de los tres
  campos que imprime el ticket —placa, fecha y peso bruto— en 50 tickets (150 lecturas), con el motor y su versión congelados durante toda la medición (D-16).
- **TDI** se mide sembrando 10 inconsistencias —2 por cada regla V1 a V5— y verificando cuántas
  detecta el sistema con la regla correcta.

Estas dos mediciones se ejecutan **una vez que el motor y las reglas están congelados**. Si el motor
cambia a mitad de la medición, ERA queda comparando dos sistemas distintos y el resultado no es
válido. Escribe la prueba automatizada que verifica el congelamiento: el `motor` y `version_motor`
de todos los reconocimientos del periodo deben ser idénticos.

## Cobertura

`coverage.py` sobre `models/`, `services/` y `reglas/` en primer lugar: son las capas donde viven las
reglas. Una cobertura alta en `serializers/` y baja en `models/` o en `reglas/` es una cobertura
engañosa. El dato que importa para el avance del proyecto es el **porcentaje de requerimientos
funcionales cumplidos** (RFC), que se calcula sobre los RF verificados por el caso de prueba
correspondiente (`CPnn`), no sobre las líneas ejecutadas.

## Protocolo de rendimiento (semana de estabilización)

Se ejecuta en **preproducción**, no en producción: producción es donde se recolecta el postest de la
investigación y una prueba de rendimiento alteraría las condiciones de observación.

| RNF típico | Umbral | Condición de medición |
|---|---|---|
| Reconocimiento de un ticket | < 5 s | Imagen de hasta 5 MB |
| Registro de un ingreso | < 2 s | 20 usuarios concurrentes |
| Consulta por placa y fecha | < 2 s | 5000 ingresos en base |
| Consolidado mensual | < 3 s | 5000 ingresos en base |

**Todo umbral se mide con su carga declarada.** Un tiempo de respuesta sin volumen de datos ni
concurrencia declarados no es evidencia de nada. Los datos sintéticos deben reproducir la
distribución real: ingresos concentrados en las horas de llegada de volquetes, no repartidos de
forma uniforme.

Registra: herramienta y versión, hardware, volumen de datos, número de usuarios virtuales, duración,
y percentiles p50/p95/p99 — no solo la media, que oculta las colas.

## Verificaciones que no son automatizables

Algunos RNF se verifican por observación y hay que planificarlas, no improvisarlas:

- Registro completo desde un teléfono, en vertical, con una sola mano: inspección en dispositivo
  real.
- Los datos del formulario **no se pierden** al caerse la conexión durante el registro: activar modo
  avión a media captura y verificar que el borrador persiste (RNF-M03-05).
- Las seis tareas de usabilidad (T01 a T06) completadas sin asistencia: observación cronometrada con
  usuarios reales, según el protocolo de `plan_de_pruebas.md` §5.

## Verificación

- [ ] Cada criterio de aceptación tiene su `CP-HU-*` correspondiente.
- [ ] Los mensajes se comparan por igualdad exacta.
- [ ] Las diez pruebas obligatorias de la tabla existen y pasan.
- [ ] El conjunto de ERA y TDI está definido, con el motor y las reglas congelados durante la medición.
- [ ] Las pruebas de rendimiento corren en preproducción y quedan registradas con su condición de medición.
- [ ] Las verificaciones manuales están planificadas con fecha, no pendientes de improvisación.
