# Requerimientos funcionales — M06 Trazabilidad del proceso

**RF asociado:** **RF07** — Vincular cada ingreso con las etapas de secado, zarandeo, molienda y
ensacado. El cierre del lote con su destino forma parte de RF07 (DR-14), no es un RF adicional.

| Función | Descripción | HU | Endpoint |
|---|---|---|---|
| Listar lotes | Consulta con filtros por estado, tipo de mineral y fecha | HU-M06-01 | `GET /api/v1/lotes/` |
| Abrir lote | Alta con nombre, tipo de mineral y fecha de apertura | HU-M06-01 | `POST /api/v1/lotes/` |
| Agregar otro mineral | Suma un tipo de mineral a la lista del lote | HU-M06-01 | `POST /api/v1/lotes/{id}/minerales/` |
| Quitar un mineral | Retira de la lista, con baja lógica, un tipo sin ingresos, con el lote Abierto | HU-M06-01 | `POST /api/v1/lotes/{id}/minerales/{id_tipo}/quitar/` |
| Consultar lote | Detalle con su estado, su composición, sus partes y su recorrido | HU-M06-01 | `GET /api/v1/lotes/{id}/` |
| Asignar ingresos al lote | Incorpora uno o varios ingresos; en un lote En recorrido, como ingresos tardíos | HU-M06-01 | `POST /api/v1/lotes/{id}/ingresos/` |
| Retirar un ingreso del lote | Devuelve a cancha un ingreso cuyo mineral aún no pasó por zarandeo ni molienda | HU-M06-01 | `POST /api/v1/lotes/{id}/ingresos/{id_ingreso}/retirar/` |
| Iniciar el recorrido | Pasa el lote a En recorrido y registra la fecha de inicio | HU-M06-01 | `PATCH /api/v1/lotes/{id}/iniciar-recorrido/` |
| Registrar paso por etapa | Anota el paso del lote o de una parte por una etapa, con la ruta cuando corresponde, y las horas de molienda o los bigbags si aplica | HU-M06-02 | `POST /api/v1/lotes/{id}/etapas/` |
| Registrar secado de un ingreso tardío | Anota el secado propio del ingreso que llegó después del secado del lote y, si el lote está dividido, su reparto entre las partes | HU-M06-02, HU-M06-04 | `POST /api/v1/lotes/{id}/ingresos/{id_ingreso}/secado/` |
| Asociar bigbags | Registra bigbags de un lote o una parte con ensacado registrado | HU-M06-02 | `POST /api/v1/lotes/{id}/bigbags/` |
| Dividir lote | Crea las partes con su nombre, su fracción y su ruta | HU-M06-04 | `POST /api/v1/lotes/{id}/division/` |
| Consultar resumen de cierre | Resumen del proceso y lista de pendientes | HU-M06-05 | `GET /api/v1/lotes/{id}/resumen/` |
| Cerrar lote | Cierre definitivo con destino | HU-M06-05 | `PATCH /api/v1/lotes/{id}/cerrar/` |
| Consultar trazabilidad de un ingreso | Etapas de la ruta recorridas por el lote o las partes del ingreso | HU-M06-03 | `GET /api/v1/ingresos/{id}/trazabilidad/` |
| Listar etapas y rutas | Catálogos cerrados de las cuatro etapas y las tres rutas | HU-M06-02 | `GET /api/v1/etapas/`, `GET /api/v1/rutas/` |

Ninguna función usa `DELETE` (D-22). Retirar un ingreso deshace su vínculo con el lote sin tocar
ningún otro dato del ingreso, y quitar un mineral marca su fila de la lista como retirada, con fecha y
usuario, en lugar de borrarla.

## Responsabilidad y límites

M06 es el dueño de las entidades del lote de proceso: el lote, sus partes, el reparto de los
ingresos tardíos, el paso por cada etapa, los bigbags y los catálogos cerrados de etapas y rutas.

**Lo que hace.** Agrupa ingresos en cargas de trabajo, gobierna el ciclo Abierto, En recorrido y
Cerrado del lote, registra la ruta y el paso por cada etapa respetando su orden, divide el lote por
fracciones, conserva los datos descriptivos de bigbags y horas de molienda, cierra el lote con su
destino y responde por dónde va el mineral de un ingreso.

**Lo que delega.**

| Delega en | A través de | Qué obtiene |
|---|---|---|
| M03 Registro | Lectura de ingresos | El ingreso, su tipo de mineral, su peso neto y su estado |
| M02 Catálogo | Lectura del catálogo | Los tipos de mineral del lote |
| M09 Auditoría | Servicio de eventos | El registro de cada operación sobre el lote |

**Lo que no hace.** No modifica el ingreso más allá de su vínculo con el lote; no calcula totales de
producción —eso es M08, que agrega por mes y tipo de mineral, no por lote—; no lleva inventario de
producto terminado ni balance de masa: los bigbags y su peso son datos descriptivos, y la diferencia
entre lo ensacado y lo registrado no mide pérdidas (DR-15). Tampoco registra la venta ni el traslado:
solo su destino, sin guía, factura ni precio (DR-14).

## Permisos

| Función | Administrador | Administrativo | Supervisor de planta |
|---|:---:|:---:|:---:|
| Listar y consultar lotes | Sí | Sí | Sí |
| Abrir lote, agregar o quitar minerales, asignar y retirar ingresos, iniciar el recorrido | Sí | Sí | No |
| Dividir lote | Sí | Sí | No |
| Registrar paso por etapa, secado de un ingreso tardío y bigbags | Sí | Sí | Sí |
| Cerrar lote con su destino | Sí | No | No |
| Consultar trazabilidad | Sí | Sí | Sí |

El Supervisor de planta registra el paso por las etapas porque es quien está en el proceso (DR-17),
pero no decide la composición de las cargas ni su división, que son decisiones administrativas. El
cierre con destino es del Administrador porque decide a dónde se entrega el mineral (DR-14).

## Dependencias

| Depende de | Para |
|---|---|
| M01 | Autenticación y atribución de cada operación |
| M02 | Los tipos de mineral del lote |
| M03 | Los ingresos que componen el lote, con su peso y su estado |
| M09 | Registro de los eventos del lote |

| Es requerido por | Para |
|---|---|
| M03 | La lista de tipos de mineral del lote al corregir un ingreso, y el retiro del ingreso anulado de un lote Abierto |
| M07 | Mostrar el recorrido del proceso en el detalle de un ingreso |
