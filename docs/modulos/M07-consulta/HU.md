# Historias de usuario — M07 Consulta de ingresos y respaldo

**RF asociado:** RF08 · **Historias:** 2

> Módulo de lectura sobre los ingresos. Existe para responder una pregunta concreta y frecuente:
> qué se registró de un volquete determinado en una fecha determinada, con el ticket a la vista. No
> escribe nada ni tiene entidad propia: lee sobre M03 y presenta el respaldo que este conserva.

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

**Detalles**
- Criterios: placa, total o parcial, y fecha o rango de fechas.
- La placa no distingue mayúsculas ni guiones.
- Resultados ordenados por fecha del ticket, del más reciente al más antiguo.
- Cada resultado muestra código, fecha y hora del ticket, placa, tipo de mineral, peso neto y estado.
- El detalle muestra la imagen del ticket ampliable y las tres marcas de tiempo.
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
titularidad y estado. Es la vista de trabajo cotidiana, complementaria de la búsqueda puntual de
HU-M07-01: aquella responde por un volquete concreto, esta permite revisar un conjunto.

El detalle de un ingreso reúne todo lo que el sistema sabe de él: los datos del ticket, la imagen,
las tres marcas de tiempo, quién lo registró, su estado, el resultado de las validaciones, la
comparación entre lo reconocido y lo confirmado, y el recorrido por las etapas del proceso. Cada
bloque lo aporta el módulo responsable; esta historia los reúne en una sola vista.

**Detalles**
- Filtros: rango de fechas, tipo de mineral, vehículo, titularidad y estado.
- Los filtros se combinan entre sí.
- Resultados paginados y ordenados por fecha del ticket descendente.
- El listado muestra el total de ingresos y la suma de toneladas del conjunto filtrado.
- El detalle incluye validaciones, reconocimiento y trazabilidad cuando existen.
- Roles autorizados: los tres.

**Criterios de aceptación**

> **CA01.** Dado que el usuario indica un rango de fechas, cuando ejecuta el listado, entonces el
> sistema muestra los ingresos de ese periodo, paginados y ordenados por fecha descendente.

> **CA02.** Dado que el usuario combina varios filtros, cuando ejecuta el listado, entonces el
> sistema muestra solo los ingresos que cumplen todos ellos.

> **CA03.** Dado que el usuario ejecuta un listado, cuando el sistema muestra los resultados,
> entonces presenta el número de ingresos y la suma de toneladas del conjunto filtrado, excluyendo
> los anulados de esa suma.

> **CA04.** Dado que el usuario abre el detalle de un ingreso, cuando el sistema lo muestra,
> entonces presenta los datos del ticket, la imagen, las tres marcas de tiempo como valores
> distintos, el usuario que registró y el estado.

> **CA05.** Dado que un ingreso tiene reconocimiento, validaciones o trazabilidad asociados, cuando
> se abre su detalle, entonces el sistema los presenta en su bloque correspondiente.

> **CA06.** Dado que un ingreso no tiene alguno de esos elementos, cuando se abre su detalle,
> entonces el sistema indica su ausencia en lugar de omitir el bloque.

> **CA07.** Dado que el rango de fechas indicado es inverso, cuando el usuario ejecuta el listado,
> entonces el sistema rechaza la operación mostrando "La fecha inicial no puede ser posterior a la
> fecha final".
