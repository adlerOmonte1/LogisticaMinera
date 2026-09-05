# Requerimientos no funcionales — M06 Consolidados y reportes

| Código | Característica ISO/IEC 25010:2023 | Requerimiento | Verificación |
|---|---|---|---|
| RNF-M06-01 | Eficiencia de desempeño — comportamiento temporal | El consolidado mensual se genera en menos de 5 segundos con 500 ingresos en el periodo | Prueba de carga con datos sintéticos |
| RNF-M06-02 | Eficiencia de desempeño | La exportación a Excel de un consolidado mensual se completa en menos de 10 segundos | Medición directa |
| RNF-M06-03 | Adecuación funcional — corrección | Las toneladas del consolidado coinciden exactamente con la suma de los pesos netos de los ingresos no anulados del periodo | Prueba automatizada comparando con consulta directa |
| RNF-M06-04 | Adecuación funcional — completitud | El consolidado se genera para cualquier periodo solicitado, incluidos los vacíos | Prueba: solicitar mes sin movimientos |
| RNF-M06-05 | Portabilidad — adaptabilidad | El archivo Excel se abre sin advertencias en LibreOffice y en Microsoft Excel | Prueba manual en ambos programas |
| RNF-M06-06 | Mantenibilidad — modularidad | Agregar un formato de exportación no requiere modificar los exportadores existentes | Revisión de diseño: interfaz común implementada |
| RNF-M06-07 | Usabilidad | La generación del consolidado del mes anterior requiere como máximo dos acciones desde la pantalla principal | Inspección funcional |

## RNF-M06-04 y el indicador I6

Este requisito parece menor y es central. El indicador I6 mide el porcentaje de meses con reporte disponible. Si el sistema fallara al generar el consolidado de un mes sin movimientos, ese mes contaría como "sin reporte" y el indicador se degradaría por una razón que no refleja la operación real. Un periodo sin producción **tiene** reporte: uno que dice que no hubo producción.

## RNF-M06-07 y el problema original

El reporte mensual se perdió porque armarlo costaba tiempo. Si generarlo en el sistema requiere navegar por cinco pantallas y configurar siete parámetros, el problema no se resuelve. La meta de dos acciones no es una preferencia estética: es la condición para que el indicador I6 mejore de forma sostenida.
