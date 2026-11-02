# Historias de usuario — M07 Consulta de ingresos y respaldo

**RF asociado:** RF08 · **Historias:** 4

> Módulo de lectura sobre los ingresos. Existe para responder una pregunta concreta y frecuente:
> qué se registró de un volquete determinado en una fecha determinada, con el ticket a la vista y
> el recorrido de su mineral en la planta. Ofrece además la vista de trabajo de un periodo, con su
> exportación, el calendario de llegadas y la pantalla de inicio con el resumen del día y los avisos
> de pendientes. No escribe datos del dominio ni tiene entidad propia: lee sobre M03 y presenta lo
> que los demás módulos conservan.

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

El Administrativo y el Administrador pueden **exportar el listado** a un archivo CSV: el archivo
contiene el conjunto filtrado completo, no solo la página visible, con los mismos estados que muestra
el listado. Es una exportación de trabajo, no un reporte de producción: el total mensual por tipo de
mineral se obtiene en la consolidación (M08). Cada exportación queda en auditoría (DR-30).

Desde la **búsqueda de la cabecera**, presente en todas las pantallas, el usuario escribe el código
de un ingreso —completo o solo sus dígitos finales— y el sistema abre su detalle. Si lo escrito no
corresponde a ningún código, se toma como placa y lleva a la consulta por placa y fecha
(HU-M07-01).

**Detalles**
- Filtros: rango de fechas —por defecto, el mes en curso hasta hoy—, tipo de mineral, vehículo,
  titularidad y estado; búsqueda por placa o código.
- Los filtros se combinan entre sí.
- Resultados paginados y ordenados por fecha del ticket descendente.
- El listado muestra el total de ingresos y la suma de toneladas del conjunto filtrado; solo suman
  los ingresos Registrados.
- Los ingresos sin respaldo fotográfico se señalan en la lista.
- El detalle incluye validaciones, reconocimiento, trazabilidad e historial.
- Exportación: CSV en UTF-8, con separador punto y coma, del conjunto filtrado completo; columnas
  código, fecha y hora del pesaje, placa, tipo de vehículo, tipo de mineral, peso bruto, tara, peso
  neto, estado y usuario que registró. Solo Administrativo y Administrador.
- Búsqueda de la cabecera: código completo o dígitos finales; si no hay coincidencia, placa.
- Roles autorizados: los tres para consultar; Administrativo y Administrador para exportar.

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

> **CA13.** Dado que el usuario es Administrativo o Administrador y el listado tiene resultados,
> cuando elige exportar, entonces el sistema genera un archivo CSV con todos los ingresos del
> conjunto filtrado, sin limitarse a la página visible, y registra la exportación en auditoría con
> el número de ingresos.

> **CA14.** Dado que el conjunto filtrado no tiene ingresos, cuando el usuario intenta exportarlo,
> entonces el sistema rechaza la operación mostrando "No hay ingresos para exportar".

> **CA15.** Dado que el usuario tiene rol de Supervisor de planta, cuando intenta exportar el
> listado, entonces el sistema rechaza la operación mostrando "Acción no autorizada".

> **CA16.** Dado que el usuario escribe en la búsqueda de la cabecera el código de un ingreso,
> completo o sus dígitos finales, cuando la ejecuta, entonces el sistema abre el detalle de ese
> ingreso.

> **CA17.** Dado que lo escrito en la búsqueda de la cabecera no corresponde a ningún código, cuando
> el usuario la ejecuta, entonces el sistema lleva a la consulta por placa y fecha con ese texto como
> placa (HU-M07-01).

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

---

## HU-M07-04 — Resumen del día y avisos de pendientes

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M07-04 |
| **Épica** | Consulta de ingresos y respaldo |
| **Prioridad** | Media |

**Historia**

Como usuario del sistema, quiero ver al entrar lo que ocurrió hoy en la planta y lo que está
pendiente de mi parte, para empezar a trabajar por lo que corresponde sin recorrer cada pantalla.

**Descripción**

La pantalla de inicio es la primera que ve el usuario tras iniciar sesión. Resume el día en cuatro
cifras: los ingresos de hoy, sin contar los anulados, con la hora y la placa del último; las
toneladas netas de hoy, que solo suman los Registrados e indican cuántos ingresos En proceso quedan
fuera; los ingresos pendientes de destare, con las placas de sus vehículos; y los lotes en proceso,
es decir, los Abiertos y los En recorrido que aún no están listos para cerrar. Debajo presenta los
cinco ingresos más recientes y las toneladas netas de los últimos siete días, día por día.

Junto al resumen, el sistema ofrece **avisos de pendientes**, calculados según el rol: los ingresos
que esperan el destare; las advertencias V4 justificadas hoy; los lotes En recorrido con su siguiente
paso; los lotes listos para cerrar con su destino, solo para el Administrador; y los ingresos
Registrados que todavía no tienen lote, solo para quien compone los lotes. Cada aviso lleva a la
pantalla donde se resuelve.

Nada de esta pantalla se almacena: cifras y avisos se calculan sobre los ingresos y los lotes al
consultarse, con el mismo criterio que el listado, el calendario y la consolidación (DR-30). Un aviso
desaparece cuando se resuelve lo que lo originó, sin que nadie lo marque como leído.

**Detalles**
- Día de referencia: el de la fecha del pesaje, en la zona horaria de la planta.
- Cifras: ingresos de hoy sin anulados; toneladas netas de hoy de los Registrados; pendientes de
  destare; lotes en proceso.
- Últimos ingresos: los cinco más recientes por fecha del pesaje, con su estado y acceso al detalle.
- Toneladas de los últimos siete días: por día del pesaje, solo de los Registrados.
- Avisos: según el rol; cada uno con acceso a la pantalla que lo resuelve.
- Accesos directos: registrar un ingreso y consultar por placa, según el rol.
- Cada cifra enlaza con su pantalla solo si el rol tiene acceso a ella.
- Roles autorizados: los tres, con el contenido que corresponde a cada rol.

**Criterios de aceptación**

> **CA01.** Dado que el usuario inicia sesión, cuando se carga la pantalla de inicio, entonces el
> sistema muestra los ingresos de hoy sin los anulados, las toneladas netas de hoy, los ingresos
> pendientes de destare y los lotes en proceso.

> **CA02.** Dado que hoy hay ingresos En proceso, cuando se muestran las toneladas netas del día,
> entonces el sistema no suma su peso e indica "Sin contar {n} en proceso".

> **CA03.** Dado que aún no se registró ningún ingreso hoy, cuando se carga la pantalla de inicio,
> entonces el sistema muestra cero ingresos y la indicación "Aún no hay ingresos hoy".

> **CA04.** Dado que se presentan las toneladas de los últimos siete días, cuando se compara la suma
> de un día con la del calendario para ese día, entonces ambas coinciden.

> **CA05.** Dado que el usuario elige uno de los últimos ingresos, cuando lo abre, entonces el
> sistema muestra su detalle completo (HU-M07-02).

> **CA06.** Dado que hay ingresos pendientes de destare, cuando el usuario abre los avisos, entonces
> el sistema muestra uno por ingreso, con la placa y el peso bruto, y lleva al registro del destare.

> **CA07.** Dado que el usuario es Administrador y un lote tiene todo su mineral ensacado, cuando
> abre los avisos, entonces el sistema le indica que el lote está listo para cerrar con su destino y
> lleva a su cierre.

> **CA08.** Dado que el usuario es Supervisor de planta, cuando abre los avisos, entonces el sistema
> no le muestra los lotes listos para cerrar ni los ingresos sin lote, porque no son operaciones de
> su rol.

> **CA09.** Dado que no hay nada pendiente para el rol del usuario, cuando abre los avisos, entonces
> el sistema muestra "No hay nada pendiente".

> **CA10.** Dado que se registra el destare que originó un aviso, cuando el usuario vuelve a abrir
> los avisos, entonces ese aviso ya no aparece.

> **CA11.** Dado que el rol del usuario no tiene acceso a la pantalla de una cifra, cuando se muestra
> el resumen, entonces el sistema presenta la cifra sin enlace a esa pantalla.
