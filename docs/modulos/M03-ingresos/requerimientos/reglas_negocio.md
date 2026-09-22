# Reglas de negocio — M03 Registro de ingresos

> Ubicación en el código: `apps/ingresos/models/` (invariantes de la entidad) y
> `apps/ingresos/services/` (reglas de proceso). Ninguna de estas reglas vive en `views/` ni en un
> componente Angular (D-08).

| Código | Regla | Consecuencia si se viola |
|---|---|---|
| RN-M03-01 | Un ingreso no se persiste sin la imagen del ticket | El registro quedaría sin respaldo verificable y sería imposible comprobar lo que se consignó |
| RN-M03-02 | Ningún valor propuesto por el reconocimiento se persiste sin confirmación del usuario | Un error de lectura se convertiría en dato oficial sin que nadie lo revisara |
| RN-M03-03 | Por cada campo del ticket se conservan el valor reconocido y el confirmado como datos separados | Se perdería la distinción entre lo que leyó el motor y lo que corrigió la persona, y nadie podría auditar las correcciones |
| RN-M03-04 | El peso neto se persiste tal como aparece en el ticket; el sistema no lo calcula | Un ticket incoherente pasaría inadvertido, porque el valor derivado siempre cuadraría consigo mismo |
| RN-M03-05 | Un ingreso no se confirma con una regla de validación bloqueante incumplida ni con una advertencia sin justificar | Se registrarían toneladas que el ticket no respalda |
| RN-M03-06 | `hora_inicio_registro` y `hora_fin_registro` las asigna el servidor y ningún rol las modifica | Las marcas de tiempo serían falsificables y el registro dejaría de describir cómo se trabajó |
| RN-M03-07 | La fecha y hora del ticket no pueden ser posteriores al instante del registro | El ingreso quedaría fechado en el futuro y el orden de los registros dejaría de ser reconstruible |
| RN-M03-08 | El vehículo debe existir y estar vigente en el catálogo al momento de confirmar | El tipo de vehículo quedaría sin determinar y no habría capacidad contra la cual contrastar el peso |
| RN-M03-09 | El código lo asigna el servidor dentro de la transacción, mediante bloqueo sobre el contador | Dos ingresos simultáneos recibirían el mismo código y dejarían de ser identificables |
| RN-M03-10 | El número de ticket, cuando se consigna, es único entre los ingresos no anulados | El mismo pesaje podría registrarse dos veces y las toneladas se contarían por duplicado |
| RN-M03-11 | Toda corrección exige un motivo y vuelve a someterse a las reglas de validación | Un ingreso corregido podría terminar incumpliendo condiciones que uno nuevo no puede incumplir |
| RN-M03-12 | La corrección conserva los valores anteriores en el registro de auditoría | No se podría reconstruir qué decía el ingreso antes del cambio ni quién lo modificó |
| RN-M03-13 | Un ingreso anulado no se corrige ni se vuelve a anular | Se acumularían anulaciones sobre el mismo registro y el motivo vigente dejaría de ser único |
| RN-M03-14 | El sistema no ofrece ninguna operación de borrado de ingresos: solo anulación | Un registro podría desaparecer del histórico sin dejar rastro |
| RN-M03-15 | El registro, la corrección y la anulación ocurren dentro de una sola transacción, junto con su evento de auditoría | Podría quedar un ingreso sin evento, o un evento sin ingreso, y el historial dejaría de ser fiable |

## Nota sobre RN-M03-04

Es la regla que más probablemente alguien «simplificará» durante la implementación, porque calcular
el neto como bruto menos tara parece más limpio que pedirlo como dato. No lo es: el ticket de
balanza ya trae el neto impreso, y el sentido de registrarlo es poder compararlo con la resta. Si el
sistema lo calcula, la comparación siempre da cero y un ticket mal impreso o mal leído entra sin que
nadie lo note. La comprobación corresponde a la regla V1, que vive en M05.

## Nota sobre RN-M03-06 y RN-M03-07

Las tres marcas de tiempo responden preguntas distintas: cuándo se pesó el volquete, cuándo se
empezó a registrarlo y cuándo el dato quedó disponible. La primera proviene del ticket y admite
corrección, porque el reconocimiento puede leerla mal; las otras dos son hechos que observa el
propio sistema y por eso no se editan (D-01). RN-M03-07 impide la única incoherencia que las tres
juntas no detectarían por sí solas: un ticket fechado después del momento en que se registra.

## Nota sobre RN-M03-13

Anular y corregir resuelven problemas distintos. La corrección arregla un dato equivocado de un
ingreso que sí ocurrió; la anulación retira un ingreso que no debió existir. Un ingreso anulado ya
no participa en ningún total, de modo que corregirlo no tendría efecto sobre nada y solo añadiría
ruido al historial.
