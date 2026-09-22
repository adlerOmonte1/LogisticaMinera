# Notas de implementación — M09 Auditoría

## Backend (Django)

**App:** `apps/auditoria/` — ya existe como esqueleto en el repositorio; se completa en la fase de
preparación del backend.

### Estructura

```
apps/auditoria/
├── models/          EVENTO_AUDITORIA
├── migrations/
├── services/         ServicioAuditoria, el unico punto de escritura
├── repositories/     historial por entidad e identificador
├── serializers/  views/  permissions.py  filters.py  urls.py  tests/
```

### Modelo

```python
class EventoAuditoria(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT, editable=False)
    accion = models.CharField(max_length=20, choices=Accion.OPCIONES, editable=False)
    entidad = models.CharField(max_length=50, editable=False)
    id_entidad = models.PositiveIntegerField(editable=False)
    valores_anteriores = models.JSONField(null=True, blank=True, editable=False)
    valores_nuevos = models.JSONField(null=True, blank=True, editable=False)
    fecha_hora = models.DateTimeField(editable=False)
    direccion_ip = models.GenericIPAddressField(null=True, blank=True, editable=False)

    class Meta:
        indexes = [
            models.Index(fields=["entidad", "id_entidad"], name="idx_evento_entidad"),
        ]
```

Decisiones no obvias:

- **Todos los campos son `editable=False`.** No hay ningún flujo legítimo de edición de un evento
  ya creado (RN-M09-02); marcarlos así lo hace explícito en el modelo, no solo en la vista.
- **No hay endpoint de `PATCH` ni `DELETE` sobre eventos en ningún rol** (RNF-M09-02). El
  `ViewSet` expone únicamente `list` y `retrieve`.
- **`Accion.OPCIONES` vive en `common/eventos.py`**, no en `apps/auditoria/models/`. Es el
  catálogo único que exige RN-M09-05: todos los módulos importan de ahí, ninguno declara sus
  propias constantes de acción.

### El servicio como única puerta de escritura

```python
class ServicioAuditoria:
    def registrar(self, *, usuario, accion, entidad, id_entidad,
                   valores_anteriores=None, valores_nuevos=None, direccion_ip=None):
        EventoAuditoria.objects.create(
            usuario=usuario, accion=accion, entidad=entidad, id_entidad=id_entidad,
            valores_anteriores=valores_anteriores, valores_nuevos=valores_nuevos,
            fecha_hora=timezone.now(), direccion_ip=direccion_ip,
        )
```

Cada servicio de escritura de los demás módulos —`ServicioIngreso`, `ServicioLote`,
`ServicioValidacion`— recibe `ServicioAuditoria` inyectado y lo invoca como el último paso dentro de
su propia `transaction.atomic()` (RN-M09-01). **No existe una señal de Django (`post_save`) que
dispare el registro automáticamente.** Fue una decisión deliberada: una señal registraría el evento
después de que la instancia ya se guardó, fuera del control explícito del servicio, y sería fácil
que un cambio hecho por una migración de datos o por el shell de administración generara —o dejara
de generar— eventos sin que nadie lo hubiera decidido.

### Acceso rechazado

El evento `ACCESO_RECHAZADO` se registra desde la capa de permisos (`permissions.py` de cada app),
en el punto donde el `ViewSet` deniega la operación, antes de que cualquier lógica de negocio se
ejecute. Ese registro no está dentro de una transacción de escritura del dominio, porque no hay
ningún cambio de dominio que proteger: es una operación de solo auditoría.

## Frontend (Angular)

**Feature:** `features/auditoria/` — solo la consulta del historial; el registro de eventos no tiene
ninguna interfaz, porque no lo activa el usuario.

- La línea de tiempo distingue visualmente los eventos de escritura de los de acceso rechazado
  (RNF-M09-05), por ejemplo con un color de acento distinto, no solo con el texto de la acción.
- El componente de historial es de `ui/`, sin estado: recibe la lista de eventos ya resuelta y la
  presenta.

## Riesgo de implementación identificado

**El riesgo principal es que algún módulo nuevo olvide invocar el registro de auditoría en una de
sus rutas de escritura.**

Como el registro no es automático por diseño (para evitar el problema de la señal descrito arriba),
depende de que cada desarrollador recuerde invocar `ServicioAuditoria.registrar(...)` en cada
operación de creación, modificación y anulación. Es fácil que una ruta de excepción —por ejemplo, un
`ViewSet` genérico de DRF que expone `update()` sin pasar por el servicio de dominio— escriba en la
base sin dejar rastro.

Ninguna prueba de la operación en sí lo detecta, porque la operación funciona correctamente. La
defensa es una prueba por módulo, no por este, que después de ejecutar cada operación de escritura
consulta `EVENTO_AUDITORIA` y exige que exista exactamente un evento nuevo con la acción esperada.
Esa prueba debe añadirse en `notas.md` de cada módulo de escritura como parte de su criterio de
módulo terminado.

**Riesgo secundario:** que alguien exponga temporalmente un endpoint de administración para
«limpiar eventos antiguos» por espacio en disco, violando RN-M09-02. Si el volumen de
`EVENTO_AUDITORIA` se vuelve un problema real, la solución es archivar fuera de la base de datos
operativa, nunca eliminar.

## Dependencias

| Depende de | Para |
|---|---|
| M01 | Autenticación y atribución del usuario que consulta el historial |

| Es requerido por | Para |
|---|---|
| M01 | Registrar inicio de sesión, cierre de sesión y acceso rechazado |
| M02 | Registrar altas, ediciones y bajas del catálogo |
| M03 | Registrar creación, corrección y anulación de ingresos |
| M04 | Registrar el reconocimiento y la corrección de datos propuestos |
| M05 | Registrar el resultado de la validación de un ingreso |
| M06 | Registrar la apertura, el cierre y el paso de un lote por etapa |
| M08 | Registrar cada exportación |

## Pendientes que afectan a este módulo

| Pendiente | Efecto |
|---|---|
| Volumen esperado de eventos durante la ventana de operación | Condiciona si conviene una política de archivado antes de que RNF-M09-04 se vuelva difícil de sostener |
