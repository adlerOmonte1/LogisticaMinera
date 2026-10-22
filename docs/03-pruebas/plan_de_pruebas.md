# Plan de pruebas — Sistema web inteligente

**Documento:** PLAN-03
**Versión:** 2.0 — versión 2 del sistema: hora del pesaje propuesta, registro sin foto, ruta del lote,
división por fracciones y cierre con destino (DR-11 a DR-22)
**Estado:** Vigente
**Depende de:** `../01-plan/PLAN_DE_TRABAJO.md` §6, `../00-tesis/marco_tesis.md`,
`../00-tesis/decisiones_reformulacion.md`

---

## 1. Propósito

Fijar, para cada uno de los tres frentes de prueba del sistema, qué se prueba, con qué datos, quién
lo ejecuta y qué evidencia deja. Los tres frentes son:

1. **Un caso de prueba por requerimiento funcional** (`CP01` a `CP10`), la lista de control de
   funcionalidad, más dos casos complementarios (`CP11` y `CP12`) para las excepciones y las
   historias de la versión 2 que no tienen RF propio.
2. **El conjunto de prueba de la capacidad inteligente** (ERA y TDI), sobre tickets reales.
3. **El protocolo de tareas de usabilidad** (T01 a T06).

Los casos de prueba por criterio de aceptación (`CP-HU-Mxx-nn-nn`) no están aquí: viven en las
pruebas automatizadas de cada módulo, junto al código que verifican.

---

## 2. Casos de prueba de la lista de control (CP01 a CP10)

Un caso por requerimiento funcional. Superar los diez es lo que sostiene el indicador CPS (% de
casos de prueba superados); cada RF cumplido y su caso superado son lo que sostiene RFC.

### CP01 — Registro de un ingreso con imagen del ticket (RF01)

| Campo | Detalle |
|---|---|
| Precondición | Usuario autenticado, catálogo de tipos de mineral cargado, un vehículo con tara registrada y una placa que no está en el catálogo |
| Pasos | (a) Capturar el ticket de un vehículo con tara; revisar la propuesta; ajustar la hora del pesaje, que el sistema propone con la hora actual, a la del pesaje real; confirmar. (b) Capturar el ticket de la placa no registrada; dar de alta el vehículo en la misma pantalla; confirmar; registrar después su destare |
| Resultado esperado | (a) El sistema persiste el ingreso como Registrado, con la hora del pesaje ajustada y las marcas de inicio y fin del registro asignadas por el servidor; calcula el peso neto con la tara del vehículo, asigna un código único y conserva la imagen. (b) El ingreso queda En proceso, sin peso neto; al registrar la tara pasa a Registrado con el neto calculado |
| Evidencia | Ambos ingresos visibles en el listado con su estado, su imagen recuperable y su peso neto igual a peso bruto menos tara |

### CP02 — Reconocimiento de la placa, la fecha y el peso bruto con su confianza (RF02)

| Campo | Detalle |
|---|---|
| Precondición | Motor de reconocimiento configurado (D-12 cerrada) |
| Pasos | Capturar la imagen de un ticket legible del conjunto de prueba |
| Resultado esperado | El sistema presenta la placa, la fecha y el peso bruto, cada uno con su nivel de confianza; la hora del pesaje se propone con la hora actual y es editable, y la tara y el peso neto no se proponen |
| Evidencia | Los tres campos precargados; los de confianza baja resaltados |

### CP03 — Detección de las cinco inconsistencias (RF03)

| Campo | Detalle |
|---|---|
| Precondición | Un ingreso por cada regla V1 a V5 sembrada (ver §4.2) |
| Pasos | Confirmar cada ingreso sembrado |
| Resultado esperado | El sistema señala la inconsistencia correspondiente con el mensaje literal de la regla; bloquea en V2, V3 y V5, y exige justificación en V1 y V4 |
| Evidencia | Cinco resultados de `RESULTADO_VALIDACION`, uno por regla, con su resolución |

### CP04 — Corrección manual de un dato reconocido (RF04)

| Campo | Detalle |
|---|---|
| Precondición | Un ingreso con al menos un campo de baja confianza |
| Pasos | Editar el campo antes de confirmar; confirmar |
| Resultado esperado | El sistema persiste el valor confirmado, distinto del reconocido, y marca el campo como corregido |
| Evidencia | `CAMPO_RECONOCIDO` con `valor_reconocido` ≠ `valor_confirmado` |

### CP05 — Asignación del código único, sin duplicados (RF05)

| Campo | Detalle |
|---|---|
| Precondición | Ninguna |
| Pasos | Registrar diez ingresos consecutivos; registrar dos ingresos con una diferencia menor a un segundo, simulando confirmación simultánea |
| Resultado esperado | Cada ingreso recibe un código distinto y correlativo, sin colisión bajo concurrencia |
| Evidencia | Lista de códigos sin repeticiones; prueba automatizada con dos hilos concurrentes en verde |

### CP06 — Registro del tipo de mineral y del tipo de vehículo (RF06)

| Campo | Detalle |
|---|---|
| Precondición | Catálogo con vehículos propios y externos, y al menos dos tipos de mineral |
| Pasos | Registrar un ingreso con un vehículo propio y otro con un vehículo externo, ambos con tara registrada |
| Resultado esperado | El tipo de vehículo y la tara se derivan del catálogo, sin digitarse; el tipo de mineral queda registrado como se eligió |
| Evidencia | Detalle del ingreso mostrando los campos correctamente derivados y la tara aplicada |

### CP07 — Vínculo del ingreso con las etapas de su ruta (RF07)

| Campo | Detalle |
|---|---|
| Precondición | Dos lotes con ingresos asignados: el lote A, Abierto; el lote B, Abierto, que se dividirá |
| Pasos | (a) Iniciar el recorrido del lote A; registrar su secado; elegir la ruta zarandeo y ensacado; registrar ambas etapas; intentar registrar molienda. (b) Iniciar el recorrido del lote B; registrar su secado; dividirlo en dos partes, 1/3 con ruta de molienda y 2/3 con ruta de zarandeo, ambas con ensacado; registrar las etapas de cada parte. (c) Consultar la trazabilidad de un ingreso de cada lote |
| Resultado esperado | (a) El sistema registra las etapas de la ruta y rechaza la molienda con "No hay etapas pendientes para este lote". (b) Las fracciones suman la unidad; cada parte registra sus etapas por separado. (c) La trazabilidad del ingreso de A muestra tres etapas recorridas de tres; la del ingreso de B, cuatro de cuatro: secado, zarandeo, molienda y ensacado, unión de las rutas de sus partes |
| Evidencia | `PASO_ETAPA` de cada lote y parte; un intento rechazado con el mensaje de la regla; las dos consultas de trazabilidad con el conteo de etapas recorridas sobre etapas de la ruta |

### CP08 — Consulta por placa y fecha con presentación del ticket (RF08)

| Campo | Detalle |
|---|---|
| Precondición | Al menos un ingreso registrado con placa conocida y uno registrado sin foto |
| Pasos | Buscar por placa parcial y fecha; abrir el detalle; ampliar la imagen. Repetir con el ingreso sin foto |
| Resultado esperado | El sistema devuelve el ingreso y muestra la imagen del ticket ampliable; el ingreso sin foto aparece señalado como sin respaldo fotográfico, con su motivo, en lugar de la imagen |
| Evidencia | Resultado de búsqueda y respaldo visible, cronometrado en menos de un minuto |

### CP09 — Total acumulado mensual y su exportación (RF09)

| Campo | Detalle |
|---|---|
| Precondición | Ingresos registrados en el mes en curso, incluidos uno anulado y uno En proceso |
| Pasos | Solicitar el consolidado del mes; exportarlo |
| Resultado esperado | El total por tipo de mineral excluye el ingreso anulado y el En proceso, e informa que hay un ingreso pendiente del destare; el archivo exportado coincide exactamente con la consulta en pantalla |
| Evidencia | Consulta en pantalla y archivo descargado, con los mismos números |

### CP10 — Gestión de usuarios y restricción por rol (RF10)

| Campo | Detalle |
|---|---|
| Precondición | Un usuario de cada rol: Administrador, Administrativo, Supervisor de planta |
| Pasos | (a) Cada usuario intenta acceder a una operación fuera de su rol: el Supervisor de planta intenta anular un ingreso y consolidar el mes; el Administrativo intenta cerrar un lote con su destino. (b) El Supervisor de planta da de alta un vehículo desde el registro, registra su destare y registra el paso de un lote por una etapa |
| Resultado esperado | (a) El sistema rechaza con "Acción no autorizada" y registra el evento en auditoría. (b) El sistema permite las tres operaciones, que forman parte del alcance del Supervisor de planta |
| Evidencia | Rechazo con código 403 para cada intento fuera de rol; evento `ACCESO_RECHAZADO` registrado; vehículo, tara y paso por etapa atribuidos al Supervisor de planta |

### Casos complementarios de la versión 2

No forman parte de la lista de control ni del denominador de CPS: verifican una excepción de RF01
y una historia de RF07 que la versión 2 incorporó sin crear un RF nuevo.

### CP11 — Registro de un ingreso sin foto (excepción de RF01, DR-13)

| Campo | Detalle |
|---|---|
| Precondición | Usuario autenticado; un vehículo con tara registrada |
| Pasos | (a) Elegir el registro sin foto y confirmar sin motivo. (b) Indicar el motivo «Ticket extraviado o dañado», digitar placa, fecha, hora y peso bruto, elegir el tipo de mineral y confirmar. (c) Buscar el ingreso en el listado y abrir su detalle |
| Resultado esperado | (a) El sistema rechaza con "Debe completar los campos obligatorios" e indica el motivo. (b) El ingreso queda Registrado, sin imagen ni reconocimiento, con su motivo; las reglas V1 a V5 se evalúan igual. (c) El ingreso aparece señalado como sin respaldo fotográfico, con su motivo |
| Evidencia | Ingreso sin `CAMPO_RECONOCIDO`, con marca de sin respaldo fotográfico y motivo; resultados de validación registrados |

### CP12 — Cierre del lote con su destino (historia de RF07, DR-14)

| Campo | Detalle |
|---|---|
| Precondición | Un lote En recorrido con todo su mineral ensacado y otro con etapas pendientes |
| Pasos | (a) Como Administrativo, intentar cerrar el primer lote. (b) Como Administrador, intentar cerrar el lote con etapas pendientes. (c) Como Administrador, cerrar el primer lote sin destino y después con destino «venta». (d) Intentar registrar una etapa en el lote cerrado |
| Resultado esperado | (a) "Acción no autorizada". (b) "Todavía no se puede cerrar el lote. Pendiente: …" con la lista de lo que falta. (c) Primero "Debe indicar el destino del lote"; después el lote queda Cerrado con su destino, fecha y responsable. (d) "El lote {codigo} ya fue cerrado" |
| Evidencia | Lote Cerrado con destino; evento de cierre en auditoría con el destino y el resumen; intentos rechazados con su mensaje |

---

## 3. Matriz CP ↔ RF ↔ módulo

| CP | RF | Módulo principal |
|---|---|---|
| CP01 | RF01 | M03 |
| CP02 | RF02 | M04 |
| CP03 | RF03 | M05 |
| CP04 | RF04 | M03 |
| CP05 | RF05 | M03 |
| CP06 | RF06 | M03, M02 |
| CP07 | RF07 | M06 |
| CP08 | RF08 | M07 |
| CP09 | RF09 | M08 |
| CP10 | RF10 | M01 |

Los diez casos cubren los diez RF sin excepción: es la condición para que CPS pueda llegar al
100 %. CP11 (M03) y CP12 (M06) se ejecutan con la misma evidencia, pero quedan fuera de esa cuenta.

---

## 4. Conjunto de prueba de la capacidad inteligente

### 4.1 Exactitud del reconocimiento (ERA)

**Tamaño:** 50 tickets reales de la balanza en uso, recogidos en condiciones normales de operación
(no seleccionados por legibilidad óptima). Un ingreso registrado sin foto no tiene imagen ni
reconocimiento y no forma parte del conjunto.

**Procedimiento:**

1. Cada ticket se lee primero por una persona, que registra el valor real de los tres campos que
   el ticket imprime: placa, fecha y peso bruto. La hora del pesaje, la tara y el peso neto no se
   reconocen y no entran en la medición.
2. Cada ticket se procesa con el sistema, con el motor y la versión congelados (D-16).
3. Se compara, campo por campo, el valor reconocido contra el valor real.
4. ERA se calcula como el porcentaje de campos que coinciden exactamente, sobre el total de
   50 × 3 = 150 lecturas.

**Registro:** una fila por ticket y campo, con valor real, valor reconocido, confianza y si
coincide. Se conserva junto con la imagen del ticket, para poder auditar cualquier discrepancia.

**Condición de congelamiento (D-16):** el motor y su versión no cambian entre el primer y el último
ticket del conjunto. Si es necesario corregir algo a mitad de la medición, se documenta la fecha y
se reporta como limitación.

### 4.2 Tasa de detección de inconsistencias (TDI)

**Tamaño:** 10 inconsistencias sembradas, 2 por cada una de las 5 reglas.

| Regla | Inconsistencia sembrada 1 | Inconsistencia sembrada 2 |
|---|---|---|
| V1 | Ticket con la misma placa, fecha y peso bruto que un ingreso ya registrado | El mismo ticket registrado por segunda vez tras una corrección de la hora del pesaje |
| V2 | Peso bruto igual a la tara del vehículo | Peso bruto menor que la tara del vehículo, con el punto decimal mal ubicado |
| V3 | Placa con una letra de más | Placa con formato de otro país |
| V4 | Peso bruto cuyo neto calculado supera en 20 % la capacidad del vehículo | Peso bruto cuyo neto calculado supera en 50 % la capacidad del vehículo |
| V5 | Fecha del ticket un día después del registro | Fecha del ticket un mes después del registro |

**Procedimiento:**

1. Se construyen 10 ingresos de prueba, cada uno con exactamente la inconsistencia sembrada
   correspondiente y el resto de los datos correctos. Los vehículos usados tienen tara registrada,
   para que V2 y V4 puedan evaluarse; V1 necesita además el ingreso original ya registrado.
2. Se confirma cada ingreso en el sistema.
3. TDI se calcula como el porcentaje de las 10 inconsistencias que el sistema señala con la regla
   correcta, sobre el total de 10.

**Condición de congelamiento (D-16):** las reglas V1 a V5 y sus parámetros (patrón de placa de
V3) no cambian entre la primera y la última inconsistencia sembrada.

### 4.3 Umbral de confianza

El umbral configurado durante el conjunto de prueba se registra junto con los resultados: cambiar
el umbral después de medir ERA invalida la comparación con lo obtenido antes.

---

## 5. Protocolo de las tareas de usabilidad (T01 a T06)

| Tarea | Descripción | Módulo | Rol que la ejecuta |
|---|---|---|---|
| T01 | Registrar un ingreso a partir de la imagen del ticket | M03, M04 | Supervisor de planta |
| T02 | Corregir un dato reconocido de forma incorrecta | M03, M05 | Supervisor de planta o Administrativo |
| T03 | Consultar un ingreso por placa y fecha | M07 | Administrativo |
| T04 | Vincular un ingreso con una etapa del proceso | M06 | Supervisor de planta o Administrativo |
| T05 | Obtener el total acumulado mensual por producto | M08 | Administrativo |
| T06 | Exportar el total acumulado mensual por producto | M08 | Administrativo |

**Procedimiento por tarea:**

1. Se entrega al participante un enunciado breve de la tarea, sin instrucciones de cómo hacerla.
2. Se cronometra desde que empieza hasta que declara terminada la tarea o desiste.
3. Se registra si la completó sin asistencia, con asistencia mínima (una pista verbal) o no la
   completó.
4. TCA se calcula como el porcentaje de tareas completadas sin ninguna asistencia, sobre el total
   de tareas ejecutadas por todos los participantes.

**Después de las seis tareas**, se aplica el cuestionario SUS al mismo participante.

---

## 6. Registro y responsables

| Instrumento | Quién lo ejecuta | Dónde se registra |
|---|---|---|
| CP01 a CP10 | Tester | Acta de aceptación de cada módulo (`PLAN_DE_TRABAJO.md` §12.2) |
| CP11 y CP12 | Tester | Acta de aceptación de M03 y de M06 |
| ERA (hoja A) | Tester, con revisión de un segundo evaluador para los desacuerdos | Anexo de la ficha de capacidad inteligente |
| TDI (hoja B) | Tester | Anexo de la ficha de capacidad inteligente |
| T01 a T06 (hoja C) | Jefatura de operaciones, con participantes reales de planta | Ficha de capacidad inteligente |
| SUS | Jefatura de operaciones | Cuestionario SUS, un formulario por participante |

Los cinco instrumentos se ejecutan en la semana de estabilización (`PLAN_DE_TRABAJO.md` §8), después
de que motor y reglas queden congelados y antes de que el sistema entre en operación real en planta.

---

## 7. Referencias

- Marco de la tesis, reglas V1 a V5 y tareas T01 a T06: `../00-tesis/marco_tesis.md`
- Decisiones DR-08 (conjunto de prueba) y D-16 (congelamiento): `../00-tesis/decisiones_reformulacion.md`,
  `../00-arquitectura/decisiones_diseno.md`
- Plan de trabajo y cronograma: `../01-plan/PLAN_DE_TRABAJO.md`
- Matriz de trazabilidad: `../02-trazabilidad/matriz_HU_RF_indicador.md`
