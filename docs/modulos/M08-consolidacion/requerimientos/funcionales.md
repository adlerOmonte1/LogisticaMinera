# Requerimientos funcionales — M08 Consolidación de la producción

**RF asociado:** **RF09** — Generar y exportar el total acumulado mensual por producto.

| Función | Descripción | HU | Endpoint |
|---|---|---|---|
| Consultar consolidado mensual | Total y número de ingresos por tipo de mineral en un periodo | HU-M08-01 | `GET /api/v1/consolidacion/mensual/` |
| Exportar consolidado mensual | Genera el archivo descargable del mismo cálculo | HU-M08-02 | `GET /api/v1/consolidacion/mensual/exportar/` |

Ambos endpoints reciben mes y año como parámetros de consulta. El de exportación no duplica el
cálculo: invoca el mismo repositorio que el de consulta y solo cambia la presentación del resultado.

## Responsabilidad y límites

M08 **no tiene entidad propia**: agrega sobre `INGRESO`, que pertenece a M03 (D-10).

**Lo que hace.** Calcula el total de toneladas y el número de ingresos por tipo de mineral para un
periodo dado, y entrega ese mismo cálculo como consulta en pantalla o como archivo descargable.

**Lo que delega.**

| Delega en | A través de | Qué obtiene |
|---|---|---|
| M03 Registro | Lectura de ingresos | Los ingresos del periodo, su tipo de mineral, su peso neto y su estado |
| M09 Auditoría | Servicio de eventos | El registro de cada exportación |

**Lo que no hace.** No agrupa por lote de proceso —eso es M06—, no busca un ingreso individual —eso
es M07— y no almacena ningún resultado calculado: cada consulta recalcula sobre los ingresos
vigentes en ese momento (RN-M08-02).

## Permisos

| Función | Administrador | Administrativo | Supervisor de planta |
|---|:---:|:---:|:---:|
| Consultar consolidado mensual | Sí | Sí | No |
| Exportar consolidado mensual | Sí | Sí | No |

La consolidación es una operación administrativa de reporte, fuera del alcance del trabajo diario de
registro que hace el Supervisor de planta.

## Dependencias

| Depende de | Para |
|---|---|
| M01 | Autenticación y control de acceso |
| M02 | Los tipos de mineral que agrupan el resultado |
| M03 | Los ingresos del periodo, con su peso neto y su estado |
| M09 | Registro del evento de exportación |

| Es requerido por | Para |
|---|---|
| — | Ningún módulo depende de M08: es un punto final de lectura |
