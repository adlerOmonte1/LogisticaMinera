# Requerimientos no funcionales — M06 Trazabilidad del proceso

| Código | Característica ISO/IEC 25010:2023 | Requerimiento | Verificación |
|---|---|---|---|
| RNF-M06-01 | Eficiencia de desempeño — comportamiento temporal | La consulta de trazabilidad de un ingreso responde en menos de 2 segundos con 5000 ingresos y 300 lotes en base | Prueba automatizada con datos sintéticos |
| RNF-M06-02 | Eficiencia de desempeño — comportamiento temporal | El detalle de un lote con 40 ingresos se compone en una sola consulta agregada, sin recorrer los ingresos uno a uno | Inspección del número de consultas ejecutadas |
| RNF-M06-03 | Adecuación funcional — corrección | El total de toneladas de un lote coincide con la suma de los pesos netos de sus ingresos no anulados | Consulta de verificación sobre la base |
| RNF-M06-04 | Fiabilidad — tolerancia a fallos | El registro de una etapa y su evento de auditoría se aplican como una sola operación | Prueba automatizada que fuerza el fallo entre ambos |
| RNF-M06-05 | Seguridad — no repudio | El usuario y el momento del registro de cada etapa no son modificables una vez guardados | Prueba automatizada que intenta alterarlos |
| RNF-M06-06 | Usabilidad — operabilidad | El registro del paso por una etapa se completa desde un teléfono en menos de tres toques desde el detalle del lote | Inspección en dispositivo real |
| RNF-M06-07 | Usabilidad — protección contra errores del usuario | La interfaz solo ofrece la etapa que corresponde registrar; las posteriores no se muestran como disponibles | Inspección en dispositivo real |
| RNF-M06-08 | Usabilidad — reconocibilidad | El recorrido se presenta como una secuencia visible de las cuatro etapas, distinguiendo las completadas de las pendientes | Inspección en dispositivo real |

## Nota sobre RNF-M06-02

El detalle de un lote muestra su composición y el total de toneladas. Componerlo recorriendo los
ingresos uno a uno funciona con lotes pequeños y se degrada en cuanto crecen, justo cuando la
consulta se vuelve más útil. La verificación cuenta consultas ejecutadas, no tiempo: es la única
forma de detectar el problema antes de que el volumen lo haga visible.

## Nota sobre RNF-M06-07

Es la contrapartida en la interfaz de la regla de orden del proceso. El servidor rechaza una etapa
fuera de secuencia, pero ofrecerla y luego rechazarla convierte una regla del dominio en un error
del usuario. Mostrar solo la etapa que corresponde hace que la restricción se note como una guía y
no como un obstáculo.
