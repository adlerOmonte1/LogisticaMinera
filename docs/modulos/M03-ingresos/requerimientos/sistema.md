# Requerimientos de sistema — M03 Registro de ingresos

| Código | Requerimiento | Deriva de |
|---|---|---|
| RS-M03-01 | El sistema recibe la imagen del ticket en formato JPG o PNG de hasta 10 MB, la conserva asociada al ingreso y rechaza cualquier otro formato o tamaño | RU-M03-01, RU-M03-06 |
| RS-M03-02 | El sistema asigna `hora_inicio_registro` al recibir la imagen y `hora_fin_registro` al persistir el ingreso; ambas son de solo lectura para todos los roles | RU-M03-01 |
| RS-M03-03 | El sistema solicita a `ReconocedorTicket` los seis campos del ticket y presenta cada uno con su nivel de confianza, sin persistirlos | RU-M03-01, RU-M03-02 |
| RS-M03-04 | El sistema somete los datos a `ValidadorConsistencia` antes de presentarlos y otra vez al confirmar, y muestra el mensaje literal de cada regla incumplida | RU-M03-03 |
| RS-M03-05 | El sistema permite editar `fecha_hora_ticket`, `peso_bruto_tn`, `tara_tn`, `peso_neto_tn`, la placa y el tipo de mineral antes de confirmar | RU-M03-02 |
| RS-M03-06 | El sistema deriva el tipo de vehículo de `tipo_titularidad` del catálogo a partir de la placa, y no lo expone como campo editable | RU-M03-04 |
| RS-M03-07 | El sistema exige que la placa corresponda a un vehículo vigente del catálogo para poder confirmar el ingreso | RU-M03-04 |
| RS-M03-08 | El sistema persiste `peso_neto_tn` con el valor leído del ticket y confirmado por el usuario, sin derivarlo de los otros pesos | RU-M03-01, RU-M03-03 |
| RS-M03-09 | El sistema asigna `codigo` al confirmar, de forma única y correlativa, dentro de la misma transacción que persiste el ingreso | — (integridad del registro) |
| RS-M03-10 | El sistema guarda, por cada campo del ticket, el valor reconocido y el valor confirmado como datos separados | RU-M03-02 |
| RS-M03-11 | El sistema permite modificar los campos provenientes del ticket de un ingreso registrado, exigiendo un motivo y revalidando las reglas | RU-M03-07 |
| RS-M03-12 | El sistema rechaza cualquier intento de modificar `codigo`, `hora_inicio_registro`, `hora_fin_registro`, `imagen_ticket` o el usuario que registró | RU-M03-07 |
| RS-M03-13 | El sistema marca un ingreso como anulado con motivo y responsable, y no ofrece ninguna operación de borrado | RU-M03-08 |
| RS-M03-14 | El sistema excluye los ingresos anulados de todo total y los conserva en el detalle y en las consultas | RU-M03-08 |
| RS-M03-15 | El sistema registra en auditoría la creación, la corrección y la anulación de cada ingreso, con el usuario y el instante de la operación | — (integridad con M09) |
| RS-M03-16 | El sistema ejecuta el registro, la corrección y la anulación como operaciones atómicas: o se completan enteras o no dejan rastro | — (integridad del registro) |
