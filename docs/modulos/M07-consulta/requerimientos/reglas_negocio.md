# Reglas de negocio — M07 Consulta de ingresos y respaldo

> Ubicación en el código: `apps/consulta/repositories/` (las consultas) y
> `apps/consulta/services/` (la composición del detalle). El módulo no tiene `models/` ni
> `migrations/`: no aporta ninguna entidad al modelo de datos (D-10).

M07 no escribe, de modo que sus reglas no son invariantes de escritura sino **invariantes de
presentación**: garantizan que lo que se muestra no induzca a conclusiones falsas.

| Código | Regla | Consecuencia si se viola |
|---|---|---|
| RN-M07-01 | Los ingresos anulados aparecen en los resultados, señalados y con su motivo | Quien consulta un volquete que sí pasó por la balanza no obtendría nada y concluiría que no se registró |
| RN-M07-02 | Los ingresos anulados no se incluyen en la suma de toneladas del conjunto filtrado | El total mostrado contradiría al de la consolidación para el mismo periodo |
| RN-M07-03 | El detalle presenta la imagen del ticket junto a los datos registrados | La consulta no permitiría contrastar lo registrado con el papel, que es su razón de ser |
| RN-M07-04 | La ausencia del respaldo se informa explícitamente | Un detalle sin imagen parecería un problema de la pantalla y no la falta de un respaldo |
| RN-M07-05 | La búsqueda exige al menos un criterio | Una consulta sin criterios recorrería el histórico completo y se degradaría conforme creciera |
| RN-M07-06 | La imagen solo se sirve a usuarios autenticados con permiso sobre el ingreso | El respaldo quedaría accesible desde una ruta adivinable, sin control de acceso |
| RN-M07-07 | El detalle muestra las tres marcas de tiempo como valores distintos | Presentarlas juntas o resumidas ocultaría cuándo se pesó y cuándo se registró |
| RN-M07-08 | La ausencia de reconocimiento, validaciones o trazabilidad se indica, no se omite | Un bloque ausente se confundiría con un elemento que el sistema no muestra |
| RN-M07-09 | El módulo no modifica ningún dato: todas sus operaciones son de lectura | Una consulta con efectos secundarios alteraría aquello que pretende mostrar |

## Nota sobre RN-M07-01 y RN-M07-02

Parecen contradictorias y no lo son: el ingreso anulado **aparece** pero **no suma**. Son dos
preguntas distintas. «¿Se registró este volquete?» se responde mostrándolo, porque el hecho ocurrió;
«¿cuántas toneladas ingresaron?» se responde sin él, porque el ingreso se retiró del cómputo. Un
sistema que ocultara los anulados respondería mal la primera; uno que los sumara respondería mal la
segunda y además contradiría a la consolidación.

## Nota sobre RN-M07-03

Es la regla que distingue este módulo de un listado más. Recuperar el dato ya lo hace el listado de
M03; lo que M07 aporta es poder **verificar** el dato contra su respaldo. Un detalle que mostrara
solo los números dejaría al módulo sin propósito propio.

## Nota sobre RN-M07-05

Es la única regla del módulo motivada por el rendimiento y no por la corrección. Una búsqueda sin
criterios devuelve el histórico completo: funciona hoy, con pocos registros, y se degrada de forma
continua hasta volverse inútil. Exigir un criterio evita esa degradación desde el principio, y no
supone ningún obstáculo real, porque quien consulta siempre sabe al menos la fecha.
