# Reglas de negocio — M06 Trazabilidad del proceso

> Ubicación en el código: `apps/trazabilidad/models/` (invariantes de lote y paso) y
> `apps/trazabilidad/services/` (reglas de proceso). Ninguna de estas reglas vive en `views/` ni en
> un componente Angular (D-08).

| Código | Regla | Consecuencia si se viola |
|---|---|---|
| RN-M06-01 | Un ingreso pertenece a un lote como máximo | Las mismas toneladas se contarían en dos cargas distintas |
| RN-M06-02 | Todos los ingresos de un lote comparten el tipo de mineral del lote | Una carga mezclaría minerales que se procesan distinto, y el recorrido por etapas no describiría a todos sus ingresos |
| RN-M06-03 | Un ingreso anulado no se asigna a ningún lote, y si se anula estando asignado deja de contar en los totales del lote | Un ingreso retirado del histórico seguiría aportando toneladas a una carga |
| RN-M06-04 | La composición de un lote cerrado no se modifica | El recorrido ya registrado dejaría de corresponder al mineral que efectivamente lo hizo |
| RN-M06-05 | Solo un lote cerrado registra etapas | Se anotaría el secado de una carga que aún puede recibir mineral sin secar |
| RN-M06-06 | Las etapas se registran en el orden secado, zarandeo, molienda, ensacado | El recorrido describiría una secuencia que la planta no puede haber ejecutado |
| RN-M06-07 | Cada etapa se registra una sola vez por lote | Habría dos fechas para el mismo hecho y ninguna sería la de referencia |
| RN-M06-08 | La fecha de una etapa no es posterior al momento del registro ni anterior a la de la etapa previa | El recorrido quedaría fechado en el futuro o en un orden imposible |
| RN-M06-09 | El catálogo de etapas es cerrado: cuatro, con su orden fijo | Un recorrido con etapas distintas dejaría de ser comparable entre lotes |
| RN-M06-10 | Un lote sin ingresos no se cierra | Existiría una carga vacía recorriendo el proceso |
| RN-M06-11 | El recorrido de un ingreso es el de su lote; un ingreso sin lote ha recorrido cero etapas | Un ingreso recién registrado aparecería como dato incompleto en lugar de como lo que es |
| RN-M06-12 | El registro de una etapa queda atribuido al usuario que lo hizo | No se podría saber quién afirmó que la carga pasó por esa etapa |

## Nota sobre RN-M06-01 y RN-M06-11

Son las dos reglas que sostienen la indirección del lote. El mineral de varios volquetes se mezcla
en cancha, de modo que preguntar por dónde va «el mineral de este ingreso» solo tiene respuesta a
través de la carga en que se integró. RN-M06-01 impide que esa respuesta sea ambigua —un ingreso en
dos lotes tendría dos recorridos— y RN-M06-11 define qué responder cuando el ingreso todavía no se
integró a ninguna carga: cero etapas, que es un hecho, no una falta de dato.

## Nota sobre RN-M06-04 y RN-M06-05

Juntas fijan el momento en que la composición de la carga deja de ser revisable. Mientras el lote
está abierto, agrupar es una decisión de trabajo que puede corregirse. Al cerrarlo, la composición
se vuelve parte del hecho registrado: si después pudieran entrar o salir ingresos, el recorrido ya
anotado dejaría de describir al mineral que efectivamente lo hizo.

## Nota sobre RN-M06-09

Las cuatro etapas provienen del proceso real de la planta y el sistema las trata como catálogo
cerrado, no como una lista que el usuario administre. Si la planta incorporara una etapa nueva, el
cambio afectaría a la comparabilidad de los recorridos anteriores y debe decidirse expresamente, no
resolverse dando de alta una fila.
