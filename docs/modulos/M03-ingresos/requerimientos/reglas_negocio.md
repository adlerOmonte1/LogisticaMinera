# Reglas de negocio — M03 Registro de ingresos

> Ubicación en el código: `apps/ingresos/models/` (invariantes de la entidad) y
> `apps/ingresos/services/` (reglas de proceso). Ninguna de estas reglas vive en `views/` ni en un
> componente Angular (D-08).

| Código | Regla | Consecuencia si se viola |
|---|---|---|
| RN-M03-01 | Un ingreso no se persiste sin la imagen del ticket | El registro quedaría sin respaldo verificable y sería imposible comprobar lo que se consignó |
| RN-M03-02 | Ningún valor propuesto por el reconocimiento se persiste sin confirmación del usuario | Un error de lectura se convertiría en dato oficial sin que nadie lo revisara |
| RN-M03-03 | Por cada campo reconocido se conservan el valor propuesto y el confirmado como datos separados | Se perdería la distinción entre lo que leyó el motor y lo que corrigió la persona, y nadie podría auditar las correcciones |
| RN-M03-04 | El peso neto lo calcula el servidor como peso bruto menos la tara del vehículo, y el ingreso conserva la tara que se le aplicó | Con un neto digitado, dos ingresos del mismo vehículo podrían aplicar taras distintas; con la tara consultada al vuelo, un cambio posterior reescribiría el histórico |
| RN-M03-05 | Un ingreso no se confirma con una regla de validación bloqueante incumplida ni con una advertencia sin justificar | Se registrarían toneladas que el ticket no respalda |
| RN-M03-06 | `hora_inicio_registro` y `hora_fin_registro` las asigna el servidor y ningún rol las modifica | Las marcas de tiempo serían falsificables y el registro dejaría de describir cómo se trabajó |
| RN-M03-07 | La fecha y hora del pesaje no pueden ser posteriores al instante del registro | El ingreso quedaría fechado en el futuro y el orden de los registros dejaría de ser reconstruible |
| RN-M03-08 | El vehículo debe existir y estar vigente en el catálogo al confirmar; si la placa no existe, se da de alta en la misma pantalla antes de confirmar | El tipo de vehículo quedaría sin determinar y no habría tara ni capacidad con que calcular y contrastar el peso |
| RN-M03-09 | El código lo asigna el servidor dentro de la transacción, mediante bloqueo sobre el contador | Dos ingresos simultáneos recibirían el mismo código y dejarían de ser identificables |
| RN-M03-10 | El número de ticket, cuando se consigna, es único entre los ingresos no anulados | El mismo pesaje podría registrarse dos veces y las toneladas se contarían por duplicado |
| RN-M03-11 | Toda corrección exige un motivo y vuelve a someterse a las reglas de validación | Un ingreso corregido podría terminar incumpliendo condiciones que uno nuevo no puede incumplir |
| RN-M03-12 | La corrección conserva los valores anteriores en el registro de auditoría | No se podría reconstruir qué decía el ingreso antes del cambio ni quién lo modificó |
| RN-M03-13 | Un ingreso anulado no se corrige ni se vuelve a anular | Se acumularían anulaciones sobre el mismo registro y el motivo vigente dejaría de ser único |
| RN-M03-14 | El sistema no ofrece ninguna operación de borrado de ingresos: solo anulación | Un registro podría desaparecer del histórico sin dejar rastro |
| RN-M03-15 | El registro, la corrección, la anulación y el destare ocurren dentro de una sola transacción, junto con su evento de auditoría | Podría quedar un ingreso sin evento, o un evento sin ingreso, y el historial dejaría de ser fiable |
| RN-M03-16 | La hora del pesaje es obligatoria y la digita el usuario, porque el ticket no la imprime | La primera marca de tiempo quedaría incompleta y el ingreso no podría ubicarse en el día |
| RN-M03-17 | Si el vehículo no tiene tara, el ingreso se confirma En proceso, sin peso neto | Se registraría un peso neto inventado o nulo como si fuera definitivo |
| RN-M03-18 | Un ingreso En proceso no cuenta en ningún total ni se asigna a un lote de proceso | Los totales sumarían toneladas brutas mezcladas con netas |
| RN-M03-19 | La tara de un vehículo se registra una sola vez, en el destare, digitada por el usuario y no reconocida de la imagen | Una anotación manuscrita mal leída se convertiría en la tara de todos los viajes futuros del vehículo |
| RN-M03-20 | La tara del destare es menor que el peso bruto del ingreso sobre el que se registra | El peso neto sería cero o negativo |

## Nota sobre RN-M03-04

El ticket de balanza imprime un único peso, el bruto (DR-09). La tara es un atributo del vehículo y
el neto es la diferencia entre ambos, de modo que el sistema lo calcula en lugar de pedirlo. Lo que
no puede hacer es consultar la tara del catálogo cada vez que muestra un ingreso: si la Gerencia
decide actualizar la tara de un vehículo, los ingresos ya registrados deben conservar el neto con
el que se registraron. Por eso el ingreso guarda la tara que se le aplicó (D-17).

## Nota sobre RN-M03-06, RN-M03-07 y RN-M03-16

Las tres marcas de tiempo responden preguntas distintas: cuándo se pesó el volquete, cuándo se
empezó a registrarlo y cuándo el dato quedó disponible. La primera se compone de la fecha que
imprime el ticket y la hora que digita el usuario, y admite corrección; las otras dos son hechos que
observa el propio sistema y por eso no se editan (D-01). RN-M03-07 impide la única incoherencia que
las tres juntas no detectarían por sí solas: un pesaje fechado después del momento en que se
registra.

## Nota sobre RN-M03-17 a RN-M03-20

Cubren el primer viaje de un vehículo (DR-10). El ingreso se confirma con lo que se sabe en ese
momento —placa, fecha, hora, peso bruto, tipo de mineral— y queda En proceso hasta que el vehículo,
ya descargado, se pesa vacío. La tara se digita en lugar de reconocerse porque, a diferencia de un
dato del ticket, un error en ella no afecta un solo ingreso sino todos los futuros del vehículo.

## Nota sobre RN-M03-13

Anular y corregir resuelven problemas distintos. La corrección arregla un dato equivocado de un
ingreso que sí ocurrió; la anulación retira un ingreso que no debió existir. Un ingreso anulado ya
no participa en ningún total, de modo que corregirlo no tendría efecto sobre nada y solo añadiría
ruido al historial.
