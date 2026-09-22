# Requerimientos no funcionales — M05 Validación automática de consistencia

| Código | Característica ISO/IEC 25010:2023 | Requerimiento | Verificación |
|---|---|---|---|
| RNF-M05-01 | Eficiencia de desempeño — comportamiento temporal | La evaluación de las cinco reglas sobre un ingreso se resuelve en menos de 200 milisegundos, incluida la lectura de la capacidad del vehículo | Prueba automatizada con medición del tiempo |
| RNF-M05-02 | Adecuación funcional — corrección | Las cinco reglas detectan la totalidad de las inconsistencias sembradas en el conjunto de prueba, con dos casos por regla | Prueba automatizada sobre el conjunto de prueba |
| RNF-M05-03 | Adecuación funcional — corrección | Ninguna regla señala como incoherente un ingreso válido | Prueba automatizada con ingresos correctos de distinta capacidad y tipo de mineral |
| RNF-M05-04 | Fiabilidad — madurez | El mismo conjunto de datos produce siempre el mismo resultado de validación | Prueba automatizada repetida sobre los mismos datos |
| RNF-M05-05 | Seguridad — integridad | Ninguna regla puede desactivarse desde la petición del cliente | Prueba automatizada que intenta enviar indicadores de omisión |
| RNF-M05-06 | Mantenibilidad — modularidad | Añadir una regla consiste en crear una clase y registrarla, sin modificar las existentes ni el servicio | Inspección de código |
| RNF-M05-07 | Mantenibilidad — capacidad de ser probado | Cada regla se prueba de forma aislada, sin base de datos ni petición HTTP | Inspección de código y ejecución de las pruebas unitarias |
| RNF-M05-08 | Mantenibilidad — capacidad de ser modificado | La tolerancia de V1 y el patrón de placa de V3 se cambian por configuración, no editando el código | Inspección de configuración |
| RNF-M05-09 | Usabilidad — protección contra errores del usuario | Cada inconsistencia se muestra junto al campo afectado, con su mensaje literal | Inspección en dispositivo real |

## Nota sobre RNF-M05-02 y RNF-M05-03

Son las dos caras de la misma exigencia y ninguna basta por separado. Un validador que señalara todo
cumpliría la primera y arruinaría el sistema: el usuario aprendería a ignorar las alertas. La
segunda es la que protege contra esa deriva, y por eso su verificación usa ingresos correctos de
distinta capacidad y tipo de mineral, no un único caso feliz.

## Nota sobre RNF-M05-06 y RNF-M05-08

Las cinco reglas actuales son las del instrumento de la investigación, pero la tolerancia de V1
todavía está pendiente de confirmarse con la empresa y el patrón de placa puede cambiar. Que ambos
sean configuración y no código evita que ajustarlos exija una nueva versión del sistema. Durante la
ventana de operación controlada esos parámetros quedan congelados (D-16), lo que es una decisión de
operación, no una limitación técnica.
