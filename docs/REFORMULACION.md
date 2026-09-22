# Análisis de impacto — Reformulación de LogisticaMinera a sistema web inteligente

| Campo | Valor |
|---|---|
| Repositorio analizado | `adlerOmonte1/LogisticaMinera`, rama `main`, commit `f8c6d7a` (10/09/2026) |
| Referencia de tesis | Título, variables, dimensiones, indicadores e instrumentos validados (Anexos 01 a 05) |
| Fecha | 21/09/2026 |
| Propósito | Inventariar todo lo que debe cambiar antes de reescribir la documentación. Este documento no reescribe nada: indica qué cambia, dónde y por qué |

---

## 0. Resumen

El repositorio documenta el **Sistema de Control de Producción y Existencias**, con 9 módulos, 34 historias, RF-01 a RF-12 e indicadores I1 a I6 de una variable dependiente que ya no existe en la tesis. La tesis validada mide el **control de inventarios de ingreso de mineral** y exige un componente inteligente (reconocimiento automático del ticket y validación automática) que el repositorio declara expresamente **fuera de alcance**.

| Aspecto | Magnitud del cambio |
|---|---|
| Variable dependiente, dimensiones e indicadores | Total |
| Variable independiente y forma de evaluarla | Total |
| Denominador del avance | 9 módulos planificados → 10 RF de la lista de control |
| Módulos | 3 se conservan, 3 se reformulan, 3 se retiran, 3 son nuevos |
| Historias de usuario | 21 de 34 sobreviven (6 de ellas reescritas), 13 se retiran, unas 10 son nuevas |
| Código implementado (M01 y M02) | M01 intacto; M02 con un ajuste menor |
| Archivos que citan conceptos antiguos | 83 (66 de 78 en `docs/`, 13 de 15 en `skills/`, 4 en `backend/`) |

Lo que **se conserva sin discusión**: stack (Django 5 + DRF + PostgreSQL 16 + Angular), arquitectura por capas, M01 completo, catálogo de vehículos con titularidad, correlativo asignado por el servidor, anulación en lugar de borrado, auditoría y las decisiones D-02, D-06, D-07, D-08, D-09 y D-11.

---

## 1. Marco de tesis: repositorio frente a tesis validada

| Elemento | En el repositorio | En la tesis validada |
|---|---|---|
| Nombre del sistema | Sistema de Control de Producción y Existencias | Sistema web inteligente |
| Título | No figura | Efecto de un sistema web inteligente en el control de inventarios de ingreso de mineral en la empresa Construcción y Minería, Huánuco, 2027 |
| Variable independiente | "El sistema", evaluado con ISO/IEC 25010:2023 en cinco características (adecuación funcional, eficiencia de desempeño, usabilidad, fiabilidad, seguridad) y % de módulos implementados | D1 Funcionalidad del sistema, D2 Capacidad inteligente del sistema, D3 Usabilidad del sistema |
| Variable dependiente | Control de producción y existencias | Control de inventarios de ingreso de mineral |
| Dimensiones de la VD | Implícitas en I1 a I6 (latencia, cobertura, stock, desviación, recuperación, consolidado) | D1 Oportunidad del registro, D2 Integridad del registro, D3 Consolidación de la producción |
| Unidad de análisis | Mezcla de ingreso, corte de stock y mes | Una sola: el ingreso de mineral registrado con ticket de balanza |
| Muestra | Pendiente ("confirmar con la asesora") | 90 a 100 ingresos por medición, censal |
| Forma de medir la VD | Calculada desde los registros del sistema (`hora_registro − hora_pesaje`, etc.) | Ficha de observación por ingreso, pretest prospectivo y postest |
| Alcance de producto | Saranda y Molido; ingresos, salidas y stock | Solo ingreso de mineral óxido en planta; sulfuro y mina fuera |
| Componente inteligente | Fuera de alcance: "predicción de demanda, aprendizaje automático o analítica avanzada" | Dentro del alcance y medido: reconocimiento automático del ticket y detección automática de inconsistencias |
| Justificación normativa | Ley 32213 y declaración semestral (M06) | Ninguna dimensión la requiere |
| Instrumentos de la VI | Acta de pruebas funcionales y protocolo de carga JMeter | Lista de control de funcionalidad, ficha de capacidad inteligente y tareas, cuestionario SUS |

**Consecuencia práctica.** En la tesis la VD se mide por observación directa, no con los datos que produce el sistema. El sistema debe seguir guardando marcas de tiempo confiables (sirven para triangular el postest), pero ya no es la fuente única del indicador. Toda la documentación que dice "el indicador se calcula con la consulta X" debe reescribirse.

---

## 2. Indicadores

### 2.1 Variable dependiente

La ficha de observación por ingreso (Anexo 02) numera los indicadores de la VD como I1 a I6, igual que el repositorio, **pero con otro significado**. Es la fuente de confusión más probable durante la reescritura.

| Antiguo | Qué medía | Nuevo | Qué mide | Situación |
|---|---|---|---|---|
| I1 | Latencia entre pesaje y disponibilidad del dato | **I1** Tiempo de espera del registro (h) | Hora del ticket → inicio del registro | Se reformula: el punto final pasa de "dato disponible" a "inicio del registro" |
| — | — | **I2** Tiempo de registro del ingreso (min) | Inicio → fin del registro | Nuevo. Ninguna entidad guarda hoy inicio y fin |
| I2 | Cobertura de registro por titularidad | **I3** Completitud del registro (%) | Campos consignados / 7 × 100 | Se reemplaza. La titularidad deja de ser el eje y pasa a ser el campo C7 |
| I3 | Tiempo de determinación del stock | — | — | Se retira |
| I4 | Desviación entre stock declarado y estimado | — | — | Se retira |
| I5 | Recuperación del dato de un ingreso | **I4** Tiempo de recuperación del respaldo (min) | Consulta → presentación del ticket y sus datos | Se conserva con cambio: ahora debe mostrarse el ticket (imagen), no solo el dato |
| I6 | % de meses con consolidado disponible | **I5** Tiempo de consolidación (min) | Solicitud → entrega del total acumulado del mes por producto que incluye el ingreso | Cambia de naturaleza: de proporción mensual a tiempo por ingreso |
| — | — | **I6** Grado de trazabilidad (%) | Etapas vinculadas / 4 × 100 (secado, zarandeo, molienda, ensacado) | Nuevo. El repositorio no modela etapas de proceso |

Los siete campos de completitud (I3) son C1 placa, C2 fecha y hora, C3 peso bruto, C4 tara, C5 peso neto, C6 tipo de mineral y C7 tipo de vehículo.

**Regla para la reescritura:** adoptar la numeración de la ficha (Anexo 02) y eliminar toda referencia antigua. Ninguna mención a I1–I6 debe sobrevivir sin revisarse.

### 2.2 Variable independiente

| Dimensión | Indicador | Sigla | Qué exige del sistema |
|---|---|---|---|
| D1 Funcionalidad | % de requerimientos funcionales cumplidos | RFC | Que existan exactamente los 10 RF de la lista de control |
| D1 Funcionalidad | % de casos de prueba superados | CPS | 10 casos de prueba, uno por RF |
| D2 Capacidad inteligente | Exactitud del reconocimiento automático del ticket | ERA | Leer 6 campos: placa, fecha, hora, peso bruto, tara y peso neto |
| D2 Capacidad inteligente | Tasa de detección de inconsistencias | TDI | Detectar los 5 tipos de inconsistencia sembrados (ver §4.3) |
| D3 Usabilidad | Puntaje System Usability Scale | SUS | Ninguna exigencia funcional adicional |
| D3 Usabilidad | % de tareas completadas sin asistencia | TCA | Que las 6 tareas T01 a T06 se puedan ejecutar |

Tareas del instrumento: T01 registrar un ingreso a partir de la imagen del ticket, T02 corregir un dato reconocido de forma incorrecta, T03 consultar un ingreso por placa y fecha, T04 vincular un ingreso con una etapa del proceso, T05 obtener el total acumulado mensual por producto, T06 exportar un reporte de ingresos.

**Consecuencias.** Las cinco características ISO/IEC 25010 y el protocolo de carga JMeter dejan de ser instrumento de la VI. Los RNF de rendimiento pueden quedar como requisitos técnicos, pero no se reportan como resultado de la tesis. El indicador "módulos implementados sobre 9 planificados" desaparece: el denominador pasa a ser **10 RF**.

---

## 3. Requerimientos funcionales

### 3.1 Correspondencia

| RF nuevo (Anexo 03) | Descripción | Origen en el repositorio | Cambio |
|---|---|---|---|
| RF01 | Registrar el ingreso de mineral con la imagen del ticket de balanza | RF-01 | La imagen pasa a ser obligatoria. Hoy el C4 declara que la foto del ticket "no es un requisito" |
| RF02 | Reconocer automáticamente placa, fecha, hora, peso bruto, tara y peso neto | — | Nuevo |
| RF03 | Validar automáticamente la consistencia entre peso bruto, tara y peso neto | RF-02 (cálculo del neto) | Cambia de lógica: el neto ya no se calcula y bloquea; se lee del ticket y se contrasta |
| RF04 | Permitir el registro y la corrección manual de los datos reconocidos | RF-09 (edición) | Se amplía: la corrección ocurre antes de confirmar, no solo después |
| RF05 | Asignar un código único a cada ingreso | HU-M03-03 (correlativo) | Compatible, sin cambio de fondo |
| RF06 | Registrar el tipo de mineral y el tipo de vehículo | RF-03 (catálogo) | Parcial: falta el tipo de mineral; la titularidad ya existe en el catálogo |
| RF07 | Vincular cada ingreso con las etapas de secado, zarandeo, molienda y ensacado | — | Nuevo |
| RF08 | Consultar un ingreso por placa y fecha con su ticket de respaldo | RF-11 (búsqueda) | El criterio principal pasa de padrón a placa y fecha, y debe mostrar la imagen |
| RF09 | Generar el total acumulado mensual por producto | RF-06 (consolidado mensual) | Se simplifica: sin declaración semestral |
| RF10 | Gestionar usuarios y roles de acceso | RF-08 | Sin cambio |

RF antiguos que salen del conteo: RF-04 existencias, RF-05 salidas y movimientos, RF-07 exportación, RF-10 captura sin conexión, RF-12 auditoría. La auditoría puede seguir existiendo como capacidad transversal, pero **no suma ni resta** en RFC.

### 3.2 Problemas que deben corregirse en el Anexo 03 y en el repositorio a la vez

1. **RF03 es más estrecho que su instrumento.** RF03 promete validar solo la relación entre pesos, pero la Hoja B del instrumento de capacidad inteligente siembra cinco tipos de inconsistencia, tres de los cuales no son de pesos (placa, capacidad del vehículo, fecha). Un jurado puede objetar que TDI mide algo que el sistema no prometía. Hay que ampliar la redacción de RF03 a los cinco tipos o reducir la Hoja B.
2. **T06 no tiene RF.** La tarea "exportar un reporte de ingresos" no corresponde a ningún RF. O la exportación entra en RF09, o la tarea se cambia.
3. **Formato del código.** El repositorio usa `RF-01`; el instrumento usa `RF01`. Conviene unificar al formato del instrumento, porque es el que validan los expertos.
4. **La lista es todavía una propuesta.** Cualquier cambio en los 10 RF debe hacerse **antes del juicio de expertos**. Después, el denominador queda fijo.

---

## 4. Módulos

### 4.1 Mapa actual → propuesto

Propuesta sujeta a las decisiones de §11. El criterio es el mismo que ya usa ARQ-01: cada módulo existe porque un RF o un indicador lo exige.

| Módulo actual | Estado del código | Acción | Módulo propuesto | RF | Indicador que habilita |
|---|---|---|---|---|---|
| M01 Autenticación | Implementado con pruebas | Conservar | M01 Autenticación y roles | RF10 | Habilitante |
| M02 Catálogo maestro | Implementado con pruebas | Ajustar | M02 Catálogo maestro | RF06 | I3 (C6, C7) y TDI (capacidad del vehículo) |
| M03 Registro de ingresos | Solo documentado | Reformular | M03 Registro de ingresos con respaldo | RF01, RF04, RF05, RF06 | I1, I2, I3 |
| — | — | Nuevo | M04 Reconocimiento automático del ticket | RF02 | ERA |
| — | — | Nuevo | M05 Validación automática de consistencia | RF03 | TDI |
| — | — | Nuevo | M06 Trazabilidad del proceso productivo | RF07 | I6 |
| M09 Búsqueda | Sin documentar, sin código | Reformular | M07 Consulta de ingresos y respaldo | RF08 | I4 |
| M06 Consolidados y reportes | Solo documentado | Reformular | M08 Consolidación de la producción | RF09 | I5 |
| M08 Auditoría | Sin documentar, sin código | Conservar | M09 Auditoría (transversal) | — | Confiabilidad del dato |
| M04 Salidas y movimientos | Solo documentado | Retirar | — | — | — |
| M05 Existencias | Solo documentado | Retirar | — | — | — |
| M07 Captura sin conexión | Solo documentado | Retirar o reducir a RNF | — | — | — |

### 4.2 Por qué salen tres módulos

- **Salidas (M04) y Existencias (M05).** Existían para sostener I3 e I4 (stock y desviación). La tesis retiró la determinación de existencias porque creaba una segunda unidad de análisis. Sin esos indicadores, ambos módulos son funcionalidad sin medición y amplían el cronograma sin aportar a la hipótesis.
- **Captura sin conexión (M07).** Era el "diferenciador" del sistema anterior. En la tesis validada el diferenciador es el componente inteligente, y ningún RF ni indicador exige operar sin señal. Si la conectividad en planta sigue siendo un riesgo real, puede quedar como un RNF acotado (por ejemplo, conservar la foto del ticket en el dispositivo y enviarla al volver la señal), sin HU propias.

### 4.3 Reglas que M05 debe implementar (derivadas de la Hoja B)

| Código | Inconsistencia | Dato que necesita |
|---|---|---|
| V1 | Peso neto distinto de peso bruto menos tara | Tolerancia de redondeo a definir |
| V2 | Tara mayor que el peso bruto | — |
| V3 | Placa con formato inválido | Patrón de placa peruana |
| V4 | Peso neto fuera del rango de carga del volquete | `capacidad_tn` del catálogo de vehículos (ya existe) |
| V5 | Fecha del ticket posterior a la fecha de registro | — |

---

## 5. Historias de usuario

| Módulo actual | HU | Acción | Motivo |
|---|---|---|---|
| M01 | 5 | Conservar | Solo actualizar las secciones de relación con indicadores |
| M02 | HU-M02-01 Productos | Reescribir | Definir tipo de mineral y producto (ver §11) |
| M02 | HU-M02-02 Vehículos | Conservar | Añadir que la capacidad alimenta la regla V4 |
| M02 | HU-M02-03 Transportistas | Conservar | — |
| M02 | HU-M02-04 Clientes | Retirar | Solo servía a salidas por venta |
| M03 | HU-M03-01 Registro | Reescribir | Registro a partir de imagen, 7 campos obligatorios, marcas de inicio y fin |
| M03 | HU-M03-02 Cálculo del neto | Reescribir | Pasa a validación contra el neto leído (RF03) |
| M03 | HU-M03-03 Correlativo | Conservar | Corresponde a RF05 |
| M03 | HU-M03-04 Listado | Conservar | Ajustar filtros a placa y fecha |
| M03 | HU-M03-05 Detalle | Reescribir | Debe mostrar la imagen del ticket y el origen de cada dato |
| M03 | HU-M03-06 Edición | Conservar | Alinear con RF04 |
| M03 | HU-M03-07 Anulación | Conservar | — |
| M04 | 3 | Retirar | Módulo retirado |
| M05 | 3 | Retirar | Módulo retirado |
| M06 | HU-M06-01 Consolidado mensual | Reescribir | Total acumulado mensual por producto, a demanda |
| M06 | HU-M06-02 Exportación | Conservar condicionalmente | Solo si la exportación entra en RF09 (T06) |
| M06 | HU-M06-03 Declaración semestral | Retirar | Sin indicador que la sostenga |
| M07 | 5 | Retirar | Módulo retirado |
| M08 | 2 | Conservar | Transversal |
| M09 | HU-M09-01 Búsqueda por padrón | Reescribir | Placa y fecha, con imagen del respaldo |
| M09 | HU-M09-02 Criterios combinados | Conservar o fusionar | Secundaria frente a RF08 |

**HU nuevas estimadas (unas 10):**

- Reconocimiento: capturar o cargar la imagen del ticket; extraer los seis campos con su nivel de confianza; presentar los campos para confirmación resaltando los de baja confianza.
- Validación: aplicar V1 a V5 al confirmar; mostrar la inconsistencia y exigir corrección o justificación; registrar el resultado de la validación.
- Trazabilidad: registrar el paso por una etapa; vincular el ingreso (o su lote) con la etapa; consultar la trazabilidad de un ingreso.

**Mapeo de las tareas del SUS/TCA a HU**, que la reescritura debe garantizar: T01 → M03 y M04, T02 → M03 (RF04), T03 → M07, T04 → M06, T05 → M08, T06 → sin RF (ver §3.2).

---

## 6. Modelo de datos

| Entidad | Acción | Detalle |
|---|---|---|
| USUARIO, ROL | Conservar | — |
| VEHICULO, TRANSPORTISTA | Conservar | `capacidad_tn` gana uso en V4 |
| PRODUCTO | Redefinir | Separar o aclarar tipo de mineral (al ingreso) y producto (al consolidar) |
| CLIENTE | Eliminar | Migración nueva; no editar `0001_initial` |
| INGRESO | Modificar | Añadir imagen del ticket (obligatoria), `hora_inicio_registro`, `hora_fin_registro`, tipo de mineral y origen de cada dato (reconocido o corregido). `peso_neto_tn` pasa de "calculado" a "leído del ticket". Retirar `uuid_local`, `capturado_offline` y `hora_sincronizacion` si sale M07 |
| RECONOCIMIENTO_TICKET | Nueva | Ingreso, motor y versión, fecha de proceso, campos reconocidos con su confianza, campos corregidos por el usuario |
| RESULTADO_VALIDACION | Nueva | Ingreso, regla (V1 a V5), detalle, resolución (corregida o justificada) |
| ETAPA_PROCESO | Nueva | Catálogo cerrado: secado, zarandeo, molienda, ensacado |
| REGISTRO_ETAPA (o LOTE) | Nueva | Vínculo entre ingreso (o lote) y etapa, con fecha y usuario |
| SALIDA, MOVIMIENTO_STOCK | Eliminar | Módulos retirados |
| EVENTO_AUDITORIA | Conservar | Añadir acciones de reconocimiento y corrección |

**Índices.** Se retira `idx_movimiento_producto_fecha`. Se conserva `idx_ingreso_fecha_producto` (I5). El índice de recuperación (I4) debe cubrir placa y fecha, es decir, `(id_vehiculo, fecha_pesaje)`. Se retira la justificación "cobertura por titularidad" de `idx_vehiculo_titularidad`, aunque el índice puede quedar.

---

## 7. Arquitectura y decisiones de diseño

### 7.1 Decisiones existentes

| Decisión | Acción | Nota |
|---|---|---|
| D-01 Hora de pesaje y hora de registro independientes | Conservar y ampliar | Sostiene I1. Se añaden inicio y fin del registro (I2) |
| D-02 Correlativo asignado por el servidor | Conservar | Corresponde a RF05 |
| D-03 Hora de registro offline = captura local | Retirar si sale M07 | Con ella desaparece la contradicción conocida con D-01 |
| D-04 Offline decidido en la semana 1 | Retirar o reemplazar | — |
| D-05 M09 existe por I5 | Reformular | La consulta existe por I4 (recuperación del respaldo) |
| D-06 Titularidad como atributo del catálogo | Conservar | Ahora alimenta C7 de completitud |
| D-07 No se borra, se anula | Conservar | — |
| D-08 Reglas de negocio solo en el servidor | Conservar | Aplica con más fuerza a V1 a V5 |
| D-09 `repositories/` como lado de lectura | Conservar | — |
| D-10 M06 y M09 como apps de lectura | Ajustar nombres | Consolidación y consulta |
| D-11 Frontend en repositorio separado | Conservar | — |

### 7.2 Decisiones nuevas que la reformulación debe fijar

| Propuesta | Contenido |
|---|---|
| D-12 Motor de reconocimiento | Elegir entre OCR local (Tesseract o PaddleOCR), servicio en la nube (por ejemplo Azure AI Document Intelligence) o modelo multimodal por API. Criterio: ERA sobre una muestra de tickets reales, costo, dependencia de conexión |
| D-13 El dato reconocido no se guarda sin confirmación | El usuario revisa y confirma antes de persistir. Sostiene RF04 y T02, y protege la completitud |
| D-14 Almacenamiento de imágenes | Volumen del servidor o almacenamiento de objetos, compresión, retención y respaldo |
| D-15 Procesamiento síncrono o asíncrono | El C4 descarta hoy un broker de tareas. Si el reconocimiento tarda más de unos segundos, esa decisión debe revisarse |
| D-16 Congelamiento durante la medición | Motor, versión y reglas no cambian entre el inicio y el fin del postest |

### 7.3 Modelo C4 (ARQ-03)

- **Nivel 1.** La balanza sigue sin integrarse, pero el ticket ya no se transcribe: se fotografía y se reconoce. Se elimina la "autoridad de formalización". Si D-12 elige un servicio en la nube, aparece como sistema externo.
- **Nivel 2.** Aparece el almacén de imágenes (hoy listado en "contenedores que deliberadamente no existen"). IndexedDB como cola de pendientes desaparece si sale M07. La tabla de contenedores inexistentes debe reescribirse.
- **Nivel 3.** M03 incorpora dos componentes con interfaz propia, `ReconocedorTicket` y `ValidadorConsistencia`, inyectados en el servicio de registro (inversión de dependencias, igual que el generador de correlativo). Los componentes de M07 salen.

---

## 8. Código

### 8.1 Backend

| Elemento | Acción |
|---|---|
| `apps/accounts` | Sin cambios |
| `apps/catalogo` | Eliminar `Cliente` (modelo, serializer, servicio, pruebas) con migración nueva; revisar `Producto`; actualizar docstrings de `filters.py` y `tests/test_api.py` que citan I2 |
| `apps/ingresos` | Construir según el nuevo M03 |
| `apps/salidas`, `apps/existencias`, `apps/sincronizacion` | Eliminar (solo contienen esqueletos vacíos) |
| `apps/busqueda` | Renombrar a consulta o conservar el nombre |
| `apps/reportes` | Reorientar a consolidación |
| `apps/auditoria` | Conservar |
| Apps nuevas | `reconocimiento`, `validacion`, `trazabilidad` |
| `config/settings/base.py` | Actualizar `LOCAL_APPS`; añadir `MEDIA_ROOT`, límites de carga y credenciales del motor si es externo |
| `requirements/base.txt` | Añadir `Pillow` y la librería o SDK del motor elegido |

### 8.2 Frontend (repositorio separado)

Retirar la cola offline y la sincronización. Añadir la captura de imagen (cámara del teléfono mediante `<input type="file" accept="image/*" capture="environment">`) y una pantalla de confirmación que resalte campos de baja confianza e inconsistencias. El service worker puede quedar solo para instalar la aplicación.

---

## 9. Inventario de archivos del repositorio

| Archivo o carpeta | Acción |
|---|---|
| `docs/HistoriasUsuario.md` | Reescribir |
| `docs/model-c4/ARQ-01_Modulos_del_Sistema.md` | Reescribir: lista de módulos, criterio de derivación, fuera de alcance, riesgos y cronograma |
| `docs/model-c4/ARQ-02_Arquitectura_Tecnica.md` | Ajustar stack y apps |
| `docs/model-c4/ARQ-03_Modelo_C4.md` | Reescribir niveles 1 a 3 |
| `docs/00-arquitectura/modelo_datos_entidad_relacion.md` | Reescribir |
| `docs/00-arquitectura/decisiones_diseno.md` | Actualizar según §7 |
| `docs/00-arquitectura/convenciones_codigo.md` | Unificar formato de RF |
| `docs/00-arquitectura/GUIA_MARCO_DE_TRABAJO.md` | Ajustar el ejemplo de M03 y retirar la cola offline (§3.6) |
| `docs/00-arquitectura/GUIA_FRONTEND_ANGULAR.md` | Retirar la PWA offline de la semana 1 |
| `docs/01-plan/PLAN_DE_TRABAJO.md` | Ajustar cronograma, indicadores de seguimiento (10 RF, no 9 módulos) y semana 8 (instrumentos de la VI en lugar de JMeter) |
| `docs/modulos/M01-autenticacion/` | Solo secciones de relación con indicadores |
| `docs/modulos/M02-catalogo/` | Ajustar |
| `docs/modulos/M03-ingresos/` | Reescribir |
| `docs/modulos/M04-…`, `M05-…`, `M07-…` | Retirar (el historial de git los conserva) |
| `docs/modulos/M06-consolidados-reportes/` | Reescribir como consolidación |
| Módulos sin carpeta (auditoría y búsqueda) | Crear |
| Módulos nuevos (reconocimiento, validación, trazabilidad) | Crear |
| `docs/02-trazabilidad/matriz_HU_RF_indicador.md` | Crear (pendiente desde antes) |
| `docs/03-pruebas/plan_de_pruebas.md` | Crear, incluido el protocolo del conjunto de prueba para ERA y TDI |
| `skills/contexto-tesis/SKILL.md` | Reescribir completa: es la fuente de verdad de todas las demás |
| `skills/offline-sincronizacion/SKILL.md` | Retirar si sale M07 |
| `skills/pruebas-y-desempeno/SKILL.md` | Ajustar: JMeter deja de ser instrumento; añadir pruebas de reconocimiento y validación |
| `skills/requisitos-modulo`, `historias-usuario`, `revision-coherencia`, `modulo-nuevo`, `commit-tesis` | Ajustar referencias a indicadores y RF |
| `skills/base-datos-postgresql`, `backend-django`, `solid-proyecto`, `diagramas-uml`, `frontend-angular`, `despliegue-docker`, `backend-auth-permisos` | Ajustar ejemplos |
| Skill nueva | `reconocimiento-validacion` (motor, reglas V1 a V5, conjunto de prueba) |

---

## 10. Inconsistencias que ya existían y conviene resolver en la reformulación

1. **Backlog frente a archivos de módulo.** `HistoriasUsuario.md` y los `HU.md` difieren en M02 (HU-M02-04 es "Desactivación" en uno y "Clientes" en otro), M03 (HU-M03-02, 04, 05 y 06 no coinciden) y M06 (orden de 02 y 03). Al reescribir, generar ambos desde una sola lista.
2. **Nota obsoleta en `contexto-tesis`.** Afirma que M03 a M07 usan la carpeta `requisitos/`, pero todos los módulos usan `requerimientos/`.
3. **Contradicción D-01 / D-03** sobre `hora_registro`. Se resuelve sola si sale M07.
4. **M08 y M09** tienen HU en el backlog pero ninguna carpeta de módulo.
5. **Matriz de trazabilidad y plan de pruebas** se citan en varios documentos y no existen.

---

## 11. Decisiones que debes tomar antes de reformular

1. **Captura sin conexión.** ¿Se retira o se reduce a un RNF? Recomendación: reducirla a un RNF sin HU propias.
2. **Motor de reconocimiento (D-12).** Probarlo con 20 o 30 tickets reales antes de fijarlo, porque ERA depende directamente de esa elección.
3. **Tipo de mineral frente a producto.** RF06 habla de tipo de mineral al ingreso y RF09 de producto al consolidar. Hay que definir si son el mismo catálogo o dos (por ejemplo, óxido por procedencia al ingreso; Saranda y Molido como producto).
4. **Vínculo del ingreso con las etapas.** Si el mineral de varios volquetes se mezcla en cancha, el vínculo directo ingreso–etapa no es realista y hace falta un lote de proceso. Esto define I6 y RF07.
5. **Placa no registrada.** Si el reconocimiento lee una placa que no está en el catálogo, no hay tipo de vehículo (C7). Definir si se bloquea, se registra el vehículo en el momento o se marca como observado.
6. **RF03 y T06** (ver §3.2).
7. **Numeración de módulos.** Renumerar (como en §4.1) es limpio porque solo M01 y M02 tienen código, pero cambia nombres de carpetas. La alternativa es conservar los números y agregar M10 a M12.
8. **Conjunto de prueba de ERA y TDI.** Cantidad de tickets y de inconsistencias sembradas (por ejemplo, 50 tickets con 10 inconsistencias, dos por tipo).

---

## 12. Orden sugerido para la reformulación

| Paso | Qué se reescribe | Por qué en este orden |
|---|---|---|
| 1 | `skills/contexto-tesis` y ARQ-01 | Son la fuente de verdad de todo lo demás |
| 2 | `decisiones_diseno.md` | Fija D-12 a D-16 antes de modelar |
| 3 | Modelo de datos | Las HU dependen de las entidades |
| 4 | Backlog de HU y matriz de trazabilidad | Deben quedar alineados con los 10 RF y las 6 tareas |
| 5 | Carpetas de módulo | Una por una, empezando por M03 |
| 6 | C4 y plan de trabajo | Reflejan lo ya decidido |
| 7 | Código | Limpieza de apps vacías, `Cliente` y apps nuevas |

**Nota de cronograma.** El pretest se mide sobre el proceso manual actual, con unos 30 ingresos al mes. Reunir 90 a 100 ingresos toma cerca de tres meses y medio, así que el pretest puede correr en paralelo con el desarrollo. La única condición es que el sistema no se use en planta hasta que el pretest termine.R