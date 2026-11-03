# Guía para el Producto de la Unidad III

**Producto:** versión funcional integrada de la solución tecnológica.
**Entrega:** viernes 06/11/2026.
**Proyecto:** Sistema web inteligente para el control de inventarios de ingreso de mineral —
Construcción y Minería, planta de Pillcomarca, Huánuco.
**Uso de esta guía:** leerla completa, decidir el alcance de la sección 2 y producir cada entregable
con la receta de la sección 4. Ningún entregable parte de cero: casi todo existe ya en los dos
repositorios y solo hay que consolidarlo y presentarlo.

---

## 1. Qué se pide y qué ya existe

| # | Entregable | Lo que ya existe | Lo que falta | Esfuerzo |
|---|---|---|---|---|
| 1 | Plan de desarrollo | `docs/01-plan/PLAN_DE_TRABAJO.md` (PLAN-01) y `docs/01-plan/PLAN_IMPLEMENTACION.md` (PLAN-02, fases F0 a F9) | Un documento corto que los resuma para el docente, con el estado real al 06/11 | Bajo |
| 2 | Backlog priorizado | 27 historias con prioridad en `docs/modulos/M*/HU.md` y su matriz en `docs/02-trazabilidad/` | Consolidarlas en una sola tabla con estimación, iteración y estado | Bajo |
| 3 | Repositorio con control de versiones | Dos repositorios en GitHub, ramas, PR #19 fusionado, CI con dos flujos | Etiqueta de versión, limpieza de una rama obsoleta, capturas | Bajo |
| 4 | Base de datos implementada | PostgreSQL 16 en Docker Compose, 8 tablas de dominio, migraciones, modelo E-R 3.1 | Diagrama generado desde la base real y capturas | Bajo |
| 5 | Lógica de negocio y servicios | M01, M02 y el registrador de M09 con capas `services/` y `repositories/`, API REST documentada en Swagger | Tabla de servicios y reglas implementadas | Bajo |
| 6 | Interfaces funcionales | Maqueta navegable (`Mockup/index.html`) y un esqueleto Angular 17 **del alcance anterior** | **Pantallas Angular reales** de inicio de sesión y catálogo conectadas al backend | **Alto** |
| 7 | Módulos integrados | M01 ↔ M02 ↔ M09 integrados en el backend, probados con Newman | La integración frontend ↔ backend y su evidencia | Medio |
| 8 | Roles, permisos y seguridad | Tres roles, matriz de permisos, JWT, bloqueo, contraseña temporal, auditoría | Una tabla de controles con su prueba | Bajo |
| 9 | Registro de incidencias | Incidencias reales resueltas durante F0 a F2, sin registrar formalmente | Pasarlas a GitHub Issues con la plantilla de PLAN-01 §7.2 | Bajo |
| 10 | Documentación técnica preliminar | ARQ-01 a ARQ-03, modelo de datos, decisiones D-01 a D-24, guías, OpenAPI, Postman | Un documento índice que la ordene | Bajo |
| 11 | Evidencias de las iteraciones | Bitácora de puertas y carpetas `docs/03-pruebas/evidencias/F1/` y `F2/` | Una ficha por iteración con capturas | Medio |

**Conclusión:** el único entregable que exige programar de verdad esta semana es el 6, y con él el 7.
Todo lo demás es consolidar lo que ya está hecho.

---

## 2. Decisión de alcance: qué es la «versión funcional integrada»

Al 02/11/2026 el backend tiene cerradas las fases F0, F1 y F2 (fusionadas en `main` con el PR #19).
F3, el registro de ingresos con reconocimiento y validación, es la fase más grande del plan y no
cabe en cuatro días junto con el frontend.

**Recomendación: presentar un incremento vertical completo, no un sistema a medias.**

| Capa | Incluido en la versión del 06/11 | Queda para la siguiente iteración |
|---|---|---|
| Backend | M01 Autenticación y roles, M02 Catálogo, registrador de M09 | M03 a M08 y las consultas de M09 |
| Frontend | Inicio y cierre de sesión, menú por rol, catálogo de vehículos, tipos de mineral y transportistas, gestión de usuarios | Registro de ingresos y demás pantallas |
| Base de datos | Las 8 tablas de dominio actuales, migradas y con datos de prueba | Tablas de reconocimiento, validación, lotes y etapas |
| Resto del sistema | Se muestra con la maqueta navegable, rotulada como prototipo | — |

Así, cada pantalla que se muestra funciona de punta a punta: interfaz → API → servicio → base de
datos → auditoría. Un docente valora más un recorrido completo que diez pantallas sin datos.

**Extensión opcional** si sobra tiempo el jueves: la subfase F3.1 (validación V1 a V5 en el
backend). Es lógica pura, se prueba sin interfaz y suma al entregable 5.

---

## 3. Calendario hasta el viernes

| Día | Trabajo | Entregables que avanzan |
|---|---|---|
| **Lun 02/11** (tarde) | Crear la carpeta de entrega, etiquetar el repositorio, limpiar la rama obsoleta, abrir las incidencias en GitHub | 3, 9 |
| **Mar 03/11** | Frontend: realinear el esqueleto Angular, inicio de sesión, guard, interceptor JWT, menú por rol | 6, 7, 8 |
| **Mié 04/11** | Frontend: catálogo (tres pantallas) y gestión de usuarios contra el backend real | 6, 7 |
| **Jue 05/11** | Recorrido integrado, regresión Newman, capturas, ficha de la iteración del frontend, diagrama de la base | 4, 7, 11 |
| **Vie 06/11** | Plan, backlog, documento técnico, PDF final y entrega | 1, 2, 5, 10 |

Regla para no fallar: **el jueves a las 18:00 se congela el código.** El viernes solo se documenta.

---

## 4. Cómo producir cada entregable

### 4.1 Plan de desarrollo

**Qué espera el docente:** cómo se organiza el desarrollo, en qué iteraciones, con qué criterios de
avance y en qué estado está hoy.

**Fuente:** PLAN-01 (`PLAN_DE_TRABAJO.md`) y PLAN-02 (`PLAN_IMPLEMENTACION.md`). No copiarlos
enteros: el docente necesita 4 a 6 páginas.

**Estructura sugerida (`01_plan_de_desarrollo.md`):**

1. **Objetivo del producto.** Una oración: registrar el ingreso de mineral a partir de la foto del
   ticket de balanza, reconociendo y validando sus datos, y seguir el mineral por sus etapas.
2. **Alcance.** RF01 a RF10 en una tabla (están en `docs/00-tesis/marco_tesis.md`, sección de
   requerimientos funcionales) y los 9 módulos.
3. **Metodología.** Desarrollo iterativo e incremental por fases, cada una cerrada por una **puerta**
   con criterios verificables: pytest sobre PostgreSQL, colección Postman ejecutada con Newman,
   trazabilidad estricta prueba ↔ criterio y aprobación del supervisor. Es una adaptación de Scrum:
   cada fase equivale a un sprint de una semana con su revisión (la puerta).
4. **Arquitectura en una figura.** Angular 17 (PWA) → API REST Django 5 + DRF → PostgreSQL 16, con
   el motor de reconocimiento como adaptador dentro del backend (D-12 provisional). Tomar la figura
   de contenedores de ARQ-03.
5. **Iteraciones** (tabla de abajo).
6. **Definición de terminado** (PLAN-01 §5), en 5 viñetas.
7. **Riesgos principales** y su respuesta (tabla de abajo).
8. **Herramientas:** GitHub, GitHub Actions, Docker Compose, Postman y Newman, pytest, ruff.

**Ejemplo de la tabla de iteraciones:**

| Iteración | Fase | Objetivo | Historias | Fechas | Estado al 06/11 |
|---|---|---|---|---|---|
| 0 | F0 | Preparar el repositorio heredado y el entorno | — | 21/10 a 25/10/2026 | Cerrada y aprobada |
| 1 | F1 | Autenticación, roles, registrador de auditoría y respaldo | HU-M01-01 a 03 | 25/10/2026 | Cerrada; fusionada el 02/11 |
| 2 | F2 | Catálogo maestro | HU-M02-01 a 03 | 26/10/2026 | Cerrada, observada por el catálogo real de la empresa |
| 3 | Frontend 1 | Interfaces de M01 y M02 integradas | HU-M01-01 a 03, HU-M02-01 a 03 | 03/11 a 05/11/2026 | En curso |
| 4 | F3 | Registro de ingresos, reconocimiento y validación | HU-M03-01 a 04, HU-M04-01 y 02, HU-M05-01 | Desde el 09/11/2026 | Planificada |
| 5 | F4 | Historial y consulta de auditoría | HU-M09-01 a 03 | Planificada | Planificada |
| 6 | F5 | Trazabilidad del proceso | HU-M06-01 a 05 | Planificada | Planificada |
| 7 | F6 | Consulta de ingresos, inicio y avisos | HU-M07-01 a 04 | Planificada | Planificada |
| 8 | F7 | Consolidación mensual y elección del motor | HU-M08-01 y 02 | Planificada | Planificada |
| 9 | F8 y F9 | Estabilización, congelamiento y despliegue | Todas | Planificada | Planificada |

> Ajusta las fechas de las iteraciones 4 a 9 con tu calendario académico; las de 0 a 2 son las
> reales de la bitácora y del historial de git.

**Ejemplo de la tabla de riesgos:**

| Riesgo | Efecto | Respuesta |
|---|---|---|
| La empresa no entrega el catálogo real ni las taras (DR-03) | El catálogo usa datos de la maqueta | Carga provisional marcada como tal; la puerta F2 queda observada |
| El motor de reconocimiento no alcanza la precisión esperada | Más correcciones manuales | Adaptador intercambiable (D-12) y piloto con tickets reales antes del congelamiento |
| Retraso del frontend respecto del backend | Funcionalidad sin interfaz | Incrementos verticales: no se cierra una fase sin su pantalla |
| Pérdida de datos | Histórico irrecuperable | Respaldo y restauración probados desde F1 (D-20) |

---

### 4.2 Backlog priorizado

**Qué espera el docente:** la lista ordenada de lo que hay que construir, con prioridad,
estimación y estado.

**Fuente:** prioridad de cada `HU.md`; módulo, RF e indicador de la matriz de trazabilidad; número
de criterios de aceptación contado en cada historia.

**Criterios usados:**

- **Prioridad:** la de la historia (Crítica, Alta, Media), traducida a MoSCoW: Crítica = *Must*,
  Alta = *Should*, Media = *Could*.
- **Estimación en puntos de historia**, propuesta a partir del número de criterios de aceptación:
  hasta 6 criterios = 3 puntos; de 7 a 10 = 5; de 11 a 14 = 8; 15 o más = 13. Es una heurística
  transparente; ajústala si conoces mejor el esfuerzo.
- **Orden:** el de construcción del plan (las dependencias mandan sobre la prioridad: no se registra
  un ingreso sin catálogo ni sin sesión).

**Backlog (archivo `02_backlog_priorizado.md`, o mejor un tablero de GitHub Projects con esta tabla):**

| Orden | Historia | Título | Módulo | RF | Prioridad | MoSCoW | CA | Puntos | Iteración | Estado |
|---:|---|---|---|---|---|---|---:|---:|---|---|
| 1 | HU-M01-01 | Inicio y cierre de sesión | M01 | RF10 | Crítica | Must | 9 | 5 | 1 | Backend hecho; interfaz en curso |
| 2 | HU-M01-03 | Control de acceso por rol | M01 | RF10 | Crítica | Must | 6 | 3 | 1 | Backend hecho; interfaz en curso |
| 3 | HU-M01-02 | Gestión de usuarios | M01 | RF10 | Alta | Should | 11 | 8 | 1 | Backend hecho; interfaz en curso |
| 4 | HU-M09-01 | Registro de eventos del sistema | M09 | — | Alta | Should | 7 | 5 | 1 | Registrador hecho |
| 5 | HU-M02-01 | Catálogo de vehículos | M02 | RF06 | Crítica | Must | 14 | 8 | 2 | Backend hecho; interfaz en curso |
| 6 | HU-M02-02 | Catálogo de tipos de mineral | M02 | RF06 | Crítica | Must | 10 | 5 | 2 | Backend hecho; interfaz en curso |
| 7 | HU-M02-03 | Gestión de transportistas | M02 | RF06 | Media | Could | 6 | 3 | 2 | Backend hecho; interfaz en curso |
| 8 | HU-M05-01 | Detección y resolución de inconsistencias | M05 | RF03 | Crítica | Must | 13 | 8 | 4 | Pendiente |
| 9 | HU-M04-01 | Reconocimiento automático del ticket | M04 | RF02 | Crítica | Must | 8 | 5 | 4 | Pendiente |
| 10 | HU-M03-01 | Registro de un ingreso desde el ticket | M03 | RF01, RF04, RF05, RF06 | Crítica | Must | 17 | 13 | 4 | Pendiente |
| 11 | HU-M03-04 | Destare en el primer viaje | M03 | RF01 | Crítica | Must | 10 | 5 | 4 | Pendiente |
| 12 | HU-M03-02 | Corrección de un ingreso | M03 | RF04 | Alta | Should | 14 | 8 | 4 | Pendiente |
| 13 | HU-M03-03 | Anulación de un ingreso | M03 | — | Alta | Should | 8 | 5 | 4 | Pendiente |
| 14 | HU-M04-02 | Dato reconocido frente al confirmado | M04 | RF02 | Media | Could | 6 | 3 | 4 | Pendiente |
| 15 | HU-M09-02 | Historial de un ingreso | M09 | — | Media | Could | 5 | 3 | 5 | Pendiente |
| 16 | HU-M09-03 | Consulta de la auditoría | M09 | — | Media | Could | 5 | 3 | 5 | Pendiente |
| 17 | HU-M06-01 | Gestión de lotes de proceso | M06 | RF07 | Alta | Should | 23 | 13 | 6 | Pendiente |
| 18 | HU-M06-02 | Paso de un lote por una etapa | M06 | RF07 | Crítica | Must | 16 | 13 | 6 | Pendiente |
| 19 | HU-M06-04 | División de un lote por fracciones | M06 | RF07 | Alta | Should | 10 | 5 | 6 | Pendiente |
| 20 | HU-M06-05 | Cierre del lote con su destino | M06 | RF07 | Alta | Should | 8 | 5 | 6 | Pendiente |
| 21 | HU-M06-03 | Trazabilidad de un ingreso | M06 | RF07 | Media | Could | 8 | 5 | 6 | Pendiente |
| 22 | HU-M07-01 | Consulta por placa y fecha con respaldo | M07 | RF08 | Crítica | Must | 12 | 8 | 7 | Pendiente |
| 23 | HU-M07-02 | Listado y detalle de ingresos | M07 | RF08 | Alta | Should | 17 | 13 | 7 | Pendiente |
| 24 | HU-M07-03 | Calendario de llegadas | M07 | RF08 | Media | Could | 8 | 5 | 7 | Pendiente |
| 25 | HU-M07-04 | Resumen del día y avisos | M07 | — | Media | Could | 11 | 8 | 7 | Pendiente |
| 26 | HU-M08-01 | Total acumulado mensual por tipo de mineral | M08 | RF09 | Crítica | Must | 10 | 5 | 8 | Pendiente |
| 27 | HU-M08-02 | Exportación del total mensual | M08 | RF09 | Alta | Should | 5 | 3 | 8 | Pendiente |

**Totales:** 27 historias, 277 criterios de aceptación, 173 puntos. Hechos en backend: 7 historias,
37 puntos (21 %).

**Cómo presentarlo mejor:** crea un tablero en GitHub Projects con las columnas *Backlog*,
*Iteración actual*, *En curso*, *En revisión* y *Hecho*; una tarjeta (issue) por historia con las
etiquetas `M01`…`M09`, `prioridad:critica|alta|media` y el campo *Puntos*. La captura del tablero es
la mejor evidencia del backlog.

---

### 4.3 Repositorio con control de versiones

**Qué espera el docente:** que el código esté versionado, con una forma de trabajo ordenada.

**Lo que ya tienes:**

| Elemento | Dónde |
|---|---|
| Repositorio del backend y la documentación | GitHub, `adlerOmonte1/LogisticaMinera` |
| Repositorio del frontend | `LogisticaMineraFront` (D-11: el frontend vive aparte) |
| Ramas por tipo | `main`, `feature/M0n-…`, `docs/{alcance}/…`, `chore/…` |
| Convención de commits | `M02: descripcion (HU-M02-01)` y `docs(alcance): Asunto` (CLAUDE.md) |
| Revisión por PR | PR #19, que fusionó F1 y F2 |
| Integración continua | `.github/workflows/backend.yml` (lint, migraciones, pytest sobre PostgreSQL, trazabilidad) y `docs.yml` (validadores de documentación) |

**Pasos para esta semana:**

1. **Limpiar la rama `feature/M03-ingresos`.** Sus tres commits son del alcance anterior
   («salidas» con «advertencia de stock») y confunden a quien revise el repositorio. Renómbrala, por
   ejemplo a `archivo/alcance-anterior-salidas`, o bórrala si ya no la necesitas; la rama real de F3
   se crea nueva desde `main`.
2. **Subir el arreglo del índice** (`scripts/indexar_docs.py` y `docs/INDICE.md`) para que el flujo
   `docs.yml` quede en verde: una insignia roja en la portada del repositorio resta.
3. **Etiquetar la versión entregada**, en los dos repositorios, el jueves al congelar:
   ```bash
   git tag -a v0.3.0 -m "Producto de la Unidad III: M01 y M02 integrados"
   ```
4. **Escribir un `CHANGELOG.md`** corto: v0.1.0 (F0), v0.2.0 (F1 y F2), v0.3.0 (interfaces).
5. **Capturas:** grafo de commits (`git log --graph --oneline --all`), lista de PR, ejecución verde
   de GitHub Actions, protección de la rama `main` si la configuras.

---

### 4.4 Base de datos implementada

**Qué espera el docente:** la base creada, no solo diseñada, y su modelo.

**Lo que ya tienes:** PostgreSQL 16 en Docker Compose (servicio `db`, puerto 5433 en el anfitrión);
migraciones de Django; modelo entidad-relación 3.1 en
`docs/00-arquitectura/modelo_datos_entidad_relacion.md`; carga de datos de prueba con
`python manage.py cargar_datos_prueba`.

**Tablas de dominio implementadas hoy (8):** `usuario`, `rol`, `vehiculo`, `transportista`,
`tipo_mineral`, `ingreso`, `contador_correlativo_ingreso`, `evento_auditoria`.

**Cómo documentarla (`04_base_de_datos.md`):**

1. **Diagrama desde la base real.** Conecta DBeaver o pgAdmin a `localhost:5433` y genera el
   diagrama E-R de las tablas de dominio. Así se ve que la base existe y coincide con el diseño.
2. **Diccionario de datos** por tabla: columna, tipo, nulo, restricción y regla de negocio que la
   respalda. Ejemplo:

   | Tabla | Columna | Tipo | Restricción | Regla |
   |---|---|---|---|---|
   | `vehiculo` | `placa` | varchar(10) | Única | RN-M02-01 |
   | `vehiculo` | `tara_tn` | numeric(8,2) | Nula al alta | RN-M02-11 |
   | `vehiculo` | `usuario_destare_id` | FK a `usuario` | PROTECT | RN-M02-11 |
   | `tipo_mineral` | `nombre` | varchar(100) | Única sin distinguir mayúsculas (`Lower`) | RN-M02-15 |
   | `transportista` | `ruc` | varchar(11) | Única | RN-M02-18 |
   | `ingreso` | `tara_tn`, `peso_bruto_tn` | numeric | CHECK tara < bruto | Coherencia de pesos |
   | `evento_auditoria` | `ingresos_relacionados` | bigint[] | Índice GIN | Historial de un ingreso |

3. **Integridad que vive en la base**, no solo en el código: claves únicas, `CHECK` de pesos,
   `PROTECT` en las claves foráneas (nada se borra en cascada, D-07), índice GIN.
4. **Migraciones:** captura de `python manage.py showmigrations` con todas aplicadas.
5. **Respaldo y restauración:** `scripts/respaldo.sh` y `scripts/restaurar.sh`, probados en F1
   (D-20). Una captura del respaldo generado basta.

> Docker Desktop está en pausa en este momento: reanúdalo antes de tomar las capturas.

---

### 4.5 Lógica de negocio y servicios

**Qué espera el docente:** que las reglas del negocio estén en el servidor, separadas de la
interfaz, y expuestas como servicios.

**Arquitectura por capas de cada app Django:** `models/` (entidades), `repositories/` (lectura),
`services/` (casos de uso y reglas), `serializers/` (contrato de entrada y salida), `views/` (HTTP),
`permissions.py` (autorización). La regla vive en `services/` y la vista solo traduce HTTP (D-08).

**Cómo documentarla (`05_logica_y_servicios.md`):**

1. **Catálogo de servicios REST** (se exporta de Swagger en `http://localhost:8000/api/v1/docs/`).
   Ejemplo:

   | Método | Ruta | Caso de uso | Roles |
   |---|---|---|---|
   | POST | `/api/v1/auth/login/` | Iniciar sesión | Todos |
   | POST | `/api/v1/auth/logout/` | Cerrar sesión | Todos |
   | GET, POST | `/api/v1/usuarios/` | Listar y crear usuarios | Administrador |
   | PATCH | `/api/v1/usuarios/{id}/desactivar/` y `reactivar/` | Baja lógica y reactivación | Administrador |
   | POST | `/api/v1/usuarios/{id}/restablecer-clave/` | Contraseña temporal | Administrador |
   | GET, POST | `/api/v1/catalogo/vehiculos/` | Listar y crear vehículos | Los tres roles |
   | PATCH | `/api/v1/catalogo/vehiculos/{id}/tara/` | Modificar la tara con motivo | Administrador |
   | GET, POST, PATCH | `/api/v1/catalogo/tipos-mineral/` | Tipos de mineral | Administrador y Administrativo |
   | GET, POST, PATCH | `/api/v1/catalogo/transportistas/` | Transportistas | Administrador y Administrativo |

   Verifica la tabla contra Swagger antes de entregarla.
2. **Reglas de negocio implementadas y su prueba.** Elige 8 a 10 representativas, por ejemplo:

   | Regla | Qué hace el sistema | Dónde | Prueba |
   |---|---|---|---|
   | RN-M01-05 | Bloquea la cuenta tras cinco intentos fallidos (423) | `accounts/services/autenticacion.py` | `test_autenticacion.py` |
   | HU-M01-01 CA09 | Obliga a cambiar la contraseña temporal | `accounts/autenticacion.py` | `test_autenticacion.py` |
   | RN-M02-11 | El vehículo nace sin tara, pendiente de destare | `catalogo/services/vehiculos.py` | `test_servicios.py` |
   | RN-M02-12 | Solo el Administrador cambia la tara, con motivo y auditoría | `catalogo/services/vehiculos.py` | `test_api.py` |
   | RN-M02-13 | El cambio de tara no altera ingresos ya registrados | ídem | `test_servicios.py` |
   | RN-M02-15 | Nombre de mineral único sin distinguir mayúsculas | Servicio y base | `test_modelos.py` |
   | RN-M02-08 | Nada se elimina: baja lógica, sin `DELETE` (D-22) | `catalogo/views/` | `test_api.py` |

3. **Calidad medible:** 143 pruebas automatizadas, cobertura del 97 %, trazabilidad de M01 al 94 % y
   de M02 al 100 % (fuente: `docs/03-pruebas/evidencias/F2/`).

---

### 4.6 Interfaces funcionales (el trabajo grueso de la semana)

**Qué espera el docente:** pantallas que el usuario pueda usar contra el sistema real.

**Situación:** el repositorio `LogisticaMineraFront` tiene Angular 17 con PWA y Material, pero sus
carpetas de `features/` son las del alcance anterior (`salidas`, `existencias`, `busqueda`,
`reportes`) y su `docs/estado-modulos.md` es del 09/09/2026. Ninguna pantalla está construida.

**Pasos:**

1. **Realinear la estructura** a los módulos vigentes: `autenticacion`, `usuarios`, `catalogo`,
   `ingresos`, `trazabilidad`, `consulta`, `consolidacion`, `auditoria`. Borra o archiva las
   carpetas del alcance anterior y actualiza `estado-modulos.md`.
2. **Infraestructura de `core/`:** interceptor que añade el token JWT, interceptor de errores que
   muestra el `mensaje` del cuerpo uniforme `{codigo, mensaje, detalles}` (D-23), guard de sesión y
   guard de rol.
3. **M01:** pantalla de inicio de sesión (con los mensajes literales de error y de bloqueo), cambio
   obligatorio de la contraseña temporal, cierre de sesión, menú lateral según el rol y gestión de
   usuarios para el Administrador.
4. **M02:** listados de vehículos, tipos de mineral y transportistas con el filtro de vigentes e
   inactivos; formularios de alta y edición; baja y reactivación; cambio de tara solo visible para el
   Administrador, con motivo obligatorio; marca «pendiente de destare».
5. **Copiar el diseño de la maqueta** (`Mockup/index.html`): ya está validada con la documentación,
   así que reproducirla evita decidir diseño esta semana.
6. **CORS:** añade `http://localhost:4200` a `CORS_ALLOWED_ORIGINS` en el `.env` del backend.

**Evidencia:** capturas de cada pantalla con datos reales y un video corto (2 a 3 minutos) del
recorrido de la sección 4.7. Para las pantallas de M03 a M08, muestra la maqueta y rotúlala
«prototipo navegable, iteraciones siguientes».

---

### 4.7 Módulos integrados

**Qué espera el docente:** que los módulos funcionen juntos, no aislados.

**Integraciones que ya funcionan en el backend:**

- M01 → todos: la sesión JWT y la matriz de permisos son la única definición de autorización
  (RN-M01-09); M02 la importa, no la reescribe.
- M02 → M09: toda alta, cambio, baja, reactivación y cambio de tara queda en `evento_auditoria`.
- M01 → M09: inicio y cierre de sesión y accesos rechazados quedan auditados.
- M02 → M03 (preparada): `registrar_tara()` y el alta de vehículo y de tipo de mineral desde el
  registro ya existen para que M03 los use.

**Guion de la demostración integrada** (el mismo del video):

1. El Supervisor inicia sesión y ve solo sus opciones del menú.
2. Intenta editar un vehículo → «Acción no autorizada» (403).
3. Da de alta un vehículo nuevo → queda «pendiente de destare».
4. El Administrativo inicia sesión e intenta cambiar una tara → «Solo el Administrador puede
   modificar la tara del vehículo».
5. El Administrador cambia la tara sin motivo (rechazo) y con motivo (aceptado).
6. Se muestra en la base, o en el historial de auditoría, el evento con el valor anterior, el nuevo y
   el motivo.

**Evidencia automática:** la regresión de Newman de F0 a F2 (80 peticiones, 261 aserciones, 0
fallos) en `docs/03-pruebas/evidencias/F2/newman.xml`. Repítela el jueves y adjunta la captura:

```bash
npx --yes newman@6.2.1 run postman/LogisticaMinera.postman_collection.json -e postman/entornos/local.postman_environment.json --folder "00 · Sesiones" --folder "F0 · Salud y esquema" --folder "F1 · M01 Autenticacion y roles" --folder "F2 · M02 Catalogo maestro"
```

---

### 4.8 Roles, permisos y mecanismos básicos de seguridad

**Roles:** Administrador, Administrativo y Supervisor de planta.

**Matriz de permisos implementada (extracto para el documento):**

| Operación | Administrador | Administrativo | Supervisor de planta |
|---|:-:|:-:|:-:|
| Consultar el catálogo | Sí | Sí | Sí |
| Dar de alta un vehículo (también desde el registro) | Sí | Sí | Sí |
| Editar, dar de baja o reactivar el catálogo | Sí | Sí | No |
| Modificar una tara ya registrada | Sí | No | No |
| Gestionar usuarios | Sí | No | No |

**Mecanismos de seguridad implementados, cada uno con su prueba:**

| Control | Implementación | Cómo se verifica |
|---|---|---|
| Autenticación | JWT (SimpleJWT) con token de acceso y de refresco; lista negra al cerrar sesión | `test_autenticacion.py`; Newman HU-M01-01 CA05 |
| Bloqueo por fuerza bruta | 5 intentos fallidos bloquean 15 minutos (423) | Newman HU-M01-01 CA03 |
| Contraseñas | Hash de Django; temporal generada con `secrets`; cambio obligatorio | `test_usuarios.py` |
| Autorización | Una clase de permiso por operación; el rol se lee de la base en cada solicitud | `test_permisos.py` |
| Rechazo auditado | Todo 403 queda como `ACCESO_RECHAZADO` | `catalogo/tests/test_permisos.py` |
| Auditoría | Servicio único de escritura; nunca guarda contraseñas | `auditoria/tests/test_servicio.py` |
| Sin borrado | Ninguna ruta acepta `DELETE` (D-22); bajas lógicas (D-07) | Newman RN-M02-08 (405) |
| Errores uniformes | Cuerpo `{codigo, mensaje, detalles}` sin trazas internas (D-23) | Todas las pruebas de rechazo |
| Secretos | Variables de entorno en `.env` fuera del repositorio; datos de prueba solo con `DEBUG` | Revisión de `.gitignore` |
| Respaldo | `pg_dump` y copia del volumen `media`, con restauración probada (D-20) | Prueba registrada en F1 |

---

### 4.9 Registro de incidencias

**Qué espera el docente:** que los problemas encontrados se registren, se clasifiquen y se cierren
con evidencia.

**Formato:** el de PLAN-01 §7.2 (ID, historia, entorno, precondición, pasos, resultado esperado,
resultado obtenido, severidad), en **GitHub Issues** con etiquetas `incidencia`,
`severidad:critica|alta|media|baja` y el módulo. Crea una plantilla en
`.github/ISSUE_TEMPLATE/incidencia.md` del frontend y del backend.

**Incidencias reales ya ocurridas** (regístralas con su fecha y su commit de corrección):

| ID | Fecha | Componente | Descripción | Severidad | Corrección | Estado |
|---|---|---|---|---|---|---|
| DEF-001 | 24/10/2026 | Migraciones | La migración 0003 de catálogo se aplicaba antes de la FK de ingresos | Alta | Dependencia explícita `ingresos 0001` en `catalogo 0003` | Cerrada |
| DEF-002 | 24/10/2026 | Postman | Las URL sin barra final provocaban un error 500 por `APPEND_SLASH` | Media | URL en texto con barra final | Cerrada |
| DEF-003 | 24/10/2026 | Trazabilidad | `reporte_trazabilidad.py` recorría los entornos virtuales | Baja | Se limita a `backend/apps` | Cerrada |
| DEF-004 | 25/10/2026 | M01 | La sesión expirada no se detectaba porque el mensaje de SimpleJWT venía traducido | Alta | Se compara la raíz «expir» | Cerrada |
| DEF-005 | 25/10/2026 | Postman | La prueba del bloqueo fallaba por peticiones en paralelo | Media | Intentos encadenados en serie | Cerrada |
| DEF-006 | 26/10/2026 | Pruebas | En el contenedor, pytest toma `config.settings.development` del entorno en lugar de la configuración de pruebas | Media | Pendiente: `--ds=config.settings.test` en `pytest.ini` | Abierta |
| DEF-007 | 02/11/2026 | CI de documentación | `validar_docs.py` falla en GitHub por enlaces a `.DS_Store` en el índice | Media | `indexar_docs.py` omite archivos ocultos | Corregida, por subir |
| DEF-008 | 02/11/2026 | Repositorio | La rama `feature/M03-ingresos` contiene commits del alcance anterior | Baja | Renombrar o archivar la rama | Abierta |

Las incidencias que salgan esta semana del frontend se registran igual. Que haya incidencias
abiertas no es malo: muestra un proceso vivo. Lo que resta es que no estén registradas.

**Evidencia:** captura de la lista de issues con sus etiquetas y uno abierto en detalle.

---

### 4.10 Documentación técnica preliminar

**Qué espera el docente:** que otro desarrollador pueda entender, instalar y continuar el sistema.

**Lo que ya existe** y solo hay que ordenar en un documento índice (`10_documentacion_tecnica.md`):

| Sección | Fuente |
|---|---|
| 1. Visión y alcance | `docs/00-tesis/marco_tesis.md` (RF01 a RF10, reglas V1 a V5) |
| 2. Arquitectura | `docs/model-c4/`: ARQ-01 módulos, ARQ-02 arquitectura técnica, ARQ-03 modelo C4 (con PDF) |
| 3. Decisiones de diseño | `docs/00-arquitectura/decisiones_diseno.md` (D-01 a D-24) |
| 4. Modelo de datos | `docs/00-arquitectura/modelo_datos_entidad_relacion.md` y el diccionario de 4.4 |
| 5. Especificación por módulo | `docs/modulos/M01` a `M09`: historias, requerimientos, diagramas UML y notas |
| 6. API | Swagger en `/api/v1/docs/` y el esquema OpenAPI en `/api/v1/esquema/` |
| 7. Convenciones | `docs/00-arquitectura/convenciones_codigo.md`, `GUIA_MARCO_DE_TRABAJO.md`, `GUIA_FRONTEND_ANGULAR.md` |
| 8. Instalación y ejecución | `README.md` del backend y `docs/entorno.md` del frontend |
| 9. Pruebas | `docs/03-pruebas/plan_de_pruebas.md`, colección Postman, bitácora de puertas |

**Lo que hay que escribir nuevo (una página):** *guía de instalación rápida* probada en limpio:

```bash
docker compose up -d
docker compose exec -T backend python manage.py migrate
docker compose exec -T backend python manage.py cargar_datos_prueba
```

Y para el frontend: `npm install` y `ng serve`, con la URL del backend. Pruébala clonando los
repositorios en otra carpeta: si falla, el docente también fallará.

---

### 4.11 Evidencias de las iteraciones de desarrollo

**Qué espera el docente:** prueba de que se trabajó por iteraciones, con resultados verificables en
cada una.

**Lo que ya existe:** `docs/03-pruebas/bitacora_puertas.md` (una fila por puerta) y las carpetas
`docs/03-pruebas/evidencias/F1/` y `F2/` con `pytest.txt`, `calidad.txt`, `trazabilidad.md` y
`newman.xml`.

**Ficha por iteración (`11_evidencias/iteracion_N.md`).** Ejemplo completo con la iteración 2:

> **Iteración 2 — F2 Catálogo maestro**
>
> | Campo | Valor |
> |---|---|
> | Fechas | 26/10/2026; fusionada el 02/11/2026 (PR #19) |
> | Objetivo | Vehículos con titularidad, capacidad y tara; tipos de mineral; transportistas; baja lógica y reactivación |
> | Historias | HU-M02-01, HU-M02-02, HU-M02-03 |
> | Commits | `21112af` (D-24), `c1240c6` (código M02) |
> | Pruebas | 143 aprobadas sobre PostgreSQL 16, 0 fallos; cobertura del 97 % |
> | Postman | 80 peticiones de F0 a F2, 261 aserciones, 0 fallos |
> | Trazabilidad | M02 al 100 %: 30 criterios y 19 reglas con prueba |
> | Decisiones tomadas | D-24: patrón de placa configurable y alta rápida desde el registro |
> | Incidencias | DEF-006 (abierta) |
> | Resultado de la puerta | Aprobada, observada: el catálogo es provisional hasta recibir el de la empresa |
> | Capturas | Newman en verde, Swagger de `/catalogo/`, base con las tablas nuevas |
> | Lecciones | La búsqueda exacta por placa se necesitará en M03; se adelantó aquí |

Haz una ficha para la iteración 0 (F0), 1 (F1), 2 (F2) y 3 (frontend de esta semana). La 3 es la que
hay que generar: anota cada día qué se hizo, qué falló y cómo se resolvió.

---

## 5. Estructura de la carpeta de entrega

```
entregables/unidad-III/
├── GUIA_PRODUCTO_UNIDAD_III.md       esta guía (no se entrega)
├── 00_portada_e_indice.md
├── 01_plan_de_desarrollo.md
├── 02_backlog_priorizado.md          + captura del tablero de GitHub Projects
├── 03_repositorio.md                 enlaces, ramas, PR, CI, etiqueta v0.3.0
├── 04_base_de_datos.md               diagrama, diccionario, migraciones
├── 05_logica_y_servicios.md          servicios REST y reglas con su prueba
├── 06_interfaces.md                  capturas y enlace al video
├── 07_integracion.md                 guion de la demostración y Newman
├── 08_seguridad.md                   roles, matriz y controles
├── 09_registro_incidencias.md        tabla y enlace a GitHub Issues
├── 10_documentacion_tecnica.md       índice de la documentación existente
├── 11_evidencias/
│   ├── iteracion_0_F0.md
│   ├── iteracion_1_F1.md
│   ├── iteracion_2_F2.md
│   ├── iteracion_3_frontend.md
│   └── capturas/
└── Producto_Unidad_III.pdf           todo lo anterior unido
```

El PDF final se genera con el script que ya tienes, que convierte un Markdown por vez (requiere el
paquete `markdown` y Chrome). Une primero los documentos en uno solo y conviértelo:

```bash
python3 scripts/md_a_pdf.py entregables/unidad-III/Producto_Unidad_III.md
```

---

## 6. Lista de control para el viernes

- [ ] El código está congelado desde el jueves a las 18:00 y etiquetado `v0.3.0` en los dos repositorios.
- [ ] Los flujos de GitHub Actions están en verde (con DEF-007 subido).
- [ ] La rama del alcance anterior está renombrada o archivada.
- [ ] La guía de instalación funciona en una carpeta limpia.
- [ ] El recorrido integrado funciona con los tres roles y está grabado en video.
- [ ] Newman de F0 a F2 está en verde y tiene captura.
- [ ] El backlog está en GitHub Projects, con el estado real de cada historia.
- [ ] Las incidencias están en GitHub Issues, incluidas las del frontend de esta semana.
- [ ] Hay una ficha por iteración, de la 0 a la 3, con sus evidencias.
- [ ] Las capturas de la base son de la base real, no del diseño.
- [ ] Las pantallas de la maqueta están rotuladas como prototipo.
- [ ] El PDF está generado y revisado completo.

---

## 7. Decisiones que debes tomar hoy

1. **Alcance de las interfaces.** Recomendado: M01 y M02 completos en Angular; el resto con la
   maqueta. La alternativa —empezar F3 en el backend— deja la entrega sin ninguna pantalla real.
2. **Tablero y registro de incidencias en GitHub.** Recomendado: sí, porque la captura sirve de
   evidencia directa; la alternativa es una tabla en Markdown, válida pero menos convincente.
3. **Qué hacer con `feature/M03-ingresos`.** Recomendado: renombrarla como archivo, no borrarla.
