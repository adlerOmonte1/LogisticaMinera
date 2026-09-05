# Notas de implementación — M03 Registro de ingresos

## Backend (Django)

**App:** `apps/ingresos/`

### Modelo

```python
class Ingreso(models.Model):
    correlativo = models.CharField(max_length=20, unique=True, editable=False)
    uuid_local = models.UUIDField(null=True, blank=True, unique=True)
    fecha_pesaje = models.DateField()
    hora_pesaje = models.TimeField()
    hora_registro = models.DateTimeField(editable=False)   # ver D-01 y D-03
    hora_sincronizacion = models.DateTimeField(null=True, blank=True)
    # ... resto de campos
```

`hora_registro` **no** usa `auto_now_add`. La razón está en la decisión D-03: para un ingreso capturado sin conexión, el valor correcto es la hora de captura local que envía el cliente, no la hora de inserción en la base. El servicio la asigna explícitamente: `timezone.now()` en línea, o `hora_captura_local` validada en sincronización.

### Correlativo

No usar `Ingreso.objects.aggregate(Max('correlativo'))`. Bajo concurrencia produce duplicados. Dos opciones aceptables:

1. Secuencia de PostgreSQL (`CREATE SEQUENCE ingreso_correlativo_seq`) consultada con `nextval`.
2. Tabla de contadores con `select_for_update()` dentro de la transacción.

La segunda es preferible si el correlativo debe reiniciarse por año o llevar prefijo. Documentar cuál se adoptó, porque es una pregunta previsible en sustentación.

### Servicio

`registrar_ingreso()` recibe el generador de correlativo por inyección, no lo instancia internamente. Esto permite sustituirlo por uno determinista en las pruebas sin tocar la lógica del caso de uso (principio de inversión de dependencias).

Toda la operación —correlativo, persistencia, movimiento de stock, evento de auditoría— ocurre en una única transacción con `transaction.atomic()`. Si falla el movimiento de stock, el ingreso no debe quedar registrado: un ingreso sin movimiento rompería RN-M03-08 de forma silenciosa.

### Índices

Los declarados en `../../00-arquitectura/modelo_datos_entidad_relacion.md` §3 deben crearse desde la primera migración, no añadirse al final. El indicador I5 se mide sobre el sistema en producción y una migración de índices a mitad de la ventana de observación introduciría un cambio no controlado en las condiciones de medición.

## Frontend (Angular)

**Feature:** `features/ingresos/`

- Formulario reactivo con `valueChanges` sobre peso bruto y tara para recalcular el neto (HU-M03-02, CA02). El campo neto es `readonly`, no `disabled`: los campos deshabilitados no se envían en el payload.
- Persistencia del borrador en IndexedDB con cada cambio, para cumplir RNF-M03-06. Se limpia al confirmar el registro.
- El teclado numérico se fuerza con `inputmode="decimal"` en los campos de peso (RNF-M03-04).
- Los mensajes de error del servidor se muestran en el campo correspondiente, no en un cuadro genérico. Los textos coinciden literalmente con los criterios de aceptación, para que las pruebas puedan verificarlos por igualdad exacta.

## Riesgo de implementación identificado

El punto más probable de fallo es la asignación del correlativo bajo sincronización simultánea de M07. Debe probarse explícitamente con dos clientes enviando lotes al mismo tiempo (caso de prueba en `../../03-pruebas/`). No basta con probar el alta en línea.

## Dependencias

| Depende de | Para |
|---|---|
| M01 | Autenticación y atribución del registro al usuario |
| M02 | Catálogos de producto y vehículo |
| M05 | Generación y reversión de movimientos de stock |
| M08 | Registro de eventos de creación, modificación y anulación |

| Es requerido por | Para |
|---|---|
| M05 | Cálculo de existencias |
| M06 | Consolidados de producción |
| M07 | Captura sin conexión del mismo formulario |
| M09 | Búsqueda de ingresos |
