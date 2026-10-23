# Requerimientos de sistema — M06 Trazabilidad del proceso

| Código | Requerimiento | Deriva de |
|---|---|---|
| RS-M06-01 | El sistema registra lotes de proceso con `codigo` asignado por el servidor, `nombre` único, `id_tipo_mineral`, `fecha_apertura` no posterior a la fecha actual y `estado` con dominio cerrado {ABIERTO, EN_RECORRIDO, CERRADO} | RU-M06-01 |
| RS-M06-02 | El sistema asigna ingresos a un lote mediante `id_lote` en el ingreso, admitiendo como máximo un lote por ingreso | RU-M06-01 |
| RS-M06-03 | El sistema mantiene la lista de tipos de mineral de cada lote; ofrece aparte, agrupados por mineral, los ingresos de otros tipos, y al unificarlos exige la autorización, suma su mineral a la lista y marca el ingreso como «Otro mineral» | RU-M06-01, RU-M06-11 |
| RS-M06-04 | El sistema admite asignar a un lote solo ingresos en estado `REGISTRADO`, e impide asignar los anulados y los que están En proceso | — (integridad con M03) |
| RS-M06-05 | El sistema permite retirar un ingreso de un lote no `CERRADO`, o trasladarlo a otro, solo mientras ninguna parte del lote —o, en un ingreso tardío con secado propio, ninguna de sus partes— tenga registrado zarandeo o molienda, y rechaza el retiro que dejaría sin ingresos a un lote `EN_RECORRIDO` | RU-M06-01 |
| RS-M06-06 | El sistema admite ingresos tardíos en un lote `EN_RECORRIDO`, los marca como tales y rechaza agregar ingresos a un lote `CERRADO` | RU-M06-08 |
| RS-M06-07 | El sistema calcula y expone, por lote, el número de ingresos asignados y la suma de sus pesos netos, incluidos los tardíos y excluidos los anulados | RU-M06-05 |
| RS-M06-08 | El sistema mantiene el catálogo cerrado de cuatro etapas —secado, zarandeo, molienda y ensacado— y el de tres rutas: zarandeo y ensacado; molienda y ensacado; zarandeo, molienda y ensacado | RU-M06-02, RU-M06-06 |
| RS-M06-09 | El sistema registra el paso por una etapa con `fecha_hora`, el usuario responsable y una observación opcional, sobre el lote —el secado común— o sobre una de sus partes | RU-M06-02 |
| RS-M06-10 | El sistema admite el registro de una etapa solo si la anterior de la ruta ya fue registrada para ese lote o esa parte | RU-M06-03 |
| RS-M06-11 | El sistema admite un único registro por combinación de lote o parte y etapa | RU-M06-02 |
| RS-M06-12 | El sistema admite el registro de etapas solo sobre lotes `EN_RECORRIDO` | RU-M06-02 |
| RS-M06-13 | El sistema rechaza una fecha de etapa posterior al momento del registro, anterior a la de la etapa previa o, en la primera etapa, anterior al inicio del recorrido | RU-M06-03 |
| RS-M06-14 | El sistema expone la trazabilidad de un ingreso con las etapas de la ruta de su lote o de cada parte, cuáles se completaron, su fecha y su responsable | RU-M06-04 |
| RS-M06-15 | El sistema expone el número de etapas recorridas sobre el número de etapas de la ruta del ingreso; en un lote dividido, sobre la unión de las etapas de las rutas de sus partes; sin ruta decidida, no calcula la proporción | RU-M06-04 |
| RS-M06-16 | El sistema presenta un ingreso sin lote como un ingreso sin etapas recorridas, no como un dato ausente | RU-M06-04 |
| RS-M06-17 | El sistema inicia el recorrido de un lote `ABIERTO` con al menos un ingreso, registra `fecha_inicio_recorrido` y lo pasa a `EN_RECORRIDO` | RU-M06-01 |
| RS-M06-18 | El sistema exige elegir la ruta al registrar el primer paso posterior al secado, para el lote o para cada parte | RU-M06-06 |
| RS-M06-19 | El sistema divide un lote una sola vez, en dos a seis partes con nombre distinto, fracción mayor que cero y ruta, siempre que las fracciones sumen la unidad y ninguna parte haya avanzado por su ruta | RU-M06-07 |
| RS-M06-20 | El sistema calcula las toneladas aproximadas de cada parte como su fracción por las toneladas netas del lote, sin almacenarlas ni usarlas en ningún total | RU-M06-07 |
| RS-M06-21 | El sistema registra el secado propio del ingreso tardío que llega después del secado del lote y, en un lote dividido, su reparto entre las partes con las fracciones del lote propuestas por defecto y editables, que deben sumar la unidad | RU-M06-08 |
| RS-M06-22 | El sistema registra las horas de molienda, mayores que cero, y calcula las toneladas por hora de la parte o del lote | RU-M06-09 |
| RS-M06-23 | El sistema asocia bigbags al lote o a una parte con ensacado registrado, con su cantidad y su peso aproximado, calculado sobre las toneladas pendientes de ensacar o recalculado por el usuario | RU-M06-09 |
| RS-M06-24 | El sistema cierra un lote solo cuando todo su mineral está ensacado, con destino obligatorio en el dominio cerrado {VENTA, TRASLADO}, observación opcional, y fecha y usuario asignados por el servidor | RU-M06-10 |
| RS-M06-25 | El sistema presenta, antes del cierre, el resumen del proceso: toneladas registradas, bigbags, ensacado aproximado, diferencia frente a lo registrado, horas de molienda y toneladas por hora por parte, y duración del proceso | RU-M06-10 |
| RS-M06-26 | El sistema rechaza agregar ingresos, registrar etapas o asociar bigbags en un lote `CERRADO` | RU-M06-10 |
| RS-M06-27 | El sistema retira de su lote el ingreso anulado mientras el lote está `ABIERTO`, a pedido del servicio de registro | — (integridad con M03) |
| RS-M06-28 | El sistema registra en auditoría la apertura, la asignación y el retiro de ingresos, el inicio del recorrido, la división, cada paso por etapa, los bigbags y el cierre del lote | — (integridad con M09) |
| RS-M06-29 | El sistema agrega un tipo de mineral a un lote no Cerrado y lo quita solo si no tiene ingresos y el lote está Abierto, registrando ambos actos en auditoría | RU-M06-11 |
| RS-M06-30 | El sistema presenta los ingresos y las toneladas del lote agrupados por tipo de mineral | RU-M06-11 |
