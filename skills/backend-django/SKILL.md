---
name: backend-django
description: Implementa el backend Django + Django REST Framework del sistema de control de producción y existencias — apps por módulo, capas models/services/selectors/serializers/views/permissions, transacciones, correlativo, filtros y formato uniforme de error. Úsala al crear o modificar cualquier app de apps/, al escribir un modelo, un caso de uso, un endpoint, un serializer o un filtro, y cuando se pida programar, implementar o levantar el backend, la API o un módulo M01 a M09.
---

# Backend Django

Carga antes `contexto-tesis` y `solid-proyecto`. Fuentes: `docs/00-arquitectura/ARQ-02_Arquitectura_Tecnica.md`,
`convenciones_codigo.md`, `modelo_datos_entidad_relacion.md` y el `notas.md` del módulo.

## Stack fijado

Django 5.x · Django REST Framework · PostgreSQL 16 · SimpleJWT · pytest-django ·
openpyxl / ReportLab (M06). No introduzcas dependencias fuera de esta lista sin justificarlo:
cada una es superficie que hay que defender en sustentación y que puede fallar en el despliegue de
la semana 8.

## Estructura

```
backend/
  config/                 settings, urls, wsgi/asgi
  apps/
    accounts/       M01   catalogo/  M02   ingresos/       M03
    salidas/        M04   existencias/ M05  reportes/       M06
    sincronizacion/ M07   auditoria/ M08   busqueda/       M09
  common/                 utilidades transversales, excepciones de dominio
```

El nombre de la app espeja el código del módulo. Dentro de cada una:

```
apps/ingresos/
    models.py         Entidades e invariantes (RN-*)
    services.py       Casos de uso (RS-*): orquestan, no contienen reglas
    selectors.py      Consultas de lectura, separadas de la escritura
    serializers.py    Traducción dominio <-> JSON
    views.py          Controladores REST (RF-*): solo entrada/salida HTTP
    permissions.py    Autorización por rol y por acción
    tests/
```

## Nomenclatura

Español para el dominio, inglés para el framework. Los términos del negocio tienen significado
preciso en la empresa y traducirlos introduce ambigüedad.

```python
apps/ingresos/models.py      class Ingreso, class TicketBalanza
apps/ingresos/services.py    def registrar_ingreso(...)
apps/ingresos/views.py       class IngresoViewSet
```

La entidad se llama **`Ingreso`**, no `IngresoVolquete`: así está en el modelo ER y en
`convenciones_codigo.md`.

## Reglas no negociables

**1. Cantidades en `DecimalField`, jamás `FloatField`.** El error acumulado del punto flotante sobre
cientos de movimientos produce desviaciones de centésimas que se confundirían con desviación real de
inventario y contaminarían el indicador I4. Tipos exactos del modelo ER: `decimal(8,2)` para pesos y
cantidades, `decimal(10,2)` para el saldo resultante, `decimal(6,2)` para capacidad.

**2. `hora_registro` NO usa `auto_now_add`.**

```python
class Ingreso(models.Model):
    correlativo = models.CharField(max_length=20, unique=True, editable=False)
    uuid_local = models.UUIDField(null=True, blank=True, unique=True)
    fecha_pesaje = models.DateField()
    hora_pesaje = models.TimeField()          # la ingresa el usuario (D-01)
    hora_registro = models.DateTimeField(editable=False)   # la asigna el servicio (D-01, D-03)
    hora_sincronizacion = models.DateTimeField(null=True, blank=True)  # solo auditoría
```

Para un ingreso capturado sin conexión el valor correcto es la hora de **captura local** que envía el
cliente, no la de inserción en la base (D-03). El servicio la asigna explícitamente: `timezone.now()`
en línea, o `hora_captura_local` validada en sincronización.

> `decisiones_diseno.md` D-01 dice `auto_now_add`; D-03 y `notas.md` de M03 dicen lo contrario y son
> los correctos. Sigue D-03. Está señalado como contradicción a corregir en la documentación.

**3. El correlativo nunca sale de `MAX(correlativo) + 1`.** Bajo concurrencia produce duplicados.
Dos implementaciones válidas (D-02): secuencia de PostgreSQL con `nextval`, o tabla de contadores con
`select_for_update()` dentro de la transacción. La segunda es preferible si el correlativo se
reinicia por año o lleva prefijo — que es el caso: `ING-{año}-{cinco dígitos}`. **Documenta cuál se
adoptó:** es pregunta previsible en sustentación.

**4. Una operación de escritura, una transacción.**

```python
with transaction.atomic():
    correlativo = generador.siguiente()
    ingreso = Ingreso.objects.create(...)
    servicio_stock.generar_movimiento_entrada(ingreso)
    auditoria.registrar(CREAR, ingreso, usuario)
```

Si falla el movimiento de stock, el ingreso no debe quedar registrado: un ingreso sin movimiento
rompe RN-M03-08 en silencio y descuadra el stock frente a los ingresos.

**5. Nada se borra.** No expongas `DELETE` en ningún ViewSet. La baja de catálogo es `PATCH
.../desactivar/`; la de un ingreso es `PATCH .../anular/` con motivo obligatorio (D-07). Un
`ModelViewSet` completo expone `destroy` por defecto: retíralo explícitamente.

**6. Los campos asignados por el servidor van `editable=False`** y toda solicitud que intente
modificar `correlativo` o `hora_registro` se rechaza con independencia del rol (RS-M03-10).

## Contrato de la API

```
POST   /api/v1/auth/login/                 M01
GET    /api/v1/catalogo/productos/         M02
GET    /api/v1/catalogo/vehiculos/         M02
POST   /api/v1/ingresos/                   M03
GET    /api/v1/ingresos/{id}/              M03
POST   /api/v1/salidas/                    M04
GET    /api/v1/existencias/                M05
GET    /api/v1/reportes/consolidado/       M06
POST   /api/v1/sincronizacion/lote/        M07
GET    /api/v1/auditoria/eventos/          M08
GET    /api/v1/busqueda/ingresos/          M09
```

Plural, con barra final. Acciones no CRUD como sub-ruta: `.../{id}/desactivar/`, `.../{id}/anular/`.

**Cuerpo de error uniforme**, en toda la API:

```json
{"codigo": "TARA_MAYOR_QUE_BRUTO", "mensaje": "La tara debe ser menor que el peso bruto", "detalles": {"campo": "tara_tn"}}
```

El `mensaje` **coincide literalmente** con el texto del criterio de aceptación de la historia. Las
pruebas lo verifican por igualdad exacta y el frontend lo muestra en el campo correspondiente, sin
reformular. Si cambias un mensaje, cambia también la HU — o rompes la prueba y la trazabilidad.

## Filtros

`django-filter` para los listados. Los filtros no son comodidad: son lo que alimenta los indicadores.

```
GET /api/v1/catalogo/vehiculos/?titularidad=PROPIO      -> denominador de I2
GET /api/v1/ingresos/?desde=&hasta=&producto=&titularidad=&usuario=
```

`titularidad` no es atributo del ingreso sino del vehículo asociado; se expone en el endpoint de
ingresos porque es la consulta directa que alimenta I2. Paginación de 25 registros por página
(HU-M03-05).

## Excepciones de dominio

Van en `common/`. El dominio lanza excepciones propias; la capa HTTP las traduce a códigos:

| Excepción de dominio | HTTP |
|---|---|
| `ErrorDeValidacionDeDominio` | 400 |
| `AccionNoAutorizada` | 403 |
| `ConflictoDeConcurrencia` | 409 |

`models.py` y `services.py` no importan nada de `rest_framework`. Si lo hacen, la regla de negocio
quedó atada al transporte y deja de ser reutilizable desde la cola de sincronización de M07.

## Al terminar un módulo

Ejecuta la verificación de `solid-proyecto` y comprueba que cada RN del módulo es localizable en el
código, que cada mensaje de error coincide con su criterio de aceptación y que los índices declarados
en el modelo ER §3 están en la **primera** migración, no añadidos después.
