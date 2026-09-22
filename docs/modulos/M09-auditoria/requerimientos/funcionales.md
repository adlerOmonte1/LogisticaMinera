# Requerimientos funcionales — M09 Auditoría

**RF asociado:** — (transversal; no corresponde a ningún RF de la lista de control, no suma ni
resta en el avance).

| Función | Descripción | HU | Endpoint |
|---|---|---|---|
| Registrar evento | Persiste un evento dentro de la transacción de la operación que audita | HU-M09-01 | (interno, invocado por todos los módulos de escritura) |
| Consultar historial de una entidad | Eventos de un registro concreto, ordenados cronológicamente | HU-M09-02 | `GET /api/v1/auditoria/{entidad}/{id}/` |

El registro de eventos no se expone como operación que el usuario active: es un efecto de cada
operación de escritura del sistema, invocado internamente por el módulo que la realiza.

## Responsabilidad y límites

M09 es el dueño de la entidad `EVENTO_AUDITORIA` y del catálogo de acciones auditables.

**Lo que hace.** Ofrece un servicio de registro que cualquier módulo invoca al completar una
operación de escritura, y una consulta que reconstruye el historial de una entidad a partir de esos
eventos.

**Lo que recibe.**

| Recibe de | A través de | Qué recibe |
|---|---|---|
| Todos los módulos de escritura (M01 a M06, M08) | Invocación del servicio de registro | Usuario, acción, entidad, identificador, valores anteriores y nuevos |

**Lo que no hace.** No decide si una operación se completa —eso lo decide el módulo que la ejecuta,
antes de invocar a M09— y no interpreta el contenido de los valores que registra: los guarda tal
como se los entregan. Auditar no es validar: un evento de modificación registra el cambio incluso si
el nuevo valor es, según otra regla del sistema, el correcto.

**El servicio de registro.** Es la única puerta de escritura hacia `EVENTO_AUDITORIA`. Ningún módulo
inserta directamente en esa tabla: todos pasan por `ServicioAuditoria.registrar(...)`, que es lo que
permite mantener el catálogo de acciones en un solo lugar (RN-M09-05).

## Permisos

| Función | Administrador | Administrativo | Supervisor de planta |
|---|:---:|:---:|:---:|
| Registrar evento (automático, dentro de otra operación) | — | — | — |
| Consultar historial de una entidad | Sí | No | No |

El registro de eventos no tiene permiso propio: ocurre como parte de una operación ya autorizada por
su propio módulo. La consulta del historial queda reservada al Administrador, porque expone
información de todos los usuarios y todas las entidades.

## Dependencias

| Depende de | Para |
|---|---|
| M01 | Autenticación y atribución del usuario que consulta el historial |

| Es requerido por | Para |
|---|---|
| M01 | Registrar inicio de sesión, cierre de sesión y acceso rechazado |
| M02 | Registrar altas, ediciones y bajas del catálogo |
| M03 | Registrar creación, corrección y anulación de ingresos |
| M04 | Registrar el reconocimiento y la corrección de datos propuestos |
| M05 | Registrar el resultado de la validación de un ingreso |
| M06 | Registrar la apertura, el cierre y el paso de un lote por etapa |
| M08 | Registrar cada exportación |
