# Reglas de negocio — M07 Captura sin conexión

> Estas reglas se aplican en el servidor (`apps/sincronizacion/services/`). El cliente replica algunas por conveniencia, pero la validación autoritativa es la del servidor (decisión D-08).

| Código | Regla | Consecuencia si se viola |
|---|---|---|
| RN-M07-01 | La hora de registro de un ingreso sincronizado es la hora de captura local, nunca la hora de sincronización | El indicador I1 mediría disponibilidad de red en lugar de oportunidad del registro |
| RN-M07-02 | La hora de captura local no puede ser posterior a la hora del servidor al momento de la sincronización | Un dispositivo con reloj adelantado produciría latencias negativas |
| RN-M07-03 | El identificador local UUID se conserva tras la sincronización, junto con el correlativo asignado | Se perdería la trazabilidad entre el registro del dispositivo y el del servidor |
| RN-M07-04 | Un mismo UUID local no puede sincronizarse dos veces | Un reintento tras respuesta perdida duplicaría el ingreso |
| RN-M07-05 | Los elementos de la cola se envían en el orden en que fueron capturados | Los correlativos no reflejarían la secuencia real de llegada de los volquetes |
| RN-M07-06 | Un elemento rechazado permanece en la cola con su motivo; nunca se descarta automáticamente | Se perderían registros de ingresos que sí ocurrieron |
| RN-M07-07 | La expiración del token no descarta la cola | El supervisor perdería una jornada de registros por un vencimiento de sesión |
| RN-M07-08 | El servidor aplica a los elementos sincronizados exactamente las mismas reglas de negocio que a los registros en línea | Un registro offline podría eludir validaciones y contaminar los datos |
| RN-M07-09 | Tras tres intentos fallidos, el elemento deja de reintentarse automáticamente y requiere intervención | Un elemento inválido consumiría batería y datos indefinidamente |

## Nota sobre RN-M07-04 y la idempotencia

El escenario a proteger es este: el cliente envía el lote, el servidor lo procesa correctamente, pero la respuesta se pierde por caída de red. El cliente, al no recibir confirmación, reintenta. Sin control de idempotencia, el ingreso quedaría duplicado.

La solución es la restricción de unicidad sobre `uuid_local` en el servidor: si un UUID ya existe, el servidor responde con el correlativo previamente asignado en lugar de crear un registro nuevo. La operación es idempotente.

## Nota sobre RN-M07-01 y la decisión D-03

Esta regla es la traducción operativa de la decisión D-03. Está registrada dos veces —en las decisiones de arquitectura y aquí— porque su violación no produce un error visible: produce datos que parecen correctos y que invalidan silenciosamente el indicador operativo principal. Es el tipo de fallo que solo se detecta al analizar los resultados, cuando ya no hay tiempo de corregirlo.
