# Matriz de trazabilidad — HU · RF · indicador · tarea · caso de prueba

**Versión:** 1.0 · **Estado:** Aprobado
**Deriva de:** `../00-tesis/marco_tesis.md` y `../model-c4/ARQ-01_Modulos_del_Sistema.md`

Este es el **único documento del repositorio donde el sistema se relaciona con los indicadores de la
tesis**. Los archivos de `docs/modulos/` describen el sistema y no citan indicadores: si necesitas
saber qué medición sostiene una historia, se consulta aquí.

Se lee en ambas direcciones: de una historia hacia lo que justifica su existencia, y de un
requerimiento o un indicador hacia las historias que lo realizan.

---

## 1. Criterio de granularidad

Una historia cubre **una capacidad completa**, no una operación suelta. El mantenimiento de una
entidad de catálogo —alta, edición, listado y baja lógica— es una sola historia con un criterio de
aceptación por operación. Se reserva historia propia para lo que tiene lógica dedicada: el
reconocimiento, la validación, la anulación con motivo, la exportación.

Por eso el backlog tiene **21 historias** y no las 34 del sistema anterior, pese a cubrir más
funcionalidad.

## 2. Matriz

| HU | Título | Rol principal | Prioridad | RF | Indicador | Tarea | Caso de prueba |
|---|---|---|---|---|---|---|---|
| **M01 — Autenticación y roles** |
| HU-M01-01 | Inicio y cierre de sesión | Todos | Crítica | RF10 | — | — | CP10 |
| HU-M01-02 | Gestión de usuarios | Administrador | Alta | RF10 | — | — | CP10 |
| HU-M01-03 | Control de acceso por rol | Administrador | Crítica | RF10 | — | — | CP10 |
| **M02 — Catálogo maestro** |
| HU-M02-01 | Gestión del catálogo de vehículos | Administrativo | Crítica | RF06 | I3 (C7), TDI (V4) | — | CP06 |
| HU-M02-02 | Gestión del catálogo de tipos de mineral | Administrativo | Crítica | RF06 | I3 (C6), I5 | — | CP06 |
| HU-M02-03 | Gestión de transportistas | Administrativo | Media | RF06 | — | — | CP06 |
| **M03 — Registro de ingresos** |
| HU-M03-01 | Registro de un ingreso a partir del ticket de balanza | Supervisor de planta | Crítica | RF01, RF04, RF05, RF06 | I1, I2, I3 | T01, T02 | CP01, CP05 |
| HU-M03-02 | Corrección de un ingreso registrado | Administrativo | Alta | RF04 | I3 | T02 | CP04 |
| HU-M03-03 | Anulación de un ingreso | Administrador | Alta | — | — | — | CP04 |
| **M04 — Reconocimiento automático del ticket** |
| HU-M04-01 | Reconocimiento automático de los datos del ticket | Supervisor de planta | Crítica | RF02 | ERA | T01 | CP02 |
| HU-M04-02 | Consulta del dato reconocido frente al confirmado | Administrativo | Media | RF02 | ERA | — | CP02 |
| **M05 — Validación automática de consistencia** |
| HU-M05-01 | Detección y resolución de inconsistencias del ticket | Supervisor de planta | Crítica | RF03 | TDI | T02 | CP03 |
| **M06 — Trazabilidad del proceso** |
| HU-M06-01 | Gestión de lotes de proceso | Administrativo | Alta | RF07 | I6 | — | CP07 |
| HU-M06-02 | Registro del paso de un lote por una etapa | Supervisor de planta | Crítica | RF07 | I6 | T04 | CP07 |
| HU-M06-03 | Consulta de la trazabilidad de un ingreso | Administrativo | Media | RF07 | I6 | T04 | CP07 |
| **M07 — Consulta de ingresos y respaldo** |
| HU-M07-01 | Consulta de un ingreso por placa y fecha con su respaldo | Administrativo | Crítica | RF08 | I4 | T03 | CP08 |
| HU-M07-02 | Listado y detalle de ingresos | Administrativo | Alta | RF08 | I4 | T03 | CP08 |
| **M08 — Consolidación de la producción** |
| HU-M08-01 | Total acumulado mensual por tipo de mineral | Administrativo | Crítica | RF09 | I5 | T05 | CP09 |
| HU-M08-02 | Exportación del total acumulado mensual | Administrativo | Alta | RF09 | I5 | T06 | CP09 |
| **M09 — Auditoría** |
| HU-M09-01 | Registro de eventos del sistema | — (automático) | Alta | — | — | — | — |
| HU-M09-02 | Consulta del historial de un registro | Administrador | Media | — | — | — | — |

**Total: 21 historias.**

## 3. Comprobación: cada RF tiene al menos una historia

| RF | Descripción abreviada | Historias que lo realizan | Módulo principal |
|---|---|---|---|
| RF01 | Registrar el ingreso con la imagen del ticket | HU-M03-01 | M03 |
| RF02 | Reconocer automáticamente los datos del ticket | HU-M04-01, HU-M04-02 | M04 |
| RF03 | Validar la consistencia de los datos | HU-M05-01 | M05 |
| RF04 | Registro y corrección manual de los datos reconocidos | HU-M03-01, HU-M03-02 | M03 |
| RF05 | Asignar un código único a cada ingreso | HU-M03-01 | M03 |
| RF06 | Registrar el tipo de mineral y el tipo de vehículo | HU-M03-01, HU-M02-01, HU-M02-02 | M03, M02 |
| RF07 | Vincular cada ingreso con las etapas del proceso | HU-M06-01, HU-M06-02, HU-M06-03 | M06 |
| RF08 | Consultar un ingreso por placa y fecha con su respaldo | HU-M07-01, HU-M07-02 | M07 |
| RF09 | Generar y exportar el total acumulado mensual | HU-M08-01, HU-M08-02 | M08 |
| RF10 | Gestionar usuarios y roles de acceso | HU-M01-01, HU-M01-02, HU-M01-03 | M01 |

**Resultado: los diez RF están cubiertos.** Ninguna historia queda sin RF salvo HU-M03-03
(anulación) y las dos de M09, que sostienen la integridad del histórico y no pertenecen a la lista
de control: no suman ni restan en el avance.

## 4. Comprobación: cada tarea tiene al menos una historia

| Tarea | Descripción | Historias que la permiten |
|---|---|---|
| T01 | Registrar un ingreso a partir de la imagen del ticket | HU-M03-01, HU-M04-01 |
| T02 | Corregir un dato reconocido de forma incorrecta | HU-M03-01, HU-M03-02, HU-M05-01 |
| T03 | Consultar un ingreso por placa y fecha | HU-M07-01, HU-M07-02 |
| T04 | Vincular un ingreso con una etapa del proceso | HU-M06-02, HU-M06-03 |
| T05 | Obtener el total acumulado mensual por producto | HU-M08-01 |
| T06 | Exportar el total acumulado mensual por producto | HU-M08-02 |

**Resultado: las seis tareas están cubiertas.** T06 dejó de estar huérfana al incorporarse la
exportación a RF09 (DR-06); si esa decisión se revirtiera, HU-M08-02 quedaría sin requerimiento que
la respalde y la tarea debería cambiarse en el instrumento.

## 5. Comprobación: cada indicador tiene quién lo sostenga

| Indicador | Qué lo hace posible en el sistema |
|---|---|
| I1 Tiempo de espera del registro | HU-M03-01: fecha y hora del ticket e inicio del registro como valores distintos |
| I2 Tiempo de registro del ingreso | HU-M03-01: inicio y fin del registro asignados por el servidor |
| I3 Completitud del registro | HU-M03-01 exige los siete campos; HU-M02-01 y HU-M02-02 aportan C6 y C7 desde el catálogo |
| I4 Tiempo de recuperación del respaldo | HU-M07-01 y HU-M07-02: consulta por placa y fecha con la imagen del ticket |
| I5 Tiempo de consolidación | HU-M08-01: total del mes por tipo de mineral, a demanda |
| I6 Grado de trazabilidad | HU-M06-01 a HU-M06-03: lote, paso por etapa y consulta |
| ERA Exactitud del reconocimiento | HU-M04-01 y HU-M04-02: valor reconocido y confirmado guardados por separado |
| TDI Detección de inconsistencias | HU-M05-01: las cinco reglas V1 a V5 y el registro de su resultado |
| RFC Requerimientos cumplidos | Sección 3: los diez RF con sus historias |
| CPS Casos de prueba superados | CP01 a CP10, uno por RF, en `../03-pruebas/plan_de_pruebas.md` |
| SUS Puntaje de usabilidad | El sistema completo; no exige una historia concreta |
| TCA Tareas completadas sin asistencia | Sección 4: las seis tareas con sus historias |

## 6. Casos de prueba de la lista de control

Un caso por RF, para el indicador CPS. Los casos por criterio de aceptación llevan el formato
`CP-HU-M03-01-01` y viven en el plan de pruebas, no aquí.

| Caso | Verifica | RF |
|---|---|---|
| CP01 | Registro de un ingreso con imagen del ticket | RF01 |
| CP02 | Reconocimiento de los seis campos con su confianza | RF02 |
| CP03 | Detección de las cinco inconsistencias | RF03 |
| CP04 | Corrección manual de un dato reconocido | RF04 |
| CP05 | Asignación del código único, sin duplicados | RF05 |
| CP06 | Registro del tipo de mineral y del tipo de vehículo | RF06 |
| CP07 | Vínculo del ingreso con las cuatro etapas | RF07 |
| CP08 | Consulta por placa y fecha con presentación del ticket | RF08 |
| CP09 | Total acumulado mensual y su exportación | RF09 |
| CP10 | Gestión de usuarios y restricción por rol | RF10 |

## 7. Historias del sistema anterior

De las 34 historias del backlog anterior, 13 se retiraron con sus módulos (salidas, inventario de
producto terminado y captura sin señal de red) y el resto se consolidó aplicando el criterio de la
sección 1. Los casos más visibles:

Los identificadores del backlog anterior **no se citan aquí**: varios de esos códigos están hoy
asignados a historias distintas, y repetirlos haría ambiguo el documento. La correspondencia se
expresa por título.

| Historia del sistema anterior | Qué ocurrió con ella |
|---|---|
| Las cuatro de catálogo, una por operación | Se consolidan en HU-M02-01 a HU-M02-03, una por entidad |
| «Cálculo automático del peso neto» | Deja de existir: el neto se lee del ticket y lo contrasta la regla V1 (HU-M05-01) |
| «Asignación de correlativo», redactada desde el punto de vista del investigador | Pasa a ser un criterio de aceptación de HU-M03-01 |
| «Listado de ingresos» y «Detalle de un ingreso» | Se unifican en HU-M07-02, en el módulo responsable de la consulta |
| «Declaración semestral» | Retirada: fuera de alcance |
| «Gestión de clientes» | Retirada: solo servía a las salidas |
| Las de salidas, inventario de producto terminado y captura sin señal de red | Retiradas con sus módulos |

## 8. Referencias

- Marco de la tesis: `../00-tesis/marco_tesis.md`
- Módulos y responsabilidades: `../model-c4/ARQ-01_Modulos_del_Sistema.md`
- Índice de historias: `../HistoriasUsuario.md`
- Detalle de cada historia: `../modulos/M{nn}-{slug}/HU.md`
- Plan de pruebas: `../03-pruebas/plan_de_pruebas.md` *(pendiente, fase 9)*
