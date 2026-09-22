# Requerimientos de sistema — M07 Consulta de ingresos y respaldo

| Código | Requerimiento | Deriva de |
|---|---|---|
| RS-M07-01 | El sistema busca ingresos por placa y por fecha o rango de fechas del ticket | RU-M07-01 |
| RS-M07-02 | El sistema admite búsqueda parcial de placa, sin distinguir mayúsculas ni guiones | RU-M07-02 |
| RS-M07-03 | El sistema exige al menos uno de los dos criterios para ejecutar la búsqueda | — (evita recorrer la tabla completa) |
| RS-M07-04 | El sistema devuelve los resultados ordenados por `fecha_hora_ticket` descendente | RU-M07-01 |
| RS-M07-05 | El sistema entrega, en el detalle de un ingreso, la imagen del ticket asociada | RU-M07-03 |
| RS-M07-06 | El sistema sirve la imagen solo a usuarios autenticados con permiso sobre el ingreso | — (integridad con M03) |
| RS-M07-07 | El sistema informa cuando el respaldo no está disponible, en lugar de presentar el detalle sin indicarlo | RU-M07-03 |
| RS-M07-08 | El sistema incluye los ingresos anulados en los resultados, señalados como tales y con su motivo | RU-M07-05 |
| RS-M07-09 | El sistema ofrece un listado con filtros combinables por rango de fechas, tipo de mineral, vehículo, titularidad y estado | RU-M07-04 |
| RS-M07-10 | El sistema pagina los resultados del listado | RU-M07-04 |
| RS-M07-11 | El sistema calcula el número de ingresos y la suma de pesos netos del conjunto filtrado, excluyendo los anulados de la suma | RU-M07-04 |
| RS-M07-12 | El sistema rechaza un rango de fechas cuyo inicio sea posterior a su fin | RU-M07-04 |
| RS-M07-13 | El sistema compone el detalle de un ingreso con sus validaciones, su reconocimiento y su trazabilidad cuando existen | — (integridad con M04, M05, M06) |
| RS-M07-14 | El sistema indica la ausencia de cada uno de esos elementos en lugar de omitir su bloque | RU-M07-03 |
| RS-M07-15 | El sistema no escribe ningún dato: todas sus operaciones son de lectura | — (D-10) |
