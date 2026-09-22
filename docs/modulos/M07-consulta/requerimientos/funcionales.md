# Requerimientos funcionales — M07 Consulta de ingresos y respaldo

**RF asociado:** **RF08** — Consultar un ingreso por placa y fecha con su ticket de respaldo.

| Función | Descripción | HU | Endpoint |
|---|---|---|---|
| Buscar por placa y fecha | Búsqueda por placa total o parcial y fecha o rango | HU-M07-01 | `GET /api/v1/consulta/ingresos/` |
| Listar ingresos con filtros | Listado paginado con filtros combinables y totales del conjunto | HU-M07-02 | `GET /api/v1/consulta/ingresos/?filtros` |
| Consultar detalle completo | Datos, imagen, marcas de tiempo, validaciones, reconocimiento y trazabilidad | HU-M07-01, HU-M07-02 | `GET /api/v1/consulta/ingresos/{id}/` |
| Obtener la imagen del ticket | Entrega el respaldo con control de acceso | HU-M07-01 | `GET /api/v1/consulta/ingresos/{id}/ticket/` |

La búsqueda y el listado comparten endpoint: son la misma operación con distintos filtros.
Separarlos obligaría a mantener dos consultas sobre la misma entidad, con el riesgo de que
divergieran.

## Responsabilidad y límites

M07 **no tiene entidad propia**: lee sobre `INGRESO`, que pertenece a M03 (D-10).

**Lo que hace.** Responde por un ingreso concreto a partir de la placa y la fecha, entrega su
respaldo con control de acceso, y compone el detalle completo reuniendo lo que aportan los demás
módulos.

**Lo que delega.**

| Delega en | A través de | Qué obtiene |
|---|---|---|
| M03 Registro | Lectura de ingresos | Los datos del ingreso, su estado y la referencia de su imagen |
| M04 Reconocimiento | Lectura del reconocimiento | La comparación entre lo reconocido y lo confirmado |
| M05 Validación | Lectura de resultados | Las reglas evaluadas y su resolución |
| M06 Trazabilidad | Lectura del recorrido | Las etapas recorridas por el lote del ingreso |

**Lo que no hace.** No escribe ningún dato, no agrega por periodo —eso es M08— y no interpreta lo
que muestra: presenta lo que cada módulo aporta, sin recalcularlo. Si el detalle mostrara un total
calculado por su cuenta, podría contradecir al del módulo responsable.

## Permisos

| Función | Administrador | Administrativo | Supervisor de planta |
|---|:---:|:---:|:---:|
| Buscar y listar | Sí | Sí | Sí |
| Consultar detalle | Sí | Sí | Sí |
| Obtener la imagen del ticket | Sí | Sí | Sí |

Los tres roles consultan, porque la consulta no modifica nada y responder por un ingreso es parte
del trabajo de todos. El control de acceso a la imagen existe frente a peticiones sin sesión, no
para distinguir entre roles.

## Dependencias

| Depende de | Para |
|---|---|
| M01 | Autenticación y control de acceso a la imagen |
| M02 | La placa y la titularidad del vehículo, usadas como criterios |
| M03 | Los ingresos y sus imágenes |
| M04 | La comparación entre lo reconocido y lo confirmado |
| M05 | El resultado de las validaciones |
| M06 | El recorrido del proceso |

| Es requerido por | Para |
|---|---|
| — | Ningún módulo depende de M07: es un punto final de lectura |
