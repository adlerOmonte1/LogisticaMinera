# Historias de usuario — M06 Trazabilidad del proceso

**RF asociado:** RF07 · **Historias:** 3

> Módulo que sigue el mineral desde que ingresa a planta hasta que sale ensacado. Como el mineral de
> varios volquetes se mezcla en cancha, el ingreso no recorre las etapas por sí solo: se asigna a un
> lote de proceso, y es el lote el que registra su paso por secado, zarandeo, molienda y ensacado.
> Esa indirección es la responsabilidad del módulo.

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

Un lote reúne los ingresos de un mismo tipo de mineral que se procesarán como una sola carga. Se
abre con una fecha, recibe ingresos mientras está abierto y se cierra cuando la carga queda
completa; a partir de ese momento no admite más ingresos y puede empezar a recorrer las etapas.

Un ingreso pertenece a un lote como máximo. Puede reasignarse a otro mientras ambos lotes sigan
abiertos, porque hasta entonces la agrupación es una decisión revisable; una vez que el lote se
cierra, la composición queda fija.

La gestión del lote es una sola capacidad: abrirlo, consultarlo, asignarle o quitarle ingresos y
cerrarlo son operaciones del mismo trabajo.

**Detalles**
- Código del lote: asignado por el servidor, único.
- Tipo de mineral: obligatorio, del catálogo; todos los ingresos del lote comparten el mismo.
- Fecha de apertura: obligatoria. Fecha de cierre: se asigna al cerrar.
- Estado: abierto o cerrado.
- Solo se asignan ingresos no anulados.
- Roles autorizados: Administrativo y Administrador.

**Criterios de aceptación**

> **CA01.** Dado que el usuario indica el tipo de mineral y la fecha de apertura, cuando crea el
> lote, entonces el sistema lo registra, le asigna un código y muestra "Lote {codigo} abierto".

> **CA02.** Dado que un lote está abierto, cuando el usuario le asigna ingresos del mismo tipo de
> mineral, entonces el sistema los incorpora y muestra el total de ingresos y de toneladas del lote.

> **CA03.** Dado que un ingreso es de un tipo de mineral distinto al del lote, cuando el usuario
> intenta asignarlo, entonces el sistema rechaza la operación mostrando "El ingreso {codigo}
> corresponde a otro tipo de mineral".

> **CA04.** Dado que un ingreso ya pertenece a otro lote abierto, cuando el usuario lo asigna a
> este, entonces el sistema lo traslada y deja constancia del cambio.

> **CA05.** Dado que un ingreso pertenece a un lote cerrado, cuando el usuario intenta reasignarlo,
> entonces el sistema rechaza la operación mostrando "El lote {codigo} ya fue cerrado".

> **CA06.** Dado que un ingreso está anulado, cuando el usuario intenta asignarlo a un lote,
> entonces el sistema rechaza la operación mostrando "No se puede asignar un ingreso anulado".

> **CA07.** Dado que un lote tiene al menos un ingreso, cuando el usuario lo cierra, entonces el
> sistema registra la fecha de cierre y muestra "Lote {codigo} cerrado".

> **CA08.** Dado que un lote no tiene ingresos, cuando el usuario intenta cerrarlo, entonces el
> sistema rechaza la operación mostrando "El lote no tiene ingresos asignados".

> **CA09.** Dado que el usuario tiene rol de Supervisor de planta, cuando intenta abrir, cerrar o
> modificar un lote, entonces el sistema rechaza la operación mostrando "Acción no autorizada".

> **CA10.** Dado que el usuario consulta un lote, cuando el sistema lo muestra, entonces presenta su
> composición: los ingresos asignados con su código, su fecha y su peso neto.

---

## HU-M06-02 — Registro del paso de un lote por una etapa

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M06-02 |
| **Épica** | Trazabilidad del proceso |
| **Prioridad** | Crítica |

**Historia**

Como supervisor de planta, quiero registrar que un lote pasó por una etapa del proceso, para que
quede constancia de dónde está el mineral y qué le falta.

**Descripción**

El proceso tiene cuatro etapas fijas: secado, zarandeo, molienda y ensacado. El supervisor registra
el paso del lote por cada una indicando el momento, y el sistema guarda quién lo registró.

Las etapas se registran en el orden del proceso: no puede anotarse la molienda de un lote que aún no
pasó por el zarandeo. Cada etapa se registra una sola vez por lote; si se anotó por error, se
corrige el registro existente en lugar de añadir otro.

Solo un lote cerrado recorre etapas. Mientras está abierto sigue recibiendo ingresos, y registrar su
paso por el secado cuando todavía puede incorporar mineral sin secar describiría algo que no ocurrió.

**Detalles**
- Etapas: secado, zarandeo, molienda, ensacado, en ese orden.
- Fecha y hora del paso: obligatorias, no posteriores al momento del registro.
- Usuario que registra: lo asigna el sistema.
- Observación: opcional.
- Una etapa se registra una sola vez por lote.
- Roles autorizados: los tres; el Supervisor de planta registra, no corrige lotes.

**Criterios de aceptación**

> **CA01.** Dado que un lote está cerrado y le corresponde la siguiente etapa, cuando el usuario
> registra su paso indicando el momento, entonces el sistema lo registra y muestra "Etapa {etapa}
> registrada para el lote {codigo}".

> **CA02.** Dado que el lote no ha pasado por la etapa anterior, cuando el usuario intenta registrar
> una etapa, entonces el sistema rechaza la operación mostrando "El lote debe pasar primero por la
> etapa {etapa anterior}".

> **CA03.** Dado que la etapa ya fue registrada para ese lote, cuando el usuario intenta registrarla
> de nuevo, entonces el sistema rechaza la operación mostrando "La etapa {etapa} ya fue registrada
> para el lote {codigo}".

> **CA04.** Dado que el lote está abierto, cuando el usuario intenta registrar una etapa, entonces
> el sistema rechaza la operación mostrando "El lote debe cerrarse antes de registrar etapas".

> **CA05.** Dado que la fecha indicada es posterior al momento del registro, cuando el usuario
> intenta guardar, entonces el sistema rechaza la operación mostrando "La fecha de la etapa no puede
> ser posterior a la fecha actual".

> **CA06.** Dado que la fecha indicada es anterior a la del paso por la etapa previa, cuando el
> usuario intenta guardar, entonces el sistema rechaza la operación mostrando "La fecha de la etapa
> no puede ser anterior a la de la etapa {etapa anterior}".

> **CA07.** Dado que el paso se registra, cuando concluye la operación, entonces el sistema guarda
> el usuario responsable y registra el evento en auditoría.

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
las cuatro etapas, cuáles se completaron, cuándo y quién las registró, y cuántas de las cuatro se
han recorrido.

Un ingreso que todavía no se asignó a ningún lote no ha recorrido ninguna etapa, y así se muestra.
No es un error ni un dato faltante: es el estado normal de un ingreso recién registrado.

**Detalles**
- Se consulta desde el detalle del ingreso o por su código.
- Muestra el lote, su estado, y las cuatro etapas con su fecha y responsable.
- Indica cuántas etapas de las cuatro se completaron.
- Roles autorizados: los tres.

**Criterios de aceptación**

> **CA01.** Dado que un ingreso pertenece a un lote, cuando el usuario consulta su trazabilidad,
> entonces el sistema muestra las cuatro etapas señalando cuáles se completaron, con su fecha y su
> responsable.

> **CA02.** Dado que un ingreso no está asignado a ningún lote, cuando el usuario consulta su
> trazabilidad, entonces el sistema muestra las cuatro etapas como no recorridas e indica que el
> ingreso aún no tiene lote.

> **CA03.** Dado que un ingreso pertenece a un lote que completó las cuatro etapas, cuando el
> usuario consulta su trazabilidad, entonces el sistema lo indica como proceso completo.

> **CA04.** Dado que el usuario consulta la trazabilidad, cuando el sistema la presenta, entonces
> muestra cuántas de las cuatro etapas se han recorrido.

> **CA05.** Dado que un ingreso fue anulado después de asignarse a un lote, cuando se consulta su
> trazabilidad, entonces el sistema la muestra señalando que el ingreso está anulado.
