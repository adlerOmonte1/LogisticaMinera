---
name: backend-django
description: Implementa el backend Django + Django REST Framework del sistema web inteligente de ingreso de mineral — apps por módulo, capas models/repositories/services/serializers/views/permissions, transacciones, código único, reconocimiento, validación y formato uniforme de error. Úsala al crear o modificar cualquier app de apps/, al escribir un modelo, un caso de uso, un endpoint, un serializer o un filtro, y cuando se pida programar, implementar o levantar el backend, la API o un módulo M01 a M09.
---

# Backend Django

Carga antes `contexto-tesis` y `solid-proyecto`. Fuentes:
`docs/model-c4/ARQ-02_Arquitectura_Tecnica.md`, `convenciones_codigo.md`,
`modelo_datos_entidad_relacion.md` y el `notas.md` del módulo.

## Stack fijado

Django 5.x · Django REST Framework · PostgreSQL 16 · SimpleJWT · Pillow · pytest-django ·
openpyxl (M08). El motor de reconocimiento **no** es una dependencia fija: su librería o SDK vive
únicamente en `apps/reconocimiento/motores/`, y se elige cuando D-12 se cierre. No introduzcas
dependencias fuera de esta lista sin justificarlo: cada una es superficie que hay que defender en
sustentación y que puede fallar en el despliegue.

## Estructura

```
backend/
  config/                 settings, urls, wsgi/asgi
  apps/
    accounts/         M01   catalogo/         M02   ingresos/       M03
    reconocimiento/    M04   validacion/        M05   trazabilidad/   M06
    consulta/          M07   consolidacion/     M08   auditoria/      M09
  utils/                  utilidades transversales, excepciones de dominio
```

El nombre de la app espeja el código del módulo. Dentro de cada una con entidad propia:

```
apps/ingresos/
    models/           Entidades e invariantes (RN-*), paquete
    repositories/     Consultas de lectura, separadas de la escritura
    services/         Casos de uso (RS-*): orquestan, no contienen reglas
    serializers/      Traducción dominio <-> JSON
    views/            Controladores REST (RF-*): solo entrada/salida HTTP
    permissions.py    Autorización por rol y por acción
    filters.py
    tests/
```

**M07 y M08 no llevan `models/` ni `migrations/`** (D-10): agregan y consultan sobre M03, M04, M05
y M06, sin entidad propia.

## Nomenclatura

Español para el dominio, inglés para el framework. Los términos del negocio tienen significado
preciso en la empresa y traducirlos introduce ambigüedad.

```python
apps/ingresos/models/ingreso.py        class Ingreso
apps/ingresos/services/registrar_ingreso.py   class ServicioIngreso
apps/ingresos/views/ingreso.py         class IngresoViewSet
apps/reconocimiento/motores/           class ReconocedorPaddleOCR (ejemplo de adaptador)
```

La entidad se llama **`Ingreso`**, según el modelo entidad-relación y `convenciones_codigo.md`.

## Reglas no negociables

**1. Cantidades en `DecimalField`, jamás `FloatField`.** El error acumulado del punto flotante sobre
cientos de registros produce desviaciones que se confundirían con diferencias reales entre el ticket
y lo registrado. Tipos exactos del modelo entidad-relación: `decimal(8,2)` para pesos, `decimal(6,2)`
para capacidad de vehículo, `decimal(4,3)` para confianza.

**2. `hora_inicio_registro` y `hora_fin_registro` NO usan `auto_now_add`.**

```python
class Ingreso(models.Model):
    codigo = models.CharField(max_length=20, unique=True, editable=False)
    imagen_ticket = models.ImageField(upload_to="tickets/%Y/%m/")
    fecha_hora_ticket = models.DateTimeField()                     # leida del ticket, editable
    hora_inicio_registro = models.DateTimeField(editable=False)    # la asigna el servicio (D-01)
    hora_fin_registro = models.DateTimeField(editable=False)       # la asigna el servicio (D-01)
    peso_neto_tn = models.DecimalField(max_digits=8, decimal_places=2)  # leido, no calculado
```

`auto_now_add` fijaría la hora de inserción en la base, que no es necesariamente el hecho que cada
marca debe describir (cuándo llegó la imagen, cuándo se confirmó). El servicio las asigna
explícitamente a través de un `Reloj` inyectado (D-01, ver `solid-proyecto`).

**3. `peso_neto_tn` no se calcula.** Es un dato del ticket, igual que el bruto y la tara. Calcularlo
como `peso_bruto_tn - tara_tn` haría que la regla V1 de M05 —que compara justamente esos dos
valores— nunca pudiera detectar un ticket incoherente, porque la comparación siempre daría cero
(RN-M03-04).

**4. El valor reconocido y el confirmado se guardan por separado.** `CampoReconocido` tiene
`valor_reconocido` y `valor_confirmado` como columnas distintas; nunca se sobrescribe la primera con
la segunda (D-13, RN-M04-02). Un campo sin lectura queda con `valor_reconocido` nulo, nunca con cero
ni con cadena vacía.

**5. El código nunca sale de `MAX(codigo) + 1`.** Bajo concurrencia produce duplicados. Dos
implementaciones válidas (D-02): secuencia de PostgreSQL con `nextval`, o tabla de contadores con
`select_for_update()` dentro de la transacción. **Documenta cuál se adoptó:** es pregunta previsible
en sustentación.

**6. El reconocimiento y la validación se inyectan, nunca se importan dentro del servicio.**

```python
class ServicioIngreso:
    def __init__(self, reconocedor: ReconocedorTicket, validador: ValidadorConsistencia,
                 generador_codigo, reloj, auditoria):
        ...
```

`apps/ingresos/services/` no importa `apps/reconocimiento/motores/` ni ninguna librería de un
proveedor. Solo conoce las interfaces `ReconocedorTicket` y `ValidadorConsistencia`. Es lo que
permite cambiar de motor cuando se cierre D-12, o añadir una regla de validación, sin tocar M03 ni
rehacer sus pruebas.

**7. Una operación de escritura, una transacción.**

```python
with transaction.atomic():
    codigo = generador_codigo.siguiente()
    ingreso = Ingreso.objects.create(..., codigo=codigo)
    guardar_campos_reconocidos(ingreso, resultado_reconocimiento)
    auditoria.registrar(usuario=usuario, accion="CREAR", entidad="INGRESO", id_entidad=ingreso.id)
```

Si falla el registro del evento de auditoría, el ingreso no debe quedar registrado: una operación
sin su rastro rompe RN-M09-01 en silencio.

**8. Nada se borra.** No expongas `DELETE` en ningún ViewSet. La baja de catálogo es `PATCH
.../desactivar/`; la de un ingreso es `PATCH .../anular/` con motivo obligatorio (D-07). Un
`ModelViewSet` completo expone `destroy` por defecto: retíralo explícitamente con `ViewSetBase`
(`GUIA_MARCO_DE_TRABAJO.md` §2.7).

**9. Los campos asignados por el servidor van `editable=False`** y toda solicitud que intente
modificar `codigo`, `hora_inicio_registro` o `hora_fin_registro` se rechaza con independencia del
rol.

## Contrato de la API

```
POST   /api/v1/auth/login/                       M01
GET    /api/v1/catalogo/vehiculos/                M02
GET    /api/v1/catalogo/tipos-mineral/            M02
POST   /api/v1/ingresos/borradores/               M03
POST   /api/v1/ingresos/                          M03
GET    /api/v1/reconocimientos/{id}/              M04
GET    /api/v1/ingresos/{id}/validaciones/        M05
POST   /api/v1/lotes/                             M06
POST   /api/v1/lotes/{id}/etapas/                 M06
GET    /api/v1/consulta/ingresos/                 M07
GET    /api/v1/consolidacion/mensual/             M08
GET    /api/v1/auditoria/{entidad}/{id}/          M09
```

Plural, con barra final. Acciones no CRUD como sub-ruta: `.../{id}/desactivar/`, `.../{id}/anular/`.

**Cuerpo de error uniforme**, en toda la API:

```json
{"codigo": "PESO_FUERA_DE_RANGO", "mensaje": "El peso neto está fuera del rango de carga del vehículo ABC-123", "detalles": {"campo": "peso_neto_tn"}}
```

El `mensaje` **coincide literalmente** con el texto del criterio de aceptación de la historia o con
el mensaje de la regla V1 a V5. Las pruebas lo verifican por igualdad exacta y el frontend lo
muestra en el campo correspondiente, sin reformular.

## Filtros

`django-filter` para los listados.

```
GET /api/v1/consulta/ingresos/?placa=&fecha=&fecha_fin=
GET /api/v1/consulta/ingresos/?tipo_mineral=&titularidad=&estado=
```

`titularidad` no es atributo del ingreso sino del vehículo asociado; se expone en el filtro de
consulta porque así se agrupa por tipo de vehículo sin duplicar el dato. Paginación de 25 registros
por página.

## Excepciones de dominio

Van en `utils/`. El dominio lanza excepciones propias; la capa HTTP las traduce a códigos:

| Excepción de dominio | HTTP |
|---|---|
| `ReglaDeNegocioError` | 400 o 422 |
| `AccionNoAutorizada` | 403 |
| `ConflictoDeConcurrencia` | 409 |

`models/` y `services/` no importan nada de `rest_framework`. Si lo hacen, la regla de negocio
queda atada al transporte HTTP.

## Al terminar un módulo

Ejecuta la verificación de `solid-proyecto` y comprueba que cada RN del módulo es localizable en el
código, que cada mensaje de error coincide con su criterio de aceptación o con el mensaje literal de
su regla V1 a V5, y que los índices declarados en el modelo entidad-relación §3 están en la
**primera** migración, no añadidos después.
