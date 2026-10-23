# Reglas de negocio — M07 Consulta de ingresos y respaldo

> Ubicación en el código: `apps/consulta/repositories/` (las consultas) y
> `apps/consulta/services/` (la composición del detalle). El módulo no tiene `models/` ni
> `migrations/`: no aporta ninguna entidad al modelo de datos (D-10).

M07 no escribe, de modo que sus reglas no son invariantes de escritura sino **invariantes de
presentación**: garantizan que lo que se muestra no induzca a conclusiones falsas.

| Código | Regla | Consecuencia si se viola |
|---|---|---|
| RN-M07-01 | Los ingresos anulados aparecen en los resultados, señalados y con su motivo | Quien consulta un volquete que sí pasó por la balanza no obtendría nada y concluiría que no se registró |
| RN-M07-02 | Solo los ingresos Registrados se incluyen en la suma de toneladas del conjunto filtrado; los anulados y los En proceso quedan fuera | El total mostrado contradiría al de la consolidación para el mismo periodo, o sumaría ingresos sin peso neto |
| RN-M07-03 | El detalle presenta la imagen del ticket junto a los datos registrados | La consulta no permitiría contrastar lo registrado con el papel, que es su razón de ser |
| RN-M07-04 | La ausencia del respaldo se informa explícitamente, distinguiendo el ingreso registrado sin foto, con su motivo, del respaldo que existe y no puede recuperarse | Un detalle sin imagen parecería un problema de la pantalla y no la falta de un respaldo |
| RN-M07-05 | La búsqueda exige al menos un criterio | Una consulta sin criterios recorrería el histórico completo y se degradaría conforme creciera |
| RN-M07-06 | La imagen solo se sirve a usuarios autenticados con permiso sobre el ingreso | El respaldo quedaría accesible desde una ruta adivinable, sin control de acceso |
| RN-M07-07 | El detalle muestra las tres marcas de tiempo como valores distintos | Presentarlas juntas o resumidas ocultaría cuándo se pesó y cuándo se registró |
| RN-M07-08 | La ausencia de reconocimiento, validaciones o trazabilidad se indica, no se omite | Un bloque ausente se confundiría con un elemento que el sistema no muestra |
| RN-M07-09 | El módulo no modifica ningún dato: todas sus operaciones son de lectura | Una consulta con efectos secundarios alteraría aquello que pretende mostrar |
| RN-M07-10 | Los ingresos En proceso aparecen en los resultados, señalados y con el peso neto indicado como pendiente del destare | Un volquete que ingresó en su primer viaje parecería no registrado, o su peso neto vacío se leería como cero |
| RN-M07-11 | El calendario ubica cada ingreso en el día de su fecha del pesaje, no en el de su registro | El calendario describiría cuándo se trabajó en el sistema y no cuándo llegaron los volquetes |
| RN-M07-12 | El calendario cuenta los ingresos no anulados y suma solo los Registrados, con el mismo criterio que el listado y la consolidación | El mismo mes tendría dos totales distintos según la pantalla que se mire |
| RN-M07-13 | La trazabilidad que muestra la consulta es la de M06, sin recalcularla | La consulta podría contradecir al módulo responsable del recorrido |
| RN-M07-14 | El resumen del día y las toneladas de los últimos siete días cuentan y suman con el criterio del calendario: día de la fecha del pesaje, sin anulados en el conteo y solo Registrados en la suma | La pantalla de inicio daría para un día una cifra distinta de la del calendario y la consolidación |
| RN-M07-15 | Los avisos se calculan al consultarse, no se almacenan, y solo muestran lo que el rol del usuario puede resolver | Un aviso guardado seguiría apareciendo después de resuelto, o el usuario recibiría pendientes que no le corresponde atender |
| RN-M07-16 | La exportación contiene exactamente el conjunto filtrado del listado —todas sus páginas—, con los anulados y los En proceso señalados por su estado | El archivo diría algo distinto de la pantalla de la que salió |
| RN-M07-17 | Solo el Administrativo y el Administrador exportan el listado, y cada exportación queda en auditoría | Los datos saldrían del sistema sin saber quién los sacó ni con qué criterio |

## Nota sobre RN-M07-01 y RN-M07-02

Parecen contradictorias y no lo son: el ingreso anulado **aparece** pero **no suma**. Son dos
preguntas distintas. «¿Se registró este volquete?» se responde mostrándolo, porque el hecho ocurrió;
«¿cuántas toneladas ingresaron?» se responde sin él, porque el ingreso se retiró del cómputo. Un
sistema que ocultara los anulados respondería mal la primera; uno que los sumara respondería mal la
segunda y además contradiría a la consolidación.

El ingreso En proceso sigue la misma lógica (RN-M07-10): aparece porque el volquete ingresó, y no
suma porque su peso neto todavía no existe.

## Nota sobre RN-M07-03

Es la regla que distingue la consulta de un listado más. Recuperar el dato es lo mínimo de cualquier
listado —y en este sistema el listado también es de M07 (D-19)—; lo que la consulta aporta es poder
**verificar** el dato contra su respaldo. Un detalle que mostrara solo los números dejaría a la
consulta sin propósito propio.

## Nota sobre RN-M07-05

Es la única regla del módulo motivada por el rendimiento y no por la corrección. Una búsqueda sin
criterios devuelve el histórico completo: funciona hoy, con pocos registros, y se degrada de forma
continua hasta volverse inútil. Exigir un criterio evita esa degradación desde el principio, y no
supone ningún obstáculo real, porque quien consulta siempre sabe al menos la fecha.

## Nota sobre RN-M07-15

Un aviso no es un mensaje que alguien envía: es una pregunta que el sistema se hace cada vez que el
usuario lo consulta —¿hay ingresos sin destare?, ¿hay un lote con la etapa siguiente pendiente?—. Por
eso no se marca como leído ni se archiva: desaparece cuando deja de ser cierto. Y como cada rol
resuelve cosas distintas, el mismo cálculo se filtra por rol: avisar al Supervisor de un lote listo
para cerrar le señalaría una tarea que no puede hacer.

## Nota sobre RN-M07-16

La exportación es del listado, no del mes: sale con los filtros que el usuario eligió e incluye los
ingresos anulados y En proceso con su estado, igual que la pantalla. Quien necesite el total de
producción del mes por tipo de mineral lo obtiene en la consolidación (M08), que tiene sus propias
reglas de cómputo y su propia exportación.

## Nota sobre RN-M07-11 y RN-M07-12

El calendario responde cuándo llegaron los volquetes, por eso usa la fecha del pesaje. Si usara la
del registro, un ingreso registrado al día siguiente de llegar aparecería en el día equivocado. Y
como el calendario muestra toneladas, debe sumar con el mismo criterio que el listado y la
consolidación: el total de un mes es uno solo, se mire desde donde se mire.

