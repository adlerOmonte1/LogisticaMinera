# Notas de implementación — M05 Existencias

## Backend (Django)

**App:** `apps/existencias/`

- `MovimientoStock` es la única tabla de escritura. No existe una tabla `Stock` con un campo actualizable: el saldo vive denormalizado en `saldo_resultante_tn` de cada movimiento, y la consulta lee el del último.
- Todos los campos de cantidad son `DecimalField(max_digits=10, decimal_places=2)`, nunca `FloatField` (RNF-M05-04).
- La generación del movimiento usa `select_for_update()` sobre el último movimiento del producto para calcular el saldo resultante bajo concurrencia. Sin ese bloqueo, dos ingresos simultáneos del mismo producto producen saldos denormalizados inconsistentes.
- `repositories/` concentra las consultas de lectura (saldos, kardex) y `services/` las de escritura (generación y reversión de movimientos). La separación no es ceremonial: las consultas de lectura son las que sostienen el indicador I3 y deben poder optimizarse sin tocar la lógica de escritura.
- La rutina de verificación de consistencia (A-M05-03) se implementa como comando de gestión de Django (`python manage.py verificar_saldos`), no como endpoint. Se ejecuta manualmente y su salida se archiva.

## Frontend (Angular)

**Feature:** `features/existencias/`

- La pantalla de existencias es la ruta predeterminada tras el login del rol Administrativo (RNF-M05-06). Cada paso de navegación eliminado reduce el tiempo medido por el indicador I3.
- El kardex usa scroll virtual (`cdk-virtual-scroll-viewport`) para no degradarse cuando el histórico crece.
- El formulario de ajuste muestra el saldo del sistema y la diferencia calculada **antes** de confirmar, para que el administrador vea exactamente qué va a registrar.
- No existe ningún componente de edición de stock. Si en una revisión de código aparece uno, es una violación de RN-M05-02.

## Sobre la denormalización

La decisión de denormalizar el saldo tiene un costo: si un movimiento antiguo se anula, todos los saldos resultantes posteriores de ese producto deben recalcularse. Es una operación de escritura que puede tocar muchas filas.

Se acepta ese costo porque las anulaciones son excepcionales mientras que las consultas de saldo son constantes, y porque el indicador I3 depende del tiempo de consulta, no del tiempo de anulación. La alternativa —calcular el saldo en cada consulta— degradaría el indicador de forma creciente a lo largo del periodo de medición.

Documentar esta decisión con su justificación es importante: es exactamente el tipo de compromiso técnico sobre el que un revisor externo puede preguntar.

## Dependencias

| Depende de | Para |
|---|---|
| M02 | Catálogo de productos |
| M03, M04 | Documentos fuente de los movimientos |
| M08 | Registro de eventos de ajuste |

| Es requerido por | Para |
|---|---|
| M03, M04 | Generación y reversión de movimientos |
| M06 | Saldos de cierre para los consolidados |
