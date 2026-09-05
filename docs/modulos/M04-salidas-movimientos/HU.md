# Historias de usuario — M04 Salidas y movimientos

**RF asociado:** RF-05 · **Indicador de tesis:** I4 · **Semana:** 5 · **Historias:** 3

> Este módulo sostiene el indicador I4 (desviación entre stock declarado y stock estimado). Sin registro de salidas, el stock calculado sería puramente acumulativo y la desviación carecería de sentido.

---

## HU-M04-01 — Registro de salida por venta

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M04-01 |
| **Épica** | Salidas y movimientos |
| **Prioridad** | Crítica |

**Historia**

Como administrativo, quiero registrar la salida de producto hacia un cliente, para que el stock refleje lo que realmente queda en planta.

**Descripción**

La salida registra fecha, producto, cliente, cantidad en toneladas y tipo de movimiento. Genera un movimiento de stock de tipo SALIDA. El sistema no gestiona precios ni facturación: eso está fuera de alcance.

**Criterios de aceptación**

> **CA01.** Dado que el usuario completa fecha, producto, cliente y cantidad, cuando confirma, entonces el sistema registra la salida, le asigna correlativo y genera el movimiento de stock correspondiente.

> **CA02.** Dado que la cantidad indicada supera el stock disponible del producto, cuando el usuario intenta guardar, entonces el sistema muestra la advertencia "La cantidad supera el stock disponible ({stock} tn). ¿Desea continuar?" y permite confirmar o cancelar.

> **CA03.** Dado que la cantidad es cero o negativa, cuando el usuario intenta guardar, entonces el sistema rechaza la operación mostrando "La cantidad debe ser mayor que cero".

> **CA04.** Dado que el tipo de movimiento es VENTA, cuando el usuario intenta guardar sin seleccionar cliente, entonces el sistema rechaza la operación mostrando "Debe indicar el cliente para una salida por venta".

> **CA05.** Dado que la salida se persiste, cuando concluye la operación, entonces el sistema registra el evento en auditoría con el usuario responsable.

---

## HU-M04-02 — Registro de traslado interno y merma

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M04-02 |
| **Prioridad** | Alta |

**Historia**

Como administrativo, quiero registrar los movimientos que no son venta —traslados internos y mermas—, para que la diferencia entre lo que entró y lo que queda tenga explicación.

**Descripción**

Los tipos de movimiento son VENTA, TRASLADO_INTERNO y MERMA. Solo VENTA exige cliente. MERMA exige motivo.

**Criterios de aceptación**

> **CA01.** Dado que el usuario selecciona tipo TRASLADO_INTERNO, cuando guarda, entonces el sistema acepta el registro sin exigir cliente.

> **CA02.** Dado que el usuario selecciona tipo MERMA, cuando intenta guardar sin indicar el motivo, entonces el sistema rechaza la operación mostrando "Debe indicar el motivo de la merma".

> **CA03.** Dado que se registra un movimiento de cualquier tipo, cuando se persiste, entonces el sistema genera el movimiento de stock correspondiente con el tipo de origen identificado.

> **CA04.** Dado que el usuario consulta el listado de salidas, cuando aplica el filtro por tipo de movimiento, entonces el sistema muestra únicamente los registros de ese tipo.

---

## HU-M04-03 — Consulta y anulación de salidas

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M04-03 |
| **Prioridad** | Media |

**Historia**

Como administrativo, quiero consultar las salidas registradas y anular las que se registraron por error, para mantener el stock consistente sin borrar información.

**Criterios de aceptación**

> **CA01.** Dado que el usuario accede al listado, cuando la pantalla carga, entonces el sistema muestra las salidas del mes en curso con filtros por fecha, producto, cliente y tipo.

> **CA02.** Dado que el usuario solicita anular una salida e indica el motivo, cuando confirma, entonces el sistema cambia el estado a ANULADO y revierte el movimiento de stock asociado.

> **CA03.** Dado que el usuario intenta anular sin motivo, cuando confirma, entonces el sistema rechaza la operación mostrando "Debe indicar el motivo de la anulación".

> **CA04.** Dado que el usuario intenta eliminar físicamente una salida, cuando envía la solicitud, entonces el sistema la rechaza: la eliminación física no está disponible.
