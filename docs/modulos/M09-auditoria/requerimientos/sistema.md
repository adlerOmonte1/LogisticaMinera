# Requerimientos de sistema — M09 Auditoría

| Código | Requerimiento | Deriva de |
|---|---|---|
| RS-M09-01 | El sistema registra un evento por cada operación de creación, modificación o anulación en cualquier módulo | RU-M09-01 |
| RS-M09-02 | El sistema registra un evento cuando se procesa un reconocimiento o se corrige un dato propuesto | RU-M09-01 |
| RS-M09-03 | El sistema registra un evento cuando se genera una exportación | RU-M09-01 |
| RS-M09-04 | El sistema registra un evento cuando se inicia sesión, se cierra sesión o se rechaza un acceso por falta de autorización | RU-M09-03 |
| RS-M09-05 | El sistema guarda en cada evento el usuario, la acción, la entidad afectada, el identificador del registro y el momento | RU-M09-01 |
| RS-M09-06 | El sistema guarda, en las modificaciones, el valor anterior y el nuevo de cada campo cambiado | RU-M09-02 |
| RS-M09-07 | El sistema registra el evento dentro de la misma transacción que la operación que describe | — (integridad del registro) |
| RS-M09-08 | El sistema no ofrece ninguna operación que permita crear, modificar o eliminar un evento fuera del propio flujo que lo genera | — (integridad del histórico) |
| RS-M09-09 | El sistema expone a los tres roles el historial de un ingreso, con sus propios eventos y los de su lote que lo afectan, ordenado cronológicamente | RU-M09-04 |
| RS-M09-10 | El sistema informa cuando una consulta no tiene eventos que mostrar | RU-M09-04, RU-M09-05 |
| RS-M09-11 | El sistema mantiene el catálogo de acciones auditables como un conjunto cerrado y compartido por todos los módulos | — (mantenibilidad) |
| RS-M09-12 | El sistema guarda, en las operaciones que lo exigen —corrección de un ingreso y su reversión, anulación, cambio de tara y unificación de un ingreso de otro tipo de mineral—, el motivo o la autorización escritos por el usuario en una columna propia del evento | — (integridad con M02, M03 y M06) |
| RS-M09-13 | El sistema guarda en cada evento de un lote los ingresos que afecta, para poder componer el historial de cada ingreso | — (integridad con M06) |
| RS-M09-14 | El sistema expone al Administrador la consulta de todos los eventos, con filtros combinables por usuario, acción, y referencia o detalle, ordenados del más reciente al más antiguo | RU-M09-05 |
| RS-M09-15 | El sistema no incluye en el historial de un ingreso eventos de usuarios, de catálogos ni accesos rechazados | — (confidencialidad) |
| RS-M09-16 | El sistema no guarda ninguna contraseña, temporal o definitiva, en los valores de un evento | — (confidencialidad, integridad con M01) |
