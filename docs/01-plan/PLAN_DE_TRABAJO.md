# PLAN-01 — Plan de trabajo, pruebas y entrega

**Documento:** PLAN-01
**Versión:** 1.0
**Estado:** Vigente
**Alcance:** Sistema web de control logístico de planta (M01 a M09, ver `../model-c4/ARQ-01_Modulos_del_Sistema.md`)

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
| Responsable técnico | Decisiones de arquitectura, revisión de PR, control de alcance | Decisiones en `decisiones_diseno.md`, aprobación de PR |
| Desarrollo backend | Modelos, reglas de negocio, servicios, API | Código, migraciones, pruebas unitarias y de integración |
| Desarrollo frontend | Aplicación Angular y capa PWA | Código, pruebas de componente, verificación offline |
| Tester / QA | Diseño y ejecución de pruebas, gestión de defectos | Casos de prueba, reportes de defecto, acta de pruebas |
| Jefatura de operaciones | Validación funcional con datos reales | Aceptación de usuario firmada por módulo |
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
| Preproducción | Copia anonimizada de producción | Pruebas de aceptación y de carga | Responsable técnico |
| Producción | Servidor de planta | Operación real y medición de indicadores | Responsable técnico, con registro de despliegue |

Todo despliegue a producción realizado durante el periodo de medición se anota en el registro de
despliegues con fecha, hora, versión y motivo. Un despliegue sin registrar introduce un cambio no
controlado en las condiciones de medición (`../model-c4/ARQ-02_Arquitectura_Tecnica.md` §7).

### 3.2 Ramas

```
main                      Código desplegado en producción, siempre etiquetado
develop                   Integración; de aquí sale preproducción
feature/M03-ingresos      Una rama por módulo
fix/M03-hora-registro     Corrección de defecto reportado
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
M03: registra hora de pesaje separada de hora de registro (HU-M03-01)
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
- [ ] Las acciones de escritura registran evento en M08.
- [ ] Ninguna entidad se borra físicamente: baja lógica o anulación con motivo.

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
| Unitaria | Reglas de negocio y cálculos en `models/` y `services/` | pytest | Desarrollo | En cada commit |
| Integración | Servicio completo contra base de datos real, con transacciones | pytest + pytest-django | Desarrollo | Al cerrar la historia |
| Contrato de API | Códigos de estado, forma del cuerpo, cuerpo de error uniforme | pytest + cliente DRF | Desarrollo | Al cerrar la historia |
| Permisos | Acceso y rechazo por cada rol declarado | pytest | Desarrollo | Al cerrar la historia |
| Componente frontend | Validaciones y estados de la interfaz | Karma / Jasmine | Desarrollo | Al cerrar la historia |
| Funcional de extremo a extremo | El criterio de aceptación tal como lo vive el usuario | Manual guiada por caso de prueba | Tester | Al pasar a preproducción |
| Sin conexión | Captura, cola, sincronización y duplicados de M07 | Manual con red deshabilitada | Tester | Semana 4 y en cada regresión |
| Carga | RNF de tiempo de respuesta y usuarios concurrentes | JMeter | Tester | Semana 8 y ante cambio de consultas |
| Aceptación de usuario | Operación real con datos de planta | Manual | Jefatura de operaciones | Cierre de cada módulo |

### 6.2 Nomenclatura y trazabilidad de casos

Cada caso de prueba se identifica como `CP-RF-xx-nn` y declara la historia y el criterio del que
nace. Las pruebas automatizadas se nombran `test_<CODIGO>_<enunciado>`, por ejemplo:

```python
def test_HU_M03_01_CA03_peso_neto_se_calcula_y_no_es_editable(): ...
def test_RN_M03_01_hora_registro_no_es_editable_por_ningun_rol(): ...
```

La cadena completa de trazabilidad es la de `convenciones_codigo.md` §5:

```
Indicador operativo  ->  RF  ->  Módulo  ->  HU  ->  Caso de prueba  ->  Commit
```

Cada eslabón debe poder recorrerse en ambos sentidos. Si un caso de prueba no se puede vincular a
un criterio de aceptación, sobra o falta el requisito.

### 6.3 Criterios de cobertura

No se persigue un porcentaje global de cobertura, que premia probar lo trivial. Se exige cobertura
por obligación:

- El 100 % de las reglas de negocio (RN) tiene prueba.
- El 100 % de los criterios de aceptación tiene caso de prueba ejecutado.
- El 100 % de las acciones con permiso declarado tiene prueba de rechazo.
- Los servicios de `services/` no bajan del 80 % de líneas cubiertas.
- Las vistas y serializadores se cubren por las pruebas de contrato, no por pruebas propias.

### 6.4 Datos de prueba

Se construyen con `factory-boy`, nunca con registros creados a mano dentro de la prueba. Existe un
juego de datos de preproducción que reproduce un mes de operación de planta: catálogo completo,
ingresos con y sin conexión, salidas de los tres tipos y un mes sin movimientos, porque el
consolidado de un mes vacío es un caso de prueba obligatorio (RNF-M06-04).

### 6.5 Pruebas de regresión

Antes de cada despliegue a producción se ejecuta la suite completa más el juego manual de
regresión, que cubre como mínimo:

1. Alta de ingreso en línea y verificación de las dos marcas de tiempo.
2. Alta de ingreso sin conexión, sincronización y asignación de correlativo.
3. Reintento de sincronización del mismo ingreso, que no debe duplicar.
4. Anulación de un ingreso y su reflejo en el kardex.
5. Consulta de stock contrastada con el cálculo manual.
6. Generación del consolidado del mes en curso y de un mes sin movimientos.
7. Búsqueda por correlativo y por criterios combinados.
8. Acceso denegado a cada acción restringida, con un usuario de cada rol.

---

## 7. Gestión de defectos

### 7.1 Severidad y plazo

| Severidad | Definición | Plazo de atención |
|---|---|---|
| Crítica | Impide registrar un ingreso, corrompe el histórico o expone datos a un rol sin permiso | Mismo día, bloquea el despliegue |
| Alta | Un criterio de aceptación no se cumple y no hay forma manual de sortearlo | Antes de cerrar el módulo |
| Media | El criterio se cumple pero con comportamiento incorrecto en un caso secundario | Dentro de la semana siguiente |
| Baja | Textos, presentación, comodidad de uso | Semana de estabilización |

Un defecto que afecte la hora de registro, el correlativo o la cola de sincronización es **crítico
por definición**, aunque parezca cosmético: son los tres puntos donde un error produce datos que
parecen correctos.

### 7.2 Contenido mínimo de un reporte

Un defecto sin estos datos se devuelve sin analizar:

```
ID:            DEF-nnn
Historia:      HU-M03-01 / CA03
Entorno:       Preproducción, versión 0.4.2
Precondición:  Usuario supervisor, catálogo cargado
Pasos:         1. ... 2. ... 3. ...
Resultado esperado:  (texto literal del criterio de aceptación)
Resultado obtenido:  (lo que ocurrió, con captura o respuesta de la API)
Severidad:     Alta
```

Toda corrección de defecto añade la prueba automatizada que lo habría detectado. Sin esa prueba, la
corrección no se aprueba.

---

## 8. Cronograma con entregables verificables

Ocho semanas, coherente con `ARQ-01` §6 y `GUIA_MARCO_DE_TRABAJO.md` §7. La columna de
verificación indica **quién** valida y **con qué evidencia**; sin esa evidencia la semana no se da
por cerrada.

### Semana 1 — Base técnica y M01

| Actividad | Entregable | Verificación |
|---|---|---|
| Esqueleto backend, PostgreSQL, ajustes por entorno | Proyecto que arranca con `runserver` y `pytest` en verde | Responsable técnico |
| Esqueleto Angular con PWA habilitada | Aplicación que carga sin conexión con página de bienvenida | Responsable técnico |
| M01 completo | Inicio de sesión, expiración, bloqueo por intentos, menú por rol | Tester: casos de HU-M01-01 a HU-M01-05 |
| Decisiones de arquitectura firmadas | `decisiones_diseno.md` sin decisiones abiertas que bloqueen M03 | Responsable técnico |

Riesgo de la semana: si la decisión sobre M07 no se cierra aquí, M03 se construirá dos veces.

### Semana 2 — M02 y arranque de M03

| Actividad | Entregable | Verificación |
|---|---|---|
| M02 catálogo maestro | Alta, edición y baja lógica de productos, vehículos y transportistas | Tester: HU-M02-01 a HU-M02-04 |
| Titularidad como campo controlado | Filtro `?titularidad=PROPIO` operativo | Prueba de contrato automatizada |
| Formulario de ingreso con validaciones | Formulario que reproduce el ticket de balanza | Revisión con jefatura de operaciones |

### Semana 3 — M03 completo y M08

| Actividad | Entregable | Verificación |
|---|---|---|
| Alta, edición, listado y detalle de ingresos | Ingreso registrado con hora de pesaje y hora de registro separadas | Tester: HU-M03-01 a HU-M03-07 |
| Asignación de correlativo en servidor | Secuencia sin saltos verificada con altas concurrentes | Prueba de integración |
| Anulación con motivo | Ingreso anulado visible en el histórico, nunca eliminado | Tester |
| M08 eventos de creación y modificación | Registro de evento por cada escritura, con usuario y momento | Prueba automatizada por acción |

Hito de la semana: a partir de aquí el sistema ya produce el dato con el que se calcula I1.

### Semana 4 — M07 sobre M03

| Actividad | Entregable | Verificación |
|---|---|---|
| Cola local y borrador del formulario | Ingreso capturado sin conexión que sobrevive al cierre de la aplicación | Tester con red deshabilitada |
| Endpoint de lote | Sincronización que asigna correlativo definitivo y conserva la hora de captura | Prueba de integración y verificación manual |
| Idempotencia por identificador local | Reenvío del mismo lote que no genera duplicados | Caso de prueba obligatorio |
| Indicador de estado de conexión | Estado visible y contador de pendientes | Tester |

Este es el entregable de mayor riesgo del proyecto. Se prueba con el dispositivo real que usará el
supervisor, no solo con el simulador del navegador.

### Semana 5 — M04 y M05

| Actividad | Entregable | Verificación |
|---|---|---|
| Registro de salidas por venta, merma y ajuste | Salida registrada que descuenta stock | Tester: HU-M04-01 a HU-M04-03 |
| Consulta de existencias | Stock por producto coincidente con el cálculo manual de la planta | Jefatura de operaciones, contraste con su hoja actual |
| Kardex por producto | Movimientos ordenados con saldo resultante por línea | Tester |
| Saldo a fecha de corte | Reconstrucción del saldo a una fecha pasada | Prueba automatizada |

Precondición: el criterio de estimación de merma por humedad debe estar definido antes del inicio
de la semana. Si no lo está, M04 se implementa igual y la interpretación de I4 queda pendiente,
pero se anota como riesgo abierto.

### Semana 6 — M09 y M08 completo

| Actividad | Entregable | Verificación |
|---|---|---|
| Búsqueda por correlativo | Recuperación del detalle completo de un ingreso en menos de un minuto | Medición cronometrada por el tester |
| Búsqueda por criterios combinados | Fecha, placa y producto combinables | Tester |
| M08 vista de consulta de auditoría | Filtros por fecha, usuario y acción, solo lectura | Tester |
| Registro de exportaciones | Evento `EXPORTAR` por cada descarga | Prueba automatizada |

### Semana 7 — M06

| Actividad | Entregable | Verificación |
|---|---|---|
| Consolidado mensual | Reporte generado en dos acciones, con detalle por correlativo | Jefatura de operaciones |
| Mes sin movimientos | Consolidado que informa ausencia de producción, sin error | Caso de prueba obligatorio |
| Exportación a Excel y PDF | Archivos abiertos correctamente en el equipo de la empresa | Tester |
| Formato de declaración semestral | Archivo con la estructura oficial vigente | Jefatura de operaciones |
| Endpoint de disponibilidad histórica | Respuesta mes a mes con indicación de consolidado disponible | Prueba de contrato |

Precondición: el formato oficial debe estar en manos del equipo antes del inicio de la semana.

### Semana 8 — Estabilización, carga y despliegue

| Actividad | Entregable | Verificación |
|---|---|---|
| Suite completa de regresión | Ejecución sin fallos de las pruebas automatizadas y del juego manual | Tester |
| Pruebas de carga con JMeter en preproducción | Protocolo de carga con tiempos de respuesta por endpoint frente a los RNF | Tester y responsable técnico |
| Corrección de defectos abiertos | Ningún defecto crítico ni alto pendiente | Tester |
| Despliegue a producción | Versión etiquetada, registro de despliegue y respaldo previo | Responsable técnico |
| Acta de pruebas y de aceptación | Documento firmado con el resultado por módulo | Todos los roles |

No se desarrolla funcionalidad nueva en esta semana. Una historia que no esté terminada en la
semana 7 se retira del alcance y se documenta, en lugar de comprimir la estabilización.

---

## 9. Criterios de escalabilidad por entregable

Cada entregable se construye pensando en el volumen de dos años de operación, no en el de la
demostración. Los controles concretos son estos:

| Ámbito | Regla | Cómo se verifica |
|---|---|---|
| Consultas | Todo listado pagina; el tamaño de página tiene tope | Prueba de contrato con más registros que el tope |
| Índices | Los declarados en el modelo de datos se crean en la primera migración del módulo | Revisión del `sqlmigrate` en el PR |
| Consultas repetidas | Ninguna vista genera consultas en bucle | `assertNumQueries` en la prueba del listado |
| Saldos | El saldo se lee denormalizado, no se recalcula recorriendo el histórico | Prueba de tiempo de respuesta con histórico cargado |
| Contratos | La API se versiona en la ruta; los cambios incompatibles abren `/api/v2/` | Revisión de PR |
| Acoplamiento | Un módulo nuevo se agrega sin modificar los existentes (exportadores, generadores) | Revisión de PR contra los ejemplos de `ARQ-03` §4 |
| Datos | Cantidades en decimal; sin borrado físico; sin campos de texto libre donde hay dominio cerrado | Prueba de regla de negocio |
| Crecimiento del histórico | Las consultas de existencias y búsqueda se miden con volumen simulado de un año | Prueba de carga de la semana 8, repetida ante cambios de consulta |

La prueba de carga no se ejecuta una sola vez al final. Se repite cada vez que se modifica una
consulta que sostiene un RNF de tiempo de respuesta.

---

## 10. Seguimiento del proyecto

### 10.1 Ritmo

| Reunión | Frecuencia | Duración | Salida |
|---|---|---|---|
| Coordinación de desarrollo | Diaria | 15 minutos | Bloqueos identificados |
| Cierre de semana | Semanal | 1 hora | Entregable verificado o causa documentada del desvío |
| Revisión con la jefatura de operaciones | Al cierre de cada módulo | 1 hora | Acta de aceptación |

### 10.2 Indicadores de seguimiento

| Indicador | Cálculo | Meta |
|---|---|---|
| Avance de implementación | Módulos terminados sobre 9 planificados | Según cronograma semanal |
| Historias aceptadas | Historias con acta sobre historias del módulo | 100 % antes de cerrar el módulo |
| Defectos abiertos por severidad | Conteo vigente | Cero críticos y altos antes de desplegar |
| Defectos escapados a producción | Defectos hallados en producción sobre total del módulo | Menor a 10 % |
| Reglas de negocio con prueba | RN cubiertas sobre RN declaradas | 100 % |

Los indicadores operativos del sistema (I1 a I6) se miden sobre la operación, no sobre el
proyecto, y se registran aparte una vez desplegado.

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
| Protocolo y resultados de carga | `../03-pruebas/protocolo_de_carga.md` | Tester |
| Registro de defectos | `../03-pruebas/registro_defectos.md` | Tester |
| Actas de aceptación por módulo | `../03-pruebas/actas/` | Jefatura de operaciones |
| Registro de despliegues | `../04-despliegue/registro_despliegues.md` | Responsable técnico |

---

## 12. Plantillas

### 12.1 Caso de prueba

```
CP-RF-01-03
Historia:            HU-M03-01
Criterio:            CA03
Objetivo:            Verificar que el peso neto se calcula y no admite edición manual
Precondiciones:      Usuario supervisor autenticado; catálogo de productos cargado
Datos de entrada:    Peso bruto 32.50 tn; tara 12.30 tn
Pasos:               1. Abrir el formulario de ingreso
                     2. Registrar peso bruto y tara
                     3. Salir del campo tara
Resultado esperado:  El sistema muestra 20.20 tn como peso neto y el campo no es editable
Resultado obtenido:
Estado:              Aprobado / Rechazado
Ejecutado por:       Fecha:
```

### 12.2 Acta de aceptación de módulo

```
Módulo:              M03 — Registro de ingresos
Versión probada:     0.5.0 (preproducción)
Historias incluidas: HU-M03-01 … HU-M03-07
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
Verificación posterior: Alta de ingreso de prueba, consulta de stock, generación de consolidado
Responsable:
```

---

## 13. Referencias

- Módulos y cronograma: `../model-c4/ARQ-01_Modulos_del_Sistema.md`
- Arquitectura técnica y contrato de rutas: `../model-c4/ARQ-02_Arquitectura_Tecnica.md`
- Flujo de trabajo por módulo y definición de terminado: `../00-arquitectura/GUIA_MARCO_DE_TRABAJO.md`
- Convención de códigos, ramas y trazabilidad: `../00-arquitectura/convenciones_codigo.md`
- Decisiones que condicionan la implementación: `../00-arquitectura/decisiones_diseno.md`
- Historias y criterios de aceptación: `../HistoriasUsuario.md`
