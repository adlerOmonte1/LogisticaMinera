# Requerimientos de sistema — M08 Consolidación de la producción

| Código | Requerimiento | Deriva de |
|---|---|---|
| RS-M08-01 | El sistema calcula el total de `peso_neto_tn` y el número de ingresos agrupados por `tipo_mineral`, para un mes y año dados | RU-M08-01 |
| RS-M08-02 | El sistema excluye los ingresos en estado `ANULADO` del cálculo | RU-M08-01 |
| RS-M08-03 | El sistema calcula el total a demanda sobre los ingresos existentes, sin almacenar un acumulado previo | RU-M08-04 |
| RS-M08-04 | El sistema omite del resultado los tipos de mineral sin ingresos en el periodo, en lugar de mostrarlos con total cero | RU-M08-01 |
| RS-M08-05 | El sistema rechaza un periodo posterior al mes en curso | — (integridad del cálculo) |
| RS-M08-06 | El sistema informa cuando el periodo solicitado no tiene ingresos | RU-M08-01 |
| RS-M08-07 | El sistema exporta el mismo cálculo de la consulta como archivo descargable | RU-M08-03 |
| RS-M08-08 | El sistema admite el formato XLSX como primer formato de exportación, con estructura que permite añadir otros sin modificar el cálculo | RU-M08-03 |
| RS-M08-09 | El sistema incluye en el archivo exportado el periodo, la fecha de generación y el detalle por tipo de mineral | RU-M08-03 |
| RS-M08-10 | El sistema registra en auditoría cada exportación, con el periodo y el usuario responsable | — (integridad con M09) |
| RS-M08-11 | El sistema no persiste ninguna entidad propia: toda su información se deriva de `INGRESO` en el momento de la consulta | — (D-10) |
