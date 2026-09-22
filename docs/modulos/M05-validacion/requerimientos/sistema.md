# Requerimientos de sistema — M05 Validación automática de consistencia

| Código | Requerimiento | Deriva de |
|---|---|---|
| RS-M05-01 | El sistema expone la validación a través de la interfaz `ValidadorConsistencia`, que recibe los datos del ticket y devuelve la lista de inconsistencias | RU-M05-01 |
| RS-M05-02 | El sistema evalúa las cinco reglas V1 a V5 en cada invocación y devuelve el resultado de todas, no solo el de la primera incumplida | RU-M05-04 |
| RS-M05-03 | El sistema devuelve, por cada inconsistencia, la regla, el campo afectado y el mensaje literal correspondiente | RU-M05-02 |
| RS-M05-04 | El sistema comprueba en V1 que la diferencia entre `peso_neto_tn` y `peso_bruto_tn` menos `tara_tn` no supere la tolerancia configurada | RU-M05-01 |
| RS-M05-05 | El sistema comprueba en V4 el `peso_neto_tn` contra la `capacidad_tn` del vehículo registrada en el catálogo | RU-M05-03 |
| RS-M05-06 | El sistema clasifica cada regla como bloqueante o como exigente de justificación, y solo V4 pertenece al segundo grupo | RU-M05-03 |
| RS-M05-07 | El sistema impide confirmar un ingreso con una regla bloqueante incumplida o con una advertencia sin justificación | RU-M05-01, RU-M05-03 |
| RS-M05-08 | El sistema ejecuta las reglas en el servidor en toda petición de escritura, con independencia del origen de la petición | — (integridad del dominio) |
| RS-M05-09 | El sistema aplica las reglas dos veces por ingreso: sobre los datos propuestos y sobre los confirmados, y distingue ambos momentos en el resultado | — (integridad con M03, M04) |
| RS-M05-10 | El sistema omite la evaluación de una regla cuando falta alguno de los datos que necesita, y no la reporta como incumplida | RU-M05-02 |
| RS-M05-11 | El sistema persiste, al confirmarse el ingreso, el resultado de cada regla con su momento, su detalle y su resolución | RU-M05-05 |
| RS-M05-12 | El sistema conserva la justificación escrita cuando una advertencia se resuelve por esa vía | RU-M05-03, RU-M05-05 |
| RS-M05-13 | El sistema mantiene la tolerancia de V1 y el patrón de placa de V3 como parámetros de configuración, no como valores dispersos en el código | — (mantenibilidad) |
