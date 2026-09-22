# Requerimientos funcionales — M06 Trazabilidad del proceso

**RF asociado:** **RF07** — Vincular cada ingreso con las etapas de secado, zarandeo, molienda y
ensacado.

| Función | Descripción | HU | Endpoint |
|---|---|---|---|
| Listar lotes | Consulta con filtros por estado, tipo de mineral y fecha | HU-M06-01 | `GET /api/v1/lotes/` |
| Abrir lote | Alta con tipo de mineral y fecha de apertura | HU-M06-01 | `POST /api/v1/lotes/` |
| Consultar lote | Detalle con su composición y su recorrido | HU-M06-01 | `GET /api/v1/lotes/{id}/` |
| Asignar ingresos al lote | Incorpora uno o varios ingresos al lote abierto | HU-M06-01 | `POST /api/v1/lotes/{id}/ingresos/` |
| Retirar un ingreso del lote | Quita el ingreso de un lote abierto | HU-M06-01 | `DELETE /api/v1/lotes/{id}/ingresos/{id_ingreso}/` |
| Cerrar lote | Fija la composición y habilita el registro de etapas | HU-M06-01 | `PATCH /api/v1/lotes/{id}/cerrar/` |
| Registrar paso por etapa | Anota el paso del lote por una etapa, con su fecha | HU-M06-02 | `POST /api/v1/lotes/{id}/etapas/` |
| Consultar trazabilidad de un ingreso | Etapas recorridas por el lote del ingreso | HU-M06-03 | `GET /api/v1/ingresos/{id}/trazabilidad/` |
| Listar etapas | Catálogo cerrado de las cuatro etapas con su orden | HU-M06-02 | `GET /api/v1/etapas/` |

`DELETE` sobre la asignación no borra ningún registro del negocio: deshace un vínculo entre un
ingreso y un lote abierto. El ingreso permanece intacto, y la prohibición de borrado (D-07) se
refiere a los ingresos, no a esta relación.

## Responsabilidad y límites

M06 es el dueño de las entidades `LOTE_PROCESO`, `ETAPA_PROCESO` y `PASO_ETAPA`.

**Lo que hace.** Agrupa ingresos en cargas de trabajo, gobierna el ciclo abierto–cerrado del lote,
registra el paso por cada etapa respetando el orden del proceso y responde por dónde va el mineral
de un ingreso.

**Lo que delega.**

| Delega en | A través de | Qué obtiene |
|---|---|---|
| M03 Registro | Lectura de ingresos | El ingreso, su tipo de mineral, su peso neto y su estado |
| M02 Catálogo | Lectura del catálogo | El tipo de mineral del lote |
| M09 Auditoría | Servicio de eventos | El registro de la apertura, el cierre y el paso por etapa |

**Lo que no hace.** No modifica el ingreso más allá de su vínculo con el lote, no calcula totales de
producción —eso es M08, que agrega por mes y tipo de mineral, no por lote— y no controla balance de
masa entre etapas: registra que la carga pasó, no cuánto mineral perdió en el camino, que está fuera
de alcance.

## Permisos

| Función | Administrador | Administrativo | Supervisor de planta |
|---|:---:|:---:|:---:|
| Listar y consultar lotes | Sí | Sí | Sí |
| Abrir, cerrar y componer lotes | Sí | Sí | No |
| Registrar paso por etapa | Sí | Sí | Sí |
| Consultar trazabilidad | Sí | Sí | Sí |

El Supervisor de planta registra el paso por etapa porque es quien está en el proceso, pero no
decide la composición de las cargas, que es una decisión administrativa.

## Dependencias

| Depende de | Para |
|---|---|
| M01 | Autenticación y atribución del registro de cada etapa |
| M02 | El tipo de mineral del lote |
| M03 | Los ingresos que componen el lote, con su peso y su estado |
| M09 | Registro de los eventos de apertura, cierre y paso por etapa |

| Es requerido por | Para |
|---|---|
| M07 | Mostrar el recorrido del proceso en el detalle de un ingreso |
