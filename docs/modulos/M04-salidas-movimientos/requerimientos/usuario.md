# Requerimientos de usuario — M04 Salidas y movimientos

| Código | Requerimiento |
|---|---|
| RU-M04-01 | Quiero registrar lo que sale hacia el cliente, para saber cuánto queda realmente |
| RU-M04-02 | No todo lo que sale es venta: a veces se traslada dentro de la planta o se pierde material |
| RU-M04-03 | Quiero saber cuándo la cantidad que estoy sacando es mayor que lo que tengo registrado |
| RU-M04-04 | Si registro una salida equivocada, quiero anularla y que el stock vuelva a como estaba |

## Contexto

RU-M04-03 es una advertencia, no un bloqueo. El stock del sistema puede diferir del stock físico real por causas legítimas —humedad, mediciones aproximadas, ingresos aún no capturados—. Bloquear la salida obligaría al usuario a inventar un ingreso ficticio para poder registrar una venta real. La advertencia informa; el usuario decide.

Esa diferencia entre stock declarado y stock estimado es precisamente lo que mide el indicador I4.
