# Historias de usuario — M03 Registro de ingresos

**RF asociados:** RF01, RF04, RF05, RF06 · **Historias:** 4

> Módulo núcleo del sistema. Aquí se materializa la unidad de registro —el ingreso de mineral a
> planta— a partir de la imagen del ticket de balanza o, cuando no hay ticket que fotografiar, de los
> datos que el usuario indica con un motivo. M03 no lee la imagen ni decide si los datos son
> coherentes: delega lo primero en `ReconocedorTicket` (M04) y lo segundo en
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
nivel de confianza y el validador señala las inconsistencias. El usuario revisa y corrige lo que haga
falta —la placa puede haberse leído mal—, ajusta la hora del pesaje y elige el tipo de mineral.

La hora del pesaje no figura en el ticket. El sistema la propone con la hora en que se abre la
revisión, señalada como propuesta, y el usuario la ajusta a la hora real del pesaje antes de
confirmar.

El tipo de vehículo y la tara no se digitan: se toman del catálogo a partir de la placa. El peso neto
tampoco: lo calcula el servidor como peso bruto menos la tara del vehículo, y el ingreso conserva la
tara que se le aplicó.

Si la placa no está en el catálogo, se trata del primer viaje de ese vehículo. El usuario lo da de
alta **en la misma pantalla**, sin perder lo ya capturado, y el registro continúa. Como un vehículo
nuevo aún no tiene tara, el ingreso se confirma en estado **En proceso**: queda con su código, su
peso bruto y sus marcas de tiempo, y recibe el peso neto cuando se registre el destare
(HU-M03-04). Lo mismo ocurre con un vehículo que ya existe en el catálogo pero todavía no fue
destarado. Del mismo modo, si el mineral es de un tipo que aún no está en el catálogo, el
Administrativo o el Administrador lo agregan sin salir del registro y queda elegido para el ingreso.

**Registro sin foto.** Si el ticket se extravió, se dañó o no puede fotografiarse, el ingreso se
registra igual, sin imagen y con un motivo obligatorio. No hay reconocimiento: el usuario indica la
placa, la fecha y la hora del pesaje, el peso bruto y el tipo de mineral, y las reglas de validación
se aplican igual que a un ingreso con foto. El ingreso queda marcado **sin respaldo fotográfico** de
forma permanente, porque la imagen no es un dato corregible.

Nada de lo propuesto se guarda como dato del ingreso hasta que el usuario confirma. Al confirmar, el
servidor vuelve a validar, asigna el código único y la hora de fin del registro, y persiste el
ingreso junto con los valores reconocidos y los confirmados, en una sola transacción. El código es
el único identificador del ingreso: no se registra un número de ticket aparte.

El ingreso guarda tres marcas de tiempo independientes: la fecha y hora del pesaje, el inicio del
registro y el fin del registro. La primera combina la fecha reconocida del ticket con la hora que
indica el usuario, y es editable antes de confirmar; las otras dos las asigna el servidor y ningún
rol las modifica.

**Detalles**
- Imagen del ticket: JPG o PNG, hasta 10 MB. Obligatoria, salvo en el registro sin foto.
- Placa: obligatoria, reconocida y editable. Si no está en el catálogo, se da de alta el vehículo en
  la misma pantalla con placa, titularidad, capacidad de carga y, si es externo, transportista.
- Fecha del pesaje: obligatoria, reconocida del ticket y editable antes de confirmar. En el registro
  sin foto la indica el usuario.
- Hora del pesaje: obligatoria; propuesta con la hora en que se abre la revisión y editable.
- Peso bruto: obligatorio, reconocido y editable, en toneladas, decimal positivo.
- Tara: tomada del catálogo del vehículo, no editable en el registro.
- Peso neto: calculado por el servidor como peso bruto menos tara, no editable; se muestra antes de
  confirmar como referencia.
- Tipo de mineral: obligatorio, seleccionado del catálogo. El Administrativo y el Administrador
  pueden agregar uno nuevo desde el registro.
- Tipo de vehículo: derivado del catálogo, no editable.
- Motivo del registro sin foto: obligatorio en ese caso, elegido entre «Ticket extraviado o dañado»,
  «Sin cámara o sin señal en el punto de pesaje», «La balanza no emitió ticket» y «Otro».
- Justificación: obligatoria solo si la validación advierte un ticket posiblemente duplicado o un
  peso fuera del rango de carga.
- Inicio y fin del registro: asignados por el servidor, no editables. En el registro sin foto, el
  inicio se asigna cuando el usuario elige registrar sin foto.
- Código: asignado por el servidor, no editable.
- Estado: Registrado si el vehículo tiene tara; En proceso si está pendiente de destare.
- Roles autorizados: Supervisor de planta, Administrativo y Administrador.

**Criterios de aceptación**

> **CA01.** Dado que el vehículo tiene tara registrada y el usuario confirma datos válidos y sin
> inconsistencias pendientes, cuando confirma el registro, entonces el sistema calcula el peso neto,
> persiste el ingreso como Registrado, le asigna un código y muestra "Ingreso registrado con el
> código {codigo}".

> **CA02.** Dado que el usuario no adjuntó la imagen del ticket ni eligió el registro sin foto,
> cuando intenta confirmar, entonces el sistema rechaza la operación mostrando "Debe adjuntar la
> imagen del ticket de balanza".

> **CA03.** Dado que falta la placa, la fecha, la hora del pesaje, el peso bruto, el tipo de mineral
> o, en el registro sin foto, el motivo, cuando el usuario intenta confirmar, entonces el sistema
> rechaza la operación mostrando "Debe completar los campos obligatorios" e indica cuáles faltan.

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

> **CA10.** Dado que el usuario abre la revisión de los datos, cuando el sistema los presenta,
> entonces propone como hora del pesaje la hora actual, la señala como propuesta y permite
> modificarla antes de confirmar.

> **CA11.** Dado que el ingreso se persiste, cuando concluye la operación, entonces el sistema
> conserva la imagen asociada al ingreso, cuando la hay, guarda para cada campo reconocido el valor propuesto y el
> confirmado, y registra el evento en auditoría.

> **CA12.** Dado que la operación falla en cualquier punto después de confirmar, cuando el sistema
> la interrumpe, entonces no queda un ingreso a medio registrar: o se persiste todo o no se persiste
> nada.

> **CA13.** Dado que la placa corresponde a un vehículo dado de baja, cuando el usuario intenta
> confirmar, entonces el sistema rechaza la operación mostrando "El vehículo {placa} está dado de
> baja: no puede asociarse a un ingreso".

> **CA14.** Dado que el tipo de mineral no está en el catálogo y el usuario es Administrativo o
> Administrador, cuando lo agrega desde el registro, entonces el sistema lo incorpora al catálogo con
> las mismas reglas del alta desde el catálogo y lo deja elegido para el ingreso, sin perder los datos
> ya capturados.

> **CA15.** Dado que el usuario es Supervisor de planta y el tipo de mineral no está en el catálogo,
> cuando abre la lista de tipos de mineral, entonces el sistema no le ofrece agregarlo y muestra "Si
> no está en la lista, pida a un administrativo que lo registre".

> **CA16.** Dado que el ticket se extravió o no puede fotografiarse, cuando el usuario elige el
> registro sin foto, indica el motivo y confirma datos válidos, entonces el sistema persiste el
> ingreso sin imagen y sin reconocimiento, con su motivo, y lo marca como sin respaldo fotográfico.

> **CA17.** Dado que un ingreso se registró sin foto, cuando se consulta en cualquier lista o en su
> detalle, entonces el sistema lo muestra señalado como sin respaldo fotográfico, con su motivo.

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

La corrección alcanza a los datos que provienen del ticket y a los que el usuario eligió o indicó:
placa, fecha y hora del pesaje, peso bruto y tipo de mineral. No alcanza al código, a las dos marcas
de tiempo del servidor ni a la imagen, que es el respaldo de lo que se registró; por eso un ingreso
registrado sin foto conserva esa marca. Tampoco a la tara ni al peso neto de forma directa: el neto
se recalcula a partir del peso bruto corregido y, si se corrige la placa, con la tara del vehículo
correcto. Si ese vehículo todavía no tiene tara, el ingreso vuelve a quedar En proceso hasta su
destare.

Toda corrección exige un motivo y vuelve a someter los datos a las reglas de validación: un ingreso
corregido cumple exactamente las mismas condiciones que uno nuevo. El sistema conserva los valores
anteriores, de modo que siempre puede reconstruirse qué decía el registro antes del cambio.

Si el ingreso ya pertenece a un lote de proceso, su tipo de mineral no puede cambiarse por otro
distinto del que tiene el lote: el lote reúne un solo tipo de mineral (M06).

**Detalles**
- Campos corregibles: placa, fecha y hora del pesaje, peso bruto, tipo de mineral y justificación.
- Campos recalculados por el sistema: tara aplicada y peso neto; el estado, si el vehículo corregido
  no tiene tara.
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

> **CA08.** Dado que la placa corregida corresponde a un vehículo sin tara, cuando el usuario guarda
> la corrección, entonces el sistema retira el peso neto y la tara aplicada, y deja el ingreso En
> proceso hasta el destare de ese vehículo.

> **CA09.** Dado que el ingreso pertenece a un lote y el usuario cambia su tipo de mineral por otro
> distinto del lote, cuando intenta guardar, entonces el sistema rechaza la operación mostrando "El
> ingreso {codigo} corresponde a otro tipo de mineral que el lote {lote}".

> **CA10.** Dado que el usuario no modificó ningún campo, cuando intenta guardar la corrección,
> entonces el sistema rechaza la operación mostrando "No hay cambios que guardar".

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

Si el ingreso pertenece a un lote que todavía reúne ingresos, la anulación lo retira del lote. Si
el lote ya inició su recorrido, el ingreso permanece vinculado a él pero deja de contar en sus
totales (M06).

**Detalles**
- Motivo de la anulación: obligatorio, texto libre.
- Rol autorizado: Administrador.
- Efecto: el ingreso se excluye de totales y consolidaciones; permanece en el detalle y en las
  consultas, señalado como anulado.

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

> **CA08.** Dado que el ingreso pertenece a un lote que todavía reúne ingresos, cuando se anula,
> entonces el sistema lo retira de ese lote y registra el retiro en auditoría.

---

## HU-M03-04 — Registro del destare de un vehículo en su primer viaje

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M03-04 |
| **Épica** | Registro de ingresos |
| **Prioridad** | Crítica |

**Historia**

Como supervisor de planta, quiero registrar la tara del volquete cuando se pesa vacío en su primer
viaje, para que el sistema calcule el peso neto de sus ingresos y de todos los siguientes sin tener
que volver a destararlo.

**Descripción**

En el primer viaje de un vehículo, después de descargar, el volquete se pesa vacío en la balanza.
El operador de la balanza anota a mano la resta en el ticket; esa anotación es parte del trabajo de
la balanza y queda fuera del sistema. En el sistema, el usuario elige el vehículo entre los que
tienen ingresos En proceso y **digita** la tara. La tara no se reconoce de la imagen: se escribe a
mano por seguridad del dato, porque de ella depende el peso neto de todos los ingresos futuros de
ese vehículo.

La fecha y hora del destare se proponen con la hora actual y el usuario las ajusta a la del pesaje
en vacío; no pueden ser posteriores al momento del registro.

El sistema guarda la tara en el catálogo del vehículo, con la fecha del destare y el usuario que la
registró, calcula el peso neto de todos los ingresos En proceso de ese vehículo, los somete a las
reglas de validación que dependen del peso y los pasa a Registrado. Desde ese momento la tara se
mantiene por decisión de la Gerencia: solo el Administrador puede modificarla, con motivo
(HU-M02-01).

**Detalles**
- Vehículo: elegido entre los que tienen ingresos En proceso.
- Tara: obligatoria, digitada, en toneladas, decimal positivo, menor que el peso bruto de cada
  ingreso En proceso del vehículo.
- Fecha y hora del destare: propuestas con la hora actual y editables; no posteriores al registro.
- Se registra una sola vez por vehículo.
- Efecto sobre el vehículo: queda con tara, fecha del destare y usuario que la registró.
- Efecto sobre cada ingreso En proceso del vehículo: tara aplicada, peso neto calculado y estado
  Registrado.
- Justificación: obligatoria por cada ingreso cuyo peso neto resulte fuera del rango de carga.
- Roles autorizados: Supervisor de planta, Administrativo y Administrador.

**Criterios de aceptación**

> **CA01.** Dado que el vehículo tiene ingresos En proceso y el usuario digita una tara válida,
> cuando confirma el destare, entonces el sistema guarda la tara en el vehículo, calcula el peso neto
> de esos ingresos, los pasa a Registrado y muestra "Destare registrado" con la lista de ingresos
> completados y su peso neto.

> **CA02.** Dado que el usuario no digita la tara, cuando intenta confirmar el destare, entonces el
> sistema rechaza la operación mostrando "Debe indicar la tara del vehículo".

> **CA03.** Dado que la tara digitada es mayor o igual que el peso bruto de alguno de los ingresos
> En proceso del vehículo, cuando el usuario intenta confirmar, entonces el sistema rechaza la
> operación mostrando "La tara no puede ser mayor o igual que el peso bruto".

> **CA04.** Dado que el peso neto resultante de un ingreso queda fuera del rango de carga del
> vehículo, cuando el usuario intenta confirmar sin justificarlo, entonces el sistema rechaza la
> operación mostrando "Debe indicar la justificación del peso fuera de rango".

> **CA05.** Dado que el vehículo ya tiene tara registrada, cuando se intenta registrar un destare,
> entonces el sistema rechaza la operación mostrando "El vehículo {placa} ya tiene tara registrada".

> **CA06.** Dado que existen ingresos En proceso, cuando el usuario abre el registro de destares,
> entonces el sistema los lista con su código, placa, fecha del pesaje y peso bruto, y permite elegir
> el vehículo.

> **CA07.** Dado que el vehículo tiene varios ingresos En proceso, cuando se registra su tara,
> entonces el sistema calcula el peso neto de todos ellos y los pasa a Registrado en la misma
> operación.

> **CA08.** Dado que el destare se persiste, cuando concluye la operación, entonces el sistema
> registra en auditoría la tara, el vehículo, los ingresos afectados y el usuario responsable.

> **CA09.** Dado que la fecha y hora del destare son posteriores al momento del registro, cuando el
> usuario intenta confirmar, entonces el sistema rechaza la operación mostrando "La fecha del
> destare no puede ser posterior a la fecha actual".

> **CA10.** Dado que no hay ingresos En proceso, cuando el usuario abre el registro de destares,
> entonces el sistema muestra "No hay vehículos pendientes de destare".
