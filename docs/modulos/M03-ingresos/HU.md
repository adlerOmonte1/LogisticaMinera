# Historias de usuario — M03 Registro de ingresos

**RF asociados:** RF01, RF04, RF05, RF06 · **Historias:** 4

> Módulo núcleo del sistema. Aquí se materializa la unidad de registro —el ingreso de mineral a
> planta— a partir de la imagen del ticket de balanza. M03 no lee la imagen ni decide si los datos
> son coherentes: delega lo primero en `ReconocedorTicket` (M04) y lo segundo en
> `ValidadorConsistencia` (M05), recoge la confirmación del usuario, calcula el peso neto con la
> tara del vehículo y persiste el ingreso con su código único, su respaldo y sus tres marcas de
> tiempo.

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
sistema conserva la imagen y asigna la hora de inicio del registro. El ticket de balanza imprime la
placa, la fecha y un único peso, que es el peso bruto: el reconocedor propone esos tres datos con su
nivel de confianza y el validador señala las inconsistencias. El usuario revisa, corrige lo que haga
falta, digita la hora del pesaje —que el ticket no imprime— y elige el tipo de mineral.

El tipo de vehículo y la tara no se digitan: se toman del catálogo a partir de la placa. El peso neto
tampoco: lo calcula el servidor como peso bruto menos la tara del vehículo, y el ingreso conserva la
tara que se le aplicó.

Si la placa no está en el catálogo, se trata del primer viaje de ese vehículo. El usuario lo da de
alta **en la misma pantalla**, sin perder lo ya capturado, y el registro continúa. Como un vehículo
nuevo aún no tiene tara, el ingreso se confirma en estado **En proceso**: queda con su código, su
peso bruto y sus marcas de tiempo, y recibe el peso neto cuando se registre el destare
(HU-M03-04). Lo mismo ocurre con un vehículo que ya existe en el catálogo pero todavía no fue
destarado.

Nada de lo propuesto se guarda como dato del ingreso hasta que el usuario confirma. Al confirmar, el
servidor vuelve a validar, asigna el código único y la hora de fin del registro, y persiste el
ingreso junto con los valores reconocidos y los confirmados, en una sola transacción.

El ingreso guarda tres marcas de tiempo independientes: la fecha y hora del pesaje, el inicio del
registro y el fin del registro. La primera combina la fecha reconocida del ticket con la hora que
digita el usuario, y es editable antes de confirmar; las otras dos las asigna el servidor y ningún
rol las modifica.

**Detalles**
- Imagen del ticket: obligatoria, JPG o PNG, hasta 10 MB.
- Placa: obligatoria, reconocida y editable. Si no está en el catálogo, se da de alta el vehículo en
  la misma pantalla con placa, titularidad, capacidad de carga y, si es externo, transportista.
- Fecha del pesaje: obligatoria, reconocida del ticket y editable antes de confirmar.
- Hora del pesaje: obligatoria, digitada por el usuario.
- Peso bruto: obligatorio, reconocido y editable, en toneladas, decimal positivo.
- Tara: tomada del catálogo del vehículo, no editable en el registro.
- Peso neto: calculado por el servidor como peso bruto menos tara, no editable; se muestra antes de
  confirmar como referencia.
- Tipo de mineral: obligatorio, seleccionado del catálogo.
- Tipo de vehículo: derivado del catálogo, no editable.
- Número de ticket: opcional; si se consigna, único entre los ingresos no anulados.
- Justificación: obligatoria solo si la validación advierte un ticket posiblemente duplicado o un
  peso fuera del rango de carga.
- Inicio y fin del registro: asignados por el servidor, no editables.
- Código: asignado por el servidor, no editable.
- Estado: Registrado si el vehículo tiene tara; En proceso si está pendiente de destare.

**Criterios de aceptación**

> **CA01.** Dado que el vehículo tiene tara registrada y el usuario confirma datos válidos y sin
> inconsistencias pendientes, cuando confirma el registro, entonces el sistema calcula el peso neto,
> persiste el ingreso como Registrado, le asigna un código y muestra "Ingreso registrado con el
> código {codigo}".

> **CA02.** Dado que el usuario no adjuntó la imagen del ticket, cuando intenta confirmar, entonces
> el sistema rechaza la operación mostrando "Debe adjuntar la imagen del ticket de balanza".

> **CA03.** Dado que falta la placa, la fecha, la hora del pesaje, el peso bruto o el tipo de
> mineral, cuando el usuario intenta confirmar, entonces el sistema rechaza la operación mostrando
> "Debe completar los campos obligatorios" e indica cuáles faltan.

> **CA04.** Dado que la placa no está registrada en el catálogo, cuando el sistema la valida,
> entonces muestra "La placa {placa} no está registrada. Complete los datos del vehículo para
> continuar" y ofrece el alta del vehículo en la misma pantalla, sin perder los datos ya capturados.

> **CA05.** Dado que el vehículo no tiene tara registrada, cuando el usuario confirma datos válidos,
> entonces el sistema persiste el ingreso En proceso, sin peso neto, y muestra "Ingreso {codigo}
> registrado en proceso: pendiente del destare del vehículo {placa}".

> **CA06.** Dado que existe una inconsistencia bloqueante o una advertencia sin justificar, cuando
> el usuario intenta confirmar, entonces el sistema rechaza la operación mostrando "Debe corregir o
> justificar las inconsistencias señaladas".

> **CA07.** Dado que el usuario adjunta un archivo que no es JPG ni PNG, o que supera los 10 MB,
> cuando intenta cargarlo, entonces el sistema lo rechaza mostrando "La imagen debe estar en formato
> JPG o PNG y no superar los 10 MB".

> **CA08.** Dado que un ingreso se confirma como Registrado, cuando el sistema lo persiste, entonces
> el peso neto es igual al peso bruto menos la tara del vehículo, no es editable, y el ingreso
> conserva la tara que se le aplicó.

> **CA09.** Dado que un ingreso fue confirmado, cuando se consulta su detalle, entonces el sistema
> muestra la fecha y hora del pesaje, el inicio del registro y el fin del registro como tres valores
> distintos, y no permite editar los dos últimos.

> **CA10.** Dado que el número de ticket ya figura en un ingreso no anulado, cuando el usuario
> intenta confirmar, entonces el sistema rechaza la operación mostrando "El ticket número {n} ya fue
> registrado en el ingreso {codigo}".

> **CA11.** Dado que el ingreso se persiste, cuando concluye la operación, entonces el sistema
> conserva la imagen asociada al ingreso, guarda para cada campo reconocido el valor propuesto y el
> confirmado, y registra el evento en auditoría.

> **CA12.** Dado que la operación falla en cualquier punto después de confirmar, cuando el sistema
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

La corrección alcanza a los datos que provienen del ticket y a los que el usuario eligió o digitó:
fecha y hora del pesaje, peso bruto, vehículo, tipo de mineral y número de ticket. No alcanza al
código, a las dos marcas de tiempo del servidor ni a la imagen, que es el respaldo de lo que se
registró. Tampoco a la tara ni al peso neto de forma directa: el neto se recalcula a partir del peso
bruto corregido, y si se corrige el vehículo, con la tara del vehículo correcto.

Toda corrección exige un motivo y vuelve a someter los datos a las reglas de validación: un ingreso
corregido cumple exactamente las mismas condiciones que uno nuevo. El sistema conserva los valores
anteriores, de modo que siempre puede reconstruirse qué decía el registro antes del cambio.

**Detalles**
- Campos corregibles: fecha y hora del pesaje, peso bruto, vehículo, tipo de mineral, número de
  ticket y justificación.
- Campos recalculados por el sistema: tara aplicada, cuando cambia el vehículo, y peso neto.
- Campos no corregibles: código, hora de inicio y fin del registro, imagen del ticket, usuario que
  registró.
- Motivo de la corrección: obligatorio, texto libre.
- Roles autorizados: Administrativo y Administrador.

**Criterios de aceptación**

> **CA01.** Dado que el usuario modifica uno o más campos corregibles e indica el motivo, cuando
> guarda la corrección, entonces el sistema actualiza el ingreso, recalcula el peso neto y muestra
> "Ingreso {codigo} actualizado".

> **CA02.** Dado que el usuario no indica el motivo, cuando intenta guardar la corrección, entonces
> el sistema rechaza la operación mostrando "Debe indicar el motivo de la corrección".

> **CA03.** Dado que los valores corregidos incumplen una regla de validación, cuando el usuario
> intenta guardar, entonces el sistema rechaza la operación con el mensaje literal de la regla
> incumplida.

> **CA04.** Dado que el usuario intenta modificar el código, alguna de las marcas de tiempo
> asignadas por el servidor, la tara o el peso neto, cuando envía la corrección, entonces el sistema
> ignora esos valores y conserva o recalcula los que corresponden.

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
registrado sobre el volquete equivocado o uno cuyo ticket no corresponde a la operación. Puede
anularse tanto un ingreso Registrado como uno En proceso.

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

---

## HU-M03-04 — Registro del destare de un vehículo en su primer viaje

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M03-04 |
| **Épica** | Registro de ingresos |
| **Prioridad** | Crítica |

**Historia**

Como supervisor de planta, quiero registrar la tara del volquete cuando se pesa vacío en su primer
viaje, para que el sistema calcule el peso neto de ese ingreso y de todos los siguientes sin tener
que volver a destararlo.

**Descripción**

En el primer viaje de un vehículo, después de descargar, el volquete se pesa vacío en la balanza.
El operador de la balanza anota a mano la resta en el ticket; esa anotación es parte del trabajo de
la balanza y queda fuera del sistema. En el sistema, el usuario **digita** la tara sobre el ingreso
que quedó En proceso. La tara no se reconoce de la imagen: se escribe a mano por seguridad del dato,
porque de ella depende el peso neto de todos los ingresos futuros de ese vehículo.

El sistema guarda la tara en el catálogo del vehículo, con la fecha y el usuario que la registró,
calcula el peso neto del ingreso, lo somete a las reglas de validación que dependen del peso y lo
pasa a Registrado. Desde ese momento la tara se mantiene por decisión de la Gerencia: solo el
Administrador puede modificarla, con motivo (HU-M02-01).

**Detalles**
- Tara: obligatoria, digitada, en toneladas, decimal positivo, menor que el peso bruto del ingreso.
- Se registra una sola vez por vehículo, sobre un ingreso En proceso.
- Efecto sobre el vehículo: queda con tara, fecha de destare y usuario que la registró.
- Efecto sobre el ingreso: tara aplicada, peso neto calculado y estado Registrado.
- Si el vehículo tiene otros ingresos En proceso, reciben la misma tara y su peso neto.
- Roles autorizados: Supervisor de planta, Administrativo y Administrador.

**Criterios de aceptación**

> **CA01.** Dado que un ingreso está En proceso y el usuario digita una tara válida, cuando confirma
> el destare, entonces el sistema guarda la tara en el vehículo, calcula el peso neto, pasa el
> ingreso a Registrado y muestra "Destare registrado. Peso neto del ingreso {codigo}: {neto} t".

> **CA02.** Dado que el usuario no digita la tara, cuando intenta confirmar el destare, entonces el
> sistema rechaza la operación mostrando "Debe indicar la tara del vehículo".

> **CA03.** Dado que la tara digitada es mayor o igual que el peso bruto del ingreso, cuando el
> usuario intenta confirmar, entonces el sistema rechaza la operación mostrando "La tara no puede ser
> mayor o igual que el peso bruto".

> **CA04.** Dado que el peso neto resultante queda fuera del rango de carga del vehículo, cuando el
> usuario intenta confirmar sin justificación, entonces el sistema rechaza la operación mostrando
> "Debe indicar la justificación del peso fuera de rango".

> **CA05.** Dado que el vehículo ya tiene tara registrada, cuando se intenta registrar un destare,
> entonces el sistema rechaza la operación mostrando "El vehículo {placa} ya tiene tara registrada".

> **CA06.** Dado que existen ingresos En proceso, cuando el usuario abre el registro de destares,
> entonces el sistema los lista con su código, placa, fecha y peso bruto.

> **CA07.** Dado que el vehículo tiene otros ingresos En proceso, cuando se registra su tara,
> entonces el sistema calcula también el peso neto de esos ingresos y los pasa a Registrado.

> **CA08.** Dado que el destare se persiste, cuando concluye la operación, entonces el sistema
> registra en auditoría la tara, el vehículo, los ingresos afectados y el usuario responsable.
