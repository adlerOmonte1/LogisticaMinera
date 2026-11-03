# Reglas de negocio — M06 Trazabilidad del proceso

> Ubicación en el código: `apps/trazabilidad/models/` (invariantes de lote, parte y paso) y
> `apps/trazabilidad/services/` (reglas de proceso). Ninguna de estas reglas vive en `views/` ni en
> un componente Angular (D-08).

| Código | Regla | Consecuencia si se viola |
|---|---|---|
| RN-M06-01 | Un ingreso pertenece a un lote como máximo | Las mismas toneladas se contarían en dos cargas distintas |
| RN-M06-02 | Un ingreso solo se asigna a un lote cuya lista de tipos de mineral incluye el suyo, o se unifica desde «Agregar de otro tipo de mineral» con autorización obligatoria, que suma su mineral a la lista y marca el ingreso como «Otro mineral» (DR-27) | La mezcla de minerales en una carga ocurriría sin que nadie la decidiera ni quedara constancia de quién la autorizó |
| RN-M06-03 | Un ingreso anulado no se asigna a ningún lote. Si se anula estando asignado, se retira del lote Abierto; en un lote En recorrido o Cerrado permanece vinculado y deja de contar en sus totales | Un ingreso retirado del histórico seguiría aportando toneladas a una carga |
| RN-M06-04 | Un ingreso se retira de su lote, o se traslada a otro, solo mientras su mineral no haya pasado por zarandeo ni molienda: ninguna parte del lote las registró o, si es un ingreso tardío con secado propio, ninguna de sus partes empezó su ruta. Un lote En recorrido conserva al menos un ingreso (DR-29) | Un zarandeo o una molienda ya registrados dejarían de corresponder al mineral que efectivamente los recorrió, o una carga en marcha quedaría sin ingresos |
| RN-M06-05 | Solo un lote En recorrido registra etapas | Se anotaría el secado de una carga que aún se está reuniendo, o un paso en una carga ya cerrada |
| RN-M06-06 | Las etapas se registran en orden: primero el secado común y después las etapas de la ruta, en el orden de esa ruta | El recorrido describiría una secuencia que la planta no puede haber ejecutado |
| RN-M06-07 | Cada etapa se registra una sola vez por lote o por parte | Habría dos fechas para el mismo hecho y ninguna sería la de referencia |
| RN-M06-08 | La fecha de una etapa no es posterior al momento del registro, ni anterior a la de la etapa previa ni, en la primera etapa, al inicio del recorrido | El recorrido quedaría fechado en el futuro o en un orden imposible |
| RN-M06-09 | Los catálogos de etapas y de rutas son cerrados: cuatro etapas y tres rutas, con su orden fijo | Un recorrido con etapas o rutas distintas dejaría de ser comparable entre lotes |
| RN-M06-10 | Un lote sin ingresos no inicia su recorrido | Existiría una carga vacía recorriendo el proceso |
| RN-M06-11 | El recorrido de un ingreso es el de su lote o el de las partes en que se repartió; un ingreso sin lote no ha recorrido ninguna etapa | Un ingreso recién registrado aparecería como dato incompleto en lugar de como lo que es |
| RN-M06-12 | El registro de una etapa queda atribuido al usuario que lo hizo | No se podría saber quién afirmó que la carga pasó por esa etapa |
| RN-M06-13 | Un ingreso En proceso, pendiente del destare de su vehículo, no se asigna a ningún lote | La carga sumaría un ingreso sin peso neto y su total de toneladas quedaría incompleto sin advertirlo |
| RN-M06-14 | El nombre del lote es único | Dos cargas con el mismo nombre serían indistinguibles en la planta, que las nombra así y no por su código |
| RN-M06-15 | La ruta se decide después del secado; sin ruta no se registra ninguna etapa posterior al secado | Se registrarían etapas sin saber cuántas debe recorrer la carga, y su trazabilidad no tendría con qué compararse |
| RN-M06-16 | Un lote se divide una sola vez, en dos a seis partes con nombre distinto, fracción y ruta; las fracciones suman la unidad y ninguna parte puede haber avanzado por su ruta (DR-18) | Parte del mineral quedaría sin parte asignada o asignada dos veces, y el recorrido de una parte ya avanzada perdería su origen |
| RN-M06-17 | Las toneladas aproximadas de cada parte y el peso de los bigbags son estimaciones: no modifican las toneladas registradas ni entran en ningún total | Una estimación hecha a la vista se presentaría como un dato de balanza |
| RN-M06-18 | El ingreso tardío que llega después del secado del lote tiene su propio secado; en un lote dividido se reparte entre las partes con fracciones que suman la unidad, propuestas por defecto con las del lote (DR-20) | El mineral tardío figuraría como secado sin haberlo sido, o parte de él no seguiría ninguna ruta |
| RN-M06-19 | Los bigbags se asocian solo a un lote o una parte con el ensacado registrado; son datos descriptivos, no inventario (DR-15) | Se registrarían bigbags de mineral que todavía no se ensacó |
| RN-M06-20 | Solo el Administrador cierra un lote, solo cuando todo su mineral está ensacado y con destino obligatorio: venta o traslado (DR-14) | Se cerraría una carga con etapas pendientes o sin saber a dónde fue el mineral |
| RN-M06-21 | Un lote Cerrado no admite ingresos, etapas ni bigbags | El resumen del cierre dejaría de corresponder al lote |
| RN-M06-22 | La trazabilidad de un ingreso se expresa sobre las etapas de su ruta; en un lote dividido, sobre la unión de las rutas de sus partes; sin ruta decidida no se calcula la proporción (DR-16, DR-21) | Una carga que siguió el camino correcto aparecería incompleta, o se calcularía una proporción sobre una ruta inexistente |
| RN-M06-23 | Un tipo de mineral solo se quita de un lote si no tiene ingresos en él y el lote está Abierto | Ingresos del lote quedarían sin el tipo que justificó su asignación |
| RN-M06-24 | Toda cifra del lote —toneladas por tipo de mineral, estimación de las partes y de los bigbags— se calcula sobre los ingresos al consultarse, de modo que una corrección o su reversión en M03 se refleja sin acción adicional (DR-28) | Las cifras del lote quedarían desactualizadas tras corregir un ingreso |

## Nota sobre RN-M06-01 y RN-M06-11

Son las dos reglas que sostienen la indirección del lote. El mineral de varios volquetes se mezcla
en cancha, de modo que preguntar por dónde va «el mineral de este ingreso» solo tiene respuesta a
través de la carga en que se integró. RN-M06-01 impide que esa respuesta sea ambigua —un ingreso en
dos lotes tendría dos recorridos— y RN-M06-11 define qué responder cuando el ingreso todavía no se
integró a ninguna carga, o cuando su carga se dividió: el recorrido de las partes.

## Nota sobre RN-M06-04 y RN-M06-05

Juntas fijan el momento en que la composición de la carga deja de ser revisable. Agregar un ingreso
al lote equivocado es un error posible del usuario, y mientras el mineral solo se ha reunido o
secado todavía puede separarse: por eso el retiro se admite con el lote Abierto y también En
recorrido, hasta el zarandeo o la molienda. Desde que el mineral pasa por una de esas etapas se
transformó junto con el resto de la carga, y retirar el ingreso haría que el recorrido anotado dejara
de describir al mineral que lo hizo. El secado ya registrado no se borra (D-07): describe lo que
ocurrió con la carga, y el retiro queda en auditoría. Además del retiro, en un lote En recorrido se
admite sumar ingresos tardíos, que es lo que ocurre en la planta cuando llegan volquetes a una carga
en marcha, y que el sistema registra señalados como tales (DR-19, DR-29).

## Nota sobre RN-M06-09 y RN-M06-15

Las cuatro etapas y las tres rutas provienen del proceso real de la planta y el sistema las trata
como catálogos cerrados, no como listas que el usuario administre. La ruta es una decisión de
planta: después del secado, quien ve el mineral decide si va a zaranda, a molino o a ambos. Si la
planta incorporara una etapa o una ruta nueva, el cambio afectaría a la comparabilidad de los
recorridos anteriores y debe decidirse expresamente, no resolverse dando de alta una fila.

## Nota sobre RN-M06-16 y RN-M06-17

El mineral acumulado no se pesa: se estima a la vista (DR-18). Por eso la división se expresa en
fracciones y no en toneladas, y las toneladas de cada parte solo se calculan para estimar el peso de
sus bigbags. Las únicas toneladas que el sistema trata como dato son las de los ingresos, que salen
de la balanza; todo lo demás se presenta como estimación y no entra en ningún total.

## Nota sobre RN-M06-20

El cierre del lote registra a dónde va el mineral, no la operación que lo lleva allí. Que el destino
sea la venta no convierte al sistema en un registro de ventas: no hay guía, factura, cliente ni
precio, que siguen fuera de alcance (DR-14).
