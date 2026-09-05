# Requerimientos de sistema — M03 Registro de ingresos

| Código | Requerimiento | Deriva de |
|---|---|---|
| RS-M03-01 | El sistema persiste el ingreso con dos marcas temporales independientes: `hora_pesaje`, ingresada por el usuario, y `hora_registro`, asignada por el servidor | RU-M03-01 |
| RS-M03-02 | El sistema calcula `peso_neto` como la diferencia entre `peso_bruto` y `tara`, tanto en el cliente (visualización) como en el servidor (autoritativo) | RU-M03-02 |
| RS-M03-03 | El sistema asigna el correlativo dentro de una transacción con bloqueo o mediante secuencia de base de datos, garantizando unicidad bajo concurrencia | RU-M03-03 |
| RS-M03-04 | El sistema rechaza el registro de un número de ticket ya existente e informa el correlativo del ingreso que lo contiene | RU-M03-03 |
| RS-M03-05 | El sistema genera un movimiento de stock de tipo ENTRADA por cada ingreso persistido, dentro de la misma transacción | — (integridad con M05) |
| RS-M03-06 | El sistema expone el listado con paginación y filtros por rango de fechas, producto, vehículo y estado | RU-M03-04 |
| RS-M03-07 | El sistema conserva los valores anteriores de todo campo modificado en el registro de auditoría | RU-M03-05 |
| RS-M03-08 | El sistema implementa la anulación como cambio de estado con motivo obligatorio, y no expone ninguna operación de eliminación física | RU-M03-06 |
| RS-M03-09 | El sistema revierte el movimiento de stock asociado al anular un ingreso, dentro de la misma transacción | RU-M03-06 |
| RS-M03-10 | El sistema rechaza toda solicitud que intente modificar `correlativo` o `hora_registro`, con independencia del rol | RU-M03-05 |
