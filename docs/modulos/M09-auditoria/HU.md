# Historias de usuario — M09 Auditoría

**RF asociado:** — (transversal) · **Historias:** 2

> Módulo que registra quién hizo qué y cuándo sobre cada entidad del sistema, incluidos el
> reconocimiento y la corrección de datos. No mejora ninguna función del negocio: sostiene que el
> histórico pueda demostrarse íntegro, condición de la que dependen todos los demás módulos.

---

## HU-M09-01 — Registro de eventos del sistema

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M09-01 |
| **Épica** | Auditoría |
| **Prioridad** | Alta |

**Historia**

Como administrador, quiero que cada operación relevante del sistema quede registrada con su autor y
su momento, para poder demostrar que el histórico no fue alterado sin dejar rastro.

**Descripción**

Cada vez que se crea, modifica o anula un registro, se reconoce un ticket, se corrige un dato
propuesto, se exporta un reporte o se rechaza un acceso por falta de autorización, el sistema
guarda un evento con el usuario responsable, la entidad afectada, el momento y, cuando corresponde,
los valores anteriores y los nuevos.

Este registro no lo activa el usuario: ocurre como parte de la misma operación que audita, dentro
de la misma transacción. Un evento no puede quedar registrado si la operación que describe no se
completó, ni una operación puede completarse sin que su evento quede registrado.

**Detalles**
- Acciones registradas: crear, modificar, anular, reconocer, corregir dato, exportar, iniciar
  sesión, cerrar sesión, acceso rechazado.
- Cada evento guarda: usuario, acción, entidad, identificador del registro afectado, fecha y hora.
- En modificaciones: valores anteriores y nuevos del campo cambiado.
- En creaciones: solo valores nuevos. En anulaciones: solo valores anteriores.
- El registro del evento es automático: ningún rol lo activa ni lo omite manualmente.

**Criterios de aceptación**

> **CA01.** Dado que se crea, modifica o anula un registro en cualquier módulo, cuando la operación
> se completa, entonces el sistema registra el evento correspondiente con el usuario y el momento.

> **CA02.** Dado que una modificación cambia el valor de un campo, cuando se registra el evento,
> entonces el sistema guarda el valor anterior y el nuevo de ese campo.

> **CA03.** Dado que una operación de escritura falla antes de completarse, cuando el sistema la
> interrumpe, entonces no queda registrado ningún evento para esa operación.

> **CA04.** Dado que un usuario intenta una operación para la que no tiene permiso, cuando el
> sistema la rechaza, entonces registra el evento de acceso rechazado con el usuario y la operación
> intentada.

> **CA05.** Dado que se reconoce un ticket o se corrige un dato propuesto, cuando la operación se
> completa, entonces el sistema registra el evento correspondiente.

> **CA06.** Dado que se genera una exportación, cuando concluye, entonces el sistema registra el
> evento con el periodo o el criterio exportado.

---

## HU-M09-02 — Consulta del historial de un registro

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M09-02 |
| **Épica** | Auditoría |
| **Prioridad** | Media |

**Historia**

Como administrador, quiero ver el historial completo de un registro concreto, para reconstruir qué
pasó con él y quién intervino en cada momento.

**Descripción**

La consulta parte de una entidad y un identificador —un ingreso, un lote, un usuario— y muestra sus
eventos en orden cronológico, con el autor de cada uno. Para las modificaciones, permite ver qué
campo cambió y cuáles fueron los dos valores.

**Detalles**
- Se consulta indicando la entidad y su identificador.
- Ordenado cronológicamente, del primero al más reciente.
- Cada evento muestra: acción, usuario, fecha y hora, y el detalle del cambio si aplica.
- Roles autorizados: Administrador.

**Criterios de aceptación**

> **CA01.** Dado que una entidad tiene eventos registrados, cuando el administrador consulta su
> historial, entonces el sistema los muestra en orden cronológico con su autor.

> **CA02.** Dado que un evento es una modificación, cuando se muestra en el historial, entonces el
> sistema presenta el valor anterior y el nuevo del campo afectado.

> **CA03.** Dado que una entidad no tiene eventos registrados, cuando se consulta su historial,
> entonces el sistema muestra "Sin eventos registrados para este registro".

> **CA04.** Dado que el usuario tiene rol de Administrativo o de Supervisor de planta, cuando
> intenta consultar un historial, entonces el sistema rechaza la operación mostrando "Acción no
> autorizada".
