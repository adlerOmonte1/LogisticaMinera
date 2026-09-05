# Decisiones de diseño fijadas

**Estado:** cerradas. Reabrir cualquiera exige justificación escrita, porque todas condicionan un indicador de la tesis o la integridad del dominio.

---

## D-01. La hora de pesaje y la hora de registro son dos campos independientes

**Módulos afectados:** M03, M07
**Indicador en juego:** I1 (latencia entre pesaje y disponibilidad del dato)

La hora de pesaje la ingresa el usuario copiándola del ticket de balanza. La hora de registro la asigna el servidor automáticamente al persistir. La diferencia entre ambas **es** el indicador I1.

Si se colapsan en un solo campo, el indicador desaparece y la dimensión D1 de la variable dependiente queda sin medición. En el código, `hora_registro` es `auto_now_add` y no es editable por ningún rol.

## D-02. El correlativo lo asigna el servidor, nunca el dispositivo

**Módulos afectados:** M03, M07

Un ingreso capturado sin conexión recibe un identificador local temporal (UUID generado en el cliente) y obtiene su correlativo definitivo al sincronizar. Si el dispositivo asignara el correlativo, dos supervisores trabajando sin conexión de forma simultánea generarían el mismo número, y la unidad de análisis de la tesis dejaría de ser identificable de forma única.

Implementación: transacción con bloqueo sobre la tabla de correlativos, o secuencia de PostgreSQL. Nunca `MAX(correlativo) + 1` fuera de transacción.

## D-03. La hora de registro de un ingreso offline es la hora de captura local, no la de sincronización

**Módulo afectado:** M07
**Indicadores en juego:** I1, I2

Si se tomara la hora de sincronización, la latencia mediría el tiempo transcurrido hasta que hubo señal de red, no el tiempo hasta que se capturó el dato. Eso invalidaría el indicador justamente en el módulo diseñado para mejorarlo.

Implementación: el cliente envía `hora_captura_local` junto con el registro; el servidor la persiste como `hora_registro` y guarda además `hora_sincronizacion` como campo auxiliar de auditoría. El sistema no acepta una `hora_captura_local` posterior a la hora del servidor.

## D-04. La captura sin conexión se decide en la semana 1, no se añade al final

**Módulo afectado:** M07

La aplicación web progresiva, el almacenamiento local y la cola de sincronización son decisiones de arquitectura, no una funcionalidad agregable. Si M03 se construye asumiendo conexión permanente, incorporar M07 obliga a reescribirlo.

Por eso M07 figura en la semana 4 del cronograma y no en la 8, y por eso el esqueleto PWA aparece como entregable de la semana 1.

## D-05. M09-Búsqueda existe porque el indicador I5 lo exige

**Módulo afectado:** M09

I5 mide el tiempo de recuperación del dato de un ingreso concreto (por padrón, fecha, placa o producto). Ninguno de los diez requerimientos originales cubría búsqueda por criterios. Sin ella, I5 no mejora en el postest y la dimensión D3 queda sin efecto medible. Se incorporó como RF-11.

## D-06. El tipo de vehículo (propio / externo) es un atributo del catálogo, no texto libre

**Módulos afectados:** M02, M03
**Indicador en juego:** I2 (cobertura de registro por tipo de vehículo)

El hallazgo central del diagnóstico es que los volquetes propios se registran peor que los externos, porque a los externos se les paga por viaje y eso obliga a fotografiar el ticket. Demostrarlo con datos requiere que la titularidad del vehículo sea un campo clasificado y obligatorio en el catálogo, no una anotación libre.

## D-07. El sistema no borra ingresos: los anula

**Módulos afectados:** M03, M08

Un ingreso registrado no se elimina físicamente. Se marca como anulado, con motivo y responsable, y permanece en el histórico. La razón es metodológica: si durante la ventana de observación un registro pudiera desaparecer, no se podría demostrar ante el jurado que la cobertura del postest no fue depurada retroactivamente.

## D-08. Las reglas de negocio no se replican en el cliente como fuente de verdad

**Módulos afectados:** todos

Angular puede validar en el formulario para mejorar la experiencia, pero la validación autoritativa está en el backend. Un registro que llega por la cola de sincronización de M07 no pasa por el formulario y debe someterse a las mismas reglas.

## Pendientes que bloquean decisiones

| Pendiente | Bloquea | Fecha límite |
|---|---|---|
| Criterio de estimación de merma por humedad | M04, indicador I4 | Antes de la semana 5 |
| Formato oficial de declaración semestral | M06 | Antes de la semana 7 |
| Confirmación de tamaño de muestra para D3 con la asesora | Análisis inferencial | Antes de cerrar el capítulo III |
