# Reglas de negocio — M03 Registro de ingresos

> Ubicación en el código: `apps/ingresos/models.py` (invariantes de la entidad) y `apps/ingresos/services.py` (reglas de proceso). Ninguna de estas reglas vive en `views.py` ni en un componente Angular.

| Código | Regla | Consecuencia si se viola |
|---|---|---|
| RN-M03-01 | La hora de pesaje la ingresa el usuario; la hora de registro la asigna el servidor. Son campos distintos y la segunda no es editable | El indicador I1 desaparece o se vuelve falsificable |
| RN-M03-02 | La fecha y hora de pesaje no pueden ser posteriores a la hora del servidor | Se registrarían pesajes futuros y la latencia sería negativa |
| RN-M03-03 | La tara debe ser estrictamente menor que el peso bruto | El peso neto sería cero o negativo |
| RN-M03-04 | El peso neto es siempre el resultado de bruto menos tara; nunca se acepta como dato de entrada | Los registros dejarían de ser comparables y el stock sería inconsistente |
| RN-M03-05 | El número de ticket de balanza es único entre los ingresos no anulados | Se contarían dos veces las mismas toneladas |
| RN-M03-06 | El correlativo es único, lo asigna el servidor y nunca cambia | Dos ingresos serían indistinguibles como unidad de análisis |
| RN-M03-07 | Todo ingreso referencia un vehículo y un producto vigentes al momento del registro | La cobertura por titularidad quedaría sin clasificar |
| RN-M03-08 | Todo ingreso genera exactamente un movimiento de stock de entrada | El stock calculado dejaría de coincidir con los ingresos |
| RN-M03-09 | Un ingreso no se elimina; se anula con motivo obligatorio y responsable identificado | Se podría depurar el histórico y falsear la cobertura del postest |
| RN-M03-10 | Un ingreso anulado no se puede editar | Se alteraría un registro ya invalidado, generando ambigüedad |
| RN-M03-11 | La anulación revierte el movimiento de stock asociado en la misma transacción | El stock quedaría inflado con toneladas de un ingreso invalidado |
| RN-M03-12 | El usuario que registra un ingreso queda asociado de forma permanente al registro | Se perdería la atribución de responsabilidad |

## Nota sobre RN-M03-05

La unicidad del ticket se evalúa **entre los ingresos no anulados**. Si un ingreso se anuló por error de transcripción del número de ticket, ese número debe poder reutilizarse en el registro correcto. Restringir la unicidad a todos los registros, incluidos los anulados, bloquearía la corrección legítima.

## Nota sobre RN-M03-01 y la validez de la tesis

Esta regla no es una preferencia técnica. Es la condición que hace medible la variable dependiente. Si durante la implementación se colapsan ambos campos "para simplificar el formulario", el indicador I1 deja de existir y la dimensión D1 se queda sin medición. Está registrada como decisión D-01 en `../../00-arquitectura/decisiones_diseno.md`.
