# Requerimientos de sistema — M02 Catálogo maestro

| Código | Requerimiento | Deriva de |
|---|---|---|
| RS-M02-01 | El sistema mantiene catálogos de productos, vehículos, transportistas y clientes con identificador único e indicador de vigencia | RU-M02-01, RU-M02-05 |
| RS-M02-02 | El sistema clasifica cada vehículo mediante un atributo enumerado de titularidad con dominio cerrado {PROPIO, EXTERNO} | RU-M02-02 |
| RS-M02-03 | El sistema exige la asociación a un transportista cuando la titularidad es EXTERNO y la impide cuando es PROPIO | RU-M02-02, RU-M02-03 |
| RS-M02-04 | El sistema valida el formato de placa vehicular y la longitud del RUC antes de persistir | RU-M02-03 |
| RS-M02-05 | El sistema aplica baja lógica a toda entidad de catálogo con registros dependientes | RU-M02-04 |
| RS-M02-06 | El sistema expone únicamente las entidades vigentes en los selectores de los formularios operativos | RU-M02-01 |
| RS-M02-07 | El sistema registra en auditoría la creación, modificación y desactivación de entidades de catálogo | — (trazabilidad) |
