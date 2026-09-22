# Requerimientos de sistema — M06 Trazabilidad del proceso

| Código | Requerimiento | Deriva de |
|---|---|---|
| RS-M06-01 | El sistema registra lotes de proceso con `codigo` asignado por el servidor, `id_tipo_mineral`, `fecha_apertura` y `estado` | RU-M06-01 |
| RS-M06-02 | El sistema asigna ingresos a un lote mediante `id_lote` en el ingreso, admitiendo como máximo un lote por ingreso | RU-M06-01 |
| RS-M06-03 | El sistema exige que el tipo de mineral del ingreso coincida con el del lote para permitir la asignación | RU-M06-01 |
| RS-M06-04 | El sistema impide asignar a un lote ingresos anulados | — (integridad con M03) |
| RS-M06-05 | El sistema permite reasignar un ingreso entre lotes mientras ambos estén abiertos | RU-M06-01 |
| RS-M06-06 | El sistema impide modificar la composición de un lote cerrado | RU-M06-01 |
| RS-M06-07 | El sistema calcula y expone, por lote, el número de ingresos asignados y la suma de sus pesos netos | RU-M06-05 |
| RS-M06-08 | El sistema mantiene el catálogo cerrado de cuatro etapas —secado, zarandeo, molienda y ensacado— con su orden | RU-M06-02 |
| RS-M06-09 | El sistema registra el paso de un lote por una etapa con `fecha_hora`, el usuario responsable y una observación opcional | RU-M06-02 |
| RS-M06-10 | El sistema admite el registro de una etapa solo si las anteriores ya fueron registradas para ese lote | RU-M06-03 |
| RS-M06-11 | El sistema admite un único registro por combinación de lote y etapa | RU-M06-02 |
| RS-M06-12 | El sistema admite el registro de etapas solo sobre lotes cerrados | RU-M06-02 |
| RS-M06-13 | El sistema rechaza una fecha de etapa posterior al momento del registro o anterior a la de la etapa previa | RU-M06-03 |
| RS-M06-14 | El sistema expone la trazabilidad de un ingreso mostrando las cuatro etapas, cuáles se completaron, su fecha y su responsable | RU-M06-04 |
| RS-M06-15 | El sistema expone el número de etapas recorridas sobre el total de cuatro para un ingreso dado | RU-M06-04 |
| RS-M06-16 | El sistema presenta un ingreso sin lote como un ingreso con cero etapas recorridas, no como un dato ausente | RU-M06-04 |
