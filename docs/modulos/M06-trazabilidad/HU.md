# Historias de usuario — M06 Trazabilidad del proceso

**RF asociado:** RF07 · **Historias:** 5

> Módulo que sigue el mineral desde que ingresa a planta hasta que sale ensacado y se entrega. Como
> el mineral de varios volquetes se mezcla en cancha, el ingreso no recorre las etapas por sí solo:
> se asigna a un lote de proceso, y es el lote el que registra su paso por las etapas de la ruta que
> la planta decide para él. Esa indirección, la ruta, la división del lote y su cierre con destino
> son la responsabilidad del módulo.

**Ciclo del lote.** Un lote está **Abierto** mientras reúne ingresos; pasa a **En recorrido** con el
inicio del recorrido, que empieza por el secado; y queda **Cerrado** cuando el Administrador lo
cierra definitivamente con su destino. El secado es común a todo el lote. Después la planta decide
una de tres rutas: zarandeo y ensacado; molienda y ensacado; o zarandeo, molienda y ensacado. Si el
lote se divide, cada parte tiene su propia ruta.

---

## HU-M06-01 — Gestión de lotes de proceso

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M06-01 |
| **Épica** | Trazabilidad del proceso |
| **Prioridad** | Alta |

**Historia**

Como administrativo, quiero agrupar en un lote los ingresos que se procesan juntos, para poder
seguir su avance por las etapas sin tener que anotar cada volquete por separado.

**Descripción**

Un lote reúne los ingresos que se procesarán como una sola carga. Se abre con un nombre, un tipo de
mineral y la fecha de apertura, y recibe ingresos mientras está Abierto. Si la carga mezcla
minerales, el usuario lo declara con la acción **Agregar otro mineral**: el tipo se suma a la lista
del lote y desde entonces admite sus ingresos (DR-27). El lote muestra sus ingresos y sus toneladas
agrupados por tipo de mineral, de modo que la mezcla siempre es visible y nunca accidental.

También se puede unificar un ingreso de otro tipo de mineral directamente al agregar ingresos: la
opción **Agregar de otro tipo de mineral** muestra esos ingresos agrupados por mineral. Elegir uno
exige indicar la autorización o el motivo —por ejemplo, que el gerente aprobó procesarlo junto—; su
mineral se suma a la lista del lote y el ingreso queda marcado «Otro mineral», con esa autorización
visible en la composición. Mientras el lote está Abierto, la agrupación es una decisión revisable: un ingreso puede
retirarse del lote o trasladarse a otro.

Cuando la carga está reunida, el usuario **inicia el recorrido**: el lote pasa a En recorrido y su
siguiente paso es el secado. El lote todavía admite **ingresos tardíos**, porque pueden llegar
volquetes que se suman a una carga ya en marcha. Y como agregar un ingreso al lote equivocado es un
error posible del usuario, el ingreso puede retirarse —y volver a cancha— hasta que su mineral pase
por zarandeo o molienda: después de esas etapas el mineral ya se transformó junto con el resto y el
retiro dejaría de describir lo ocurrido (DR-29). El secado ya registrado del lote se conserva.
Un ingreso tardío que llega antes del secado del lote se seca junto con el resto; uno que llega
después tiene su propio secado. Si el lote está dividido, el ingreso tardío se reparte entre las
partes (HU-M06-04).

La gestión del lote es una sola capacidad: abrirlo, consultarlo, asignarle o retirarle ingresos e
iniciar su recorrido son operaciones del mismo trabajo. El cierre definitivo, con su destino, es una
historia aparte (HU-M06-05).

**Detalles**
- Código del lote: asignado por el servidor, único.
- Nombre: obligatorio, único entre los lotes.
- Tipos de mineral: uno obligatorio al abrir, del catálogo; otros se agregan con «Agregar otro
  mineral». Un tipo sin ingresos puede quitarse mientras el lote está Abierto.
- Composición: ingresos y toneladas agrupados por tipo de mineral.
- Fecha de apertura: obligatoria, no posterior a la fecha actual.
- Fecha de inicio del recorrido: se asigna al iniciarlo.
- Estado: Abierto, En recorrido o Cerrado.
- Solo se asignan ingresos en estado Registrado: ni los anulados ni los que siguen En proceso,
  pendientes del destare, porque aún no tienen peso neto.
- Retiro y traslado de ingresos: mientras el mineral del ingreso no haya pasado por zarandeo ni
  molienda; un lote En recorrido conserva al menos un ingreso (DR-29).
- Ingresos tardíos: admitidos mientras el lote está En recorrido, señalados como tales.
- Roles autorizados: Administrativo y Administrador.

**Criterios de aceptación**

> **CA01.** Dado que el usuario indica el nombre, el tipo de mineral y la fecha de apertura, cuando
> crea el lote, entonces el sistema lo registra Abierto, le asigna un código y muestra "Lote
> {nombre} abierto".

> **CA02.** Dado que ya existe un lote con el mismo nombre, cuando el usuario intenta crearlo,
> entonces el sistema rechaza la operación mostrando "Ya existe un lote con el nombre «{nombre}»".

> **CA03.** Dado que la fecha de apertura es posterior a la fecha actual, cuando el usuario intenta
> crear el lote, entonces el sistema rechaza la operación mostrando "La fecha de apertura no puede
> ser posterior a hoy".

> **CA04.** Dado que un lote está Abierto, cuando el usuario le asigna ingresos Registrados de un
> tipo de mineral que está en la lista del lote, entonces el sistema los incorpora y muestra el total
> de ingresos y de toneladas del lote, y el de cada tipo de mineral.

> **CA05.** Dado que un ingreso es de un tipo de mineral que no está en la lista del lote, cuando el
> usuario abre la asignación, entonces el sistema no lo ofrece entre los ingresos del lote, sino en
> «Agregar de otro tipo de mineral», agrupado por su tipo de mineral.

> **CA06.** Dado que un ingreso está anulado, cuando el usuario intenta asignarlo a un lote,
> entonces el sistema rechaza la operación mostrando "No se puede asignar un ingreso anulado".

> **CA07.** Dado que un ingreso está En proceso, cuando el usuario intenta asignarlo a un lote,
> entonces el sistema rechaza la operación mostrando "El ingreso {codigo} está en proceso: falta el
> destare del vehículo".

> **CA08.** Dado que un ingreso pertenece a otro lote cuyo mineral aún no pasó por zarandeo ni
> molienda, cuando el usuario lo asigna a este, entonces el sistema lo traslada y deja constancia del
> cambio en ambos lotes.

> **CA09.** Dado que el mineral del ingreso ya pasó por zarandeo o molienda —en alguna parte del lote
> o, si es un ingreso tardío con secado propio, en alguna de sus partes—, cuando el usuario intenta
> retirarlo o trasladarlo a otro lote, entonces el sistema rechaza la operación mostrando "El mineral
> del ingreso {codigo} ya pasó por zarandeo o molienda".

> **CA10.** Dado que un lote Abierto tiene al menos un ingreso, cuando el usuario inicia el
> recorrido, entonces el sistema registra la fecha de inicio, pasa el lote a En recorrido y muestra
> "Recorrido del lote {nombre} iniciado".

> **CA11.** Dado que un lote no tiene ingresos, cuando el usuario intenta iniciar el recorrido,
> entonces el sistema rechaza la operación mostrando "El lote no tiene ingresos asignados".

> **CA12.** Dado que el lote está En recorrido y su secado aún no se registró, cuando el usuario le
> agrega un ingreso, entonces el sistema lo incorpora como ingreso tardío que se seca junto con el
> resto del lote.

> **CA13.** Dado que el lote está En recorrido y su secado ya se registró, cuando el usuario le
> agrega un ingreso, entonces el sistema lo incorpora como ingreso tardío con secado propio.

> **CA14.** Dado que el usuario no seleccionó ningún ingreso, cuando intenta asignar, entonces el
> sistema rechaza la operación mostrando "Seleccione al menos un ingreso".

> **CA15.** Dado que el usuario tiene rol de Supervisor de planta, cuando intenta abrir un lote,
> asignarle o retirarle ingresos o iniciar su recorrido, entonces el sistema rechaza la operación
> mostrando "Acción no autorizada".

> **CA16.** Dado que el usuario consulta un lote, cuando el sistema lo muestra, entonces presenta su
> estado y su composición —los ingresos con su código, su fecha y su peso neto, con los tardíos
> señalados— y el total de toneladas.

> **CA17.** Dado que el lote no está Cerrado, cuando el usuario elige «Agregar otro mineral» e indica
> un tipo de mineral del catálogo, entonces el sistema lo suma a la lista del lote, muestra su grupo
> sin ingresos y registra el cambio en auditoría.

> **CA18.** Dado que un tipo de mineral ya está en el lote, cuando el usuario intenta agregarlo de
> nuevo, entonces el sistema rechaza la operación mostrando "El mineral {mineral} ya está en el
> lote".

> **CA19.** Dado que un tipo de mineral del lote tiene ingresos asignados, cuando el usuario intenta
> quitarlo, entonces el sistema rechaza la operación mostrando "No se puede quitar {mineral}: tiene
> ingresos en el lote".

> **CA20.** Dado que el usuario eligió ingresos de otro tipo de mineral, cuando intenta agregarlos sin
> indicar la autorización o el motivo, entonces el sistema rechaza la operación mostrando "Indique
> quién autorizó o el motivo para unificar otro tipo de mineral".

> **CA21.** Dado que el usuario agrega un ingreso de otro tipo de mineral con su autorización, cuando
> el sistema lo incorpora, entonces suma ese mineral a la lista del lote, muestra el ingreso en su
> grupo marcado «Otro mineral» con la autorización, y registra ambos actos en auditoría.

> **CA22.** Dado que el lote está En recorrido y ninguna de sus partes registró zarandeo ni molienda,
> cuando el usuario retira un ingreso agregado por error, entonces el sistema lo devuelve a cancha sin
> lote, recalcula los totales del lote, conserva el secado ya registrado y registra el retiro en
> auditoría.

> **CA23.** Dado que el lote está En recorrido y tiene un solo ingreso, cuando el usuario intenta
> retirarlo o trasladarlo, entonces el sistema rechaza la operación mostrando "El lote {codigo} en
> recorrido debe conservar al menos un ingreso".

---

## HU-M06-02 — Registro del paso de un lote por una etapa de su ruta

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M06-02 |
| **Épica** | Trazabilidad del proceso |
| **Prioridad** | Crítica |

**Historia**

Como supervisor de planta, quiero registrar que un lote pasó por una etapa del proceso, para que
quede constancia de dónde está el mineral y qué le falta.

**Descripción**

El primer paso de todo lote En recorrido es el secado, común a todo el lote. Al registrar el paso
siguiente, el usuario elige la **ruta** que sigue el mineral: zarandeo y ensacado; molienda y
ensacado; o zarandeo, molienda y ensacado. Si el lote se dividió, cada parte tiene su ruta y sus
etapas se registran por separado. El sistema guarda el momento de cada paso y quién lo registró.

Las etapas se registran en el orden de la ruta: no puede anotarse el ensacado de una parte que aún
no pasó por la molienda que su ruta exige. Cada etapa se registra una sola vez por lote o por parte.
Un ingreso tardío que llega después del secado registra primero su propio secado y después sus
porciones siguen la ruta de las partes a las que se reparten.

Al registrar la molienda, el usuario puede indicar las horas de uso del molino; con ellas el sistema
calcula las toneladas por hora. Al registrar el ensacado, indica cuántos bigbags se llenaron: el
sistema estima el peso de cada uno a partir de las toneladas pendientes de ensacar, o el usuario lo
recalcula con el peso observado. Ambos son datos descriptivos de la gestión de la planta: no son
inventario de producto terminado ni miden pérdidas (DR-15).

**Detalles**
- Etapas: secado, zarandeo, molienda y ensacado.
- Rutas: zarandeo y ensacado; molienda y ensacado; zarandeo, molienda y ensacado. Siempre después
  del secado común.
- Fecha y hora del paso: obligatorias; no posteriores al momento del registro, no anteriores a la
  etapa previa ni, en la primera etapa, al inicio del recorrido.
- Usuario que registra: lo asigna el sistema.
- Observación: opcional.
- Horas de molienda: opcionales, mayores que cero.
- Bigbags: cantidad al registrar el ensacado o después; peso aproximado calculado por el sistema o
  recalculado por el usuario.
- Roles autorizados: los tres.

**Criterios de aceptación**

> **CA01.** Dado que el lote está En recorrido y le corresponde la siguiente etapa de su ruta, cuando
> el usuario registra su paso indicando el momento, entonces el sistema lo registra y muestra "Etapa
> {etapa} registrada para el lote {codigo}".

> **CA02.** Dado que el lote ya registró su secado y todavía no tiene ruta, cuando el usuario intenta
> registrar el paso siguiente sin elegirla, entonces el sistema rechaza la operación mostrando
> "Elija qué etapa sigue después del secado".

> **CA03.** Dado que el lote no ha pasado por la etapa anterior de su ruta, cuando el usuario intenta
> registrar una etapa, entonces el sistema rechaza la operación mostrando "El lote debe pasar primero
> por la etapa {etapa anterior}".

> **CA04.** Dado que la etapa ya fue registrada para ese lote o esa parte, cuando el usuario intenta
> registrarla de nuevo, entonces el sistema rechaza la operación mostrando "La etapa {etapa} ya fue
> registrada para el lote {codigo}".

> **CA05.** Dado que el lote está Abierto, cuando el usuario intenta registrar una etapa, entonces el
> sistema rechaza la operación mostrando "El lote debe iniciar su recorrido antes de registrar
> etapas".

> **CA06.** Dado que la fecha indicada es posterior al momento del registro, cuando el usuario
> intenta guardar, entonces el sistema rechaza la operación mostrando "La fecha de la etapa no puede
> ser posterior a la fecha actual".

> **CA07.** Dado que la fecha indicada es anterior a la del paso por la etapa previa, cuando el
> usuario intenta guardar, entonces el sistema rechaza la operación mostrando "La fecha de la etapa
> no puede ser anterior a la de la etapa {etapa anterior}".

> **CA08.** Dado que la fecha de la primera etapa es anterior al inicio del recorrido, cuando el
> usuario intenta guardar, entonces el sistema rechaza la operación mostrando "La fecha de la etapa
> no puede ser anterior al inicio del recorrido".

> **CA09.** Dado que el lote o la parte ya completó su ruta, cuando el usuario intenta registrar otra
> etapa, entonces el sistema rechaza la operación mostrando "No hay etapas pendientes para este
> lote".

> **CA10.** Dado que el usuario registra la molienda con horas de molino, cuando las horas no son
> mayores que cero, entonces el sistema rechaza la operación mostrando "Las horas de molienda deben
> ser mayores que cero"; si son válidas, muestra las toneladas por hora.

> **CA11.** Dado que el usuario registra el ensacado con una cantidad de bigbags, cuando guarda,
> entonces el sistema asocia los bigbags al lote o a la parte y estima el peso aproximado de cada
> uno a partir de las toneladas pendientes de ensacar.

> **CA12.** Dado que todo lo registrado ya está ensacado, cuando el usuario asocia más bigbags sin
> recalcular, entonces el sistema rechaza la operación mostrando "Lo registrado ya está ensacado:
> marque Recalcular e indique el peso de cada bigbag".

> **CA13.** Dado que el usuario intenta asociar bigbags a un lote o una parte que no registró su
> ensacado, cuando lo solicita, entonces el sistema lo rechaza mostrando "Los bigbags se asocian al
> registrar el ensacado".

> **CA14.** Dado que un ingreso tardío llegó después del secado del lote, cuando el usuario registra
> su secado propio, entonces el sistema lo registra aparte y sus porciones quedan a la espera de la
> ruta de las partes a las que se reparten.

> **CA15.** Dado que el lote está Cerrado, cuando el usuario intenta registrar una etapa o asociar
> bigbags, entonces el sistema rechaza la operación mostrando "El lote {codigo} ya fue cerrado".

> **CA16.** Dado que el paso se registra, cuando concluye la operación, entonces el sistema guarda el
> usuario responsable y registra el evento en auditoría.

---

## HU-M06-03 — Consulta de la trazabilidad de un ingreso

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M06-03 |
| **Épica** | Trazabilidad del proceso |
| **Prioridad** | Media |

**Historia**

Como administrativo, quiero ver por qué etapas pasó el mineral de un ingreso concreto, para
responder dónde está y qué le falta sin recorrer la planta preguntando.

**Descripción**

La consulta parte de un ingreso y llega a su recorrido a través del lote al que pertenece. Muestra
las etapas de la ruta del lote, cuáles se completaron, cuándo y quién las registró, y cuántas de las
etapas de su ruta se han recorrido. Si el lote se dividió, muestra cada parte con su ruta, y el total
de etapas es la unión de las etapas de esas rutas: una parte molida y otra zarandeada suman secado,
zarandeo, molienda y ensacado. Si el ingreso fue tardío y llegó después del secado, se muestra su
secado propio.

Mientras la ruta no se ha decidido, el sistema muestra las etapas recorridas e indica que la ruta
está por decidir: no calcula una proporción sobre una ruta que todavía no existe.

Un ingreso que todavía no se asignó a ningún lote no ha recorrido ninguna etapa, y así se muestra.
No es un error ni un dato faltante: es el estado normal de un ingreso recién registrado.

**Detalles**
- Se consulta desde el detalle del ingreso o por su código.
- Muestra el lote, su estado, su ruta o las de sus partes, y cada etapa con su fecha y responsable.
- Indica cuántas etapas de la ruta se completaron; en un lote dividido, sobre la unión de las rutas.
- Si el lote está Cerrado, muestra su destino y la fecha de cierre.
- Roles autorizados: los tres.

**Criterios de aceptación**

> **CA01.** Dado que un ingreso pertenece a un lote con ruta decidida, cuando el usuario consulta su
> trazabilidad, entonces el sistema muestra las etapas de esa ruta señalando cuáles se completaron,
> con su fecha y su responsable.

> **CA02.** Dado que un ingreso no está asignado a ningún lote, cuando el usuario consulta su
> trazabilidad, entonces el sistema indica que el ingreso aún no tiene lote y que no ha recorrido
> ninguna etapa.

> **CA03.** Dado que el lote del ingreso completó todas las etapas de su ruta, cuando el usuario
> consulta su trazabilidad, entonces el sistema lo indica como proceso completo.

> **CA04.** Dado que el usuario consulta la trazabilidad, cuando el sistema la presenta, entonces
> muestra cuántas etapas de la ruta del ingreso se han recorrido sobre el total de etapas de esa
> ruta.

> **CA05.** Dado que un ingreso fue anulado después de asignarse a un lote, cuando se consulta su
> trazabilidad, entonces el sistema la muestra señalando que el ingreso está anulado.

> **CA06.** Dado que el lote del ingreso se dividió en partes con rutas distintas, cuando se consulta
> su trazabilidad, entonces el sistema muestra cada parte con su ruta y calcula las etapas recorridas
> sobre la unión de las etapas de esas rutas.

> **CA07.** Dado que el lote registró el secado y todavía no tiene ruta, cuando se consulta la
> trazabilidad, entonces el sistema muestra el secado como recorrido e indica que la ruta está por
> decidir, sin calcular la proporción.

> **CA08.** Dado que el lote del ingreso está Cerrado, cuando se consulta su trazabilidad, entonces el
> sistema muestra también su destino y la fecha del cierre.

---

## HU-M06-04 — División de un lote por fracciones

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M06-04 |
| **Épica** | Trazabilidad del proceso |
| **Prioridad** | Alta |

**Historia**

Como administrativo, quiero dividir un lote en partes que siguen rutas distintas, para registrar que
una parte del mineral se muele y otra solo se zarandea sin perder la trazabilidad de la carga.

**Descripción**

El mineral acumulado en cancha no se pesa: se estima a la vista. Por eso el lote no se divide en
toneladas sino en **fracciones**: el usuario indica qué fracción del lote va a cada parte —por
ejemplo, 1/3 a molienda y 2/3 a zarandeo— y la ruta de cada una. Las fracciones suman la unidad. El
sistema calcula las toneladas aproximadas de cada parte como la fracción por el total de toneladas
netas del lote, solo para estimar el peso de sus bigbags.

Un lote se divide una sola vez, en dos partes o más y hasta seis, y solo mientras ninguna parte ha
avanzado por su ruta. Desde la división, cada parte registra sus etapas por separado.

Si después llega un ingreso tardío, el sistema propone repartirlo con las mismas fracciones del
lote; el usuario puede ajustarlas, siempre que sumen la unidad (DR-20).

**Detalles**
- Partes: de dos a seis, cada una con nombre distinto, fracción y ruta.
- Fracción: proporción del lote, mayor que cero; la suma de las fracciones es la unidad.
- Toneladas aproximadas por parte: fracción × toneladas netas del lote, señaladas como estimación.
- Momento: antes de que ninguna parte avance por su ruta; una sola vez por lote.
- Reparto de un ingreso tardío: con las fracciones del lote por defecto, editables.
- Roles autorizados: Administrativo y Administrador.

**Criterios de aceptación**

> **CA01.** Dado que el usuario indica el nombre, la fracción y la ruta de cada parte y las
> fracciones suman la unidad, cuando confirma la división, entonces el sistema la registra y muestra
> "Lote dividido en {n} partes".

> **CA02.** Dado que falta el nombre, la fracción o la ruta de alguna parte, cuando el usuario
> intenta confirmar, entonces el sistema rechaza la operación mostrando "Debe completar los campos
> obligatorios de cada parte".

> **CA03.** Dado que dos partes tienen el mismo nombre, cuando el usuario intenta confirmar,
> entonces el sistema rechaza la operación mostrando "Cada parte debe tener un nombre distinto".

> **CA04.** Dado que las fracciones no suman la unidad, cuando el usuario intenta confirmar,
> entonces el sistema rechaza la operación mostrando "Las fracciones de las partes deben sumar el
> total del lote".

> **CA05.** Dado que el usuario indica más de seis partes, cuando intenta confirmar, entonces el
> sistema rechaza la operación mostrando "Puede dividir el lote en seis partes como máximo".

> **CA06.** Dado que el lote ya fue dividido, cuando el usuario intenta dividirlo de nuevo, entonces
> el sistema rechaza la operación mostrando "El lote ya fue dividido".

> **CA07.** Dado que alguna parte del lote ya avanzó por su ruta, cuando el usuario intenta
> dividirlo, entonces el sistema rechaza la operación mostrando "No se puede dividir: el lote ya
> avanzó por su ruta".

> **CA08.** Dado que el lote se dividió, cuando el usuario consulta las partes, entonces el sistema
> muestra para cada una su fracción, su ruta y sus toneladas aproximadas, señaladas como estimación.

> **CA09.** Dado que llega un ingreso tardío a un lote dividido, cuando el usuario lo reparte,
> entonces el sistema propone las fracciones del lote, permite editarlas y rechaza el reparto si no
> suman la unidad, con el mensaje de CA04.

> **CA10.** Dado que el usuario tiene rol de Supervisor de planta, cuando intenta dividir un lote,
> entonces el sistema rechaza la operación mostrando "Acción no autorizada".

---

## HU-M06-05 — Cierre del lote con su destino

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M06-05 |
| **Épica** | Trazabilidad del proceso |
| **Prioridad** | Alta |

**Historia**

Como administrador, quiero cerrar definitivamente un lote cuando todo su mineral está ensacado,
registrando a dónde va, para dejar constancia del proceso completo de esa carga y de su destino.

**Descripción**

Un lote puede cerrarse cuando todo su mineral está ensacado: el secado registrado, la ruta decidida y
completa en el lote o en cada parte, y los ingresos tardíos con su propio recorrido terminado. Antes
de confirmar, el sistema presenta el **resumen del proceso**: toneladas netas registradas, bigbags y
su peso aproximado, la diferencia entre lo ensacado aproximado y lo registrado, las horas de
molienda y las toneladas por hora de cada parte, y la duración del proceso desde la apertura y desde
el inicio del recorrido hasta el último ensacado.

El Administrador registra el **destino** del lote: venta o traslado a otro punto, por ejemplo por ley
baja. El sistema no registra la venta ni el traslado en sí: no emite guía, factura ni precio (DR-14).
La diferencia entre lo ensacado y lo registrado es un dato descriptivo, no una medición de pérdidas
(DR-15).

Un lote Cerrado ya no admite ingresos, etapas ni bigbags. Permanece consultable con todo su
recorrido.

**Detalles**
- Condición: todo el mineral del lote ensacado.
- Destino: obligatorio; venta o traslado a otro punto.
- Observación: opcional.
- Fecha y usuario del cierre: los asigna el sistema.
- Resumen: toneladas registradas, bigbags, ensacado aproximado, diferencia, horas de molienda y
  toneladas por hora por parte, duración del proceso.
- Rol autorizado: Administrador.

**Criterios de aceptación**

> **CA01.** Dado que todo el mineral del lote está ensacado y el administrador indica el destino,
> cuando confirma el cierre, entonces el sistema cierra el lote, registra la fecha y el responsable,
> y muestra "Lote {nombre} cerrado con destino {destino}".

> **CA02.** Dado que el lote tiene etapas pendientes, cuando el administrador intenta cerrarlo,
> entonces el sistema rechaza la operación mostrando "Todavía no se puede cerrar el lote. Pendiente:
> {pendientes}", con la lista de lo que falta.

> **CA03.** Dado que el administrador no indica el destino, cuando intenta cerrar el lote, entonces
> el sistema rechaza la operación mostrando "Debe indicar el destino del lote".

> **CA04.** Dado que el lote ya está Cerrado, cuando se intenta cerrarlo de nuevo, entonces el
> sistema rechaza la operación mostrando "El lote ya fue cerrado".

> **CA05.** Dado que el usuario tiene rol de Administrativo o de Supervisor de planta, cuando intenta
> cerrar un lote, entonces el sistema rechaza la operación mostrando "Acción no autorizada".

> **CA06.** Dado que el administrador va a cerrar un lote, cuando el sistema presenta la
> confirmación, entonces muestra el resumen del proceso, con la diferencia entre lo ensacado y lo
> registrado señalada como estimación.

> **CA07.** Dado que el lote está Cerrado, cuando alguien intenta agregarle ingresos, registrar
> etapas o asociar bigbags, entonces el sistema rechaza la operación mostrando "El lote {codigo} ya
> fue cerrado".

> **CA08.** Dado que el cierre se persiste, cuando concluye la operación, entonces el sistema registra
> en auditoría el destino, el resumen y el usuario responsable.
