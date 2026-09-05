# Notas de implementación — M04 Salidas y movimientos

## Backend (Django)

**App:** `apps/salidas/`

- `TipoMovimiento` como `models.TextChoices`. La validación condicional (cliente obligatorio si VENTA, motivo obligatorio si MERMA) va en `Salida.clean()`, no en el serializer, por la misma razón que en M02: debe aplicarse a cualquier origen del dato.
- La consulta de saldo previa (CA02) es informativa y ocurre en el cliente. **No debe convertirse en una validación de servidor que bloquee**, según RN-M04-06. Si en el futuro alguien "arregla" esto añadiendo un bloqueo, rompería el diseño deliberadamente.
- La reversión de stock al anular no crea un movimiento con cantidad negativa: crea un movimiento de tipo ENTRADA con referencia a la salida anulada. Mantener las cantidades siempre positivas y expresar el signo en el tipo simplifica los cálculos agregados y evita errores de signo en los reportes de M06.

## Frontend (Angular)

**Feature:** `features/salidas/`

- El selector de tipo de movimiento controla la visibilidad condicional de los campos cliente y motivo mediante `computed()` sobre un signal, no mediante `*ngIf` anidados sobre el valor crudo del formulario.
- El diálogo de advertencia por stock insuficiente usa un modal con confirmación explícita (RNF-M04-04), no un `confirm()` nativo del navegador, que en móvil es fácil de descartar por accidente.

## Dependencias

| Depende de | Para |
|---|---|
| M01 | Autenticación y control de rol (el Supervisor no registra salidas) |
| M02 | Catálogo de productos y clientes |
| M05 | Consulta de saldo y generación de movimientos |
| M08 | Registro de eventos |

| Es requerido por | Para |
|---|---|
| M05 | Cálculo del saldo vigente |
| M06 | Consolidado de despachos del periodo |

## Bloqueo activo

Este módulo **no puede cerrarse** hasta que se defina el criterio de estimación de merma por humedad. Se puede implementar la funcionalidad completa —el tipo MERMA es un enumerado más—, pero la interpretación del indicador I4 queda suspendida. Consultar con la asesora antes de la semana 5.
