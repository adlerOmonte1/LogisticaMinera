# Requerimientos no funcionales — M06 Trazabilidad del proceso

| Código | Característica ISO/IEC 25010:2023 | Requerimiento | Verificación |
|---|---|---|---|
| RNF-M06-01 | Eficiencia de desempeño — comportamiento temporal | La consulta de trazabilidad de un ingreso responde en menos de 2 segundos con 5000 ingresos y 300 lotes en base | Prueba automatizada con datos sintéticos |
| RNF-M06-02 | Eficiencia de desempeño — comportamiento temporal | El detalle de un lote con 40 ingresos se compone en una sola consulta agregada, sin recorrer los ingresos uno a uno | Inspección del número de consultas ejecutadas |
| RNF-M06-03 | Adecuación funcional — corrección | El total de toneladas de un lote coincide con la suma de los pesos netos de sus ingresos no anulados, incluidos los tardíos | Consulta de verificación sobre la base |
| RNF-M06-04 | Fiabilidad — tolerancia a fallos | El registro de una etapa, de una división o de un cierre y su evento de auditoría se aplican como una sola operación | Prueba automatizada que fuerza el fallo entre ambos |
| RNF-M06-05 | Seguridad — no repudio | El usuario y el momento del registro de cada etapa y del cierre no son modificables una vez guardados | Prueba automatizada que intenta alterarlos |
| RNF-M06-06 | Capacidad de interacción — operabilidad | El registro del paso por una etapa se completa desde un teléfono en menos de tres toques desde el detalle del lote | Inspección en dispositivo real |
| RNF-M06-07 | Capacidad de interacción — protección contra errores del usuario | La interfaz solo ofrece la etapa que corresponde registrar según la ruta, y la elección de la ruta justo después del secado; las etapas posteriores no se muestran como disponibles | Inspección en dispositivo real |
| RNF-M06-08 | Capacidad de interacción — reconocibilidad de la adecuación | El recorrido se presenta como una secuencia visible de las etapas de la ruta, por parte cuando el lote está dividido, distinguiendo las completadas de las pendientes | Inspección en dispositivo real |
| RNF-M06-09 | Capacidad de interacción — reconocibilidad de la adecuación | Las toneladas aproximadas de cada parte, el peso de los bigbags y la diferencia frente a lo registrado se muestran señalados como estimación, distinguibles de las toneladas registradas | Inspección en dispositivo real |
| RNF-M06-10 | Capacidad de interacción — protección contra errores del usuario | Al dividir un lote, la interfaz muestra la suma de las fracciones y cuánto falta o sobra para la unidad antes de confirmar | Inspección en dispositivo real |
| RNF-M06-11 | Adecuación funcional — corrección | La suma de las fracciones de un lote se comprueba de forma exacta, sin errores de redondeo con fracciones como 1/3 | Prueba automatizada con divisiones en tercios y sextos |

## Nota sobre RNF-M06-02

El detalle de un lote muestra su composición y el total de toneladas. Componerlo recorriendo los
ingresos uno a uno funciona con lotes pequeños y se degrada en cuanto crecen, justo cuando la
consulta se vuelve más útil. La verificación cuenta consultas ejecutadas, no tiempo: es la única
forma de detectar el problema antes de que el volumen lo haga visible.

## Nota sobre RNF-M06-07

Es la contrapartida en la interfaz de la regla de orden del proceso. El servidor rechaza una etapa
fuera de la ruta, pero ofrecerla y luego rechazarla convierte una regla del dominio en un error del
usuario. Mostrar solo la etapa que corresponde hace que la restricción se note como una guía y no
como un obstáculo.

## Nota sobre RNF-M06-09 y RNF-M06-11

La división del lote trabaja con estimaciones, porque el mineral en cancha no se pesa (DR-18). Esas
estimaciones no deben confundirse con las toneladas registradas, que salen de la balanza, ni
contaminar ningún total. RNF-M06-11 cubre el caso contrario: aunque las toneladas por parte sean
aproximadas, la regla de que las fracciones sumen la unidad es exacta, y tres tercios deben sumar
uno sin que el redondeo decimal rechace una división correcta.
