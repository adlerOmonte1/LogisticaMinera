# Historias de usuario — M07 Consulta de ingresos y respaldo

**RF asociado:** RF08 · **Historias:** 3

> Módulo de lectura sobre los ingresos. Existe para responder una pregunta concreta y frecuente:
> qué se registró de un volquete determinado en una fecha determinada, con el ticket a la vista y
> el recorrido de su mineral en la planta. Ofrece además la vista de trabajo de un periodo y el
> calendario de llegadas. No escribe nada ni tiene entidad propia: lee sobre M03 y presenta lo que
> los demás módulos conservan.

---

## HU-M07-01 — Consulta de un ingreso por placa y fecha con su respaldo

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M07-01 |
| **Épica** | Consulta de ingresos y respaldo |
| **Prioridad** | Crítica |

**Historia**

Como administrativo, quiero encontrar un ingreso por la placa del volquete y la fecha, y ver la
fotografía del ticket junto a los datos, para responder una consulta sin ir a buscar el papel al
archivador.

**Descripción**

La consulta se hace por placa y fecha, que es como se pregunta en la práctica: alguien menciona un
volquete y un día. La placa admite búsqueda parcial, porque quien pregunta suele recordar solo parte
del número; la fecha admite un día concreto o un rango.

El resultado lleva a la imagen del ticket. No basta con mostrar los datos: el valor de la consulta
está en poder contrastar lo registrado con lo que dice el papel, y por eso la imagen se presenta de
forma que pueda ampliarse y leerse.

Los ingresos anulados aparecen en los resultados, señalados como tales y con su motivo. Ocultarlos
haría que una consulta sobre un volquete que sí pasó por la balanza no devolviera nada, y quien
pregunta concluiría que no se registró.

Los ingresos En proceso —primer viaje de un vehículo, pendiente del destare— también aparecen,
señalados como tales y sin peso neto, porque todavía no lo tienen. Aparecen porque el volquete sí
ingresó; no suman toneladas hasta que se registre el destare.

Un ingreso registrado sin foto (DR-13) aparece igual, pero en lugar de la imagen se muestra que no
tiene respaldo fotográfico y el motivo. Es distinto del respaldo que existe y no puede recuperarse en
ese momento, que se informa como no disponible.

El resultado incluye la **trazabilidad** del ingreso: el lote al que pertenece, su estado y el
recorrido por las etapas de su ruta (HU-M06-03). Así la misma consulta responde qué se registró y
dónde está el mineral. Un ingreso sin lote se muestra como mineral que espera en cancha.

**Detalles**
- Criterios: placa, total o parcial, y fecha o rango de fechas.
- La placa no distingue mayúsculas ni guiones.
- Resultados ordenados por fecha del ticket, del más reciente al más antiguo.
- Cada resultado muestra código, fecha y hora del pesaje, placa, tipo de mineral, peso bruto, peso
  neto y estado; un ingreso En proceso muestra el peso neto como pendiente del destare.
- El detalle muestra la imagen del ticket ampliable —o el motivo de su ausencia— y las tres marcas
  de tiempo.
- La trazabilidad del ingreso se muestra junto al resultado.
- Roles autorizados: los tres.

**Criterios de aceptación**

> **CA01.** Dado que el usuario indica una placa y una fecha, cuando ejecuta la consulta, entonces
> el sistema muestra los ingresos de ese vehículo en esa fecha, ordenados del más reciente al más
> antiguo.

> **CA02.** Dado que el usuario indica solo parte de la placa, cuando ejecuta la consulta, entonces
> el sistema muestra los ingresos de todos los vehículos cuya placa contenga ese texto.

> **CA03.** Dado que el usuario abre un resultado, cuando el sistema muestra el detalle, entonces
> presenta la imagen del ticket junto a los datos registrados, y permite ampliarla.

> **CA04.** Dado que no existen ingresos para esos criterios, cuando se ejecuta la consulta,
> entonces el sistema muestra "No se encontraron ingresos con los criterios indicados".

> **CA05.** Dado que uno de los resultados corresponde a un ingreso anulado, cuando se muestran los
> resultados, entonces el sistema lo incluye señalado como anulado y con su motivo.

> **CA06.** Dado que el usuario no indica ningún criterio, cuando intenta ejecutar la consulta,
> entonces el sistema rechaza la operación mostrando "Debe indicar al menos la placa o la fecha".

> **CA07.** Dado que un ingreso se registró sin imagen recuperable, cuando se abre su detalle,
> entonces el sistema muestra los datos e indica que el respaldo no está disponible.

> **CA08.** Dado que uno de los resultados corresponde a un ingreso En proceso, cuando se muestran
> los resultados, entonces el sistema lo incluye señalado como En proceso, con su peso bruto y con el
> peso neto indicado como pendiente del destare.

> **CA09.** Dado que el ingreso se registró sin foto, cuando se abre su resultado, entonces el
> sistema muestra los datos, indica que no tiene respaldo fotográfico y presenta el motivo, en lugar
> de la imagen.

> **CA10.** Dado que el ingreso pertenece a un lote, cuando se muestra el resultado, entonces el
> sistema presenta el lote, su estado y el recorrido por las etapas de su ruta.

> **CA11.** Dado que el ingreso aún no tiene lote, cuando se muestra el resultado, entonces el
> sistema indica que el mineral espera en cancha y que no ha recorrido ninguna etapa.

> **CA12.** Dado que el rango de fechas indicado es inverso, cuando el usuario ejecuta la consulta,
> entonces el sistema rechaza la operación mostrando "La fecha inicial no puede ser posterior a la
> fecha final".

---

## HU-M07-02 — Listado y detalle de ingresos

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M07-02 |
| **Épica** | Consulta de ingresos y respaldo |
| **Prioridad** | Alta |

**Historia**

Como administrativo, quiero revisar los ingresos de un periodo con filtros y ver el detalle completo
de cualquiera, para hacer seguimiento del trabajo sin depender de una consulta puntual.

**Descripción**

El listado muestra los ingresos con filtros combinables por fecha, tipo de mineral, vehículo,
titularidad y estado, y una búsqueda por placa o por código. Al abrirse, presenta el mes en curso
hasta la fecha actual. Es la vista de trabajo cotidiana, complementaria de la búsqueda puntual de
HU-M07-01: aquella responde por un volquete concreto, esta permite revisar un conjunto.

El detalle de un ingreso reúne todo lo que el sistema sabe de él: los datos del ticket, la imagen,
las tres marcas de tiempo, quién lo registró, su estado, el resultado de las validaciones, la
comparación entre lo reconocido y lo confirmado, el recorrido por las etapas del proceso y el
historial de todo lo que le ocurrió (HU-M09-02). Cada bloque lo aporta el módulo responsable; esta
historia los reúne en una sola vista, organizada en pestañas: datos, ticket, reconocimiento,
validación, trazabilidad e historial.

**Detalles**
- Filtros: rango de fechas —por defecto, el mes en curso hasta hoy—, tipo de mineral, vehículo,
  titularidad y estado; búsqueda por placa o código.
- Los filtros se combinan entre sí.
- Resultados paginados y ordenados por fecha del ticket descendente.
- El listado muestra el total de ingresos y la suma de toneladas del conjunto filtrado; solo suman
  los ingresos Registrados.
- Los ingresos sin respaldo fotográfico se señalan en la lista.
- El detalle incluye validaciones, reconocimiento, trazabilidad e historial.
- Roles autorizados: los tres.

**Criterios de aceptación**

> **CA01.** Dado que el usuario indica un rango de fechas, cuando ejecuta el listado, entonces el
> sistema muestra los ingresos de ese periodo, paginados y ordenados por fecha descendente.

> **CA02.** Dado que el usuario combina varios filtros, cuando ejecuta el listado, entonces el
> sistema muestra solo los ingresos que cumplen todos ellos.

> **CA03.** Dado que el usuario ejecuta un listado, cuando el sistema muestra los resultados,
> entonces presenta el número de ingresos y la suma de toneladas del conjunto filtrado, excluyendo
> de esa suma los anulados y los que están En proceso.

> **CA04.** Dado que el usuario abre el detalle de un ingreso, cuando el sistema lo muestra,
> entonces presenta los datos del ticket, la imagen, las tres marcas de tiempo como valores
> distintos, el usuario que registró, el estado, la tara aplicada y el peso neto calculado.

> **CA05.** Dado que un ingreso tiene reconocimiento, validaciones o trazabilidad asociados, cuando
> se abre su detalle, entonces el sistema los presenta en su bloque correspondiente.

> **CA06.** Dado que un ingreso no tiene alguno de esos elementos, cuando se abre su detalle,
> entonces el sistema indica su ausencia en lugar de omitir el bloque.

> **CA07.** Dado que el rango de fechas indicado es inverso, cuando el usuario ejecuta el listado,
> entonces el sistema rechaza la operación mostrando "La fecha inicial no puede ser posterior a la
> fecha final".

> **CA08.** Dado que el usuario abre el listado sin indicar fechas, cuando el sistema lo presenta,
> entonces muestra los ingresos del mes en curso hasta la fecha actual.

> **CA09.** Dado que un ingreso del listado se registró sin foto, cuando se muestran los resultados,
> entonces el sistema lo señala como sin respaldo fotográfico sin necesidad de abrir el detalle.

> **CA10.** Dado que el usuario escribe parte de una placa o de un código, cuando ejecuta la
> búsqueda, entonces el sistema muestra los ingresos cuya placa o cuyo código lo contienen.

> **CA11.** Dado que no hay ingresos con los filtros indicados, cuando se ejecuta el listado,
> entonces el sistema muestra "No hay ingresos con estos filtros".

> **CA12.** Dado que el usuario abre la pestaña de historial del detalle, cuando el sistema la
> presenta, entonces muestra los eventos del ingreso en orden cronológico (HU-M09-02).

---

## HU-M07-03 — Calendario de llegadas

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M07-03 |
| **Épica** | Consulta de ingresos y respaldo |
| **Prioridad** | Media |

**Historia**

Como administrativo, quiero ver en un calendario cuántos volquetes llegaron cada día y cuántas
toneladas sumaron, para entender de un vistazo el ritmo de llegadas del mes.

**Descripción**

El calendario presenta un mes. Cada día muestra cuántos ingresos llegaron, sin contar los anulados,
y cuántas toneladas netas suman los Registrados; el color del día se intensifica con las toneladas.
Un día con ingresos En proceso o anulados lleva una marca que lo indica. Arriba, el mes se resume en
cuatro cifras: ingresos del mes, toneladas netas, días con llegadas e ingresos En proceso.

Al elegir un día, el sistema lista sus ingresos con la hora del pesaje, la placa, el código, el tipo
de mineral, el peso neto —o su condición de pendiente del destare— y el estado. Desde ahí se abre el
detalle de cualquiera.

El día de cada ingreso es el de su fecha del pesaje, no el del registro: el calendario describe
cuándo llegaron los volquetes. Los totales siguen el mismo criterio que el listado y la
consolidación: solo suman los Registrados.

**Detalles**
- Periodo: un mes; navegación al mes anterior, al siguiente y al mes en curso.
- Por día: número de ingresos no anulados y toneladas netas de los Registrados.
- Marcas por día: hay ingresos En proceso; hay ingresos anulados.
- Resumen del mes: ingresos sin anulados, toneladas netas de los Registrados, días con llegadas e
  ingresos En proceso.
- Día elegido: lista de sus ingresos, con acceso al detalle.
- Roles autorizados: los tres.

**Criterios de aceptación**

> **CA01.** Dado que el usuario abre el calendario, cuando el sistema lo presenta, entonces muestra
> el mes en curso con el número de ingresos y las toneladas netas de cada día.

> **CA02.** Dado que un día tiene ingresos anulados, cuando se muestra el calendario, entonces el
> sistema no los cuenta ni los suma, y marca el día como con anulados.

> **CA03.** Dado que un día tiene ingresos En proceso, cuando se muestra el calendario, entonces el
> sistema los cuenta como llegadas, no suma su peso y marca el día como con ingresos en proceso.

> **CA04.** Dado que el usuario elige un día, cuando el sistema lo presenta, entonces lista sus
> ingresos con la hora del pesaje, la placa, el código, el tipo de mineral, el peso neto y el estado.

> **CA05.** Dado que el día elegido no tiene ingresos, cuando el sistema lo presenta, entonces
> muestra "No llegaron volquetes este día".

> **CA06.** Dado que el usuario navega a otro mes, cuando el sistema lo presenta, entonces recalcula
> los días y el resumen del mes con el mismo criterio.

> **CA07.** Dado que el usuario elige un ingreso de la lista del día, cuando lo abre, entonces el
> sistema muestra su detalle completo (HU-M07-02).

> **CA08.** Dado que se calcula el total de toneladas de un mes en el calendario, cuando se compara
> con el consolidado de ese mes, entonces ambos coinciden.

