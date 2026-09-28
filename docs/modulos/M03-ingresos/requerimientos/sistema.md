# Requerimientos de sistema — M03 Registro de ingresos

| Código | Requerimiento | Deriva de |
|---|---|---|
| RS-M03-01 | El sistema recibe la imagen del ticket en formato JPG o PNG de hasta 10 MB, la conserva asociada al ingreso y rechaza cualquier otro formato o tamaño | RU-M03-01, RU-M03-06 |
| RS-M03-02 | El sistema asigna `hora_inicio_registro` al recibir la imagen y `hora_fin_registro` al confirmar el ingreso, también cuando queda En proceso; ambas son de solo lectura para todos los roles | RU-M03-01 |
| RS-M03-03 | El sistema solicita a `ReconocedorTicket` la placa, la fecha y el peso bruto del ticket y presenta cada uno con su nivel de confianza, sin persistirlos | RU-M03-01, RU-M03-02 |
| RS-M03-04 | El sistema somete los datos a `ValidadorConsistencia` antes de presentarlos y otra vez al confirmar, y muestra el mensaje literal de cada regla incumplida | RU-M03-03 |
| RS-M03-05 | El sistema permite editar la placa, la fecha del pesaje y `peso_bruto_tn` reconocidos, exige que el usuario digite la hora del pesaje, y compone `fecha_hora_pesaje` con ambas antes de confirmar | RU-M03-02, RU-M03-09 |
| RS-M03-06 | El sistema deriva el tipo de vehículo de `tipo_titularidad` y la tara de `VEHICULO.tara_tn` a partir de la placa, y no expone ninguno de los dos como campo editable del registro | RU-M03-04 |
| RS-M03-07 | El sistema exige que la placa corresponda a un vehículo vigente del catálogo para confirmar, y cuando no existe ofrece su alta en la misma pantalla sin descartar los datos capturados | RU-M03-04, RU-M03-10 |
| RS-M03-08 | El sistema calcula `peso_neto_tn` como `peso_bruto_tn` menos la tara vigente del vehículo, lo persiste junto con la tara aplicada en `tara_tn`, y no lo acepta desde el cliente | RU-M03-04, RU-M03-11 |
| RS-M03-09 | El sistema asigna `codigo` al confirmar, de forma única y correlativa, dentro de la misma transacción que persiste el ingreso | — (integridad del registro) |
| RS-M03-10 | El sistema guarda, por cada campo reconocido del ticket, el valor propuesto y el valor confirmado como datos separados | RU-M03-02 |
| RS-M03-11 | El sistema permite modificar los campos provenientes del ticket de un ingreso registrado, exigiendo un motivo y revalidando las reglas | RU-M03-07 |
| RS-M03-12 | El sistema rechaza cualquier intento de modificar `codigo`, `hora_inicio_registro`, `hora_fin_registro`, `imagen_ticket` o el usuario que registró | RU-M03-07 |
| RS-M03-13 | El sistema marca un ingreso como anulado con motivo y responsable, y no ofrece ninguna operación de borrado | RU-M03-08 |
| RS-M03-14 | El sistema excluye de todo total los ingresos anulados y los que siguen En proceso, y conserva ambos en el detalle y en las consultas | RU-M03-08 |
| RS-M03-15 | El sistema registra en auditoría la creación, la corrección, la anulación y el destare de cada ingreso, con el usuario y el instante de la operación | — (integridad con M09) |
| RS-M03-16 | El sistema ejecuta el registro, la corrección, la anulación y el destare como operaciones atómicas: o se completan enteras o no dejan rastro | — (integridad del registro) |
| RS-M03-17 | El sistema confirma en estado `EN_PROCESO`, sin `tara_tn` ni `peso_neto_tn`, el ingreso cuyo vehículo no tiene tara registrada | RU-M03-10, RU-M03-11 |
| RS-M03-18 | El sistema lista los ingresos `EN_PROCESO` pendientes de destare | RU-M03-11 |
| RS-M03-19 | El sistema recibe la tara digitada del destare, la guarda en el vehículo con `fecha_destare` y el usuario que la registró, y calcula el peso neto de todos los ingresos `EN_PROCESO` del vehículo, que pasan a `REGISTRADO` | RU-M03-11 |
| RS-M03-20 | El sistema rechaza el registro de un destare sobre un vehículo que ya tiene tara | RU-M03-11 |
