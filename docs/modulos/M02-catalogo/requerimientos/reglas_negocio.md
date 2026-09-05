# Reglas de negocio — M02 Catálogo maestro

> Ubicación en el código: `apps/catalogo/models/` y validadores asociados.

| Código | Regla | Consecuencia si se viola |
|---|---|---|
| RN-M02-01 | El código de producto es único | Los consolidados por producto (I6) se duplicarían |
| RN-M02-02 | La placa de vehículo es única | Un mismo volquete tendría dos identidades y la cobertura por titularidad (I2) sería incorrecta |
| RN-M02-03 | La titularidad del vehículo es obligatoria y pertenece al dominio cerrado {PROPIO, EXTERNO} | El indicador I2 quedaría sin clasificación posible |
| RN-M02-04 | Un vehículo EXTERNO debe tener transportista asociado | No se podría analizar cobertura por proveedor |
| RN-M02-05 | Un vehículo PROPIO no tiene transportista asociado | Se introduciría ambigüedad en la clasificación de titularidad |
| RN-M02-06 | El RUC tiene exactamente once dígitos numéricos | Registros inválidos en documentos formales |
| RN-M02-07 | Ninguna entidad de catálogo con registros dependientes se elimina físicamente | Se romperían las claves foráneas del histórico y se perderían ingresos del periodo de observación |
| RN-M02-08 | Una entidad desactivada no se ofrece en formularios operativos, pero sí aparece en consultas históricas | Los registros antiguos quedarían sin etiqueta legible |
| RN-M02-09 | La unidad de medida de todo producto es la tonelada | Los cálculos de stock mezclarían unidades incompatibles |

## Nota sobre RN-M02-09

La unidad única simplifica el alcance del proyecto y es coherente con la operación real: la balanza reporta en toneladas y todos los productos en alcance (Saranda, Molido) se manejan en esa unidad. Si en el futuro se incorporara un producto en otra unidad, esta regla debe revisarse antes de que el sistema acepte el registro.
