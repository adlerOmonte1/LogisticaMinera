# Requerimientos no funcionales — M08 Consolidación de la producción

| Código | Característica ISO/IEC 25010:2023 | Requerimiento | Verificación |
|---|---|---|---|
| RNF-M08-01 | Eficiencia de desempeño — comportamiento temporal | El consolidado mensual se calcula en menos de 3 segundos con 5000 ingresos en base | Prueba automatizada con datos sintéticos |
| RNF-M08-02 | Eficiencia de desempeño — comportamiento temporal | La exportación se genera y descarga en menos de 5 segundos para un mes con hasta 1000 ingresos | Cronometraje con datos sintéticos |
| RNF-M08-03 | Adecuación funcional — corrección | El total calculado coincide exactamente con la suma manual de los pesos netos no anulados del periodo | Consulta de verificación sobre la base contrastada con cálculo independiente |
| RNF-M08-04 | Mantenibilidad — modularidad | Añadir un formato de exportación no modifica el repositorio del cálculo ni los exportadores existentes | Inspección de código |
| RNF-M08-05 | Fiabilidad — exactitud | El total exportado es idéntico, campo por campo, al que muestra la consulta en pantalla para el mismo periodo | Prueba automatizada que compara ambas salidas |
| RNF-M08-06 | Usabilidad — operabilidad | El periodo se selecciona con un control de mes y año, sin escribir fechas completas | Inspección en dispositivo real |

## Nota sobre RNF-M08-01

El cálculo se hace a demanda (RN-M08-02) y por lo tanto recorre los ingresos del mes en cada
consulta. Con el volumen previsto durante la ventana de operación esto es rápido, pero conviene
vigilarlo conforme crezca el histórico: si el tiempo empeora con los meses, la solución no es
almacenar un acumulado —eso reintroduce el problema que RN-M08-02 evita— sino un índice adecuado
sobre `fecha_hora_ticket` y `tipo_mineral`, que ya existe según el modelo de datos.

## Nota sobre RNF-M08-05

Es la verificación operativa de RN-M08-05. No basta con que ambos caminos «usen la misma función»
en el código: la prueba debe ejecutar los dos endpoints sobre el mismo periodo y comparar sus
salidas, porque un error de formato en la exportación —redondeo, columna traspuesta— podría alterar
el número sin que el cálculo subyacente haya cambiado.
