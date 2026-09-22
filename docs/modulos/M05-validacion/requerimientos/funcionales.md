# Requerimientos funcionales — M05 Validación automática de consistencia

**RF asociado:** **RF03** — Validar automáticamente la consistencia de los datos del ticket: pesos,
formato de placa, capacidad del vehículo y fecha.

| Función | Descripción | HU | Endpoint |
|---|---|---|---|
| Validar datos propuestos | Aplica V1 a V5 sobre el resultado del reconocimiento y devuelve las inconsistencias | HU-M05-01 | (interno, desde M03) |
| Validar al confirmar | Repite V1 a V5 sobre los datos confirmados antes de persistir | HU-M05-01 | (interno, desde M03) |
| Registrar resultado | Persiste el resultado por regla, con su momento y su resolución | HU-M05-01 | (interno, en la transacción de M03) |
| Consultar validaciones de un ingreso | Devuelve qué reglas se evaluaron y cómo se resolvieron | HU-M05-01 | `GET /api/v1/ingresos/{id}/validaciones/` |

La validación no se expone como endpoint de escritura propio. Validar sin registrar no es una
operación del negocio: el resultado solo tiene sentido dentro del registro de un ingreso concreto.

## Responsabilidad y límites

M05 es el dueño de la entidad `RESULTADO_VALIDACION` y de las reglas V1 a V5.

**Lo que hace.** Decide si un conjunto de datos es coherente, devuelve la lista de inconsistencias
con su mensaje literal y su carácter —bloqueante o exigente de justificación—, y conserva el
resultado de cada evaluación.

**Lo que delega.**

| Delega en | A través de | Qué obtiene |
|---|---|---|
| M02 Catálogo | Lectura del catálogo | La capacidad declarada del vehículo, que necesita V4 |
| M03 Registro | Invocación desde el servicio de registro | Los datos a evaluar y el momento de la evaluación |

**Lo que no hace.** No lee la imagen ni sabe de dónde vienen los datos —pueden provenir del
reconocimiento o del teclado—, no persiste el ingreso, no decide si la operación continúa: devuelve
el resultado y M03 decide. Tampoco reclama campos vacíos, que es trabajo del registro.

**La interfaz.** `ValidadorConsistencia` recibe los datos del ticket y el vehículo asociado, y
devuelve una lista de inconsistencias. M03 depende de ese contrato y no de las reglas concretas:
añadir una regla no modifica M03.

## Permisos

| Función | Administrador | Administrativo | Supervisor de planta |
|---|:---:|:---:|:---:|
| Validar (dentro del registro o la corrección) | Sí | Sí | Sí |
| Justificar una advertencia de V4 | Sí | Sí | Sí |
| Consultar las validaciones de un ingreso | Sí | Sí | No |

La validación no es una operación que el usuario invoque por su cuenta: ocurre dentro del registro,
con los permisos de este. La consulta del resultado sí es una operación propia y queda fuera del
alcance del Supervisor de planta.

## Dependencias

| Depende de | Para |
|---|---|
| M01 | Autenticación y atribución de la consulta |
| M02 | La capacidad declarada del vehículo, que necesita V4 |
| M03 | Los datos a evaluar y la transacción en que se persiste el resultado |

| Es requerido por | Para |
|---|---|
| M03 | Evaluar los datos propuestos y los confirmados antes de persistir el ingreso |
