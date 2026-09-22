# Historias de usuario — índice

**Versión:** 2.0 · **Total: 21 historias en 9 módulos**

Este archivo es un **índice**. El detalle de cada historia —descripción, campos y criterios de
aceptación— vive únicamente en el `HU.md` de su módulo; aquí solo constan el identificador, el
título, el rol y la prioridad. Así no hay dos versiones de la misma historia.

Para saber qué requerimiento, indicador o tarea sostiene cada historia, consulta
[la matriz de trazabilidad](02-trazabilidad/matriz_HU_RF_indicador.md).

**Criterio de granularidad.** Una historia cubre una capacidad completa, no una operación suelta: el
mantenimiento de una entidad de catálogo es una sola historia, con un criterio de aceptación por
operación. Se reserva historia propia para lo que tiene lógica dedicada.

---

## M01 — Autenticación y roles

*Detalle en [`modulos/M01-autenticacion/HU.md`](modulos/M01-autenticacion/HU.md)*

| HU | Título | Rol | Prioridad |
|---|---|---|---|
| HU-M01-01 | Inicio y cierre de sesión | Todos | Crítica |
| HU-M01-02 | Gestión de usuarios | Administrador | Alta |
| HU-M01-03 | Control de acceso por rol | Administrador | Crítica |

## M02 — Catálogo maestro

*Detalle en [`modulos/M02-catalogo/HU.md`](modulos/M02-catalogo/HU.md)*

| HU | Título | Rol | Prioridad |
|---|---|---|---|
| HU-M02-01 | Gestión del catálogo de vehículos | Administrativo | Crítica |
| HU-M02-02 | Gestión del catálogo de tipos de mineral | Administrativo | Crítica |
| HU-M02-03 | Gestión de transportistas | Administrativo | Media |

## M03 — Registro de ingresos

*Detalle en [`modulos/M03-ingresos/HU.md`](modulos/M03-ingresos/HU.md)*

| HU | Título | Rol | Prioridad |
|---|---|---|---|
| HU-M03-01 | Registro de un ingreso a partir del ticket de balanza | Supervisor de planta | Crítica |
| HU-M03-02 | Corrección de un ingreso registrado | Administrativo | Alta |
| HU-M03-03 | Anulación de un ingreso | Administrador | Alta |

## M04 — Reconocimiento automático del ticket

*Detalle en `modulos/M04-reconocimiento/HU.md`* — pendiente, fase 6

| HU | Título | Rol | Prioridad |
|---|---|---|---|
| HU-M04-01 | Reconocimiento automático de los datos del ticket | Supervisor de planta | Crítica |
| HU-M04-02 | Consulta del dato reconocido frente al confirmado | Administrativo | Media |

## M05 — Validación automática de consistencia

*Detalle en `modulos/M05-validacion/HU.md`* — pendiente, fase 6

| HU | Título | Rol | Prioridad |
|---|---|---|---|
| HU-M05-01 | Detección y resolución de inconsistencias del ticket | Supervisor de planta | Crítica |

## M06 — Trazabilidad del proceso

*Detalle en `modulos/M06-trazabilidad/HU.md`* — pendiente, fase 6

| HU | Título | Rol | Prioridad |
|---|---|---|---|
| HU-M06-01 | Gestión de lotes de proceso | Administrativo | Alta |
| HU-M06-02 | Registro del paso de un lote por una etapa | Supervisor de planta | Crítica |
| HU-M06-03 | Consulta de la trazabilidad de un ingreso | Administrativo | Media |

## M07 — Consulta de ingresos y respaldo

*Detalle en `modulos/M07-consulta/HU.md`* — pendiente, fase 7

| HU | Título | Rol | Prioridad |
|---|---|---|---|
| HU-M07-01 | Consulta de un ingreso por placa y fecha con su respaldo | Administrativo | Crítica |
| HU-M07-02 | Listado y detalle de ingresos | Administrativo | Alta |

## M08 — Consolidación de la producción

*Detalle en `modulos/M08-consolidacion/HU.md`* — pendiente, fase 7

| HU | Título | Rol | Prioridad |
|---|---|---|---|
| HU-M08-01 | Total acumulado mensual por tipo de mineral | Administrativo | Crítica |
| HU-M08-02 | Exportación del total acumulado mensual | Administrativo | Alta |

## M09 — Auditoría

*Detalle en `modulos/M09-auditoria/HU.md`* — pendiente, fase 7

| HU | Título | Rol | Prioridad |
|---|---|---|---|
| HU-M09-01 | Registro de eventos del sistema | — (automático) | Alta |
| HU-M09-02 | Consulta del historial de un registro | Administrador | Media |

---

## Cómo se mantiene este índice

Al crear o modificar una historia en el `HU.md` de un módulo, se actualiza aquí la fila
correspondiente y la de la matriz de trazabilidad. La numeración es estable: una historia retirada
no libera su número.

La comprobación de que ninguna historia figura en un sitio y falta en el otro la realiza la skill
`revision-coherencia`.
