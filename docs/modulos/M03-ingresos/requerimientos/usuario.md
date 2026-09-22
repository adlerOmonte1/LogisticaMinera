# Requerimientos de usuario — M03 Registro de ingresos

| Código | Requerimiento |
|---|---|
| RU-M03-01 | Quiero sacarle una foto al ticket apenas el volquete baja de la balanza, ahí mismo en la planta, y que el sistema lea los datos |
| RU-M03-02 | Si el sistema lee mal un número, quiero corregirlo ahí mismo, antes de que quede guardado |
| RU-M03-03 | Quiero que me avise cuando un dato del ticket no cuadra, para no darme cuenta recién en la oficina |
| RU-M03-04 | No quiero escribir a mano si el volquete es propio o alquilado: eso ya está en la lista de vehículos |
| RU-M03-05 | Quiero elegir de una lista qué tipo de mineral trajo el volquete |
| RU-M03-06 | Quiero que la foto del ticket quede guardada con el ingreso, para poder mostrarla cuando alguien pregunte |
| RU-M03-07 | Si me equivoqué en un dato, quiero arreglarlo sin tener que borrar el registro y hacerlo de nuevo |
| RU-M03-08 | Si un ingreso no debió registrarse, quiero sacarlo de las cuentas pero que no desaparezca |

## Contexto del diagnóstico

| Requerimiento | Situación que resuelve |
|---|---|
| RU-M03-01, RU-M03-02 | Hoy el dato del ticket se anota en papel en la planta y se transcribe después en la oficina. Entre el pesaje y el registro pasan horas o días, y la transcripción introduce errores que ya nadie puede contrastar contra el papel original |
| RU-M03-03 | Un ticket con pesos que no cuadran se detecta, cuando se detecta, mucho después del pesaje, cuando el volquete ya se fue y no hay forma de verificar |
| RU-M03-04, RU-M03-05 | La clasificación del vehículo y del mineral se anota de memoria y con distintas palabras según quién registre, lo que impide agrupar después |
| RU-M03-06 | El respaldo en papel se archiva en desorden y recuperarlo para verificar un ingreso concreto puede tomar mucho tiempo o resultar imposible |
| RU-M03-07, RU-M03-08 | Hoy corregir significa tachar el papel, y no queda constancia de qué decía antes ni de quién lo cambió |
