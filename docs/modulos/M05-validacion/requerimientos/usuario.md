# Requerimientos de usuario — M05 Validación automática de consistencia

| Código | Requerimiento |
|---|---|
| RU-M05-01 | Quiero que el sistema me avise cuando los pesos del ticket no cuadran, antes de guardar |
| RU-M05-02 | Quiero que me diga exactamente qué dato está mal, no un mensaje general de error |
| RU-M05-03 | Si el volquete trae más carga de la que debería, quiero poder registrarlo igual, pero explicando por qué |
| RU-M05-04 | Quiero que me muestre todo lo que está mal de una vez, no de a uno cada vez que intento guardar |
| RU-M05-05 | Quiero que quede anotado qué se revisó y qué explicación se dio, por si después alguien pregunta |

## Contexto del diagnóstico

| Requerimiento | Situación que resuelve |
|---|---|
| RU-M05-01, RU-M05-02 | Un ticket con pesos que no cuadran se detecta mucho después, cuando se pasa al computador en la oficina. Para entonces el volquete ya descargó y se fue, y nadie puede verificar cuál de los tres pesos era el correcto |
| RU-M05-03 | Las sobrecargas ocurren y hoy se registran sin distinguirlas de un error de transcripción: ambas aparecen como un número raro en la planilla |
| RU-M05-04 | Corregir de a un error por intento alarga un trabajo que se hace de pie junto al volquete |
| RU-M05-05 | Cuando un dato llama la atención semanas después, no hay forma de saber si en su momento se revisó y se dio por bueno, o si pasó inadvertido |
