# Reglas de negocio — M02 Catálogo maestro

> Ubicación en el código: `apps/catalogo/models/` (invariantes de las entidades) y
> `apps/catalogo/services/` (baja lógica y validaciones cruzadas). Ninguna de estas reglas vive en
> `views/` ni en un componente Angular (D-08).

| Código | Regla | Consecuencia si se viola |
|---|---|---|
| RN-M02-01 | La placa de vehículo es única | Un mismo volquete tendría dos identidades en el catálogo |
| RN-M02-02 | La titularidad del vehículo es obligatoria y pertenece al dominio cerrado {PROPIO, EXTERNO} | El tipo de vehículo del ingreso quedaría sin clasificación posible (D-06) |
| RN-M02-03 | Un vehículo EXTERNO debe tener transportista asociado | No se podría atribuir el vehículo a ningún proveedor |
| RN-M02-04 | Un vehículo PROPIO no tiene transportista asociado | Se introduciría ambigüedad en la clasificación de titularidad |
| RN-M02-05 | La capacidad de carga de un vehículo es un decimal positivo | La regla V4 no tendría un límite válido contra el cual contrastar el peso neto |
| RN-M02-06 | El código de tipo de mineral es único | Un ingreso podría clasificarse en dos categorías a la vez |
| RN-M02-07 | El RUC de un transportista tiene exactamente once dígitos numéricos | Se registrarían identificadores que ningún documento formal reconoce |
| RN-M02-08 | Ninguna entidad de catálogo con registros dependientes se elimina físicamente | Se romperían las referencias del histórico de ingresos |
| RN-M02-09 | Una entidad desactivada no se ofrece en el formulario de registro, pero sí aparece en consultas históricas | Los ingresos antiguos quedarían sin una etiqueta legible para su vehículo o su tipo de mineral |
| RN-M02-10 | La unidad de medida de todo tipo de mineral es la tonelada | Los totales de la consolidación mezclarían unidades incompatibles |

## Nota sobre RN-M02-05

Es la regla que conecta este módulo con la validación de M05. La capacidad no se usa dentro de M02
más que como un dato del vehículo; su propósito completo solo se entiende en la regla V4, que la
lee para decidir si un peso neto es razonable. Un vehículo con capacidad cero o negativa haría que
esa regla fallara o se volviera inservible para ese vehículo.

## Nota sobre RN-M02-10

La unidad única simplifica el alcance del sistema y es coherente con la operación real: el ticket de
balanza reporta en toneladas. Si en el futuro se incorporara un tipo de mineral medido en otra
unidad, esta regla debe revisarse antes de que el sistema acepte el registro.
