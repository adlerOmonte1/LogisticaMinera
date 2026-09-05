# Requerimientos de sistema — M05 Existencias

| Código | Requerimiento | Deriva de |
|---|---|---|
| RS-M05-01 | El sistema deriva el saldo de cada producto a partir de la suma algebraica de sus movimientos no anulados | RU-M05-01, RU-M05-04 |
| RS-M05-02 | El sistema no expone ninguna operación de escritura directa sobre el saldo | RU-M05-04 |
| RS-M05-03 | El sistema denormaliza el saldo resultante en cada movimiento para responder la consulta sin recorrer el histórico completo | RU-M05-01 |
| RS-M05-04 | El sistema entrega el kardex de un producto con tipo, cantidad, origen, correlativo del documento fuente y saldo resultante | RU-M05-02 |
| RS-M05-05 | El sistema genera un movimiento de tipo AJUSTE con la diferencia entre la medición física y el saldo del sistema, sin sobrescribir el saldo | RU-M05-03 |
| RS-M05-06 | El sistema restringe el registro de ajustes al rol Administrador | RU-M05-03 |
| RS-M05-07 | El sistema conserva en el kardex tanto los movimientos originales como sus reversiones por anulación | RU-M05-02 |

## Nota sobre RS-M05-03

La denormalización del saldo resultante es una decisión de rendimiento con consecuencia metodológica: sostiene el indicador I3. Calcular el saldo recorriendo todos los movimientos cada vez haría que el tiempo de consulta creciera con el histórico, y el indicador se degradaría a lo largo de la ventana de observación por una razón ajena al diseño del sistema.
