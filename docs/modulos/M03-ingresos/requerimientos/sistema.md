# Requerimientos de sistema — M03 Registro de ingresos

| Código | Requerimiento | Deriva de |
|---|---|---|
| RS-M03-01 | El sistema recibe la imagen del ticket en formato JPG o PNG de hasta 10 MB, la conserva asociada al ingreso y rechaza cualquier otro formato o tamaño; la exige salvo en el registro sin foto | RU-M03-01, RU-M03-06 |
| RS-M03-02 | El sistema asigna `hora_inicio_registro` al recibir la imagen —o al iniciarse el registro sin foto— y `hora_fin_registro` al confirmar el ingreso, también cuando queda En proceso; ambas son de solo lectura para todos los roles | RU-M03-01 |
| RS-M03-03 | El sistema solicita a `ReconocedorTicket` la placa, la fecha y el peso bruto del ticket y presenta cada uno con su nivel de confianza, sin persistirlos | RU-M03-01, RU-M03-02 |
| RS-M03-04 | El sistema somete los datos a `ValidadorConsistencia` antes de presentarlos y otra vez al confirmar, y muestra el mensaje literal de cada regla incumplida | RU-M03-03 |
| RS-M03-05 | El sistema permite editar la placa, la fecha del pesaje y `peso_bruto_tn` reconocidos, propone la hora del pesaje con la hora en que se abre la revisión, permite editarla, y compone `fecha_hora_pesaje` con la fecha y la hora confirmadas | RU-M03-02, RU-M03-09 |
| RS-M03-06 | El sistema deriva el tipo de vehículo de `tipo_titularidad` y la tara de `VEHICULO.tara_tn` a partir de la placa, y no expone ninguno de los dos como campo editable del registro | RU-M03-04 |
| RS-M03-07 | El sistema exige que la placa corresponda a un vehículo vigente del catálogo para confirmar, rechaza el vehículo dado de baja, y cuando la placa no existe ofrece su alta en la misma pantalla sin descartar los datos capturados | RU-M03-04, RU-M03-10 |
| RS-M03-08 | El sistema calcula `peso_neto_tn` como `peso_bruto_tn` menos la tara vigente del vehículo, lo persiste junto con la tara aplicada en `tara_tn`, y no lo acepta desde el cliente | RU-M03-04, RU-M03-11 |
| RS-M03-09 | El sistema asigna `codigo` al confirmar, de forma única y correlativa, dentro de la misma transacción que persiste el ingreso | — (integridad del registro) |
| RS-M03-10 | El sistema guarda, por cada campo reconocido del ticket, el valor propuesto y el valor confirmado como datos separados | RU-M03-02 |
| RS-M03-11 | El sistema permite modificar la placa, la fecha y hora del pesaje, el peso bruto y el tipo de mineral de un ingreso registrado, exigiendo un motivo, revalidando las reglas y recalculando la tara aplicada, el peso neto y el estado | RU-M03-07 |
| RS-M03-12 | El sistema rechaza cualquier intento de modificar `codigo`, `hora_inicio_registro`, `hora_fin_registro`, `imagen_ticket` o el usuario que registró | RU-M03-07 |
| RS-M03-13 | El sistema marca un ingreso como anulado con motivo y responsable, y no ofrece ninguna operación de borrado | RU-M03-08 |
| RS-M03-14 | El sistema excluye de todo total los ingresos anulados y los que siguen En proceso, y conserva ambos en el detalle y en las consultas | RU-M03-08 |
| RS-M03-15 | El sistema registra en auditoría la creación, la corrección, la anulación y el destare de cada ingreso, con el usuario y el instante de la operación | — (integridad con M09) |
| RS-M03-16 | El sistema ejecuta el registro, la corrección, la anulación y el destare como operaciones atómicas: o se completan enteras o no dejan rastro | — (integridad del registro) |
| RS-M03-17 | El sistema confirma en estado `EN_PROCESO`, sin `tara_tn` ni `peso_neto_tn`, el ingreso cuyo vehículo no tiene tara registrada | RU-M03-10, RU-M03-11 |
| RS-M03-18 | El sistema lista los ingresos `EN_PROCESO` pendientes de destare y los vehículos a los que pertenecen | RU-M03-11 |
| RS-M03-19 | El sistema recibe la tara digitada y la fecha y hora del destare, propuestas con la hora actual y no posteriores al registro; guarda la tara en el vehículo con `fecha_destare` y el usuario que la registró, y calcula el peso neto de todos los ingresos `EN_PROCESO` del vehículo, que pasan a `REGISTRADO` | RU-M03-11 |
| RS-M03-20 | El sistema rechaza el registro de un destare sobre un vehículo que ya tiene tara | RU-M03-11 |
| RS-M03-21 | El sistema permite iniciar el registro sin imagen, sin invocar a `ReconocedorTicket`, con un motivo obligatorio elegido de una lista cerrada; persiste el ingreso con `sin_respaldo_fotografico` y el motivo, y lo somete a las mismas reglas de validación | RU-M03-12 |
| RS-M03-22 | El sistema presenta el ingreso sin respaldo fotográfico señalado como tal, con su motivo, en toda lista y en el detalle | RU-M03-12 |
| RS-M03-23 | El sistema permite al Administrativo y al Administrador dar de alta un tipo de mineral desde el registro, a través del servicio de M02, y lo deja elegido para el ingreso sin descartar los datos capturados | RU-M03-13 |
| RS-M03-24 | El sistema rechaza la corrección del tipo de mineral de un ingreso asignado a un lote cuando el nuevo tipo difiere del lote | — (integridad con M06) |
| RS-M03-25 | El sistema retira de su lote el ingreso que se anula mientras el lote todavía reúne ingresos | — (integridad con M06) |
