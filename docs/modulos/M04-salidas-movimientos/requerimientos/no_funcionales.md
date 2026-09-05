# Requerimientos no funcionales — M04 Salidas y movimientos

| Código | Característica ISO/IEC 25010:2023 | Requerimiento | Verificación |
|---|---|---|---|
| RNF-M04-01 | Eficiencia de desempeño | El registro de una salida responde en menos de 2 segundos, incluida la consulta previa de saldo | Prueba de carga JMeter |
| RNF-M04-02 | Adecuación funcional — corrección | La reversión de una salida anulada restituye exactamente la cantidad restada, sin desviación decimal | Prueba automatizada: saldo antes = saldo después de anular |
| RNF-M04-03 | Fiabilidad — tolerancia a fallos | Si falla la generación del movimiento de stock, la salida no queda persistida | Prueba de transaccionalidad con fallo inducido |
| RNF-M04-04 | Usabilidad — protección contra errores | La advertencia de stock insuficiente exige confirmación explícita, no se descarta con un clic accidental | Inspección funcional |
| RNF-M04-05 | Adecuación funcional — pertinencia | El sistema no solicita ni almacena precios, montos ni datos de facturación | Inspección del modelo de datos |

**RNF-M04-05 es una restricción de alcance con valor defensivo.** Está declarada explícitamente para poder responder en sustentación por qué el sistema no factura: no es una omisión, es una decisión documentada (ver ARQ-01 §5).
