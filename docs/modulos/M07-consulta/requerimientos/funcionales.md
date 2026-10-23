# Requerimientos funcionales — M07 Consulta de ingresos y respaldo

**RF asociado:** **RF08** — Consultar un ingreso por placa y fecha con su ticket de respaldo.

| Función | Descripción | HU | Endpoint |
|---|---|---|---|
| Buscar por placa y fecha | Búsqueda por placa total o parcial y fecha o rango | HU-M07-01 | `GET /api/v1/consulta/ingresos/` |
| Listar ingresos con filtros | Listado paginado con filtros combinables y totales del conjunto | HU-M07-02 | `GET /api/v1/consulta/ingresos/?filtros` |
| Consultar detalle completo | Datos, imagen o motivo de su ausencia, marcas de tiempo, validaciones, reconocimiento, trazabilidad e historial | HU-M07-01, HU-M07-02 | `GET /api/v1/consulta/ingresos/{id}/` |
| Obtener la imagen del ticket | Entrega el respaldo con control de acceso | HU-M07-01 | `GET /api/v1/consulta/ingresos/{id}/ticket/` |
| Consultar el calendario de un mes | Llegadas y toneladas por día, marcas y resumen del mes | HU-M07-03 | `GET /api/v1/consulta/calendario/?anio&mes` |
| Listar los ingresos de un día | Ingresos de una fecha del pesaje | HU-M07-03 | `GET /api/v1/consulta/ingresos/?fecha` |
| Exportar el listado | Archivo CSV con el conjunto filtrado completo | HU-M07-02 | `GET /api/v1/consulta/ingresos/exportar/?filtros` |
| Buscar desde la cabecera | Resuelve un código, completo o por sus dígitos finales; sin coincidencia, deriva a la búsqueda por placa | HU-M07-02 | `GET /api/v1/consulta/ingresos/?codigo` |
| Consultar el resumen del día | Cifras del día, últimos ingresos y toneladas de los últimos siete días | HU-M07-04 | `GET /api/v1/consulta/inicio/` |
| Consultar los avisos de pendientes | Pendientes calculados según el rol del usuario | HU-M07-04 | `GET /api/v1/consulta/avisos/` |

La búsqueda y el listado comparten endpoint: son la misma operación con distintos filtros.
Separarlos obligaría a mantener dos consultas sobre la misma entidad, con el riesgo de que
divergieran.

## Responsabilidad y límites

M07 **no tiene entidad propia**: lee sobre `INGRESO`, que pertenece a M03 (D-10).

**Lo que hace.** Responde por un ingreso concreto a partir de la placa y la fecha, entrega su
respaldo con control de acceso, muestra el recorrido de su mineral, compone el detalle completo
reuniendo lo que aportan los demás módulos, presenta el calendario de llegadas de un mes, exporta
el listado filtrado y compone la pantalla de inicio con el resumen del día y los avisos de pendientes
según el rol.

**Lo que delega.**

| Delega en | A través de | Qué obtiene |
|---|---|---|
| M03 Registro | Lectura de ingresos | Los datos del ingreso, su estado y la referencia de su imagen |
| M04 Reconocimiento | Lectura del reconocimiento | La comparación entre lo reconocido y lo confirmado |
| M05 Validación | Lectura de resultados | Las reglas evaluadas y su resolución |
| M06 Trazabilidad | Lectura del recorrido | El lote del ingreso y las etapas recorridas de su ruta |
| M09 Auditoría | Lectura del historial | Los eventos del ingreso y de su lote, en orden cronológico |

**Lo que no hace.** No escribe datos del dominio, no consolida por periodo y tipo de mineral —eso
es M08, y la exportación del listado no lo sustituye— y no interpreta lo que muestra: presenta lo que cada módulo aporta, sin recalcularlo. Si el detalle mostrara un total
calculado por su cuenta, podría contradecir al del módulo responsable.

## Permisos

| Función | Administrador | Administrativo | Supervisor de planta |
|---|:---:|:---:|:---:|
| Buscar y listar | Sí | Sí | Sí |
| Consultar detalle | Sí | Sí | Sí |
| Obtener la imagen del ticket | Sí | Sí | Sí |
| Consultar el calendario de llegadas | Sí | Sí | Sí |
| Buscar desde la cabecera | Sí | Sí | Sí |
| Consultar el resumen del día y los avisos | Sí | Sí | Sí, con los avisos de su rol |
| Exportar el listado | Sí | Sí | No |

Los tres roles consultan, porque la consulta no modifica nada y responder por un ingreso es parte
del trabajo de todos. El control de acceso a la imagen existe frente a peticiones sin sesión, no
para distinguir entre roles. La exportación saca los datos del sistema en un archivo y por eso queda
con el Administrativo y el Administrador, igual que la exportación del consolidado (M08). Los avisos
se filtran por rol: solo se avisa lo que el rol puede resolver.

## Dependencias

| Depende de | Para |
|---|---|
| M01 | Autenticación y control de acceso a la imagen |
| M02 | La placa y la titularidad del vehículo, usadas como criterios |
| M03 | Los ingresos y sus imágenes |
| M04 | La comparación entre lo reconocido y lo confirmado |
| M05 | El resultado de las validaciones |
| M06 | El lote y el recorrido del proceso, y los lotes con pasos pendientes para los avisos |
| M09 | El historial del ingreso y el registro del evento de exportación |

| Es requerido por | Para |
|---|---|
| — | Ningún módulo depende de M07: es un punto final de lectura |
