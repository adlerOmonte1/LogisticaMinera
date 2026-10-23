# Historias de usuario — M09 Auditoría

**RF asociado:** — (transversal) · **Historias:** 3

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
- En las operaciones que exigen motivo —corrección de un ingreso y su reversión, anulación, cambio
  de la tara de un vehículo y unificación de un ingreso de otro tipo de mineral a un lote—: el motivo
  o la autorización escritos por el usuario.
- La desactivación y la reactivación de usuarios y de registros de catálogo se registran como
  modificaciones de su estado. El restablecimiento de una contraseña se registra como modificación
  del usuario, sin guardar ninguna contraseña.
- La exportación del listado de ingresos y la del consolidado mensual se registran como
  exportaciones, con el criterio y el número de registros exportados.
- El destare se registra como modificación del vehículo, que recibe su tara, y de cada ingreso que
  pasa de En proceso a Registrado.
- El registro sin foto se registra como creación del ingreso, con el motivo de la falta de imagen.
- Las operaciones sobre un lote —apertura, tipos de mineral agregados o quitados, asignación, retiro
  y traslado de ingresos, inicio del recorrido, división, paso por etapa, bigbags y cierre— se
  registran como eventos del lote, con los códigos de los ingresos afectados.
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

> **CA07.** Dado que una modificación exige motivo, cuando se registra el evento, entonces el sistema
> guarda el motivo junto con el valor anterior y el nuevo.

---

## HU-M09-02 — Historial de un ingreso

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M09-02 |
| **Épica** | Auditoría |
| **Prioridad** | Media |

**Historia**

Como supervisor de planta, quiero ver todo lo que le ocurrió a un ingreso —quién lo registró, quién
lo corrigió y por qué, a qué lote pasó y por qué etapas—, para responder por él sin depender de la
memoria de nadie.

**Descripción**

El historial se consulta desde el detalle del ingreso y lo ven los tres roles. Reúne, en orden
cronológico, los eventos del propio ingreso —reconocimiento, datos propuestos corregidos, registro,
destare, corrección, reversión de una corrección, anulación— y los eventos de su lote que lo afectan:
su asignación, su retiro o traslado, el inicio del recorrido, el paso por cada etapa y el cierre. Cada evento muestra la acción, el usuario, el momento
y el detalle del cambio, con el motivo cuando lo hubo.

El historial es de solo lectura y no permite filtrar ni salir del ingreso: para revisar la auditoría
del sistema completo existe una consulta aparte, reservada al Administrador (HU-M09-03).

**Detalles**
- Se consulta desde el detalle del ingreso.
- Incluye los eventos del ingreso y los de su lote que lo afectan.
- Ordenado cronológicamente, del primero al más reciente.
- Cada evento muestra: acción, usuario, fecha y hora, y el detalle del cambio con su motivo, si aplica.
- Roles autorizados: los tres.

**Criterios de aceptación**

> **CA01.** Dado que un ingreso tiene eventos registrados, cuando el usuario abre su historial,
> entonces el sistema los muestra en orden cronológico con su autor.

> **CA02.** Dado que un evento es una modificación, cuando se muestra en el historial, entonces el
> sistema presenta el valor anterior, el nuevo y el motivo, si lo hubo.

> **CA03.** Dado que el ingreso pertenece a un lote, cuando se muestra su historial, entonces el
> sistema incluye la asignación al lote, el inicio del recorrido, el paso por las etapas y el cierre
> del lote.

> **CA04.** Dado que el usuario es Supervisor de planta, cuando abre el historial de un ingreso,
> entonces el sistema se lo muestra igual que a los demás roles.

> **CA05.** Dado que el usuario no es Administrador, cuando consulta el historial de un ingreso,
> entonces el sistema no le ofrece el acceso a la auditoría completa.

---

## HU-M09-03 — Consulta de la auditoría del sistema

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M09-03 |
| **Épica** | Auditoría |
| **Prioridad** | Media |

**Historia**

Como administrador, quiero consultar todos los eventos del sistema filtrando por usuario, acción o
referencia, para reconstruir qué pasó con cualquier registro y detectar accesos no autorizados.

**Descripción**

La consulta abarca todos los eventos de todas las entidades —ingresos, lotes, vehículos, tipos de
mineral, usuarios— y los accesos rechazados. Se filtra por usuario, por acción y por un texto que se
busca en la referencia y en el detalle, por ejemplo el código de un ingreso o la placa de un
vehículo. Para las modificaciones muestra qué campo cambió y cuáles fueron los dos valores.

**Detalles**
- Filtros combinables: usuario, acción, y referencia o detalle.
- Abarca todas las entidades y los accesos rechazados.
- Ordenada cronológicamente, del más reciente al más antiguo.
- Cada evento muestra: acción, entidad y referencia, usuario, fecha y hora, y el detalle del cambio.
- Rol autorizado: Administrador.

**Criterios de aceptación**

> **CA01.** Dado que existen eventos, cuando el administrador abre la auditoría, entonces el sistema
> los muestra del más reciente al más antiguo, con su entidad, su referencia y su autor.

> **CA02.** Dado que el administrador combina filtros de usuario, acción y referencia, cuando los
> aplica, entonces el sistema muestra solo los eventos que cumplen todos ellos.

> **CA03.** Dado que un evento es una modificación, cuando se muestra, entonces el sistema presenta el
> valor anterior y el nuevo del campo afectado, y el motivo si lo hubo.

> **CA04.** Dado que ningún evento cumple los filtros, cuando se aplican, entonces el sistema muestra
> "No hay eventos con estos filtros".

> **CA05.** Dado que el usuario tiene rol de Administrativo o de Supervisor de planta, cuando intenta
> consultar la auditoría, entonces el sistema rechaza la operación mostrando "Acción no autorizada".
