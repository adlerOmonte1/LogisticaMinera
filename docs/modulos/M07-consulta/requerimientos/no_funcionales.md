# Requerimientos no funcionales — M07 Consulta de ingresos y respaldo

| Código | Característica ISO/IEC 25010:2023 | Requerimiento | Verificación |
|---|---|---|---|
| RNF-M07-01 | Eficiencia de desempeño — comportamiento temporal | La búsqueda por placa y fecha devuelve resultados en menos de 2 segundos con 5000 ingresos en base | Prueba automatizada con datos sintéticos |
| RNF-M07-02 | Eficiencia de desempeño — comportamiento temporal | El detalle completo de un ingreso, con todos sus bloques, se compone en menos de 2 segundos | Prueba automatizada con datos sintéticos |
| RNF-M07-03 | Eficiencia de desempeño — utilización de recursos | El listado compone cada página con un número fijo de consultas, independiente del número de resultados | Inspección del número de consultas ejecutadas |
| RNF-M07-04 | Eficiencia de desempeño — comportamiento temporal | La imagen del ticket se entrega en una versión reducida para la lista y en su resolución original solo al ampliarla | Inspección en dispositivo real sobre red móvil |
| RNF-M07-05 | Seguridad — confidencialidad | La imagen no es accesible sin sesión válida ni desde una ruta adivinable | Intento de acceso sin sesión y con identificador alterado |
| RNF-M07-06 | Adecuación funcional — corrección | La búsqueda parcial de placa encuentra el vehículo con independencia de mayúsculas, guiones y espacios | Prueba automatizada con las variantes de escritura |
| RNF-M07-07 | Capacidad de interacción — operabilidad | La consulta por placa y fecha se completa desde la pantalla inicial, sin navegar por menús | Inspección en dispositivo real |
| RNF-M07-08 | Capacidad de interacción — reconocibilidad de la adecuación | El estado anulado, el estado En proceso y la falta de respaldo fotográfico se distinguen en la lista sin necesidad de abrir el detalle | Inspección en dispositivo real |
| RNF-M07-09 | Fiabilidad — tolerancia a fallos | Si el almacén de imágenes no responde, el detalle se muestra igualmente con sus datos y avisa de la ausencia del respaldo | Prueba automatizada con el almacén desactivado |
| RNF-M07-10 | Eficiencia de desempeño — utilización de recursos | El calendario de un mes se calcula en una sola consulta agregada por día, sin recorrer los ingresos uno a uno | Inspección del número de consultas ejecutadas |
| RNF-M07-11 | Capacidad de interacción — reconocibilidad de la adecuación | La intensidad del color de cada día del calendario no es la única señal: el número de ingresos y las toneladas se leen como texto, y las marcas de En proceso y anulados tienen leyenda | Inspección en dispositivo real |
| RNF-M07-12 | Adecuación funcional — corrección | Las toneladas de un mes en el calendario coinciden exactamente con el consolidado de M08 para ese mes | Prueba automatizada sobre el mismo conjunto de datos |
| RNF-M07-13 | Eficiencia de desempeño — comportamiento temporal | La pantalla de inicio, con el resumen y los avisos, responde en menos de 2 segundos con 5000 ingresos en base, con un número fijo de consultas agregadas | Prueba automatizada con datos sintéticos e inspección del número de consultas |
| RNF-M07-14 | Eficiencia de desempeño — comportamiento temporal | La exportación del listado de un mes con 1000 ingresos se genera en menos de 5 segundos | Prueba automatizada con datos sintéticos |
| RNF-M07-15 | Compatibilidad — interoperabilidad | El archivo CSV se abre en una hoja de cálculo con la configuración regional de la planta sin perder tildes ni partir columnas | Inspección del archivo abierto en la hoja de cálculo de la empresa |
| RNF-M07-16 | Capacidad de interacción — operabilidad | Cada aviso lleva en un solo paso a la pantalla donde se resuelve | Inspección en dispositivo real por rol |

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
