# Requerimientos de sistema — M05 Validación automática de consistencia

| Código | Requerimiento | Deriva de |
|---|---|---|
| RS-M05-01 | El sistema expone la validación a través de la interfaz `ValidadorConsistencia`, que recibe los datos del ticket y devuelve la lista de inconsistencias | RU-M05-01 |
| RS-M05-02 | El sistema evalúa las cinco reglas V1 a V5 en cada invocación y devuelve el resultado de todas, no solo el de la primera incumplida | RU-M05-04 |
| RS-M05-03 | El sistema devuelve, por cada inconsistencia, la regla, el campo afectado y el mensaje literal correspondiente | RU-M05-02 |
| RS-M05-04 | El sistema comprueba en V1 que no exista un ingreso no anulado con la misma placa, la misma fecha del pesaje y el mismo `peso_bruto_tn`, y devuelve su código si lo encuentra | RU-M05-06 |
| RS-M05-05 | El sistema comprueba en V2 la `tara_tn` del vehículo contra `peso_bruto_tn`, y en V4 el peso neto calculado contra la `capacidad_tn` del vehículo; ambas se omiten si el vehículo aún no tiene tara y se evalúan al registrar el destare | RU-M05-01, RU-M05-03 |
| RS-M05-06 | El sistema clasifica cada regla como bloqueante o como exigente de justificación; V1 y V4 pertenecen al segundo grupo | RU-M05-03, RU-M05-06 |
| RS-M05-07 | El sistema impide confirmar un ingreso con una regla bloqueante incumplida o con una advertencia sin justificación | RU-M05-01, RU-M05-03 |
| RS-M05-08 | El sistema ejecuta las reglas en el servidor en toda petición de escritura, con independencia del origen de la petición | — (integridad del dominio) |
| RS-M05-09 | El sistema aplica las reglas sobre los datos propuestos y sobre los confirmados y, en el primer viaje de un vehículo, de nuevo al registrar el destare; distingue los tres momentos en el resultado | — (integridad con M03, M04) |
| RS-M05-10 | El sistema omite la evaluación de una regla cuando falta alguno de los datos que necesita, y no la reporta como incumplida | RU-M05-02 |
| RS-M05-11 | El sistema persiste, al confirmarse el ingreso, el resultado de cada regla con su momento, su detalle y su resolución | RU-M05-05 |
| RS-M05-12 | El sistema conserva la justificación escrita cuando una advertencia se resuelve por esa vía | RU-M05-03, RU-M05-05 |
| RS-M05-13 | El sistema mantiene el patrón de placa de V3 como parámetro de configuración, no como valores dispersos en el código | — (mantenibilidad) |
