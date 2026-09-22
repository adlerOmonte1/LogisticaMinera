# Historias de usuario — M03 Registro de ingresos

**RF asociados:** RF01, RF04, RF05, RF06 · **Historias:** 3

> Módulo núcleo del sistema. Aquí se materializa la unidad de registro —el ingreso de mineral a
> planta— a partir de la imagen del ticket de balanza. M03 no lee la imagen ni decide si los datos
> son coherentes: delega lo primero en `ReconocedorTicket` (M04) y lo segundo en
> `ValidadorConsistencia` (M05), recoge la confirmación del usuario y persiste el ingreso con su
> código único, su respaldo y sus tres marcas de tiempo.

---

## HU-M03-01 — Registro de un ingreso a partir del ticket de balanza

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M03-01 |
| **Épica** | Registro de ingresos |
| **Prioridad** | Crítica |

**Historia**

Como supervisor de planta, quiero registrar el ingreso fotografiando el ticket de balanza apenas el
volquete sale de la balanza, para que el dato y su respaldo queden disponibles sin transcripción
posterior en la oficina.

**Descripción**

El registro empieza cuando el usuario captura o carga la imagen del ticket. En ese momento el
sistema conserva la imagen y asigna la hora de inicio del registro. El reconocedor propone los seis
datos del ticket con su nivel de confianza y el validador señala las inconsistencias. El usuario
revisa, corrige lo que haga falta y elige el tipo de mineral. El tipo de vehículo no se digita: se
deriva del catálogo a partir de la placa.

Nada de lo propuesto se guarda como dato del ingreso hasta que el usuario confirma. Al confirmar, el
servidor vuelve a validar, asigna el código único y la hora de fin del registro, y persiste el
ingreso junto con los valores reconocidos y los confirmados, en una sola transacción.

El ingreso guarda tres marcas de tiempo independientes: la fecha y hora del ticket, el inicio del
registro y el fin del registro. La primera se lee del ticket y es editable antes de confirmar; las
otras dos las asigna el servidor y ningún rol las modifica.

**Detalles**
- Imagen del ticket: obligatoria, JPG o PNG, hasta 10 MB.
- Placa: obligatoria, reconocida y editable; debe corresponder a un vehículo vigente del catálogo.
- Fecha y hora del ticket: obligatorias, reconocidas y editables antes de confirmar.
- Peso bruto, tara y peso neto: obligatorios, reconocidos y editables, en toneladas, decimales
  positivos. El peso neto se toma del ticket; no se calcula.
- Tipo de mineral: obligatorio, seleccionado del catálogo.
- Tipo de vehículo: derivado del catálogo, no editable.
- Número de ticket: opcional; si se consigna, único entre los ingresos no anulados.
- Justificación del peso: obligatoria solo si el peso neto quedó fuera del rango de carga.
- Inicio y fin del registro: asignados por el servidor, no editables.
- Código: asignado por el servidor, no editable.

**Criterios de aceptación**

> **CA01.** Dado que el usuario capturó la imagen y confirma datos válidos y sin inconsistencias
> pendientes, cuando confirma el registro, entonces el sistema persiste el ingreso, le asigna un
> código y muestra "Ingreso registrado con el código {codigo}".

> **CA02.** Dado que el usuario no adjuntó la imagen del ticket, cuando intenta confirmar, entonces
> el sistema rechaza la operación mostrando "Debe adjuntar la imagen del ticket de balanza".

> **CA03.** Dado que falta alguno de los campos obligatorios, cuando el usuario intenta confirmar,
> entonces el sistema rechaza la operación mostrando "Debe completar los campos obligatorios" e
> indica cuáles faltan.

> **CA04.** Dado que la placa no corresponde a un vehículo vigente del catálogo, cuando el usuario
> intenta confirmar, entonces el sistema rechaza la operación mostrando "La placa {placa} no está
> registrada en el catálogo de vehículos".

> **CA05.** Dado que existe una inconsistencia bloqueante o una advertencia sin justificar, cuando
> el usuario intenta confirmar, entonces el sistema rechaza la operación mostrando "Debe corregir o
> justificar las inconsistencias señaladas".

> **CA06.** Dado que el usuario adjunta un archivo que no es JPG ni PNG, o que supera los 10 MB,
> cuando intenta cargarlo, entonces el sistema lo rechaza mostrando "La imagen debe estar en formato
> JPG o PNG y no superar los 10 MB".

> **CA07.** Dado que un ingreso fue registrado, cuando se consulta su detalle, entonces el sistema
> muestra la fecha y hora del ticket, el inicio del registro y el fin del registro como tres valores
> distintos, y no permite editar los dos últimos.

> **CA08.** Dado que el número de ticket ya figura en un ingreso no anulado, cuando el usuario
> intenta confirmar, entonces el sistema rechaza la operación mostrando "El ticket número {n} ya fue
> registrado en el ingreso {codigo}".

> **CA09.** Dado que el ingreso se persiste, cuando concluye la operación, entonces el sistema
> conserva la imagen asociada al ingreso, guarda para cada campo el valor reconocido y el confirmado,
> y registra el evento en auditoría.

> **CA10.** Dado que la operación falla en cualquier punto después de confirmar, cuando el sistema
> la interrumpe, entonces no queda un ingreso a medio registrar: o se persiste todo o no se persiste
> nada.

---

## HU-M03-02 — Corrección de un ingreso registrado

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M03-02 |
| **Épica** | Registro de ingresos |
| **Prioridad** | Alta |

**Historia**

Como administrativo, quiero corregir un dato equivocado de un ingreso ya registrado, para que el
histórico refleje lo que dice el ticket sin tener que anular el registro y volver a crearlo.

**Descripción**

La corrección alcanza a los datos que provienen del ticket y a los que el usuario eligió: fecha y
hora del ticket, pesos, vehículo, tipo de mineral y número de ticket. No alcanza al código, a las
dos marcas de tiempo del servidor ni a la imagen, que es el respaldo de lo que se registró.

Toda corrección exige un motivo y vuelve a someter los datos a las reglas de validación: un ingreso
corregido cumple exactamente las mismas condiciones que uno nuevo. El sistema conserva los valores
anteriores, de modo que siempre puede reconstruirse qué decía el registro antes del cambio.

**Detalles**
- Campos corregibles: fecha y hora del ticket, peso bruto, tara, peso neto, vehículo, tipo de
  mineral, número de ticket y justificación del peso.
- Campos no corregibles: código, hora de inicio y fin del registro, imagen del ticket, usuario que
  registró.
- Motivo de la corrección: obligatorio, texto libre.
- Roles autorizados: Administrativo y Administrador.

**Criterios de aceptación**

> **CA01.** Dado que el usuario modifica uno o más campos corregibles e indica el motivo, cuando
> guarda la corrección, entonces el sistema actualiza el ingreso y muestra "Ingreso {codigo}
> actualizado".

> **CA02.** Dado que el usuario no indica el motivo, cuando intenta guardar la corrección, entonces
> el sistema rechaza la operación mostrando "Debe indicar el motivo de la corrección".

> **CA03.** Dado que los valores corregidos incumplen una regla de validación, cuando el usuario
> intenta guardar, entonces el sistema rechaza la operación con el mensaje literal de la regla
> incumplida.

> **CA04.** Dado que el usuario intenta modificar el código o alguna de las marcas de tiempo
> asignadas por el servidor, cuando envía la corrección, entonces el sistema ignora esos valores y
> conserva los originales.

> **CA05.** Dado que el ingreso está anulado, cuando el usuario intenta corregirlo, entonces el
> sistema rechaza la operación mostrando "No se puede corregir un ingreso anulado".

> **CA06.** Dado que el usuario tiene rol de Supervisor de planta, cuando intenta corregir un
> ingreso, entonces el sistema rechaza la operación mostrando "Acción no autorizada".

> **CA07.** Dado que la corrección se persiste, cuando concluye la operación, entonces el sistema
> registra en auditoría el valor anterior y el nuevo de cada campo modificado, junto con el motivo y
> el usuario responsable.

---

## HU-M03-03 — Anulación de un ingreso

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M03-03 |
| **Épica** | Registro de ingresos |
| **Prioridad** | Alta |

**Historia**

Como administrador, quiero anular un ingreso que no debió registrarse, para que deje de contar en
los totales sin desaparecer del histórico.

**Descripción**

Un ingreso no se elimina nunca. Se marca como anulado con un motivo y un responsable, y permanece
consultable. A partir de ese momento queda fuera de todo total y de toda consolidación, pero sigue
apareciendo en el detalle y en el historial, con su imagen y sus datos intactos.

La anulación es la vía para los errores que no se resuelven corrigiendo: un ingreso duplicado, uno
registrado sobre el volquete equivocado o uno cuyo ticket no corresponde a la operación.

**Detalles**
- Motivo de la anulación: obligatorio, texto libre.
- Rol autorizado: Administrador.
- Efecto: el ingreso se excluye de totales y consolidaciones; permanece en el detalle y en las
  consultas, señalado como anulado.
- El número de ticket de un ingreso anulado vuelve a quedar disponible para otro ingreso.

**Criterios de aceptación**

> **CA01.** Dado que el administrador indica el motivo, cuando confirma la anulación, entonces el
> sistema marca el ingreso como anulado y muestra "Ingreso {codigo} anulado".

> **CA02.** Dado que el administrador no indica el motivo, cuando intenta anular, entonces el
> sistema rechaza la operación mostrando "Debe indicar el motivo de la anulación".

> **CA03.** Dado que el ingreso ya está anulado, cuando se intenta anularlo de nuevo, entonces el
> sistema rechaza la operación mostrando "El ingreso {codigo} ya fue anulado".

> **CA04.** Dado que el usuario tiene rol de Administrativo o de Supervisor de planta, cuando
> intenta anular un ingreso, entonces el sistema rechaza la operación mostrando "Acción no
> autorizada".

> **CA05.** Dado que un ingreso fue anulado, cuando se consulta su detalle, entonces el sistema lo
> muestra con todos sus datos, su imagen, su estado de anulado, el motivo y el responsable.

> **CA06.** Dado que un ingreso fue anulado, cuando se calcula cualquier total por periodo o por
> tipo de mineral, entonces ese ingreso no se incluye.

> **CA07.** Dado que la anulación se persiste, cuando concluye la operación, entonces el sistema
> registra el evento en auditoría con el motivo y el usuario responsable.
