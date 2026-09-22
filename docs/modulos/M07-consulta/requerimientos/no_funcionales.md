# Requerimientos no funcionales — M07 Consulta de ingresos y respaldo

| Código | Característica ISO/IEC 25010:2023 | Requerimiento | Verificación |
|---|---|---|---|
| RNF-M07-01 | Eficiencia de desempeño — comportamiento temporal | La búsqueda por placa y fecha devuelve resultados en menos de 2 segundos con 5000 ingresos en base | Prueba automatizada con datos sintéticos |
| RNF-M07-02 | Eficiencia de desempeño — comportamiento temporal | El detalle completo de un ingreso, con sus cuatro bloques, se compone en menos de 2 segundos | Prueba automatizada con datos sintéticos |
| RNF-M07-03 | Eficiencia de desempeño — utilización de recursos | El listado compone cada página con un número fijo de consultas, independiente del número de resultados | Inspección del número de consultas ejecutadas |
| RNF-M07-04 | Eficiencia de desempeño — comportamiento temporal | La imagen del ticket se entrega en una versión reducida para la lista y en su resolución original solo al ampliarla | Inspección en dispositivo real sobre red móvil |
| RNF-M07-05 | Seguridad — confidencialidad | La imagen no es accesible sin sesión válida ni desde una ruta adivinable | Intento de acceso sin sesión y con identificador alterado |
| RNF-M07-06 | Adecuación funcional — corrección | La búsqueda parcial de placa encuentra el vehículo con independencia de mayúsculas, guiones y espacios | Prueba automatizada con las variantes de escritura |
| RNF-M07-07 | Usabilidad — operabilidad | La consulta por placa y fecha se completa desde la pantalla inicial, sin navegar por menús | Inspección en dispositivo real |
| RNF-M07-08 | Usabilidad — reconocibilidad | El estado anulado de un ingreso se distingue en la lista sin necesidad de abrir el detalle | Inspección en dispositivo real |
| RNF-M07-09 | Fiabilidad — tolerancia a fallos | Si el almacén de imágenes no responde, el detalle se muestra igualmente con sus datos y avisa de la ausencia del respaldo | Prueba automatizada con el almacén desactivado |

## Nota sobre RNF-M07-03

El detalle reúne datos de cuatro módulos y el listado muestra varios ingresos por página. Componer
esa información consultando por cada resultado funciona con pocos registros y se degrada de forma
proporcional al volumen. La verificación cuenta consultas ejecutadas, no mide tiempo: el problema
aparece antes en el número de consultas que en el reloj, y para cuando se nota en el reloj ya está
instalado.

## Nota sobre RNF-M07-04 y RNF-M07-09

La consulta se hace a menudo desde el teléfono, con la conectividad de la planta. Entregar la imagen
en su resolución original para cada fila de la lista haría la consulta inservible justo donde más se
necesita. Y como el respaldo vive en un almacén que puede fallar con independencia de la base, la
ausencia de la imagen no debe impedir ver los datos: se informa y se sigue trabajando.
