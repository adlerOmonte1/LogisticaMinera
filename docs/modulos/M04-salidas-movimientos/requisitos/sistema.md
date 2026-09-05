# Requerimientos de sistema — M04 Salidas y movimientos

| Código | Requerimiento | Deriva de |
|---|---|---|
| RS-M04-01 | El sistema persiste la salida con correlativo propio, distinto de la serie de ingresos | RU-M04-01 |
| RS-M04-02 | El sistema clasifica cada salida mediante un atributo enumerado de dominio cerrado {VENTA, TRASLADO_INTERNO, MERMA} | RU-M04-02 |
| RS-M04-03 | El sistema exige cliente cuando el tipo es VENTA y motivo cuando el tipo es MERMA | RU-M04-02 |
| RS-M04-04 | El sistema consulta el saldo vigente del producto antes de persistir y emite advertencia si la cantidad lo supera, sin impedir la operación | RU-M04-03 |
| RS-M04-05 | El sistema genera un movimiento de stock de tipo SALIDA por cada salida persistida, en la misma transacción | — (integridad con M05) |
| RS-M04-06 | El sistema implementa la anulación como cambio de estado con motivo obligatorio y revierte el movimiento asociado | RU-M04-04 |
| RS-M04-07 | El sistema no expone ninguna operación de eliminación física de salidas | RU-M04-04 |
