# Historias de usuario — M05 Existencias

**RF asociado:** RF-04 · **Indicadores de tesis:** I3, I4 · **Semana:** 5 · **Historias:** 3

> El indicador I3 mide el tiempo de determinación del stock por producto. Hoy ese cálculo es manual sobre papel y toma minutos; el módulo lo convierte en una consulta.

---

## HU-M05-01 — Consulta de existencias por producto

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M05-01 |
| **Épica** | Existencias |
| **Prioridad** | Crítica |

**Historia**

Como administrativo, quiero consultar el stock actual de cada producto, para saber cuánto hay disponible sin tener que sumar ingresos y restar salidas a mano.

**Descripción**

El stock se calcula a partir de los movimientos registrados, no se almacena como un campo editable. La consulta muestra el saldo vigente por producto y la fecha del último movimiento.

**Criterios de aceptación**

> **CA01.** Dado que el usuario accede a la pantalla de existencias, cuando esta carga, entonces el sistema muestra el saldo actual de cada producto vigente con su unidad de medida.

> **CA02.** Dado que un producto no tiene movimientos registrados, cuando aparece en la consulta, entonces el sistema muestra saldo cero y no lo omite de la lista.

> **CA03.** Dado que el usuario consulta el stock, cuando el sistema responde, entonces el valor mostrado coincide con la diferencia entre las entradas y las salidas no anuladas de ese producto.

> **CA04.** Dado que el usuario intenta editar directamente el valor del stock, cuando busca esa opción, entonces no existe: el stock es un valor calculado y no se modifica manualmente.

---

## HU-M05-02 — Kardex de movimientos por producto

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M05-02 |
| **Prioridad** | Alta |

**Historia**

Como administrativo, quiero ver el detalle cronológico de entradas y salidas de un producto con su saldo resultante, para poder explicar cómo se llegó al stock actual.

**Criterios de aceptación**

> **CA01.** Dado que el usuario selecciona un producto y un rango de fechas, cuando confirma, entonces el sistema muestra los movimientos ordenados cronológicamente con tipo, cantidad, origen y saldo resultante.

> **CA02.** Dado que un movimiento proviene de un ingreso, cuando aparece en el kardex, entonces el sistema muestra el correlativo del ingreso y permite abrir su detalle.

> **CA03.** Dado que un movimiento proviene de una salida, cuando aparece en el kardex, entonces el sistema muestra el correlativo de la salida y su tipo de movimiento.

> **CA04.** Dado que un ingreso o salida fue anulado, cuando se consulta el kardex, entonces el sistema muestra tanto el movimiento original como su reversión, sin ocultar ninguno.

---

## HU-M05-03 — Registro de ajuste de inventario

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M05-03 |
| **Prioridad** | Alta |

**Historia**

Como administrador, quiero registrar un ajuste cuando la medición física difiere del stock del sistema, para dejar constancia de la diferencia en lugar de corregirla en silencio.

**Descripción**

El ajuste no reemplaza el stock: genera un movimiento de tipo AJUSTE con la diferencia, motivo obligatorio y responsable identificado. La magnitud de estos ajustes es la evidencia directa del indicador I4.

**Criterios de aceptación**

> **CA01.** Dado que el administrador indica el producto, la cantidad medida físicamente y el motivo, cuando confirma, entonces el sistema calcula la diferencia respecto al saldo del sistema y genera un movimiento de tipo AJUSTE por esa diferencia.

> **CA02.** Dado que el administrador intenta registrar un ajuste sin motivo, cuando confirma, entonces el sistema rechaza la operación mostrando "Debe indicar el motivo del ajuste".

> **CA03.** Dado que la cantidad medida coincide exactamente con el saldo del sistema, cuando el administrador confirma, entonces el sistema informa "No hay diferencia que ajustar" y no genera movimiento.

> **CA04.** Dado que un usuario con rol distinto de Administrador intenta registrar un ajuste, cuando envía la solicitud, entonces el sistema la rechaza respondiendo "Acción no autorizada".

> **CA05.** Dado que se registra un ajuste, cuando concluye la operación, entonces el sistema registra en auditoría el saldo previo, la cantidad medida, la diferencia, el motivo y el responsable.
