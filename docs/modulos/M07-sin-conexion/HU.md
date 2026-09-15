# Historias de usuario — M07 Captura sin conexión (PWA)

**RF asociado:** RF-10 · **Indicadores:** I1, I2 · **Semana:** 4 · **Historias:** 5

> Módulo diferenciador. Deriva de una restricción documentada: la conectividad en planta es intermitente. Si el registro exigiera conexión, la latencia (I1) no bajaría en las horas sin señal y la cobertura (I2) se degradaría justamente en los turnos con más ingresos.

---

## HU-M07-01 — Operación de la aplicación sin conexión

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M07-01 |
| **Épica** | Captura sin conexión |
| **Prioridad** | Alta |

**Historia**

Como supervisor de planta, quiero que la aplicación se abra y funcione aunque no haya señal, para poder registrar el volquete en el momento en que llega.

**Descripción**

La aplicación se instala como aplicación web progresiva. El service worker cachea la interfaz y los catálogos. Al perder conexión, la aplicación permanece operativa para el registro de ingresos.

**Criterios de aceptación**

> **CA01.** Dado que el usuario abre la aplicación sin conexión a internet, cuando la aplicación carga, entonces se muestra la interfaz completa y el formulario de registro de ingreso queda disponible.

> **CA02.** Dado que la aplicación está sin conexión, cuando el usuario abre el formulario de ingreso, entonces los selectores de producto y vehículo muestran los catálogos almacenados localmente.

> **CA03.** Dado que la aplicación pierde la conexión, cuando esto ocurre, entonces muestra un indicador visible del estado sin conexión, sin bloquear la operación.

> **CA04.** Dado que el catálogo local tiene más de siete días sin revalidarse, cuando el usuario abre el formulario sin conexión, entonces el sistema muestra una advertencia pero permite continuar con el registro.

> **CA05.** Dado que el usuario intenta acceder sin conexión a una función que requiere servidor —reportes, existencias, búsqueda—, cuando lo hace, entonces el sistema informa "Esta función requiere conexión" sin cerrar la aplicación.

---

## HU-M07-02 — Registro de un ingreso sin conexión

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M07-02 |
| **Épica** | Captura sin conexión |
| **Prioridad** | Alta |

**Historia**

Como supervisor, quiero registrar el ingreso sin conexión y que se guarde en el dispositivo, para no perder el dato ni tener que anotarlo en papel.

**Descripción**

El ingreso capturado sin conexión se almacena en IndexedDB con un identificador local (UUID) y la hora de captura local. Al recuperar conexión, se sincroniza con el servidor, que le asigna el correlativo definitivo.

**Criterios de aceptación**

> **CA01.** Dado que el usuario completa el formulario sin conexión, cuando confirma el registro, entonces el sistema lo almacena localmente y muestra "Ingreso guardado en el dispositivo. Se enviará al recuperar conexión".

> **CA02.** Dado que un ingreso está pendiente de sincronizar, cuando el usuario consulta la aplicación, entonces el sistema lo muestra en una lista de pendientes visualmente diferenciada de los ya sincronizados.

> **CA03.** Dado que el ingreso se captura sin conexión, cuando se almacena localmente, entonces el sistema registra la hora de captura del dispositivo, que será la hora de registro definitiva tras la sincronización.

> **CA04.** Dado que el ingreso capturado sin conexión se sincroniza, cuando el servidor lo procesa, entonces asigna como hora de registro la hora de captura local recibida, **no** la hora de sincronización, y almacena esta última por separado.

> **CA05.** Dado que el usuario intenta guardar sin conexión con campos inválidos, cuando confirma, entonces el sistema aplica las mismas validaciones que en línea y rechaza el registro con el mismo mensaje.

> **CA06.** Dado que el usuario cierra la aplicación con ingresos pendientes, cuando la vuelve a abrir, entonces los ingresos pendientes siguen almacenados y visibles.

---

## HU-M07-03 — Sincronización automática al recuperar conexión

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M07-03 |
| **Épica** | Captura sin conexión |
| **Prioridad** | Alta |

**Historia**

Como supervisor, quiero que los ingresos pendientes se envíen solos cuando vuelva la señal, para no tener que acordarme de hacerlo.

**Criterios de aceptación**

> **CA01.** Dado que existen ingresos pendientes y el dispositivo recupera conexión, cuando esto se detecta, entonces el sistema envía automáticamente los pendientes al servidor en el orden en que fueron capturados.

> **CA02.** Dado que la sincronización de un ingreso es exitosa, cuando el servidor confirma, entonces el sistema lo retira de la lista de pendientes y muestra el correlativo asignado.

> **CA03.** Dado que la sincronización está en curso, cuando el usuario consulta la aplicación, entonces el sistema muestra el progreso sin bloquear el uso.

> **CA04.** Dado que la conexión se interrumpe a mitad de la sincronización, cuando esto ocurre, entonces los ingresos ya confirmados no se reenvían y los pendientes permanecen en cola.

> **CA05.** Dado que el usuario prefiere sincronizar manualmente, cuando selecciona la acción correspondiente, entonces el sistema envía los pendientes de inmediato.

---

## HU-M07-04 — Manejo de conflictos y errores de sincronización

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M07-04 |
| **Épica** | Captura sin conexión |
| **Prioridad** | Alta |

**Historia**

Como supervisor, quiero saber si un ingreso no se pudo enviar y por qué, para poder corregirlo en lugar de perderlo.

**Criterios de aceptación**

> **CA01.** Dado que el servidor rechaza un ingreso por validación, cuando responde, entonces el sistema lo mantiene en la cola marcado como rechazado, con el motivo visible, y continúa con los siguientes.

> **CA02.** Dado que un ingreso fue rechazado, cuando el usuario lo abre, entonces puede corregirlo y reintentar el envío.

> **CA03.** Dado que el ticket de un ingreso pendiente ya fue registrado en línea por otro usuario, cuando se sincroniza, entonces el servidor lo rechaza indicando el correlativo existente y el sistema lo muestra como duplicado, sin descartarlo automáticamente.

> **CA04.** Dado que el token de sesión expiró durante la operación sin conexión, cuando se intenta sincronizar, entonces el sistema solicita reautenticación y **conserva** todos los ingresos pendientes.

> **CA05.** Dado que un ingreso lleva más de tres intentos fallidos de envío, cuando esto ocurre, entonces el sistema deja de reintentar automáticamente y solicita intervención del usuario.

---

## HU-M07-05 — Visibilidad del estado de sincronización

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M07-05 |
| **Épica** | Captura sin conexión |
| **Prioridad** | Media |

**Historia**

Como administrativo, quiero ver cuáles ingresos fueron capturados sin conexión y cuánto tardaron en sincronizarse, para entender el comportamiento del registro en planta.

**Criterios de aceptación**

> **CA01.** Dado que un ingreso fue capturado sin conexión, cuando se consulta su detalle, entonces el sistema lo indica de forma visible junto con su hora de captura y su hora de sincronización.

> **CA02.** Dado que el usuario consulta el listado de ingresos, cuando aplica el filtro de captura sin conexión, entonces el sistema muestra únicamente esos registros.

> **CA03.** Dado que existen ingresos pendientes de sincronizar en algún dispositivo, cuando el administrador consulta el panel correspondiente, entonces el sistema no puede informarlos: los pendientes residen en el dispositivo y no son visibles desde el servidor hasta que se sincronizan.
