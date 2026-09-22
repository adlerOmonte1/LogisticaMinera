# Reglas de negocio — M08 Consolidación de la producción

> Ubicación en el código: `apps/consolidacion/repositories/` (el cálculo agregado) y
> `apps/consolidacion/exportadores/` (un exportador por formato). El módulo no tiene `models/` ni
> `migrations/`: no aporta ninguna entidad al modelo de datos (D-10).

| Código | Regla | Consecuencia si se viola |
|---|---|---|
| RN-M08-01 | El total de un periodo excluye los ingresos anulados | El total declarado incluiría toneladas que se retiraron del histórico |
| RN-M08-02 | El total se calcula a demanda, sin acumulado almacenado | Un acumulado guardado se desincronizaría en cuanto un ingreso se corrigiera o anulara después de calculado, y el error no sería visible hasta compararlo |
| RN-M08-03 | Un tipo de mineral sin ingresos en el periodo no aparece en el resultado | Un total en cero sugeriría que hubo actividad sin producción, cuando en realidad no hubo actividad |
| RN-M08-04 | No se consolida un periodo posterior al mes en curso | El total describiría producción que todavía no puede haber ocurrido |
| RN-M08-05 | El total exportado es el mismo que se muestra en pantalla para el mismo periodo | Dos cifras distintas para el mismo mes serían indefendibles ante cualquiera que las contraste |
| RN-M08-06 | Añadir un formato de exportación no modifica el cálculo del total ni los formatos existentes | Cada formato nuevo arriesgaría introducir una discrepancia en el número que reporta |

## Nota sobre RN-M08-02

Es la decisión que distingue este módulo de un cierre contable. Un cierre fija un número en una
fecha y ya no cambia; este sistema, en cambio, permite corregir un ingreso después de registrado
(HU-M03-02), y esa corrección debe reflejarse la próxima vez que alguien pida el total del mes. Si
el total se guardara al calcularse, cada corrección posterior lo dejaría desactualizado sin que
nada lo advirtiera: el número parecería correcto y no lo sería.

## Nota sobre RN-M08-05

Existe porque hay dos caminos para llegar al mismo número —la consulta en pantalla de HU-M08-01 y la
exportación de HU-M08-02— y ambos deben usar exactamente el mismo cálculo. Implementarlos por
separado, aunque sea con la misma lógica escrita dos veces, es la forma más probable de que
terminen divergiendo con el tiempo.
