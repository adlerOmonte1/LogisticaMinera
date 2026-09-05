# Requerimientos de usuario — M07 Captura sin conexión

| Código | Requerimiento |
|---|---|
| RU-M07-01 | En la planta la señal se cae seguido; necesito registrar igual, no esperar |
| RU-M07-02 | Si guardo algo sin señal, no quiero perderlo cuando cierre la aplicación |
| RU-M07-03 | Quiero que se envíe solo cuando vuelva la señal, sin que yo tenga que acordarme |
| RU-M07-04 | Si algo no se pudo enviar, quiero saberlo y poder arreglarlo |
| RU-M07-05 | Necesito ver cuáles están pendientes de enviar |

## Contexto y por qué este módulo es el diferenciador

El diagnóstico documentó que la conectividad en planta es intermitente. El proceso actual funciona así: el supervisor recibe el volquete, toma el ticket, y el dato queda en papel hasta que alguien lo transcribe en la oficina —horas o días después—. Esa demora es el indicador I1.

Un sistema web que exija conexión permanente **no resuelve el problema**: el supervisor seguiría anotando en papel durante las horas sin señal, y la latencia se mantendría. Peor aún, la cobertura (I2) se degradaría precisamente en los turnos de mayor actividad.

Por eso M07 no es una funcionalidad opcional. Es la condición para que los indicadores I1 e I2 mejoren en las condiciones reales de operación.
