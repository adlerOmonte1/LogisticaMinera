# Requerimientos de usuario — M04 Reconocimiento automático del ticket

| Código | Requerimiento |
|---|---|
| RU-M04-01 | Quiero que el sistema saque solo los datos de la foto del ticket, para no escribirlos uno por uno |
| RU-M04-02 | Quiero que me avise cuáles datos leyó con dudas, para revisar esos y no todos |
| RU-M04-03 | Si no pudo leer un dato, prefiero el casillero vacío antes que un número inventado |
| RU-M04-04 | Si el sistema no logra leer el ticket, quiero poder escribir los datos a mano y seguir trabajando |
| RU-M04-05 | Quiero poder ver después qué leyó el sistema y qué tuvimos que corregir |

## Contexto del diagnóstico

| Requerimiento | Situación que resuelve |
|---|---|
| RU-M04-01 | Los seis datos del ticket se copian a mano, primero al papel en planta y después al computador en la oficina. Cada copia añade una oportunidad de equivocarse |
| RU-M04-02 | Revisar los seis campos con el mismo cuidado toma tanto tiempo como escribirlos; sin una señal de qué revisar, el usuario termina revisando nada |
| RU-M04-03, RU-M04-04 | El ticket se imprime en papel térmico y se maneja con las manos sucias: hay tickets que sencillamente no se dejan leer, y el trabajo no puede detenerse por eso |
| RU-M04-05 | Hoy no hay forma de saber si la transcripción es fiel, porque no queda registro de qué decía el original |
