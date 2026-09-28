# PLAN-01 — Plan de trabajo, pruebas y entrega

**Documento:** PLAN-01
**Versión:** 2.0
**Estado:** Vigente
**Alcance:** Sistema web inteligente de control de inventarios de ingreso de mineral (M01 a M09,
ver `../model-c4/ARQ-01_Modulos_del_Sistema.md`)

---

## 1. Propósito

Definir cómo se construye, se prueba y se acepta cada entregable del sistema, de modo que en
cualquier momento se pueda responder tres preguntas sin improvisar:

1. Qué está terminado y con qué evidencia.
2. Quién lo verificó y contra qué criterio.
3. Qué falta y qué lo bloquea.

El plan no reemplaza la documentación de requisitos. La consume: cada módulo ya tiene sus RU, RF,
RNF, RN y RS en `../modulos/Mxx-*/requerimientos/`, y sus historias con criterios de aceptación en
`../HistoriasUsuario.md`. Este documento describe el proceso que convierte esos criterios en
software verificado.

---

## 2. Roles y responsabilidades

| Rol | Responsabilidad principal | Produce |
|---|---|---|
| Responsable técnico | Decisiones de arquitectura, revisión de PR, control de alcance, cierre de D-12 y D-14 | Decisiones en `decisiones_diseno.md`, aprobación de PR |
| Desarrollo backend | Modelos, reglas de negocio, servicios, API, adaptadores del motor de reconocimiento | Código, migraciones, pruebas unitarias y de integración |
| Desarrollo frontend | Aplicación Angular: captura de imagen, pantalla de confirmación, consultas | Código, pruebas de componente |
| Tester / QA | Diseño y ejecución de pruebas, gestión de defectos, conjunto de prueba de ERA y TDI | Casos de prueba, reportes de defecto, acta de pruebas |
| Jefatura de operaciones | Validación funcional con datos reales de planta | Aceptación de usuario firmada por módulo |
| Administrador de base de datos (rol compartido) | Revisión de migraciones e índices | Visto bueno de migración antes de preproducción |

En un equipo reducido una persona puede asumir varios roles, con una excepción que no se negocia:
**quien desarrolla una historia no es quien la aprueba en pruebas**. Si el equipo es de dos
personas, se cruzan: el backend prueba las historias del frontend y viceversa.

---

## 3. Entornos y ramas

### 3.1 Entornos

| Entorno | Base de datos | Uso | Quién despliega |
|---|---|---|---|
| Desarrollo | Local por desarrollador | Trabajo diario | Cada desarrollador |
| Preproducción | Copia anonimizada de producción | Pruebas de aceptación y de rendimiento | Responsable técnico |
| Producción | Servidor de planta | Operación real, solo después del pretest de la investigación | Responsable técnico, con registro de despliegue |

**El sistema no se usa en planta hasta que el pretest de la investigación haya terminado**
(`../00-tesis/marco_tesis.md` §11). Todo despliegue a producción realizado durante la ventana de
medición del postest se anota en el registro de despliegues con fecha, hora, versión y motivo. Un
despliegue sin registrar introduce un cambio no controlado en las condiciones de observación
(`../model-c4/ARQ-02_Arquitectura_Tecnica.md` §7).

### 3.2 Ramas

```
main                      Código desplegado en producción, siempre etiquetado
develop                   Integración; de aquí sale preproducción
feature/M04-reconocimiento  Una rama por módulo
fix/M03-marcas-tiempo       Corrección de defecto reportado
```

Nada entra a `develop` sin pull request. Nada entra a `main` sin acta de pruebas del alcance que
se despliega.

---

## 4. Ciclo de vida de un entregable

El entregable mínimo es la **historia de usuario**, no el módulo. Un módulo se cierra cuando todas
sus historias están aceptadas.

```
Requisito -> Listo para desarrollar -> En desarrollo -> En revisión -> En pruebas -> Aceptado -> Desplegado
```

### 4.1 Definición de listo (antes de empezar a codificar)

Una historia solo entra en desarrollo si cumple todo lo siguiente:

- [ ] Tiene criterios de aceptación escritos en `HistoriasUsuario.md` o en el `HU.md` del módulo.
- [ ] Las reglas de negocio que la afectan están identificadas (RN-Mxx-nn).
- [ ] Las entidades que toca están en `modelo_datos_entidad_relacion.md`.
- [ ] El contrato de la ruta está definido en `ARQ-02` §6, o se define en esta historia.
- [ ] No depende de una decisión abierta. Si depende, la decisión se cierra primero.

Una historia que no pasa esta lista no se estima ni se programa. Se devuelve a análisis.

### 4.2 Desarrollo

Se sigue el orden del flujo de trabajo por módulo de `../00-arquitectura/GUIA_MARCO_DE_TRABAJO.md`
§4: modelos, repositorios, servicios, serializadores y vistas, permisos, migración, pruebas,
frontend. Cada paso produce evidencia citable.

Commits por historia, con el formato de `convenciones_codigo.md` §4:

```
M04: reconoce placa fecha y peso bruto del ticket (HU-M04-01)
```

### 4.3 Revisión

El pull request incluye, sin excepción:

- Lista de historias cerradas con su código.
- Salida de `pytest` con las pruebas nuevas visibles.
- Salida de `ruff check`.
- El SQL de las migraciones nuevas (`python manage.py sqlmigrate`).
- Nota de cualquier decisión tomada durante la implementación que no estuviera documentada.

El revisor verifica la definición de terminado (§5) antes de aprobar. Un PR aprobado sin esa
verificación traslada el defecto a pruebas, donde cuesta varias veces más.

### 4.4 Pruebas

El tester recibe la historia en preproducción con datos de prueba cargados. Ejecuta los casos
diseñados a partir de los criterios de aceptación y registra el resultado. Una historia rechazada
vuelve a desarrollo con el defecto documentado; no se discute verbalmente.

### 4.5 Aceptación

Al cierre de cada módulo, la jefatura de operaciones ejecuta el escenario de aceptación con datos
propios de la planta. La firma de esa acta es lo que permite mover el módulo a producción.

---

## 5. Definición de terminado

Es la de `GUIA_MARCO_DE_TRABAJO.md` §5, ampliada con los puntos de verificación y escalabilidad
que exige este plan. Una historia está terminada cuando:

**Corrección**

- [ ] Cada RN implicada tiene una prueba que falla si se elimina la regla.
- [ ] Cada criterio de aceptación tiene su caso de prueba automatizado o ejecutado y registrado.
- [ ] Los mensajes de error visibles coinciden literalmente con los criterios de aceptación.
- [ ] Los permisos están declarados por acción y existe una prueba de rechazo por rol.

**Arquitectura**

- [ ] Ninguna regla de negocio vive en `views/` ni existe únicamente en Angular.
- [ ] `repositories/` no escribe; `services/` no consulta para presentar.
- [ ] Las acciones de escritura registran evento en M09.
- [ ] Ninguna entidad se borra físicamente: baja lógica o anulación con motivo.
- [ ] Ningún valor reconocido se persiste sin confirmación del usuario; el valor reconocido y el
      confirmado se guardan por separado.

**Escalabilidad**

- [ ] Todo listado devuelve resultados paginados; ninguno devuelve la tabla completa.
- [ ] Las consultas del módulo usan los índices declarados en `modelo_datos_entidad_relacion.md` §3,
      creados en migración desde el inicio y no añadidos al final.
- [ ] No hay consultas en bucle (`N+1`); las relaciones se resuelven con `select_related` o
      `prefetch_related` y se verifica con `assertNumQueries` en la prueba del listado.
- [ ] Las cantidades y pesos usan tipo decimal, nunca punto flotante.
- [ ] El contrato de la ruta respeta el prefijo de versión `/api/v1/`; un cambio incompatible abre
      una versión nueva, no modifica la existente.
- [ ] La migración es reversible o documenta explícitamente por qué no lo es.

**Trazabilidad**

- [ ] Los commits referencian su historia.
- [ ] La fila correspondiente de la matriz de trazabilidad está actualizada.

---

## 6. Estrategia de pruebas

### 6.1 Niveles

| Nivel | Qué verifica | Herramienta | Responsable | Cuándo |
|---|---|---|---|---|
| Unitaria | Reglas de negocio y validaciones en `models/` y `services/` | pytest | Desarrollo | En cada commit |
| Integración | Servicio completo contra base de datos real, con transacciones | pytest + pytest-django | Desarrollo | Al cerrar la historia |
| Contrato de API | Códigos de estado, forma del cuerpo, cuerpo de error uniforme | pytest + cliente DRF | Desarrollo | Al cerrar la historia |
| Permisos | Acceso y rechazo por cada rol declarado | pytest | Desarrollo | Al cerrar la historia |
| Reconocimiento (ERA) | Exactitud de lectura del motor sobre el conjunto de tickets de prueba | Script sobre el conjunto de prueba (`plan_de_pruebas.md`) | Desarrollo + Tester | Al cerrar M04 y ante cambio de motor |
| Validación (TDI) | Detección de cada tipo de inconsistencia sembrada | pytest + conjunto sembrado | Desarrollo | Al cerrar M05 y ante cambio de reglas |
| Componente frontend | Validaciones y estados de la interfaz, incluida la pantalla de confirmación | Karma / Jasmine | Desarrollo | Al cerrar la historia |
| Funcional de extremo a extremo | El criterio de aceptación tal como lo vive el usuario | Manual guiada por caso de prueba | Tester | Al pasar a preproducción |
| Rendimiento | RNF de tiempo de respuesta y de reconocimiento | Herramienta de carga a definir en preproducción | Tester | Semana de estabilización y ante cambio de consultas |
| Aceptación de usuario | Operación real con datos de planta | Manual | Jefatura de operaciones | Cierre de cada módulo |

### 6.2 Nomenclatura y trazabilidad de casos

Dos niveles de caso de prueba, según `convenciones_codigo.md` §1:

- **`CPnn`**, uno por requerimiento funcional (RF01 a RF10), para el indicador de la lista de
  control de funcionalidad. Viven en `../03-pruebas/plan_de_pruebas.md`.
- **`CP-HU-Mxx-nn-nn`**, uno por criterio de aceptación, para la cobertura de cada historia. Las
  pruebas automatizadas se nombran `test_<CODIGO>_<enunciado>`, por ejemplo:

```python
def test_RN_M03_04_peso_neto_no_se_calcula_se_lee_del_ticket(): ...
def test_RN_M04_02_valor_reconocido_y_confirmado_se_guardan_por_separado(): ...
```

La cadena completa de trazabilidad es la de `convenciones_codigo.md` §5:

```
RF  ->  Módulo  ->  HU  ->  Caso de prueba  ->  Commit
```

Cada eslabón debe poder recorrerse en ambos sentidos. Si un caso de prueba no se puede vincular a
un criterio de aceptación, sobra o falta el requisito. La relación de cada RF y cada caso con los
indicadores de la tesis se consulta en `../02-trazabilidad/matriz_HU_RF_indicador.md`, no aquí.

### 6.3 Criterios de cobertura

No se persigue un porcentaje global de cobertura, que premia probar lo trivial. Se exige cobertura
por obligación:

- El 100 % de las reglas de negocio (RN) tiene prueba.
- El 100 % de los criterios de aceptación tiene caso de prueba ejecutado.
- El 100 % de las acciones con permiso declarado tiene prueba de rechazo.
- El 100 % de las reglas de validación (V1 a V5) tiene una prueba que sembra la inconsistencia
  correspondiente y verifica que se detecta.
- Los servicios de `services/` no bajan del 80 % de líneas cubiertas.
- Las vistas y serializadores se cubren por las pruebas de contrato, no por pruebas propias.

### 6.4 Datos de prueba

Se construyen con `factory-boy`, nunca con registros creados a mano dentro de la prueba. Existe un
juego de datos de preproducción que reproduce un mes de operación de planta: catálogo completo,
ingresos con reconocimiento exitoso y con reconocimiento fallido, ingresos con cada una de las
inconsistencias V1 a V5, lotes en distintos puntos de su recorrido por las etapas, y un mes sin
ingresos, porque la consolidación de un mes vacío es un caso de prueba obligatorio (HU-M08-01 CA03).

El conjunto de tickets reales para medir ERA y TDI se guarda aparte, con las inconsistencias
sembradas documentadas en `../03-pruebas/plan_de_pruebas.md` §4 (DR-08): no se genera
sintéticamente, porque la exactitud del reconocimiento solo es significativa sobre fotografías
reales de tickets de la balanza.

### 6.5 Pruebas de regresión

Antes de cada despliegue a producción se ejecuta la suite completa más el juego manual de
regresión, que cubre como mínimo:

1. Registro de un ingreso a partir de la imagen del ticket y verificación de las tres marcas de
   tiempo como valores distintos.
2. Reconocimiento de un ticket con un campo ilegible, que debe quedar vacío y editable, sin valor
   inventado.
3. Confirmación de un ingreso con una inconsistencia V4 (peso fuera de rango), que exige
   justificación y no bloquea.
4. Corrección de un dato de un ingreso ya registrado, con motivo y revalidación.
5. Anulación de un ingreso y su exclusión de los totales, sin desaparecer del histórico.
6. Consulta de un ingreso por placa y fecha, con su imagen de respaldo.
7. Asignación de un ingreso a un lote y registro del paso por las cuatro etapas, respetando el
   orden.
8. Consolidado mensual de un mes con ingresos y de un mes sin ingresos, y su exportación.
9. Acceso denegado a cada acción restringida, con un usuario de cada rol.

---

## 7. Gestión de defectos

### 7.1 Severidad y plazo

| Severidad | Definición | Plazo de atención |
|---|---|---|
| Crítica | Impide registrar un ingreso, corrompe el histórico o expone datos a un rol sin permiso | Mismo día, bloquea el despliegue |
| Alta | Un criterio de aceptación no se cumple y no hay forma manual de sortearlo | Antes de cerrar el módulo |
| Media | El criterio se cumple pero con comportamiento incorrecto en un caso secundario | Dentro de la semana siguiente |
| Baja | Textos, presentación, comodidad de uso | Semana de estabilización |

Un defecto que afecte alguna de las tres marcas de tiempo, el código único, o la separación entre
el valor reconocido y el confirmado es **crítico por definición**, aunque parezca cosmético: son
los puntos donde un error produce datos que parecen correctos.

### 7.2 Contenido mínimo de un reporte

Un defecto sin estos datos se devuelve sin analizar:

```
ID:            DEF-nnn
Historia:      HU-M03-01 / CA07
Entorno:       Preproducción, versión 0.4.2
Precondición:  Usuario supervisor de planta, catálogo cargado
Pasos:         1. ... 2. ... 3. ...
Resultado esperado:  (texto literal del criterio de aceptación)
Resultado obtenido:  (lo que ocurrió, con captura o respuesta de la API)
Severidad:     Alta
```

Toda corrección de defecto añade la prueba automatizada que lo habría detectado. Sin esa prueba, la
corrección no se aprueba.

---

## 8. Cronograma con entregables verificables

El orden de construcción es el de `ARQ-01` §6: M01 y M02 primero, M03 después, M04 y M05 inyectados
en M03 desde el principio, M09 junto con las operaciones que audita, y M06, M07, M08 al final,
porque leen sobre lo que M03 ya produce. La columna de verificación indica **quién** valida y **con
qué evidencia**; sin esa evidencia la semana no se da por cerrada.

### Semana 1 — Base técnica y M01

| Actividad | Entregable | Verificación |
|---|---|---|
| Esqueleto backend, PostgreSQL, ajustes por entorno | Proyecto que arranca con `runserver` y `pytest` en verde | Responsable técnico |
| Esqueleto Angular | Aplicación que carga y navega entre pantallas | Responsable técnico |
| M01 completo | Inicio y cierre de sesión, expiración, bloqueo por intentos, menú por rol | Tester: casos de HU-M01-01 a HU-M01-03 |
| Decisiones de arquitectura firmadas | `decisiones_diseno.md` sin decisiones abiertas que bloqueen M03 | Responsable técnico |

Riesgo de la semana: si D-12 (motor de reconocimiento) no tiene al menos un candidato para el
piloto, M04 no puede arrancar en la semana 3.

### Semana 2 — M02 y piloto de motores de reconocimiento

| Actividad | Entregable | Verificación |
|---|---|---|
| M02 catálogo maestro | Alta, edición y baja lógica de vehículos, tipos de mineral y transportistas | Tester: HU-M02-01 a HU-M02-03 |
| Capacidad de carga del vehículo | Campo disponible para que V4 lo consuma en M05 | Prueba de contrato automatizada |
| Piloto de D-12 | Comparación de 20 a 30 tickets reales entre dos o tres motores; motor elegido y documentado | Responsable técnico |

### Semana 3 — M03 con M04 y M05 inyectados

| Actividad | Entregable | Verificación |
|---|---|---|
| Captura de imagen y propuesta de reconocimiento | Foto del ticket que devuelve la placa, la fecha y el peso bruto con su confianza | Tester: HU-M04-01 |
| Pantalla de confirmación con validación | Inconsistencias señaladas junto al campo, con mensaje literal de V1 a V5 | Tester: HU-M05-01 |
| Registro del ingreso | Ingreso persistido con código único y tres marcas de tiempo distintas | Tester: HU-M03-01 |
| Corrección y anulación | Corrección con motivo y revalidación; anulación excluida de totales | Tester: HU-M03-02, HU-M03-03 |

Hito de la semana: a partir de aquí el sistema produce el dato completo que la ficha de observación
de la investigación contrasta en el postest.

### Semana 4 — M09 Auditoría

| Actividad | Entregable | Verificación |
|---|---|---|
| Registro de eventos de M01 a M05 | Evento por cada creación, modificación, anulación, reconocimiento y corrección | Prueba automatizada por acción |
| Registro de acceso rechazado | Evento por cada intento sin permiso | Tester |
| Consulta del historial de una entidad | Historial cronológico con valores anteriores y nuevos | Tester: HU-M09-02 |

### Semana 5 — M06 Trazabilidad

| Actividad | Entregable | Verificación |
|---|---|---|
| Gestión de lotes de proceso | Apertura, composición y cierre de un lote | Tester: HU-M06-01 |
| Registro del paso por etapa | Secado, zarandeo, molienda y ensacado, en orden | Tester: HU-M06-02 |
| Consulta de trazabilidad de un ingreso | Recorrido de las cuatro etapas a través del lote | Tester: HU-M06-03 |

Precondición: la forma real de agrupar el mineral en cancha debe verificarse con la jefatura de
operaciones antes de esta semana. Si el vínculo directo es más fiel que el lote, este módulo se
ajusta antes de implementarse.

### Semana 6 — M07 Consulta

| Actividad | Entregable | Verificación |
|---|---|---|
| Búsqueda por placa y fecha | Recuperación del ingreso y su ticket de respaldo en menos de un minuto | Medición cronometrada por el tester |
| Listado con filtros combinables | Fecha, tipo de mineral, vehículo, titularidad y estado | Tester |
| Detalle completo del ingreso | Datos, imagen, reconocimiento, validaciones y trazabilidad en una vista | Tester: HU-M07-01, HU-M07-02 |

### Semana 7 — M08 Consolidación

| Actividad | Entregable | Verificación |
|---|---|---|
| Total acumulado mensual por tipo de mineral | Reporte generado a demanda, sin acumulado almacenado | Jefatura de operaciones |
| Mes sin ingresos | Consolidado que informa ausencia de producción, sin error | Caso de prueba obligatorio |
| Exportación a hoja de cálculo | Archivo con el mismo total que la consulta en pantalla | Tester |

### Semana 8 — Estabilización e instrumentos de la variable independiente

| Actividad | Entregable | Verificación |
|---|---|---|
| Suite completa de regresión | Ejecución sin fallos de las pruebas automatizadas y del juego manual | Tester |
| Lista de control de funcionalidad (RFC, CPS) | Los 10 RF y sus 10 casos de prueba superados | Tester y responsable técnico |
| Ficha de capacidad inteligente, hojas A, B y C (ERA, TDI, TCA) | Conjunto de prueba de 50 tickets y 10 inconsistencias sembradas, ejecutado y registrado | Tester |
| Cuestionario SUS | Aplicado a los usuarios que ejecutan las tareas T01 a T06 | Jefatura de operaciones |
| Corrección de defectos abiertos | Ningún defecto crítico ni alto pendiente | Tester |
| Congelamiento de motor y reglas (D-16) | Versión del motor y de las reglas V1 a V5 fijada antes de iniciar el postest | Responsable técnico |

No se desarrolla funcionalidad nueva en esta semana. Esta semana **no** aplica una prueba de carga
con una herramienta específica de la tesis: los instrumentos que se aplican son los de la variable
independiente (lista de control, ficha de capacidad inteligente, SUS), no un protocolo de carga
técnico. Una historia que no esté terminada en la semana 7 se retira del alcance y se documenta, en
lugar de comprimir la estabilización.

**Condición de todo el cronograma:** el sistema queda listo al final de la semana 8, pero no entra
en operación real en planta hasta que el pretest de la investigación —sobre el proceso manual
actual— haya concluido (`../00-tesis/marco_tesis.md` §11).

---

## 9. Criterios de escalabilidad por entregable

Cada entregable se construye pensando en el volumen de operación continuada, no en el de la
demostración. Los controles concretos son estos:

| Ámbito | Regla | Cómo se verifica |
|---|---|---|
| Consultas | Todo listado pagina; el tamaño de página tiene tope | Prueba de contrato con más registros que el tope |
| Índices | Los declarados en el modelo de datos se crean en la primera migración del módulo | Revisión del `sqlmigrate` en el PR |
| Consultas repetidas | Ninguna vista genera consultas en bucle | `assertNumQueries` en la prueba del listado |
| Totales | El total mensual y el de un lote se calculan por agregación en una sola consulta, nunca recorriendo registros en el lenguaje de aplicación | Prueba de tiempo de respuesta con histórico cargado |
| Contratos | La API se versiona en la ruta; los cambios incompatibles abren `/api/v2/` | Revisión de PR |
| Acoplamiento | Un módulo nuevo se agrega sin modificar los existentes (motor de reconocimiento, reglas de validación, exportadores) | Revisión de PR contra los ejemplos de `ARQ-03` §4 |
| Datos | Cantidades en decimal; sin borrado físico; sin campos de texto libre donde hay dominio cerrado | Prueba de regla de negocio |
| Crecimiento del histórico | Las consultas de consulta y consolidación se miden con volumen simulado de un año | Prueba de rendimiento de la semana de estabilización, repetida ante cambios de consulta |

La prueba de rendimiento no se ejecuta una sola vez al final. Se repite cada vez que se modifica una
consulta que sostiene un RNF de tiempo de respuesta.

---

## 10. Seguimiento del proyecto

### 10.1 Ritmo

| Reunión | Frecuencia | Duración | Salida |
|---|---|---|---|
| Coordinación de desarrollo | Diaria | 15 minutos | Bloqueos identificados |
| Cierre de semana | Semanal | 1 hora | Entregable verificado o causa documentada del desvío |
| Revisión con la jefatura de operaciones | Al cierre de cada módulo | 1 hora | Acta de aceptación |

### 10.2 Indicadores de seguimiento del proyecto

| Indicador | Cálculo | Meta |
|---|---|---|
| Avance de implementación | RF cumplidos sobre 10 (RFC) | Según cronograma semanal |
| Historias aceptadas | Historias con acta sobre historias del módulo | 100 % antes de cerrar el módulo |
| Defectos abiertos por severidad | Conteo vigente | Cero críticos y altos antes de desplegar |
| Defectos escapados a producción | Defectos hallados en producción sobre total del módulo | Menor a 10 % |
| Reglas de negocio con prueba | RN cubiertas sobre RN declaradas | 100 % |

El denominador del avance son los **10 requerimientos funcionales**, no un número de módulos: un
módulo puede cubrir varios RF y viceversa (`ARQ-01` §1). Los indicadores de la variable dependiente
de la investigación (I1 a I6) se miden por observación directa durante el pretest y el postest, no
sobre estos datos de seguimiento del proyecto; su relación con el sistema vive únicamente en
`../02-trazabilidad/matriz_HU_RF_indicador.md`.

### 10.3 Control de cambios

Toda solicitud de funcionalidad no prevista se evalúa contra la lista cerrada de módulos de
`ARQ-01` §3. Si se acepta, se documenta el impacto en el cronograma y se ajusta el denominador del
avance antes de comprometerse. Si se rechaza, se anota en el apartado de fuera de alcance con la
razón. Ningún cambio entra por conversación informal.

---

## 11. Artefactos del plan

| Artefacto | Ubicación | Responsable |
|---|---|---|
| Matriz de trazabilidad HU-RF-indicador | `../02-trazabilidad/matriz_HU_RF_indicador.md` | Responsable técnico |
| Plan de pruebas y casos | `../03-pruebas/plan_de_pruebas.md` | Tester |
| Registro de defectos | `../03-pruebas/registro_defectos.md` | Tester |
| Actas de aceptación por módulo | `../03-pruebas/actas/` | Jefatura de operaciones |
| Registro de despliegues | `../04-despliegue/registro_despliegues.md` | Responsable técnico |

---

## 12. Plantillas

### 12.1 Caso de prueba

```
CP-HU-M05-01-02
Historia:            HU-M05-01
Criterio:            CA02
Objetivo:            Verificar que un peso neto fuera del rango de carga exige justificacion
Precondiciones:      Usuario supervisor de planta autenticado; vehiculo con capacidad_tn cargada
Datos de entrada:    Peso neto 35.00 tn; capacidad del vehiculo 30.00 tn
Pasos:               1. Completar el registro con los datos del ticket
                     2. Intentar confirmar sin justificacion
Resultado esperado:  El sistema rechaza mostrando "Debe indicar la justificacion del peso fuera de rango"
Resultado obtenido:
Estado:              Aprobado / Rechazado
Ejecutado por:       Fecha:
```

### 12.2 Acta de aceptación de módulo

```
Módulo:              M04 — Reconocimiento automático del ticket
Versión probada:     0.5.0 (preproducción)
Historias incluidas: HU-M04-01, HU-M04-02
Casos ejecutados:    n     Aprobados: n     Rechazados: n
Defectos abiertos:   Críticos 0  Altos 0  Medios n  Bajos n
Observaciones:
Resultado:           Aceptado / Aceptado con observaciones / Rechazado
Firmas:              Tester            Responsable técnico            Jefatura de operaciones
```

### 12.3 Registro de despliegue

```
Versión:      0.5.0
Fecha y hora:
Entorno:      Producción
Alcance:      Módulos y correcciones incluidas
Respaldo:     Ruta y hora del respaldo previo
Verificación posterior: Registro de un ingreso de prueba, reconocimiento, consulta y consolidado
Responsable:
```

---

## 13. Referencias

- Módulos y orden de construcción: `../model-c4/ARQ-01_Modulos_del_Sistema.md`
- Arquitectura técnica y contrato de rutas: `../model-c4/ARQ-02_Arquitectura_Tecnica.md`
- Flujo de trabajo por módulo y definición de terminado: `../00-arquitectura/GUIA_MARCO_DE_TRABAJO.md`
- Convención de códigos, ramas y trazabilidad: `../00-arquitectura/convenciones_codigo.md`
- Decisiones que condicionan la implementación: `../00-arquitectura/decisiones_diseno.md`
- Marco de la tesis, instrumentos de la variable independiente y condición del pretest: `../00-tesis/marco_tesis.md`
- Historias y criterios de aceptación: `../HistoriasUsuario.md`
- Plan de pruebas: `../03-pruebas/plan_de_pruebas.md`
