# Requerimientos de sistema — M07 Consulta de ingresos y respaldo

| Código | Requerimiento | Deriva de |
|---|---|---|
| RS-M07-01 | El sistema busca ingresos por placa y por fecha o rango de fechas del ticket | RU-M07-01 |
| RS-M07-02 | El sistema admite búsqueda parcial de placa, sin distinguir mayúsculas ni guiones | RU-M07-02 |
| RS-M07-03 | El sistema exige al menos uno de los dos criterios para ejecutar la búsqueda | — (evita recorrer la tabla completa) |
| RS-M07-04 | El sistema devuelve los resultados ordenados por `fecha_hora_pesaje` descendente | RU-M07-01 |
| RS-M07-05 | El sistema entrega, en el detalle de un ingreso, la imagen del ticket asociada o, si el ingreso se registró sin foto, la indicación de que no tiene respaldo fotográfico y su motivo | RU-M07-03 |
| RS-M07-06 | El sistema sirve la imagen solo a usuarios autenticados con permiso sobre el ingreso | — (integridad con M03) |
| RS-M07-07 | El sistema informa cuando el respaldo no está disponible, en lugar de presentar el detalle sin indicarlo | RU-M07-03 |
| RS-M07-08 | El sistema incluye los ingresos anulados en los resultados, señalados como tales y con su motivo | RU-M07-05 |
| RS-M07-09 | El sistema ofrece un listado con filtros combinables por rango de fechas, tipo de mineral, vehículo, titularidad y estado, y búsqueda por placa o código; sin fechas indicadas, presenta el mes en curso hasta la fecha actual | RU-M07-04 |
| RS-M07-10 | El sistema pagina los resultados del listado | RU-M07-04 |
| RS-M07-11 | El sistema calcula el número de ingresos y la suma de pesos netos del conjunto filtrado considerando solo los ingresos en estado `REGISTRADO` | RU-M07-04 |
| RS-M07-12 | El sistema rechaza un rango de fechas cuyo inicio sea posterior a su fin | RU-M07-04 |
| RS-M07-13 | El sistema compone el detalle de un ingreso con sus validaciones, su reconocimiento, su trazabilidad y su historial | — (integridad con M04, M05, M06, M09) |
| RS-M07-14 | El sistema indica la ausencia de cada uno de esos elementos en lugar de omitir su bloque | RU-M07-03 |
| RS-M07-15 | El sistema no escribe ningún dato del dominio: todas sus operaciones son de lectura, y el evento de una exportación lo registra el registrador común de M09 | — (D-10) |
| RS-M07-16 | El sistema incluye los ingresos En proceso en los resultados, señalados como tales y con el peso neto indicado como pendiente del destare | RU-M07-04 |
| RS-M07-17 | El sistema presenta, junto al resultado de la búsqueda por placa y fecha, el lote del ingreso, su estado y su recorrido por las etapas de la ruta, o indica que el ingreso aún no tiene lote | RU-M07-06 |
| RS-M07-18 | El sistema señala en el listado los ingresos sin respaldo fotográfico | RU-M07-03 |
| RS-M07-19 | El sistema calcula, para un mes, por cada día según la fecha del pesaje, el número de ingresos no anulados, las toneladas netas de los Registrados y si hay ingresos En proceso o anulados | RU-M07-07 |
| RS-M07-20 | El sistema calcula el resumen del mes: ingresos no anulados, toneladas netas de los Registrados, días con llegadas e ingresos En proceso | RU-M07-07 |
| RS-M07-21 | El sistema lista los ingresos de un día con su hora del pesaje, placa, código, tipo de mineral, peso neto y estado | RU-M07-07 |
| RS-M07-22 | El sistema presenta el historial de un ingreso que provee M09, sin componerlo por su cuenta | RU-M07-08 |
| RS-M07-23 | El sistema calcula el resumen del día según la fecha del pesaje: ingresos no anulados, con la hora y la placa del último; toneladas netas de los Registrados y número de ingresos En proceso excluidos; ingresos pendientes de destare con sus placas; y lotes Abiertos o En recorrido que no están listos para cerrar | RU-M07-09 |
| RS-M07-24 | El sistema presenta los cinco ingresos más recientes por fecha del pesaje y las toneladas netas de los Registrados de cada uno de los últimos siete días | RU-M07-09 |
| RS-M07-25 | El sistema calcula los avisos de pendientes según el rol del usuario: ingresos que esperan destare, advertencias V4 justificadas en el día, lotes En recorrido con su siguiente paso, lotes listos para cerrar —solo para el Administrador— e ingresos Registrados sin lote —solo para quien compone lotes— | RU-M07-09 |
| RS-M07-26 | El sistema no almacena los avisos: los calcula al consultarse, de modo que un aviso desaparece cuando se resuelve lo que lo originó | RU-M07-09 |
| RS-M07-27 | El sistema exporta a CSV, en UTF-8 con marca de orden de bytes y separador punto y coma, todos los ingresos del conjunto filtrado del listado, con código, fecha y hora del pesaje, placa, tipo de vehículo, tipo de mineral, peso bruto, tara, peso neto, estado y usuario que registró | RU-M07-10 |
| RS-M07-28 | El sistema autoriza la exportación del listado solo al Administrativo y al Administrador, rechaza la de un conjunto vacío y registra cada exportación en auditoría como `EXPORTAR`, con los filtros y el número de ingresos | RU-M07-10 |
| RS-M07-29 | El sistema resuelve el texto de la búsqueda de la cabecera como código de ingreso, completo o por sus dígitos finales; si no corresponde a ningún código, lo deriva a la búsqueda por placa | RU-M07-11 |
