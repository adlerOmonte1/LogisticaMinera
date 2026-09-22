# Requerimientos funcionales — M04 Reconocimiento automático del ticket

**RF asociado:** **RF02** — Reconocer automáticamente los datos del ticket: placa, fecha, hora, peso
bruto, tara y peso neto.

| Función | Descripción | HU | Endpoint |
|---|---|---|---|
| Reconocer ticket | Procesa la imagen y devuelve los seis campos con su confianza | HU-M04-01 | (interno, invocado por M03) |
| Persistir reconocimiento | Guarda el resultado con los valores confirmados al cerrarse el ingreso | HU-M04-01 | (interno, desde la transacción de M03) |
| Consultar reconocimiento | Comparación campo a campo entre lo reconocido y lo confirmado | HU-M04-02 | `GET /api/v1/reconocimientos/{id}/` |
| Listar reconocimientos | Consulta con filtros por fecha, motor y campos corregidos | HU-M04-02 | `GET /api/v1/reconocimientos/` |

El reconocimiento no se expone como endpoint público propio: se invoca desde el flujo de registro de
M03, que es quien gobierna la imagen y las marcas de tiempo. Exponerlo por separado permitiría
procesar imágenes sin ingreso asociado, lo que dejaría reconocimientos huérfanos.

## Responsabilidad y límites

M04 es el dueño de las entidades `RECONOCIMIENTO_TICKET` y `CAMPO_RECONOCIDO`.

**Lo que hace.** Convierte una imagen en seis valores con su nivel de confianza, marca los que
quedan por debajo del umbral, registra qué motor y qué versión produjeron el resultado, y conserva
la comparación entre lo leído y lo confirmado.

**Lo que delega.**

| Delega en | A través de | Qué obtiene |
|---|---|---|
| Motor de reconocimiento | `ReconocedorTicket` | La lectura de los seis campos con su confianza |
| M03 Registro | Invocación desde el servicio de registro | La imagen, y la confirmación del usuario |

**Lo que no hace.** No decide si los datos son coherentes —eso es M05—, no conserva la imagen —lo
hace M03—, no persiste el ingreso ni asigna su código, y no corrige valores por su cuenta: solo
propone.

**La interfaz.** `ReconocedorTicket` recibe una imagen y devuelve, por cada uno de los seis campos,
un valor y una confianza, más el identificador del motor y su versión. Cualquier motor que cumpla
ese contrato es sustituible sin modificar M03 ni M05. El motor concreto lo fija D-12, pendiente de
un piloto con tickets reales.

## Permisos

| Función | Administrador | Administrativo | Supervisor de planta |
|---|:---:|:---:|:---:|
| Reconocer ticket (dentro del registro) | Sí | Sí | Sí |
| Consultar y listar reconocimientos | Sí | Sí | No |

La consulta comparativa queda fuera del alcance del Supervisor de planta porque su trabajo es
registrar, no evaluar el desempeño de la lectura automática.

## Dependencias

| Depende de | Para |
|---|---|
| M01 | Autenticación y atribución de la consulta |
| M03 | La imagen del ticket y el momento en que se invoca el reconocimiento |

| Es requerido por | Para |
|---|---|
| M03 | Proponer los seis campos del ticket al iniciar el registro |
