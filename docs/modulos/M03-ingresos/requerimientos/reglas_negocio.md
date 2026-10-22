# Reglas de negocio — M03 Registro de ingresos

> Ubicación en el código: `apps/ingresos/models/` (invariantes de la entidad) y
> `apps/ingresos/services/` (reglas de proceso). Ninguna de estas reglas vive en `views/` ni en un
> componente Angular (D-08).

| Código | Regla | Consecuencia si se viola |
|---|---|---|
| RN-M03-01 | Un ingreso no se persiste sin la imagen del ticket, salvo en el registro sin foto de RN-M03-21 | El registro quedaría sin respaldo verificable y sería imposible comprobar lo que se consignó |
| RN-M03-02 | Ningún valor propuesto por el reconocimiento se persiste sin confirmación del usuario | Un error de lectura se convertiría en dato oficial sin que nadie lo revisara |
| RN-M03-03 | Por cada campo reconocido se conservan el valor propuesto y el confirmado como datos separados | Se perdería la distinción entre lo que leyó el motor y lo que corrigió la persona, y nadie podría auditar las correcciones |
| RN-M03-04 | El peso neto lo calcula el servidor como peso bruto menos la tara del vehículo, y el ingreso conserva la tara que se le aplicó | Con un neto digitado, dos ingresos del mismo vehículo podrían aplicar taras distintas; con la tara consultada al vuelo, un cambio posterior reescribiría el histórico |
| RN-M03-05 | Un ingreso no se confirma con una regla de validación bloqueante incumplida ni con una advertencia sin justificar | Se registrarían toneladas que el ticket no respalda |
| RN-M03-06 | `hora_inicio_registro` y `hora_fin_registro` las asigna el servidor y ningún rol las modifica | Las marcas de tiempo serían falsificables y el registro dejaría de describir cómo se trabajó |
| RN-M03-07 | La fecha y hora del pesaje no pueden ser posteriores al instante del registro | El ingreso quedaría fechado en el futuro y el orden de los registros dejaría de ser reconstruible |
| RN-M03-08 | El vehículo debe existir y estar vigente en el catálogo al confirmar; si la placa no existe, se da de alta en la misma pantalla antes de confirmar | El tipo de vehículo quedaría sin determinar y no habría tara ni capacidad con que calcular y contrastar el peso |
| RN-M03-09 | El código lo asigna el servidor dentro de la transacción, mediante bloqueo sobre el contador | Dos ingresos simultáneos recibirían el mismo código y dejarían de ser identificables |
| RN-M03-10 | *Retirada por DR-12.* El ingreso no registra un número de ticket: el código único lo identifica, y el pesaje registrado dos veces lo advierte V1 | — |
| RN-M03-11 | Toda corrección exige un motivo y vuelve a someterse a las reglas de validación | Un ingreso corregido podría terminar incumpliendo condiciones que uno nuevo no puede incumplir |
| RN-M03-12 | La corrección conserva los valores anteriores en el registro de auditoría | No se podría reconstruir qué decía el ingreso antes del cambio ni quién lo modificó |
| RN-M03-13 | Un ingreso anulado no se corrige ni se vuelve a anular | Se acumularían anulaciones sobre el mismo registro y el motivo vigente dejaría de ser único |
| RN-M03-14 | El sistema no ofrece ninguna operación de borrado de ingresos: solo anulación | Un registro podría desaparecer del histórico sin dejar rastro |
| RN-M03-15 | El registro, la corrección, la anulación y el destare ocurren dentro de una sola transacción, junto con su evento de auditoría | Podría quedar un ingreso sin evento, o un evento sin ingreso, y el historial dejaría de ser fiable |
| RN-M03-16 | La hora del pesaje es obligatoria y la indica el usuario sobre una propuesta editable, porque el ticket no la imprime | La primera marca de tiempo quedaría incompleta y el ingreso no podría ubicarse en el día |
| RN-M03-17 | Si el vehículo no tiene tara, el ingreso se confirma En proceso, sin peso neto | Se registraría un peso neto inventado o nulo como si fuera definitivo |
| RN-M03-18 | Un ingreso En proceso no cuenta en ningún total ni se asigna a un lote de proceso | Los totales sumarían toneladas brutas mezcladas con netas |
| RN-M03-19 | La tara de un vehículo se registra una sola vez, en el destare, digitada por el usuario y no reconocida de la imagen | Una anotación manuscrita mal leída se convertiría en la tara de todos los viajes futuros del vehículo |
| RN-M03-20 | La tara del destare es menor que el peso bruto de cada ingreso En proceso del vehículo | El peso neto de alguno de esos ingresos sería cero o negativo |
| RN-M03-21 | El ingreso puede registrarse sin foto solo con un motivo elegido de una lista cerrada, y queda marcado como sin respaldo fotográfico de forma permanente | Un ingreso sin respaldo sería indistinguible de uno respaldado, y la falta de la imagen no tendría explicación |
| RN-M03-22 | El ingreso sin foto no pasa por el reconocimiento, pero sí por las mismas reglas de validación que un ingreso con foto | Un registro sin imagen se convertiría en la vía para eludir las reglas V1 a V5 |
| RN-M03-23 | La fecha y hora del destare no pueden ser posteriores al momento del registro | La tara quedaría fechada en el futuro y el orden entre el primer viaje y su destare dejaría de ser reconstruible |
| RN-M03-24 | Desde el registro, solo el Administrativo y el Administrador dan de alta un tipo de mineral, con las mismas reglas que el alta desde el catálogo | El catálogo crecería con denominaciones distintas para un mismo mineral y la consolidación dejaría de agrupar |
| RN-M03-25 | La corrección no cambia el tipo de mineral de un ingreso asignado a un lote por otro que no está en la lista del lote (DR-27) | El lote reuniría un mineral que nadie decidió agregar y su composición dejaría de explicar lo que contiene |
| RN-M03-26 | Si la corrección asocia el ingreso a un vehículo sin tara, el ingreso vuelve a En proceso, sin tara aplicada ni peso neto | Quedaría un peso neto calculado con la tara de otro vehículo |
| RN-M03-27 | La anulación retira el ingreso del lote que todavía reúne ingresos; si el lote ya inició su recorrido, el ingreso permanece vinculado y deja de contar en sus totales | Un lote en formación arrastraría un ingreso que ya no debía existir |
| RN-M03-28 | Solo se revierte la última corrección vigente de un ingreso, con motivo, y los valores restaurados se revalidan como en una corrección (DR-28) | Revertir una corrección intermedia dejaría el ingreso en un estado que nunca existió, o reintroduciría un dato que las reglas ya rechazan |
| RN-M03-29 | La reversión es un cambio nuevo, atribuido y auditado; la corrección revertida permanece en el historial | Se perdería la evidencia de que el dato estuvo mal y de quién lo corrigió |

## Nota sobre RN-M03-04

El ticket de balanza imprime un único peso, el bruto (DR-09). La tara es un atributo del vehículo y
el neto es la diferencia entre ambos, de modo que el sistema lo calcula en lugar de pedirlo. Lo que
no puede hacer es consultar la tara del catálogo cada vez que muestra un ingreso: si la Gerencia
decide actualizar la tara de un vehículo, los ingresos ya registrados deben conservar el neto con
el que se registraron. Por eso el ingreso guarda la tara que se le aplicó (D-17).

## Nota sobre RN-M03-06, RN-M03-07 y RN-M03-16

Las tres marcas de tiempo responden preguntas distintas: cuándo se pesó el volquete, cuándo se
empezó a registrarlo y cuándo el dato quedó disponible. La primera se compone de la fecha que
imprime el ticket y la hora que indica el usuario sobre una propuesta, y admite corrección; las otras dos son hechos que
observa el propio sistema y por eso no se editan (D-01). RN-M03-07 impide la única incoherencia que
las tres juntas no detectarían por sí solas: un pesaje fechado después del momento en que se
registra.

## Nota sobre RN-M03-13

Anular y corregir resuelven problemas distintos. La corrección arregla un dato equivocado de un
ingreso que sí ocurrió; la anulación retira un ingreso que no debió existir. Un ingreso anulado ya
no participa en ningún total, de modo que corregirlo no tendría efecto sobre nada y solo añadiría
ruido al historial.

## Nota sobre RN-M03-17 a RN-M03-20

Cubren el primer viaje de un vehículo (DR-10). El ingreso se confirma con lo que se sabe en ese
momento —placa, fecha, hora, peso bruto, tipo de mineral— y queda En proceso hasta que el vehículo,
ya descargado, se pesa vacío. La tara se digita en lugar de reconocerse porque, a diferencia de un
dato del ticket, un error en ella no afecta un solo ingreso sino todos los futuros del vehículo.

## Nota sobre RN-M03-21 y RN-M03-22

El registro sin foto (DR-13) existe para que un ticket perdido no deje un ingreso sin registrar o
anotado de memoria fuera del sistema. Es una excepción, no un camino alternativo: el motivo se elige
de una lista cerrada para que las causas puedan contarse, y la marca de ingreso sin respaldo no se
retira, porque la imagen no es un dato corregible. Lo único que el ingreso sin foto omite es el
reconocimiento, que no tiene imagen que leer; la validación se aplica igual, para que la ausencia de
foto no sea una forma de registrar datos que con foto se rechazarían.
