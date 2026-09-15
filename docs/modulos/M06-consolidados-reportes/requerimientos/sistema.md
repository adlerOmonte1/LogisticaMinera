# Requerimientos de sistema — M06 Consolidados y reportes

| Código | Requerimiento | Deriva de |
|---|---|---|
| RS-M06-01 | El sistema agrega los ingresos no anulados de un periodo por producto, calculando cantidad de viajes y toneladas totales | RU-M06-01 |
| RS-M06-02 | El sistema desagrega los agregados de producción según la titularidad del vehículo asociado a cada ingreso | RU-M06-02 |
| RS-M06-03 | El sistema genera el consolidado incluso para periodos sin movimientos, devolviendo valores en cero con nota explicativa | RU-M06-01 |
| RS-M06-04 | El sistema excluye del cálculo los documentos anulados y reporta su cantidad de forma separada | — (integridad) |
| RS-M06-05 | El sistema exporta el consolidado a los formatos XLSX y PDF mediante estrategias intercambiables que comparten una misma interfaz | RU-M06-03 |
| RS-M06-06 | El sistema incorpora en el encabezado de toda exportación el periodo, la fecha de generación y el usuario responsable | RU-M06-03 |
| RS-M06-07 | El sistema produce el consolidado semestral con la estructura del formato oficial vigente, sin transmitirlo a ninguna entidad externa | RU-M06-04 |
| RS-M06-08 | El sistema registra en auditoría todo evento de generación y exportación de reportes | — (trazabilidad) |

## Nota sobre RS-M06-05

La exportación se implementa con una interfaz común y una estrategia por formato (`ExportadorExcel`, `ExportadorPDF`). Añadir el formato de la declaración semestral no debe requerir modificar el código existente de los exportadores: es la aplicación concreta del principio de abierto/cerrado en este proyecto, y el ejemplo que conviene tener preparado para la revisión técnica.
