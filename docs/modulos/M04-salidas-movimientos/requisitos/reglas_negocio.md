# Reglas de negocio — M04 Salidas y movimientos

> Ubicación en el código: `apps/salidas/models/` y `apps/salidas/services/`.

| Código | Regla | Consecuencia si se viola |
|---|---|---|
| RN-M04-01 | La cantidad de una salida es estrictamente mayor que cero | Un movimiento nulo o negativo invertiría el sentido del asiento |
| RN-M04-02 | El tipo de movimiento pertenece al dominio cerrado {VENTA, TRASLADO_INTERNO, MERMA} | El indicador I4 quedaría sin explicación por categoría |
| RN-M04-03 | Una salida de tipo VENTA debe tener cliente asociado | No se podría rastrear el destino del producto |
| RN-M04-04 | Una salida de tipo MERMA debe tener motivo registrado | La desviación de stock quedaría sin justificación auditable |
| RN-M04-05 | Toda salida genera exactamente un movimiento de stock de tipo SALIDA | El stock dejaría de reflejar los despachos |
| RN-M04-06 | El stock insuficiente genera advertencia pero no impide el registro | Se forzaría al usuario a falsear ingresos para poder despachar |
| RN-M04-07 | Una salida no se elimina; se anula con motivo obligatorio | Se podría depurar el histórico de despachos |
| RN-M04-08 | La anulación de una salida revierte su movimiento de stock en la misma transacción | El stock quedaría subestimado |
| RN-M04-09 | Una salida anulada no se puede editar | Se alteraría un registro ya invalidado |
| RN-M04-10 | El correlativo de salidas es una serie independiente de la de ingresos | Los correlativos se solaparían y la trazabilidad documental se rompería |

## Nota sobre RN-M04-06

Esta regla merece justificación explícita porque contradice la intuición habitual en sistemas de inventario. El stock del sistema es una **estimación** construida a partir de los ingresos y salidas registrados; el stock físico real difiere por humedad, precisión de la balanza e ingresos aún no capturados. Impedir una salida real porque la estimación no la respalda invitaría a registrar ingresos ficticios, contaminando la propia variable que la tesis mide.

## Pendiente que bloquea este módulo

El **criterio de estimación de merma por humedad** sigue sin definirse. Sin él, el tipo MERMA no puede aplicarse de forma consistente y el indicador I4 no tiene marco de interpretación. Registrado en `../../00-arquitectura/decisiones_diseno.md`, sección de pendientes. Fecha límite: antes de la semana 5.
