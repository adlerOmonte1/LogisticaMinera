# Historias de usuario — M03 Registro de ingresos

**RF asociados:** RF-01, RF-02, RF-09 · **Indicadores:** I1, I2, I5 · **Semanas:** 2–3 · **Historias:** 7

> Módulo núcleo. La unidad de registro de todo el sistema —el ingreso de volquete a planta— se materializa aquí. Los indicadores I1 (latencia entre pesaje y disponibilidad del dato) e I2 (cobertura de registro por tipo de vehículo) se calculan directamente sobre los registros que produce este módulo.

---

## HU-M03-01 — Registro de un ingreso de volquete

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M03-01 |
| **Épica** | Registro de ingresos |
| **Prioridad** | Crítica |

**Historia**

Como supervisor de planta, quiero registrar el ingreso de un volquete apenas sale de la balanza, para que el dato quede disponible sin esperar a que alguien lo transcriba en la oficina.

**Descripción**

El registro toma los datos del ticket de balanza: fecha y hora de pesaje, número de ticket, placa del vehículo, producto, peso bruto y tara. El peso neto lo calcula el sistema. La hora de registro la asigna el servidor de forma automática y no es editable por ningún rol.

**Detalles**
- Fecha y hora de pesaje: obligatorias, tomadas del ticket.
- Número de ticket: obligatorio, texto.
- Vehículo: obligatorio, seleccionado del catálogo (M02).
- Producto: obligatorio, seleccionado del catálogo (M02).
- Peso bruto y tara: obligatorios, decimales positivos.
- Peso neto: calculado, no editable.
- Correlativo: asignado por el servidor.

**Criterios de aceptación**

> **CA01.** Dado que el usuario completa todos los campos obligatorios con datos válidos, cuando confirma el registro, entonces el sistema persiste el ingreso, le asigna un correlativo y muestra "Ingreso registrado con el número {correlativo}".

> **CA02.** Dado que el usuario omite un campo obligatorio, cuando intenta guardar, entonces el sistema rechaza la operación indicando cuáles campos faltan.

> **CA03.** Dado que la tara es mayor o igual al peso bruto, cuando el usuario intenta guardar, entonces el sistema rechaza la operación mostrando "La tara no puede ser mayor o igual al peso bruto".

> **CA04.** Dado que el número de ticket ya fue registrado, cuando el usuario intenta guardar, entonces el sistema rechaza la operación mostrando "El ticket número {n} ya fue registrado en el ingreso {correlativo}".

> **CA05.** Dado que el usuario registra un ingreso, cuando el sistema lo persiste, entonces almacena la hora de pesaje ingresada por el usuario y la hora de registro asignada por el servidor como **dos campos independientes**, y no permite editar la segunda.

> **CA06.** Dado que la fecha y hora de pesaje son posteriores a la hora del servidor, cuando el usuario intenta guardar, entonces el sistema rechaza la operación mostrando "La fecha y hora de pesaje no pueden ser posteriores a la hora actual".

> **CA07.** Dado que el ingreso se persiste correctamente, cuando concluye la operación, entonces el sistema genera el movimiento de stock de entrada correspondiente y registra el evento en auditoría.

---

## HU-M03-02 — Cálculo automático del peso neto

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M03-02 |
| **Prioridad** | Crítica |

**Historia**

Como supervisor, quiero que el sistema calcule el peso neto, para no equivocarme restando a mano y para que todos los registros usen el mismo criterio.

**Criterios de aceptación**

> **CA01.** Dado que el usuario ingresa peso bruto y tara válidos, cuando ambos campos pierden el foco, entonces el sistema muestra el peso neto calculado como la diferencia, sin permitir su edición.

> **CA02.** Dado que el usuario modifica el peso bruto o la tara, cuando el campo cambia, entonces el sistema recalcula el peso neto de inmediato.

> **CA03.** Dado que un registro llega por la cola de sincronización, cuando el servidor lo procesa, entonces recalcula el peso neto en el servidor y descarta el valor enviado por el cliente.

---

## HU-M03-03 — Asignación de correlativo por el servidor

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M03-03 |
| **Prioridad** | Crítica |

**Historia**

Como administrador, quiero que el número correlativo de cada ingreso lo asigne el servidor, para que no existan dos ingresos con el mismo número aunque se registren desde dispositivos distintos.

**Descripción**

Un ingreso capturado sin conexión lleva un identificador local temporal (UUID) y recibe su correlativo definitivo al sincronizar. La asignación ocurre dentro de una transacción con bloqueo, no mediante una consulta del máximo actual.

**Criterios de aceptación**

> **CA01.** Dado que el sistema persiste un ingreso, cuando asigna el correlativo, entonces este es único en todo el sistema y estrictamente creciente.

> **CA02.** Dado que dos registros se sincronizan de forma simultánea, cuando el servidor los procesa, entonces cada uno recibe un correlativo distinto.

> **CA03.** Dado que un ingreso fue capturado sin conexión, cuando se sincroniza, entonces conserva su identificador local en el campo correspondiente y recibe además el correlativo del servidor.

> **CA04.** Dado que un ingreso ya tiene correlativo asignado, cuando se edita cualquier otro campo, entonces el correlativo permanece inalterado.

---

## HU-M03-04 — Listado y filtrado de ingresos

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M03-04 |
| **Prioridad** | Alta |

**Historia**

Como administrativo, quiero ver la lista de ingresos registrados con filtros por fecha, producto y vehículo, para revisar la operación del periodo.

**Criterios de aceptación**

> **CA01.** Dado que el usuario accede al listado, cuando la pantalla carga, entonces el sistema muestra los ingresos del mes en curso ordenados por fecha de pesaje descendente.

> **CA02.** Dado que el usuario aplica un filtro por rango de fechas, cuando confirma, entonces el sistema muestra únicamente los ingresos comprendidos en ese rango.

> **CA03.** Dado que el listado supera cincuenta registros, cuando se muestra, entonces el sistema pagina los resultados.

> **CA04.** Dado que un ingreso está anulado, cuando aparece en el listado, entonces el sistema lo muestra visualmente diferenciado y con su motivo de anulación accesible.

---

## HU-M03-05 — Consulta del detalle de un ingreso

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M03-05 |
| **Prioridad** | Alta |

**Historia**

Como administrativo, quiero abrir un ingreso y ver todos sus datos, para verificarlo contra el ticket físico cuando haya alguna duda.

**Criterios de aceptación**

> **CA01.** Dado que el usuario selecciona un ingreso, cuando se abre el detalle, entonces el sistema muestra todos sus campos, incluidos la hora de pesaje, la hora de registro y, si corresponde, la hora de sincronización.

> **CA02.** Dado que el ingreso fue capturado sin conexión, cuando se muestra el detalle, entonces el sistema lo indica de forma visible.

> **CA03.** Dado que el usuario tiene rol Supervisor, cuando abre el detalle de un ingreso, entonces puede consultarlo pero no editarlo.

---

## HU-M03-06 — Edición de un ingreso registrado

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M03-06 |
| **Prioridad** | Media |

**Historia**

Como administrativo, quiero corregir un ingreso cuando detecto un error de transcripción, para que el histórico refleje el ticket real.

**Criterios de aceptación**

> **CA01.** Dado que el usuario con rol Administrativo o Administrador modifica campos editables, cuando guarda, entonces el sistema actualiza el registro y conserva los valores anteriores en auditoría.

> **CA02.** Dado que el usuario intenta modificar el correlativo o la hora de registro, cuando envía la solicitud, entonces el sistema la rechaza: ambos campos no son editables por ningún rol.

> **CA03.** Dado que la edición modifica el peso bruto, la tara o el producto, cuando se guarda, entonces el sistema recalcula el movimiento de stock asociado.

> **CA04.** Dado que un ingreso está anulado, cuando el usuario intenta editarlo, entonces el sistema rechaza la operación mostrando "No se puede editar un ingreso anulado".

---

## HU-M03-07 — Anulación de un ingreso

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M03-07 |
| **Prioridad** | Media |

**Historia**

Como administrativo, quiero anular un ingreso registrado por error indicando el motivo, para que quede constancia de la corrección sin borrar información.

**Descripción**

El sistema no elimina ingresos. La anulación es un cambio de estado con motivo obligatorio y responsable identificado. El ingreso anulado permanece en el histórico y su movimiento de stock se revierte.

**Criterios de aceptación**

> **CA01.** Dado que el usuario solicita anular un ingreso e indica el motivo, cuando confirma, entonces el sistema cambia el estado a ANULADO, conserva el registro y revierte el movimiento de stock asociado.

> **CA02.** Dado que el usuario intenta anular sin indicar motivo, cuando confirma, entonces el sistema rechaza la operación mostrando "Debe indicar el motivo de la anulación".

> **CA03.** Dado que el usuario intenta eliminar físicamente un ingreso, cuando envía la solicitud, entonces el sistema la rechaza: la eliminación física no está disponible en ninguna interfaz ni endpoint.

> **CA04.** Dado que un ingreso se anula, cuando concluye la operación, entonces el sistema registra en auditoría el usuario, la fecha, la hora y el motivo.
