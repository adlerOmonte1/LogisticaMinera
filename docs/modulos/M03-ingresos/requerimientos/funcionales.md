# Requerimientos funcionales — M03 Registro de ingresos

**RF asociados:** **RF01** — Registrar el ingreso de mineral con la imagen del ticket de balanza ·
**RF04** — Permitir el registro y la corrección manual de los datos reconocidos · **RF05** — Asignar
un código único a cada ingreso · **RF06** — Registrar el tipo de mineral y el tipo de vehículo.

| Función | Descripción | HU | Endpoint |
|---|---|---|---|
| Iniciar registro | Recibe la imagen, la conserva, asigna la hora de inicio y devuelve la propuesta de datos con sus inconsistencias | HU-M03-01 | `POST /api/v1/ingresos/borradores/` |
| Registrar ingreso | Revalida, calcula el peso neto y persiste los datos confirmados, con código y hora de fin; En proceso si el vehículo no tiene tara | HU-M03-01 | `POST /api/v1/ingresos/` |
| Alta rápida de vehículo | Da de alta un vehículo nuevo desde la pantalla de registro, sin salir de ella | HU-M03-01 | `POST /api/v1/catalogo/vehiculos/` (servicio de M02) |
| Listar ingresos | Consulta paginada con filtros por fecha, vehículo, tipo de mineral y estado | HU-M03-01 | `GET /api/v1/ingresos/` |
| Consultar un ingreso | Detalle con la imagen del ticket y las tres marcas de tiempo | HU-M03-01 | `GET /api/v1/ingresos/{id}/` |
| Corregir ingreso | Modifica los campos corregibles, con motivo y revalidación | HU-M03-02 | `PATCH /api/v1/ingresos/{id}/` |
| Anular ingreso | Baja lógica con motivo y responsable | HU-M03-03 | `PATCH /api/v1/ingresos/{id}/anular/` |
| Listar ingresos pendientes de destare | Ingresos En proceso con su placa, fecha y peso bruto | HU-M03-04 | `GET /api/v1/ingresos/?estado=EN_PROCESO` |
| Registrar destare | Recibe la tara digitada, la guarda en el vehículo y completa sus ingresos En proceso | HU-M03-04 | `POST /api/v1/ingresos/{id}/destare/` |

El listado y el detalle que expone M03 son los de su propio recurso. La consulta por placa y fecha
con presentación del respaldo es responsabilidad de M07, que lee sobre esta misma entidad.

## Responsabilidad y límites

M03 es el dueño de la entidad `INGRESO`: es el único módulo que la escribe.

**Lo que hace.** Conserva la imagen, gobierna las tres marcas de tiempo, recoge la confirmación del
usuario, asigna el código único, deriva el tipo de vehículo y la tara del catálogo, calcula el peso
neto, gestiona el estado En proceso hasta el destare y persiste el ingreso con sus valores
reconocidos y confirmados.

**Lo que delega.**

| Delega en | A través de | Qué obtiene |
|---|---|---|
| M04 Reconocimiento | `ReconocedorTicket` | La placa, la fecha y el peso bruto del ticket, con su nivel de confianza |
| M05 Validación | `ValidadorConsistencia` | La lista de inconsistencias de las reglas V1 a V5 |
| M02 Catálogo | Servicio del catálogo | El vehículo vigente con su titularidad, capacidad y tara; el tipo de mineral; el alta rápida de un vehículo nuevo y el registro de su tara en el destare |
| M09 Auditoría | Servicio de eventos | El registro de la creación, la corrección, la anulación y el destare |

M03 no sabe qué motor lee la imagen ni cómo se evalúa cada regla: recibe resultados y decide con
ellos. Añadir una regla de validación o cambiar de motor no modifica este módulo.

**Lo que no hace.** No escribe directamente sobre la tabla de vehículos: el alta rápida y la tara
del destare pasan por el servicio de M02, que es el dueño de esa entidad. Tampoco busca por placa y
fecha —eso es M07—, no agrega por periodo —eso es M08— y no gestiona lotes de proceso —eso es M06,
que referencia al ingreso desde su propio lado.

## Permisos

| Función | Administrador | Administrativo | Supervisor de planta |
|---|:---:|:---:|:---:|
| Iniciar registro | Sí | Sí | Sí |
| Registrar ingreso | Sí | Sí | Sí |
| Listar y consultar | Sí | Sí | Sí |
| Corregir ingreso | Sí | Sí | No |
| Anular ingreso | Sí | No | No |
| Alta rápida de vehículo desde el registro | Sí | Sí | Sí |
| Registrar destare | Sí | Sí | Sí |

Las restricciones se aplican en el servidor. Ocultar un botón en la interfaz no es un control de
acceso: toda operación rechazada por rol devuelve "Acción no autorizada" y queda registrada en
auditoría.

## Dependencias

| Depende de | Para |
|---|---|
| M01 | Autenticación y atribución de cada operación a un usuario |
| M02 | Vehículo vigente con su titularidad, capacidad y tara; alta rápida de vehículos; catálogo de tipos de mineral |
| M04 | Propuesta de la placa, la fecha y el peso bruto del ticket |
| M05 | Evaluación de las reglas V1 a V5 |
| M09 | Registro de los eventos de creación, corrección, anulación y destare |

| Es requerido por | Para |
|---|---|
| M06 | Asignar ingresos Registrados a un lote de proceso |
| M07 | Consultar un ingreso por placa y fecha con su respaldo |
| M08 | Calcular el total acumulado mensual por tipo de mineral |
