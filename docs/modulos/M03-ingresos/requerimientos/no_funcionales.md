# Requerimientos no funcionales — M03 Registro de ingresos

| Código | Característica ISO/IEC 25010:2023 | Requerimiento | Verificación |
|---|---|---|---|
| RNF-M03-01 | Eficiencia de desempeño — comportamiento temporal | El alta de un ingreso responde en menos de 2 segundos con 20 usuarios concurrentes | Prueba de carga JMeter (semana 8) |
| RNF-M03-02 | Eficiencia de desempeño — comportamiento temporal | El listado filtrado de un mes devuelve resultados en menos de 3 segundos con 1000 ingresos en base | Prueba de carga con datos sintéticos |
| RNF-M03-03 | Usabilidad — operabilidad | El formulario de registro se completa en menos de 90 segundos por un usuario capacitado, medido desde que abre la pantalla | Observación cronometrada en campo |
| RNF-M03-04 | Usabilidad — protección contra errores del usuario | Los campos numéricos abren teclado numérico en dispositivos móviles | Inspección en dispositivo real |
| RNF-M03-05 | Usabilidad — operabilidad | El formulario es completamente operable en pantalla de 5 pulgadas sin desplazamiento horizontal | Inspección en dispositivo real |
| RNF-M03-06 | Fiabilidad — tolerancia a fallos | La pérdida de conexión durante el llenado del formulario no borra los datos ingresados | Prueba manual: activar modo avión a media captura |
| RNF-M03-07 | Adecuación funcional — corrección | El peso neto calculado por el servidor coincide con la diferencia bruto − tara en el 100 % de los registros | Consulta de verificación sobre la base |
| RNF-M03-08 | Seguridad — no repudio | Todo ingreso queda asociado de forma inmutable al usuario que lo registró | Inspección: campo no editable, evento en auditoría |

## Relación con los objetivos de calidad

RNF-M03-01, RNF-M03-02 y RNF-M03-03 constituyen la evidencia de la dimensión *eficiencia de desempeño* de la solución implantada bajo ISO/IEC 25010:2023. El protocolo de medición está en `../../03-pruebas/plan_de_pruebas.md`.

RNF-M03-03 merece atención especial: el tiempo de llenado del formulario es un componente del indicador I1. Si el formulario es lento de completar, la latencia no baja lo suficiente aunque el registro sea inmediato. Un formulario de treinta campos anularía el beneficio del sistema.

## Relación con el indicador I1

RNF-M03-06 es más que una comodidad. Si el formulario pierde los datos al caerse la conexión, el supervisor abandona el registro en campo y vuelve al método antiguo: anotar en papel y transcribir después. Eso devolvería la latencia a los valores de la línea base.
