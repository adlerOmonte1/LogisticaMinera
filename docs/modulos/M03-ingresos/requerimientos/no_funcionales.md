# Requerimientos no funcionales — M03 Registro de ingresos

| Código | Característica ISO/IEC 25010:2023 | Requerimiento | Verificación |
|---|---|---|---|
| RNF-M03-01 | Adecuación funcional — corrección | La imagen del ticket se acepta en JPG o PNG de hasta 10 MB; cualquier otro formato o tamaño se rechaza con mensaje explícito | Prueba automatizada con archivos de muestra de cada formato y tamaño límite |
| RNF-M03-02 | Eficiencia de desempeño — comportamiento temporal | Desde que se envía la imagen hasta que se presentan los campos propuestos transcurren menos de 8 segundos con una imagen de 5 MB sobre red móvil | Cronometraje en planta con diez capturas consecutivas |
| RNF-M03-03 | Eficiencia de desempeño — comportamiento temporal | La confirmación del ingreso responde en menos de 2 segundos con 5000 ingresos en base | Prueba automatizada con datos sintéticos |
| RNF-M03-04 | Eficiencia de desempeño — utilización de recursos | La imagen se reduce en el cliente antes de enviarse, conservando legible el texto del ticket | Inspección en dispositivo real sobre veinte tickets, comparando la lectura antes y después de reducir |
| RNF-M03-05 | Fiabilidad — tolerancia a fallos | El borrador del registro —imagen y campos editados— se conserva en el dispositivo si se pierde la conexión, y se reanuda al recuperarla sin volver a fotografiar | Inspección en dispositivo real desactivando la red a mitad del registro |
| RNF-M03-06 | Fiabilidad — capacidad de recuperación | Si la operación falla después de confirmar, no queda un ingreso parcialmente persistido | Prueba automatizada que fuerza el fallo en cada paso de la transacción |
| RNF-M03-07 | Capacidad de interacción — operabilidad | El registro completo se realiza desde un teléfono, en vertical y con una sola mano, sin desplazamiento horizontal | Inspección en dispositivo real |
| RNF-M03-08 | Capacidad de interacción — protección contra errores del usuario | Los campos con confianza inferior al umbral se resaltan visualmente antes de confirmar, y las inconsistencias se muestran junto al campo afectado | Inspección en dispositivo real |
| RNF-M03-09 | Capacidad de interacción — protección contra errores del usuario | Los campos numéricos abren el teclado numérico en dispositivos móviles | Inspección en dispositivo real |
| RNF-M03-10 | Seguridad — no repudio | La imagen del ticket se conserva sin alteración mientras el ingreso exista, incluso si este se anula | Consulta de verificación sobre el almacén de imágenes tras una anulación |
| RNF-M03-11 | Seguridad — confidencialidad | La imagen solo es accesible para usuarios autenticados con permiso sobre el ingreso; no se sirve desde una ruta pública adivinable | Inspección de configuración e intento de acceso sin sesión |
| RNF-M03-12 | Mantenibilidad — modularidad | Cambiar el motor de reconocimiento o añadir una regla de validación no obliga a modificar el servicio de registro | Inspección de código: el servicio depende de las interfaces, no de implementaciones |
| RNF-M03-13 | Capacidad de interacción — operabilidad | El alta de un vehículo nuevo o de un tipo de mineral se completa en la misma pantalla del registro, sin navegar a otra y sin perder la imagen ni los campos ya capturados | Inspección en dispositivo real registrando el primer viaje de un vehículo y un tipo de mineral nuevo |
| RNF-M03-14 | Capacidad de interacción — protección contra errores del usuario | La hora del pesaje se propone con la hora en que se abre la revisión, se muestra marcada como propuesta junto a la fecha reconocida y se edita con un control de hora | Inspección en dispositivo real |
| RNF-M03-15 | Capacidad de interacción — reconocibilidad de la adecuación | Los ingresos En proceso se distinguen de los Registrados en toda lista, y el sistema muestra cuántos están pendientes de destare | Inspección en dispositivo real |
| RNF-M03-16 | Capacidad de interacción — reconocibilidad de la adecuación | Los ingresos sin respaldo fotográfico se distinguen en toda lista sin abrir el detalle, y el detalle muestra el motivo en lugar de la imagen | Inspección en dispositivo real |
| RNF-M03-17 | Capacidad de interacción — operabilidad | El registro sin foto se elige desde la misma pantalla de captura, sin navegar a otra | Inspección en dispositivo real |

## Nota sobre RNF-M03-02 y RNF-M03-04

Son el par que decide si el sistema se usa o se abandona. El registro ocurre de pie junto al
volquete, con la conectividad de la planta, y una espera larga empuja al usuario a volver al papel.
RNF-M03-04 es la palanca principal: una fotografía de teléfono actual supera con facilidad los 5 MB
y casi todo ese peso es irrelevante para leer un ticket. Reducir de más, en cambio, vuelve ilegible
el texto impreso en papel térmico, por eso la verificación compara la lectura antes y después.

## Nota sobre RNF-M03-05

Sustituye a la operación sin conexión que contemplaba el alcance anterior. No se trata de registrar <!-- migracion:ok -->
sin red, sino de no perder el trabajo ya hecho: la fotografía tomada y los campos corregidos siguen
disponibles cuando la señal vuelve. El ingreso se confirma siempre contra el servidor, porque el
código único y la validación viven allí (D-02, D-08).

## Nota sobre RNF-M03-14

La hora del pesaje es el único dato del registro que no sale del ticket ni del sistema: la indica el
usuario (DR-09, DR-11). El sistema la propone con la hora en que se abre la revisión porque, cuando
el registro se hace junto a la balanza, esa hora está a pocos minutos del pesaje y el usuario solo
la ajusta.

La propuesta tiene un costo que debe controlarse: si el usuario la acepta sin ajustarla, la fecha y
hora del pesaje queda casi igual al inicio del registro y el tiempo de espera entre ambos parece
nulo. Por eso la hora se muestra **marcada como propuesta** y no como un dato reconocido, y la
verificación en dispositivo comprueba que el usuario la distingue de la fecha leída del ticket.
