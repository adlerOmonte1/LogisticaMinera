# Backlog del producto

| Campo | Valor |
|---|---|
| Proyecto | Sistema web inteligente para el control de inventarios de ingreso de mineral — Construcción y Minería, planta de Pillcomarca, Huánuco |
| Productos | **Backend**: API REST Django 5 + DRF sobre PostgreSQL 16 (repositorio `LogisticaMinera`). **Frontend**: aplicación Angular 17 con PWA (repositorio `LogisticaMineraFront`) |
| Periodo | Del 04/09/2026, primer commit, al 22/01/2027, puesta en marcha propuesta |
| Corte de estado | 02/11/2026 |
| Elementos | 132: 27 historias de usuario y 105 elementos técnicos, de documentación, de investigación, externos y defectos |
| Tamaño | 578 puntos; terminados 200 (35 %) |
| Fuentes | `docs/modulos/M*/HU.md`, `docs/02-trazabilidad/matriz_HU_RF_indicador.md`, `docs/01-plan/PLAN_DE_TRABAJO.md`, `docs/01-plan/PLAN_IMPLEMENTACION.md`, historial de git de los dos repositorios |

---

## 1. Cómo leer este backlog

**Identificadores.** Cada elemento tiene un código `PB-nnn`, fijo para siempre aunque cambie de
sprint. Las historias conservan además su código `HU-Mnn-nn` de la especificación.

**Tipos de elemento.**

| Tipo | Significado |
|---|---|
| HU | Historia de usuario de la especificación: lo que el usuario necesita |
| TEC | Elemento técnico habilitador: infraestructura, subfase de construcción o pieza transversal |
| DOC | Documentación del sistema o del proyecto |
| SPK | Investigación con plazo fijo para cerrar una decisión |
| EXT | Dependencia de la empresa; no la resuelve el equipo |
| DEF | Defecto registrado en el registro de incidencias |
| DES | Trabajo del alcance anterior a la reformulación, reemplazado o descartado. Se conserva por trazabilidad y no suma puntos |

**Prioridad.** La de cada historia en la especificación, traducida a MoSCoW: Crítica = *Must*,
Alta = *Should*, Media = *Could*. El orden de construcción no sigue solo la prioridad: lo fijan las
dependencias de `ARQ-01` §6 —sin sesión y sin catálogo no hay ingreso; sin ingreso no hay lote ni
consolidado—.

**Estimación.** En puntos de historia de la serie de Fibonacci.

- *Backend de una historia:* según su número de criterios de aceptación, porque cada criterio es al
  menos una prueba y una rama de código: hasta 6 criterios, 3 puntos; de 7 a 10, 5; de 11 a 14, 8;
  15 o más, 13.
- *Frontend de una historia:* según las pantallas y estados que exige: 1 a 2 una acción sobre una
  pantalla existente, 3 una pantalla, 5 una pantalla con formulario, filtros y estados, 8 un flujo
  de varios pasos.
- *Elementos técnicos:* estimación del equipo.

**Estados.** Hecho · En curso · Pendiente · Bloqueado (espera algo externo) · Reemplazado o
Descartado (solo en `DES`).

**Doble entrega.** Cada historia se entrega en dos productos, backend y frontend, con estado propio.
Una historia está terminada cuando los dos lo están.

---

## 2. Visión del producto

Registrar el ingreso de mineral a planta a partir de la fotografía del ticket de balanza:
reconocer la placa, la fecha y el peso bruto; validar su consistencia con las reglas V1 a V5;
pedir la confirmación del usuario antes de guardar; calcular el peso neto con la tara del vehículo;
seguir el mineral por sus etapas de secado, zarandeo, molienda y ensacado; y consolidar el total
mensual por tipo de mineral. Todo con roles, auditoría y sin borrar registros.

| Objetivo de versión | Contenido | Fecha |
|---|---|---|
| Especificación cerrada | Línea base 2.1: 9 módulos, 27 historias, 277 criterios | 23/10/2026 |
| Base técnica | Backend con sesión, roles, auditoría y catálogo | 02/11/2026 |
| Producto de la Unidad III | Backend y frontend integrados en M01 y M02 | 06/11/2026 |
| Núcleo funcional | Registro de ingresos con reconocimiento y validación | 20/11/2026 |
| Producto completo | M01 a M09 en los dos productos | 08/01/2027 |
| Puesta en marcha | Sistema estabilizado y desplegado | 22/01/2027 |

---

## 3. Sprints

| Sprint | Nombre | Inicio | Fin | Elementos | Puntos planificados | Puntos terminados | Estado |
|---|---|---|---|---:|---:|---:|---|
| S0 | Inicio y especificación v1 | 04/09/2026 | 08/09/2026 | 7 | 24 | 24 | Cerrado |
| S1 | Construcción del alcance v1 | 09/09/2026 | 19/09/2026 | 8 | 10 | 10 | Cerrado |
| S2 | Reformulación al sistema inteligente | 22/09/2026 | 30/09/2026 | 14 | 54 | 54 | Cerrado |
| S3 | Especificación v2 y v2.1, cierre documental | 20/10/2026 | 23/10/2026 | 12 | 49 | 49 | Cerrado |
| S4 | F0 · Preparación del backend | 24/10/2026 | 25/10/2026 | 5 | 14 | 14 | Cerrado |
| S5 | F1 y F2 · Autenticación, auditoría y catálogo | 25/10/2026 | 02/11/2026 | 15 | 54 | 49 | Cerrado |
| S6 | Frontend base, M01 y M02 integrados · Unidad III | 03/11/2026 | 06/11/2026 | 15 | 38 | 0 | En curso |
| S7 | F3 · Registro, reconocimiento y validación | 09/11/2026 | 20/11/2026 | 18 | 114 | 0 | Planificado |
| S8 | F4 · Auditoría: historial y consulta | 23/11/2026 | 27/11/2026 | 4 | 16 | 0 | Planificado |
| S9 | F5 · Trazabilidad del proceso | 30/11/2026 | 11/12/2026 | 12 | 86 | 0 | Planificado |
| S10 | F6 · Consulta, inicio y avisos | 14/12/2026 | 18/12/2026 | 8 | 62 | 0 | Planificado |
| S11 | F7 · Consolidación y elección del motor | 04/01/2027 | 08/01/2027 | 5 | 25 | 0 | Planificado |
| S12 | F8 · Estabilización y congelamiento | 11/01/2027 | 15/01/2027 | 7 | 16 | 0 | Planificado |
| S13 | F9 · Despliegue y puesta en marcha | 18/01/2027 | 22/01/2027 | 8 | 16 | 0 | Planificado |
| **Total** | | 04/09/2026 | 22/01/2027 | **132** | **578** | **200** | |

**Lectura de la tabla.**

- **S0 a S5 son el historial real** del repositorio: fechas de los commits y números de PR
  verificables en GitHub. Entre el 01/10 y el 19/10/2026 no hay commits en ningún repositorio.
- **S1 construyó el alcance anterior** —salidas, existencias y operación sin conexión—. La
  reformulación de S2 lo retiró del alcance; sus elementos figuran como `DES` y no suman puntos, pero
  muestran por qué el código actual se rehízo en S4 y S5.
- **S6 en adelante es la planificación.** Sigue las fases F3 a F9 de `PLAN_IMPLEMENTACION.md`, con
  sprints de una semana y de dos para las fases más grandes (F3 y F5). Las fechas son propuestas:
  ajústalas al calendario académico, que no deja trabajar la segunda quincena de diciembre.
- **Velocidad observada:** 49 a 54 puntos por sprint en S2, S3 y S5. S7 (114 puntos en dos semanas) y
  S9 (86 en dos semanas) están en ese ritmo; si un sprint no cierra su puerta, el siguiente no
  empieza (`PLAN_IMPLEMENTACION.md` §7).

---

## 4. Épicas

| Épica | Nombre | RF | Historias | Elementos técnicos | Puntos | Terminados |
|---|---|---|---:|---:|---:|---:|
| EP-01 | M01 Autenticación, usuarios y roles | RF10 | 3 | 1 | 27 | 16 |
| EP-02 | M02 Catálogo maestro | RF06 | 3 | 2 | 28 | 17 |
| EP-03 | M03 Registro de ingresos | RF01, RF04, RF05, RF06 | 4 | 4 | 70 | 5 |
| EP-04 | M04 Reconocimiento automático del ticket | RF02 | 2 | 3 | 32 | 0 |
| EP-05 | M05 Validación automática de consistencia | RF03 | 1 | 1 | 16 | 0 |
| EP-06 | M06 Trazabilidad del proceso | RF07 | 5 | 6 | 83 | 0 |
| EP-07 | M07 Consulta de ingresos | RF08 | 4 | 4 | 62 | 0 |
| EP-08 | M08 Consolidación mensual | RF09 | 2 | 2 | 17 | 0 |
| EP-09 | M09 Auditoría | Transversal | 3 | 2 | 24 | 5 |
| EP-10 | Especificación y gestión del proyecto | Transversal | 0 | 32 | 124 | 118 |
| EP-11 | Infraestructura, integración continua y respaldo | Transversal | 0 | 13 | 25 | 21 |
| EP-12 | Frontend base: armazón, sesión y navegación | Transversal | 0 | 6 | 16 | 5 |
| EP-13 | Calidad, estabilización y pruebas | Transversal | 0 | 16 | 35 | 13 |
| EP-14 | Despliegue y puesta en marcha | Transversal | 0 | 9 | 19 | 0 |

---

## 5. Historias de usuario

Ordenadas por orden de construcción. Totales: 27 historias, 277 criterios de aceptación,
173 puntos de backend y 91 de frontend.

| ID | Historia | Título | Épica | Rol | RF | Prioridad | MoSCoW | CA | Pts back | Pts front | Sprint | Backend | Frontend |
|---|---|---|---|---|---|---|---|---:|---:|---:|---|---|---|
| PB-001 | HU-M01-01 | Inicio y cierre de sesión | EP-01 | Todos | RF10 | Crítica | Must | 9 | 5 | 3 | S5 / S6 | Hecho | En curso |
| PB-002 | HU-M01-03 | Control de acceso por rol | EP-01 | Administrador | RF10 | Crítica | Must | 6 | 3 | 2 | S5 / S6 | Hecho | En curso |
| PB-003 | HU-M01-02 | Gestión de usuarios | EP-01 | Administrador | RF10 | Alta | Should | 11 | 8 | 5 | S5 / S6 | Hecho | En curso |
| PB-004 | HU-M02-01 | Gestión del catálogo de vehículos | EP-02 | Administrativo | RF06 | Crítica | Must | 14 | 8 | 5 | S5 / S6 | Hecho | En curso |
| PB-005 | HU-M02-02 | Gestión del catálogo de tipos de mineral | EP-02 | Administrativo | RF06 | Crítica | Must | 10 | 5 | 3 | S5 / S6 | Hecho | En curso |
| PB-006 | HU-M02-03 | Gestión de transportistas | EP-02 | Administrativo | RF06 | Media | Could | 6 | 3 | 2 | S5 / S6 | Hecho | En curso |
| PB-007 | HU-M05-01 | Detección y resolución de inconsistencias del ticket | EP-05 | Supervisor de planta | RF03 | Crítica | Must | 13 | 8 | 3 | S7 | Pendiente | Pendiente |
| PB-008 | HU-M04-01 | Reconocimiento automático de los datos del ticket | EP-04 | Supervisor de planta | RF02 | Crítica | Must | 8 | 5 | 3 | S7 | Pendiente | Pendiente |
| PB-009 | HU-M03-01 | Registro de un ingreso a partir del ticket de balanza | EP-03 | Supervisor de planta | RF01, RF04, RF05, RF06 | Crítica | Must | 17 | 13 | 8 | S7 | Pendiente | Pendiente |
| PB-010 | HU-M03-04 | Registro del destare de un vehículo en su primer viaje | EP-03 | Supervisor de planta | RF01 | Crítica | Must | 10 | 5 | 3 | S7 | Pendiente | Pendiente |
| PB-011 | HU-M03-02 | Corrección de un ingreso registrado | EP-03 | Administrativo | RF04 | Alta | Should | 14 | 8 | 5 | S7 | Pendiente | Pendiente |
| PB-012 | HU-M03-03 | Anulación de un ingreso | EP-03 | Administrador | — | Alta | Should | 8 | 5 | 2 | S7 | Pendiente | Pendiente |
| PB-013 | HU-M04-02 | Consulta del dato reconocido frente al confirmado | EP-04 | Administrativo | RF02 | Media | Could | 6 | 3 | 3 | S7 | Pendiente | Pendiente |
| PB-014 | HU-M09-01 | Registro de eventos del sistema | EP-09 | Administrador | — | Alta | Should | 7 | 5 | — | S5 / S8 | En curso | No aplica |
| PB-015 | HU-M09-02 | Historial de un ingreso | EP-09 | Supervisor de planta | — | Media | Could | 5 | 3 | 2 | S8 | Pendiente | Pendiente |
| PB-016 | HU-M09-03 | Consulta de la auditoría del sistema | EP-09 | Administrador | — | Media | Could | 5 | 3 | 3 | S8 | Pendiente | Pendiente |
| PB-017 | HU-M06-01 | Gestión de lotes de proceso | EP-06 | Administrativo | RF07 | Alta | Should | 23 | 13 | 5 | S9 | Pendiente | Pendiente |
| PB-018 | HU-M06-02 | Registro del paso de un lote por una etapa de su ruta | EP-06 | Supervisor de planta | RF07 | Crítica | Must | 16 | 13 | 5 | S9 | Pendiente | Pendiente |
| PB-019 | HU-M06-04 | División de un lote por fracciones | EP-06 | Administrativo | RF07 | Alta | Should | 10 | 5 | 3 | S9 | Pendiente | Pendiente |
| PB-020 | HU-M06-05 | Cierre del lote con su destino | EP-06 | Administrador | RF07 | Alta | Should | 8 | 5 | 3 | S9 | Pendiente | Pendiente |
| PB-021 | HU-M06-03 | Consulta de la trazabilidad de un ingreso | EP-06 | Administrativo | RF07 | Media | Could | 8 | 5 | 3 | S9 | Pendiente | Pendiente |
| PB-022 | HU-M07-01 | Consulta de un ingreso por placa y fecha con su respaldo | EP-07 | Administrativo | RF08 | Crítica | Must | 12 | 8 | 5 | S10 | Pendiente | Pendiente |
| PB-023 | HU-M07-02 | Listado y detalle de ingresos | EP-07 | Administrativo | RF08 | Alta | Should | 17 | 13 | 5 | S10 | Pendiente | Pendiente |
| PB-024 | HU-M07-03 | Calendario de llegadas | EP-07 | Administrativo | RF08 | Media | Could | 8 | 5 | 3 | S10 | Pendiente | Pendiente |
| PB-025 | HU-M07-04 | Resumen del día y avisos de pendientes | EP-07 | Todos | — | Media | Could | 11 | 8 | 3 | S10 | Pendiente | Pendiente |
| PB-026 | HU-M08-01 | Total acumulado mensual por tipo de mineral | EP-08 | Administrativo | RF09 | Crítica | Must | 10 | 5 | 3 | S11 | Pendiente | Pendiente |
| PB-027 | HU-M08-02 | Exportación del total acumulado mensual | EP-08 | Administrativo | RF09 | Alta | Should | 5 | 3 | 1 | S11 | Pendiente | Pendiente |
| | | **Total** | | | | | | **277** | **173** | **91** | | | |

**Notas.**

- **HU-M09-01** está en curso: su registrador existe desde S5 y ya audita M01 y M02; la historia se
  completa cuando cada módulo registra sus eventos, y se verifica en S8. No tiene pantalla propia.
- **El frontend de M01 y M02** se construye en S6 sobre un backend terminado; desde S7, cada sprint
  entrega el backend y la pantalla de sus historias, como manda la Parte B de cada fase del plan.
- **Ninguna historia está sin estimar ni sin sprint.** Si una se aplaza, se mueve de sprint; no se
  quita del backlog.

---

## 6. Elementos técnicos, de documentación, investigación, externos y defectos

Todo lo que no es una historia de usuario pero consume esfuerzo del equipo. Los terminados llevan su
evidencia: fecha, PR o commit.

#### S0 · Inicio y especificación v1

| ID | Tipo | Elemento | Épica | Puntos | Estado | Evidencia |
|---|---|---|---|---:|---|---|
| PB-028 | TEC | Inicialización del repositorio y `.gitignore` del proyecto | EP-11 | 1 | Hecho | 04/09 · PR #5 |
| PB-029 | DOC | Historias, requisitos y diagramas v1 de autenticación y catálogo | EP-10 | 5 | Hecho | 04/09 · PR #1, #2 |
| PB-030 | DOC | Historias, requisitos y diagramas v1 de ingresos y demás módulos | EP-10 | 5 | Hecho | 04/09 · PR #4 |
| PB-031 | DOC | Arquitectura base, modelo de datos v1 y modelo C4 en cuatro niveles | EP-10 | 5 | Hecho | 04/09 · PR #3 |
| PB-032 | DOC | Integración de la arquitectura con las decisiones de diseño | EP-10 | 2 | Hecho | 05/09 |
| PB-033 | TEC | Entorno de desarrollo del backend Django + DRF | EP-11 | 3 | Hecho | 05/09 |
| PB-034 | TEC | Esqueleto Angular 17 con PWA, Material y estructura por features | EP-12 | 3 | Hecho | 07/09 · frontend |

#### S1 · Construcción del alcance v1

| ID | Tipo | Elemento | Épica | Puntos | Estado | Evidencia |
|---|---|---|---|---:|---|---|
| PB-035 | DOC | PLAN-01 v1 de trabajo y pruebas; normalización de la terminología | EP-10 | 3 | Hecho | 09/09 |
| PB-036 | TEC | Skills de desarrollo colaborativo del backend | EP-10 | 2 | Hecho | 09/09 |
| PB-037 | TEC | Skills, README de arquitectura, `HttpClient` y documentación propia del frontend | EP-12 | 2 | Hecho | 09/09 · frontend |
| PB-038 | DES | M01 v1: registro de usuarios y autenticación (alcance anterior) | EP-01 | 5 | Reemplazado | 09/09 · rehecho en S5 |
| PB-039 | DES | M02 v1: catálogo con producto y cliente (alcance anterior) | EP-02 | 5 | Reemplazado | 10/09 · PR #6 · rehecho en S4 y S5 |
| PB-040 | DES | M03 v1: ingresos con correlativo transaccional (alcance anterior) | EP-03 | 8 | Reemplazado | 12-15/09 · PR #7 · refactor en S4 |
| PB-041 | TEC | Refactor de arquitectura tras la revisión de M01 a M03 | EP-11 | 3 | Hecho | 13/09 |
| PB-042 | DES | M04 v1: salidas con advertencia de stock (alcance anterior) | EP-10 | 5 | Descartado | 17/09 · retirado del alcance |

#### S2 · Reformulación al sistema inteligente

| ID | Tipo | Elemento | Épica | Puntos | Estado | Evidencia |
|---|---|---|---|---:|---|---|
| PB-043 | DOC | Análisis de impacto y plan de migración al sistema inteligente | EP-10 | 3 | Hecho | 22/09 · PR #8 |
| PB-044 | DOC | Marco de tesis, decisiones de reformulación y plantillas | EP-10 | 5 | Hecho | 22/09 · PR #8 |
| PB-045 | DOC | Módulos M01 a M09 y decisiones de diseño del sistema inteligente | EP-10 | 3 | Hecho | 22/09 · PR #8 |
| PB-046 | DOC | Modelo de datos del sistema inteligente | EP-10 | 5 | Hecho | 22/09 · PR #8 |
| PB-047 | DOC | Matriz de trazabilidad HU → RF → indicador e índice del backlog | EP-10 | 3 | Hecho | 22/09 · PR #8 |
| PB-048 | DOC | Historias, requisitos y diagramas de M04 a M09; M01 a M03 alineados | EP-10 | 13 | Hecho | 22/09 · PR #9 |
| PB-049 | DOC | Retiro de salidas, existencias, reportes y sin conexión del alcance | EP-10 | 2 | Hecho | 22/09 · PR #9 |
| PB-050 | DOC | ARQ-02, ARQ-03, convenciones y guías del marco de trabajo y del frontend | EP-10 | 5 | Hecho | 22/09 · PR #9 |
| PB-051 | DOC | README general del proyecto | EP-10 | 1 | Hecho | 22/09 |
| PB-052 | DOC | Plan de trabajo y plan de pruebas del sistema inteligente | EP-10 | 5 | Hecho | 27/09 |
| PB-053 | DOC | Skills actualizadas y skill de reconocimiento y validación | EP-10 | 3 | Hecho | 27/09 |
| PB-054 | DOC | Formato real del ticket de balanza y flujo del destare | EP-10 | 3 | Hecho | 28/09 · PR #11 |
| PB-055 | DOC | Especificación de requerimientos y diagramas en PDF | EP-10 | 2 | Hecho | 29/09 |
| PB-056 | DOC | Depuración de documentos de la migración | EP-10 | 1 | Hecho | 30/09 |

#### S3 · Especificación v2 y v2.1, cierre documental

| ID | Tipo | Elemento | Épica | Puntos | Estado | Evidencia |
|---|---|---|---|---:|---|---|
| PB-057 | DOC | Reformulación de historias y requerimientos: versión 2 | EP-10 | 8 | Hecho | 20/10 |
| PB-058 | DOC | Decisiones DR-11 a DR-28 aplicadas a las fuentes y a M03, M04 y M06 | EP-10 | 8 | Hecho | 21-22/10 · PR #12, #13, #15, #17 |
| PB-059 | DOC | Modelo de datos 3.1, decisiones, guías y ARQ-01 a ARQ-03 en versión 2 | EP-10 | 5 | Hecho | 21/10 |
| PB-060 | TEC | Scripts de validación de la documentación y de trazabilidad de pruebas | EP-13 | 3 | Hecho | 21/10 |
| PB-061 | TEC | Workflows de integración continua: documentación y backend | EP-11 | 3 | Hecho | 21/10 · PR #14 |
| PB-062 | TEC | Pruebas sobre PostgreSQL con `TEST_DATABASE_URL` | EP-13 | 1 | Hecho | 21/10 |
| PB-063 | DOC | Revisión técnica de la versión 2, índice y generadores de PDF | EP-10 | 3 | Hecho | 21/10 |
| PB-064 | TEC | Retiro de salidas, sincronización y `Cliente` del backend | EP-11 | 2 | Hecho | 22/10 · PR #16 |
| PB-065 | DOC | Maqueta navegable alineada con DR-24 a DR-28 | EP-10 | 5 | Hecho | 22/10 |
| PB-066 | DOC | Revisión y validación v2.1: DR-29 a DR-31, D-18 a D-22 | EP-10 | 5 | Hecho | 23/10 |
| PB-067 | DOC | PLAN-02 de implementación y Anexo A de 277 casos de Postman | EP-10 | 5 | Hecho | 23/10 |
| PB-068 | DOC | Acta de cierre de la fase documental, línea base 2.1 | EP-10 | 1 | Hecho | 23/10 |

#### S4 · F0 · Preparación del backend

| ID | Tipo | Elemento | Épica | Puntos | Estado | Evidencia |
|---|---|---|---|---:|---|---|
| PB-069 | TEC | 0.1 Docker Compose de desarrollo y Dockerfile del backend | EP-11 | 3 | Hecho | 24/10 |
| PB-070 | TEC | 0.2 a 0.5 `Ingreso` alineado al modelo 3.1, `TipoMineral` y retiro del alcance anterior | EP-03 | 5 | Hecho | 24/10 |
| PB-071 | TEC | 0.6 y 0.7 Esqueletos de M04 a M06, renombres y `settings` | EP-11 | 2 | Hecho | 24/10 · 9e5c600 |
| PB-072 | TEC | 0.8 a 0.10 Datos de prueba, colección de Postman y trazabilidad estricta | EP-13 | 3 | Hecho | 24/10 |
| PB-073 | DOC | Puerta de F0 registrada y aprobada | EP-13 | 1 | Hecho | 25/10 · c063b07 |

#### S5 · F1 y F2 · Autenticación, auditoría y catálogo

| ID | Tipo | Elemento | Épica | Puntos | Estado | Evidencia |
|---|---|---|---|---:|---|---|
| PB-074 | TEC | 1.1 `EVENTO_AUDITORIA` y `ServicioAuditoria` como único punto de escritura | EP-09 | 5 | Hecho | 04b2537 |
| PB-075 | TEC | 1.6 Respaldo y restauración ejecutables (D-20) | EP-11 | 2 | Hecho | scripts/respaldo.sh |
| PB-076 | DOC | D-23 Convención de códigos HTTP y cuerpo de error uniforme | EP-10 | 1 | Hecho | decisiones_diseno.md |
| PB-077 | TEC | 2.6 Catálogo provisional cargado desde la maqueta | EP-02 | 1 | Hecho | datos_prueba.py |
| PB-078 | DOC | D-24 Patrón de placa configurable y alta rápida | EP-10 | 1 | Hecho | 21112af |
| PB-079 | TEC | Carpetas de Postman F1 y F2: 67 peticiones | EP-13 | 3 | Hecho | postman/ |
| PB-080 | DOC | Puertas técnicas de F1 y F2 con evidencias | EP-13 | 2 | Hecho | 8e948ac, evidencias/F1 y F2 |
| PB-081 | TEC | Preparación del pipeline para el despliegue | EP-11 | 2 | Hecho | 02/11 · 3845675 |

#### S6 · Frontend base, M01 y M02 integrados · Unidad III

| ID | Tipo | Elemento | Épica | Puntos | Estado | Evidencia |
|---|---|---|---|---:|---|---|
| PB-082 | TEC | Realinear las features del frontend a los módulos M01 a M09 | EP-12 | 2 | Pendiente | — |
| PB-083 | TEC | Interceptores JWT y de errores con el cuerpo uniforme (D-23) | EP-12 | 3 | Pendiente | — |
| PB-084 | TEC | Guards de sesión y de rol; armazón con menú por rol | EP-12 | 3 | Pendiente | — |
| PB-085 | TEC | CORS del backend para el origen del frontend | EP-11 | 1 | Pendiente | — |
| PB-086 | DEF | DEF-006 pytest toma la configuración de desarrollo dentro del contenedor | EP-13 | 1 | Pendiente | — |
| PB-087 | DEF | DEF-007 Índice de documentación con enlaces a `.DS_Store` | EP-10 | 1 | En curso | Corregido en local |
| PB-088 | DEF | DEF-008 Rama `feature/M03-ingresos` con commits del alcance anterior | EP-11 | 1 | Pendiente | — |
| PB-089 | TEC | Etiqueta `v0.3.0` y CHANGELOG en los dos repositorios | EP-11 | 1 | Pendiente | — |
| PB-090 | DOC | Documentos del Producto de la Unidad III | EP-10 | 5 | En curso | entregables/unidad-III/ |

#### S7 · F3 · Registro, reconocimiento y validación

| ID | Tipo | Elemento | Épica | Puntos | Estado | Evidencia |
|---|---|---|---|---:|---|---|
| PB-091 | TEC | F3.1 `ValidadorConsistencia` con una clase por regla V1 a V5 | EP-05 | 5 | Pendiente | — |
| PB-092 | TEC | F3.2 Interfaz `ReconocedorTicket`, adaptador determinista y adaptador local | EP-04 | 8 | Pendiente | — |
| PB-093 | TEC | F3.3 Borrador y confirmación del registro con código, marcas de tiempo y tara | EP-03 | 8 | Pendiente | — |
| PB-094 | TEC | F3.4 Ingreso En proceso y destare | EP-03 | 3 | Pendiente | — |
| PB-095 | TEC | F3.5 Corrección, reversión y anulación | EP-03 | 5 | Pendiente | — |
| PB-096 | TEC | F3.6 Consultas de reconocimiento y validación | EP-04 | 2 | Pendiente | — |
| PB-097 | TEC | Tickets de prueba en `postman/archivos/` | EP-13 | 1 | Pendiente | — |
| PB-098 | TEC | Carpeta de Postman F3 y puerta de F3 | EP-13 | 3 | Pendiente | — |
| PB-099 | TEC | Borrador del registro conservado ante pérdida de conexión (RNF-M03-05) | EP-12 | 3 | Pendiente | — |
| PB-100 | EXT | Validar los roles y la matriz de permisos con la empresa (DR-23) | EP-01 | 1 | Bloqueado | Depende de la empresa |
| PB-101 | EXT | Catálogo real de tipos de mineral y taras de la empresa (DR-03) | EP-02 | 1 | Bloqueado | Depende de la empresa |

#### S8 · F4 · Auditoría: historial y consulta

| ID | Tipo | Elemento | Épica | Puntos | Estado | Evidencia |
|---|---|---|---|---:|---|---|
| PB-102 | TEC | Historial de un ingreso y consulta de auditoría en la API | EP-09 | 3 | Pendiente | — |
| PB-103 | TEC | Verificación en Postman de los eventos de F1 a F3 | EP-13 | 2 | Pendiente | — |

#### S9 · F5 · Trazabilidad del proceso

| ID | Tipo | Elemento | Épica | Puntos | Estado | Evidencia |
|---|---|---|---|---:|---|---|
| PB-104 | TEC | F5.1 Etapas y rutas como catálogos cerrados (D-21) | EP-06 | 2 | Pendiente | — |
| PB-105 | TEC | F5.2 Lotes y composición por mineral | EP-06 | 5 | Pendiente | — |
| PB-106 | TEC | F5.3 Recorrido de etapas y ruta | EP-06 | 5 | Pendiente | — |
| PB-107 | TEC | F5.4 División por fracciones e ingresos tardíos | EP-06 | 5 | Pendiente | — |
| PB-108 | TEC | F5.5 Bigbags y cierre del lote | EP-06 | 3 | Pendiente | — |
| PB-109 | TEC | F5.6 Trazabilidad de un ingreso | EP-06 | 3 | Pendiente | — |
| PB-110 | TEC | Carpeta de Postman F5 y puerta de F5 | EP-13 | 3 | Pendiente | — |

#### S10 · F6 · Consulta, inicio y avisos

| ID | Tipo | Elemento | Épica | Puntos | Estado | Evidencia |
|---|---|---|---|---:|---|---|
| PB-111 | TEC | F6.1 Búsqueda, listado y detalle compuesto | EP-07 | 5 | Pendiente | — |
| PB-112 | TEC | F6.2 Calendario agregado por mes | EP-07 | 2 | Pendiente | — |
| PB-113 | TEC | F6.3 Exportación CSV y búsqueda de la cabecera | EP-07 | 2 | Pendiente | — |
| PB-114 | TEC | F6.4 Inicio y avisos por rol | EP-07 | 3 | Pendiente | — |

#### S11 · F7 · Consolidación y elección del motor

| ID | Tipo | Elemento | Épica | Puntos | Estado | Evidencia |
|---|---|---|---|---:|---|---|
| PB-115 | TEC | 7.1 Consolidado mensual con el filtro compartido con M07 | EP-08 | 3 | Pendiente | — |
| PB-116 | TEC | 7.2 Exportación XLSX del consolidado | EP-08 | 2 | Pendiente | — |
| PB-117 | SPK | 7.3 Piloto de motores con 20 a 30 tickets reales; cierre de D-12 y D-15 | EP-04 | 8 | Pendiente | — |

#### S12 · F8 · Estabilización y congelamiento

| ID | Tipo | Elemento | Épica | Puntos | Estado | Evidencia |
|---|---|---|---|---:|---|---|
| PB-118 | TEC | 8.1 Regresión completa: pytest y Newman de todas las carpetas | EP-13 | 3 | Pendiente | — |
| PB-119 | TEC | 8.2 Preproducción con el mismo Compose | EP-14 | 3 | Pendiente | — |
| PB-120 | TEC | 8.3 Pruebas de rendimiento de los RNF | EP-13 | 3 | Pendiente | — |
| PB-121 | TEC | 8.4 Lista de control CP01 a CP12 ejecutada y firmada | EP-13 | 2 | Pendiente | — |
| PB-122 | DEF | 8.5 Corrección de defectos abiertos | EP-13 | 3 | Pendiente | — |
| PB-123 | TEC | 8.6 Congelamiento del motor, su versión y las reglas V1 a V5 (D-16) | EP-13 | 1 | Pendiente | — |
| PB-124 | TEC | 8.7 Restauración del último respaldo en preproducción | EP-11 | 1 | Pendiente | — |

#### S13 · F9 · Despliegue y puesta en marcha

| ID | Tipo | Elemento | Épica | Puntos | Estado | Evidencia |
|---|---|---|---|---:|---|---|
| PB-125 | SPK | 9.1 Elección del servicio de alojamiento | EP-14 | 1 | Pendiente | — |
| PB-126 | TEC | 9.2 Medio definitivo de las imágenes (D-14, D-18) | EP-14 | 2 | Pendiente | — |
| PB-127 | TEC | 9.3 Política de respaldo programada y probada (D-20) | EP-14 | 2 | Pendiente | — |
| PB-128 | TEC | 9.4 HTTPS, secretos, zona horaria y límite de subida | EP-14 | 3 | Pendiente | — |
| PB-129 | DOC | 9.5 Bitácora de despliegues | EP-14 | 1 | Pendiente | — |
| PB-130 | TEC | 9.6 Prueba de humo en el servidor con Postman | EP-14 | 2 | Pendiente | — |
| PB-131 | DOC | Manual de usuario por rol | EP-14 | 3 | Pendiente | — |
| PB-132 | DOC | Capacitación de los usuarios de planta | EP-14 | 2 | Pendiente | — |

---

## 7. Plan de versiones

| Versión | Sprint | Contenido | Fecha |
|---|---|---|---|
| `v0.1.0` | S3 | Especificación línea base 2.1, maqueta y CI de documentación | 23/10/2026 |
| `v0.2.0` | S5 | Backend: M01, registrador de M09 y M02 | 02/11/2026 |
| `v0.3.0` | S6 | Backend y frontend integrados en M01 y M02 · Producto de la Unidad III | 06/11/2026 |
| `v0.4.0` | S7 | Registro de ingresos, reconocimiento y validación | 20/11/2026 |
| `v0.5.0` | S8 | Historial y auditoría | 27/11/2026 |
| `v0.6.0` | S9 | Trazabilidad del proceso | 11/12/2026 |
| `v0.7.0` | S10 | Consulta, inicio y avisos | 18/12/2026 |
| `v0.8.0` | S11 | Consolidación y motor elegido | 08/01/2027 |
| `v1.0.0-rc` | S12 | Sistema congelado en preproducción | 15/01/2027 |
| `v1.0.0` | S13 | Sistema en el alojamiento de la presentación | 22/01/2027 |

Las versiones `v0.1.0` y `v0.2.0` corresponden a trabajo ya fusionado en `main`; se etiquetan sobre
sus commits de cierre (`c063b07` y `af66b3e`).

---

## 8. Dependencias externas y riesgos del backlog

| Elemento afectado | Dependencia o riesgo | Efecto si no se resuelve | Respuesta |
|---|---|---|---|
| HU-M02-01, HU-M02-02 | Catálogo real de tipos de mineral y taras (DR-03) | La puerta de F2 sigue observada; los vehículos sin tara quedan En proceso hasta su destare | Catálogo provisional de la maqueta, reemplazable sin cambiar código |
| HU-M01-03 | Validación de los roles con la empresa (DR-23) | Una matriz de permisos que no corresponde a la operación | Matriz centralizada en una sola clase por operación; cambiarla es configuración |
| HU-M04-01 | Precisión del motor de reconocimiento (D-12) | Más correcciones manuales | Adaptador intercambiable; piloto con tickets reales en S11 |
| HU-M03-01 | Código único bajo concurrencia | Dos ingresos con el mismo código | Prueba de transacciones concurrentes en pytest |
| Todo el frontend | El frontend empieza después del backend | Funcionalidad sin pantalla al final | Desde S7, ningún sprint cierra sin la Parte B de su fase |
| S12 y S13 | Servicio de alojamiento sin elegir (D-20) | Despliegue improvisado | SPK 9.1 al inicio de S13; preproducción con el mismo Compose en S12 |

---

## 9. Definición de listo y de terminado

**Listo** (`PLAN_DE_TRABAJO.md` §4.1). Un elemento entra a un sprint solo si:

- tiene criterios de aceptación escritos;
- las reglas de negocio que lo afectan están identificadas;
- sus entidades están en el modelo de datos;
- el contrato de su ruta está definido;
- no depende de una decisión abierta.

**Terminado** (`PLAN_DE_TRABAJO.md` §5), resumido:

- cada regla y cada criterio tienen su prueba, y los mensajes coinciden con el criterio;
- los permisos están declarados por acción, con una prueba de rechazo por rol;
- ninguna regla vive en la vista ni solo en Angular; toda escritura registra su evento en M09;
- nada se borra físicamente; nada reconocido se guarda sin confirmación;
- listados paginados, sin consultas N+1, pesos en decimal;
- el commit cita la historia y la matriz de trazabilidad está al día;
- la puerta de la fase pasa: pytest, Newman y trazabilidad estricta, registrados en la bitácora.

---

## 10. Cómo llevar este backlog a GitHub Projects

1. Crea un proyecto de tipo *Board* en la organización o cuenta, vinculado a los dos repositorios.
2. Columnas: **Backlog**, **Sprint actual**, **En curso**, **En revisión**, **Hecho**.
3. Campos personalizados: *Puntos* (número), *Sprint* (iteración, con las fechas de la sección 3),
   *Tipo* (selección: HU, TEC, DOC, SPK, EXT, DEF), *Épica* (selección: EP-01 a EP-14),
   *Producto* (Backend, Frontend).
4. Una issue por elemento, con el título `PB-nnn · HU-Mnn-nn · Título` y, en el cuerpo, el enlace al
   `HU.md` del módulo. Las historias llevan dos issues, una por producto, enlazadas.
5. Etiquetas: `M01` a `M09`, `prioridad:critica`, `prioridad:alta`, `prioridad:media`, `incidencia`.
6. Los elementos `DES` se crean cerrados como *not planned*, con el enlace a su PR, para que el
   historial se vea completo.
7. Cada PR cierra su issue con `Closes #n`; así el tablero se mueve solo y el docente ve la relación
   entre el backlog y el código.
