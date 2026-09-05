# Guía definitiva del marco de trabajo

**Documento:** transversal
**Aplica a:** `backend/` (Django 5 + DRF + PostgreSQL 16) y `frontend/` (Angular 17+ PWA)
**Depende de:** `ARQ-02_Arquitectura_Tecnica.md`, `convenciones_codigo.md`, `decisiones_diseno.md`, `modelo_datos_entidad_relacion.md`

Esta guía es operativa: se sigue de arriba abajo una sola vez, en la semana 1, y deja el esqueleto listo para que M01…M09 se implementen sin volver a discutir estructura. Todo lo que aquí se fija ya estaba decidido en los documentos de arquitectura; lo que se agrega es el *cómo*.

---

## 0. Requisitos previos

| Herramienta | Versión | Verificación |
|---|---|---|
| Python | 3.12.x | `python3 --version` |
| Node.js | 20 LTS | `node --version` |
| PostgreSQL | 16 | `psql --version` |
| Angular CLI | 17+ | `npx @angular/cli version` |
| Git | cualquiera | `git --version` |

No se instala Angular CLI globalmente: se usa `npx` para que la versión quede fijada en `package.json` y el entorno sea reproducible (requisito de la ficha técnica).

---

## 1. Base de datos PostgreSQL

### 1.1 Creación

```bash
psql -U postgres -c "CREATE DATABASE logistica_minera ENCODING 'UTF8';"
psql -U postgres -c "CREATE USER logistica WITH PASSWORD 'cambiar_en_produccion';"
psql -U postgres -c "ALTER ROLE logistica SET client_encoding TO 'utf8';"
psql -U postgres -c "ALTER ROLE logistica SET default_transaction_isolation TO 'read committed';"
psql -U postgres -c "ALTER ROLE logistica SET timezone TO 'America/Lima';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE logistica_minera TO logistica;"
```

`timezone = America/Lima` no es cosmético: el indicador I1 es una diferencia de tiempos entre la hora del ticket de balanza (local) y la hora asignada por el servidor. Un desfase de zona horaria contamina la medición de la tesis.

### 1.2 Tres bases, tres entornos

```
logistica_minera_dev     desarrollo local, datos de prueba
logistica_minera_pre     preproducción, pruebas de carga JMeter (semana 8)
logistica_minera         producción, donde se recolecta el postest
```

Nunca se ejecutan pruebas de carga contra producción: alterarían los tiempos de respuesta que sostienen el RNF de eficiencia de desempeño.

### 1.3 Secuencia del correlativo (D-02)

El correlativo lo asigna el servidor, nunca el dispositivo. Se implementa con una secuencia nativa de PostgreSQL, creada en una migración de Django (nunca a mano en el servidor, o el entorno deja de ser reproducible):

```python
# apps/ingresos/migrations/0002_secuencia_correlativo.py
from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [("ingresos", "0001_initial")]
    operations = [
        migrations.RunSQL(
            sql="CREATE SEQUENCE IF NOT EXISTS seq_ingreso_correlativo START 1;",
            reverse_sql="DROP SEQUENCE IF EXISTS seq_ingreso_correlativo;",
        ),
    ]
```

`MAX(correlativo) + 1` está prohibido: dos supervisores sincronizando a la vez producirían el mismo número y el ingreso dejaría de ser identificable de forma única.

---

## 2. Backend — Django

### 2.1 Entorno y dependencias

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

`requirements/base.txt`:

```
Django==5.0.*
djangorestframework==3.15.*
djangorestframework-simplejwt==5.3.*
psycopg[binary]==3.1.*
django-environ==0.11.*
django-cors-headers==4.3.*
django-filter==24.*
drf-spectacular==0.27.*
openpyxl==3.1.*
reportlab==4.1.*
```

`requirements/dev.txt`:

```
-r base.txt
pytest==8.*
pytest-django==4.8.*
factory-boy==3.3.*
ruff==0.4.*
django-extensions==3.2.*
```

```bash
pip install -r requirements/dev.txt
```

### 2.2 Esqueleto del proyecto

```bash
django-admin startproject config .
mkdir -p apps utils
touch apps/__init__.py utils/__init__.py

for m in accounts catalogo ingresos salidas existencias reportes sincronizacion auditoria busqueda; do
  mkdir -p apps/$m
  python manage.py startapp $m apps/$m
  # archivos sueltos -> paquetes
  for capa in models repositories services serializers views; do
    rm -f apps/$m/$capa.py
    mkdir -p apps/$m/$capa && touch apps/$m/$capa/__init__.py
  done
  mkdir -p apps/$m/tests && touch apps/$m/tests/__init__.py
  touch apps/$m/permissions.py apps/$m/filters.py apps/$m/urls.py
  rm -f apps/$m/admin.py apps/$m/tests.py
done
```

`startapp` crea `models.py`, `views.py` y `tests.py` como archivos; el bucle los sustituye por
paquetes con `__init__.py`. Se elimina `admin.py` de las apps de dominio: el admin de Django no es
una interfaz del sistema y exponer por ahí un borrado físico contradice D-07.

Después de `startapp`, en cada `apps/<app>/apps.py` corregir el `name` para que incluya el paquete:

```python
class IngresosConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.ingresos"
    verbose_name = "M03 — Registro de ingresos"
```

El `verbose_name` con el código de módulo hace que el admin de Django sea, sin trabajo extra, una vista de la trazabilidad módulo → código.

### 2.3 Árbol resultante

```
backend/
  manage.py
  .env                      NO versionado
  .env.example              versionado
  pytest.ini
  requirements/
    base.txt  dev.txt  prod.txt
  config/
    settings/
      __init__.py  base.py  dev.py  pre.py  prod.py
    urls.py  wsgi.py  asgi.py
  utils/
    excepciones.py          excepciones de dominio (no importan DRF)
    manejador_errores.py    respuesta uniforme {codigo, mensaje, detalles}
    modelos.py              ModeloBase (creado_en, actualizado_en)
    vistas.py               ViewSetBase sin destroy (D-07)
    permisos.py             permisos por acción reutilizables
    paginacion.py           25 por página (HU-M03-05)
    query_builder.py        armado mecánico de Q(), sin reglas de negocio
    serializer_mixin.py
    throttles.py            evidencia del RNF de desempeño (JMeter, semana 8)
  apps/
    accounts/       M01
    catalogo/       M02
    ingresos/       M03
    salidas/        M04
    existencias/    M05
    reportes/       M06
    sincronizacion/ M07
    auditoria/      M08
    busqueda/       M09
```

Y dentro de cada app, paquetes en lugar de archivos sueltos:

```
apps/ingresos/
  migrations/       los índices del modelo ER §3, desde la PRIMERA migración
  models/           entidades e invariantes (RN)
  repositories/     LECTURA. No escribe nunca (D-09)
  services/         casos de uso (RS): transacción e inyección de dependencias
  serializers/      dominio <-> JSON, sin reglas de negocio
  views/            solo HTTP (RF)
  permissions.py    por acción: PuedeRegistrarIngreso, PuedeAnularIngreso (ISP)
  filters.py        django-filter; alimenta I2 e I5
  urls.py
  apps.py           verbose_name = "M03 — Registro de ingresos"
  tests/
```

Cada paquete reexporta en su `__init__.py`:

```python
# apps/catalogo/models/__init__.py
from .producto import Producto
from .vehiculo import Vehiculo
from .transportista import Transportista
from .cliente import Cliente

__all__ = ["Producto", "Vehiculo", "Transportista", "Cliente"]
```

Sin esto Django detecta los modelos igual, pero mover un archivo rompe las migraciones y las
referencias por cadena (`"catalogo.Vehiculo"`).

### 2.4 Configuración por entornos

`config/settings/base.py` (fragmentos que importan):

```python
import environ
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("DJANGO_SECRET_KEY")
LANGUAGE_CODE = "es-pe"
TIME_ZONE = "America/Lima"
USE_TZ = True

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "django_filters",
    "corsheaders",
    "drf_spectacular",
    "apps.accounts",
    "apps.catalogo",
    "apps.ingresos",
    "apps.salidas",
    "apps.existencias",
    "apps.reportes",
    "apps.sincronizacion",
    "apps.auditoria",
    "apps.busqueda",
]

DATABASES = {"default": env.db("DATABASE_URL")}

AUTH_USER_MODEL = "accounts.Usuario"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
    "DEFAULT_PAGINATION_CLASS": "utils.paginacion.PaginacionEstandar",
    "PAGE_SIZE": 25,
    "EXCEPTION_HANDLER": "utils.manejador_errores.manejador_uniforme",
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}
```

`.env.example` (versionado, sin secretos reales):

```
DJANGO_SETTINGS_MODULE=config.settings.dev
DJANGO_SECRET_KEY=cambiar
DEBUG=True
DATABASE_URL=postgres://logistica:cambiar_en_produccion@localhost:5432/logistica_minera_dev
CORS_ALLOWED_ORIGINS=http://localhost:4200
JWT_ACCESS_MINUTES=30
JWT_REFRESH_DAYS=7
```

### 2.5 Las capas, con un ejemplo completo de M03

La regla de asignación de `ARQ-02` §3.1 es la única que hay que memorizar: **si una validación puede enunciarse sin mencionar HTTP, no vive en `views/`.**

**`models/` — invariantes del dominio (RN)**

```python
# apps/ingresos/models/ingreso.py
from django.core.exceptions import ValidationError
from django.db import models
from utils.modelos import ModeloBase

class Ingreso(ModeloBase):
    class Estado(models.TextChoices):
        REGISTRADO = "REGISTRADO", "Registrado"
        ANULADO = "ANULADO", "Anulado"

    correlativo = models.CharField(max_length=20, unique=True, editable=False)
    uuid_local = models.UUIDField(null=True, blank=True, unique=True)
    fecha_pesaje = models.DateField()
    hora_pesaje = models.TimeField()                      # del ticket (D-01)
    hora_registro = models.DateTimeField(editable=False)  # del servidor (D-01/D-03)
    hora_sincronizacion = models.DateTimeField(null=True, blank=True)
    vehiculo = models.ForeignKey("catalogo.Vehiculo", on_delete=models.PROTECT)
    producto = models.ForeignKey("catalogo.Producto", on_delete=models.PROTECT)
    peso_bruto_tn = models.DecimalField(max_digits=8, decimal_places=2)
    tara_tn = models.DecimalField(max_digits=8, decimal_places=2)
    peso_neto_tn = models.DecimalField(max_digits=8, decimal_places=2, editable=False)
    numero_ticket = models.CharField(max_length=20)
    usuario_registro = models.ForeignKey("accounts.Usuario", on_delete=models.PROTECT)
    capturado_offline = models.BooleanField(default=False)
    estado = models.CharField(max_length=12, choices=Estado.choices, default=Estado.REGISTRADO)
    motivo_anulacion = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "ingreso"
        indexes = [
            models.Index(fields=["correlativo"], name="idx_ingreso_correlativo"),
            models.Index(fields=["fecha_pesaje", "producto"], name="idx_ingreso_fecha_prod"),
            models.Index(fields=["vehiculo"], name="idx_ingreso_vehiculo"),
        ]

    def clean(self):
        # RN-M03-01: la tara nunca supera al peso bruto
        if self.tara_tn >= self.peso_bruto_tn:
            raise ValidationError({"tara_tn": "La tara no puede ser mayor o igual al peso bruto."})
        # RN-M03-02: el pesaje nunca es posterior al registro
        if self.hora_registro and self.momento_pesaje() > self.hora_registro:
            raise ValidationError({"hora_pesaje": "La hora de pesaje no puede ser posterior a la hora de registro."})
        # D-07: la anulación exige motivo
        if self.estado == self.Estado.ANULADO and not self.motivo_anulacion:
            raise ValidationError({"motivo_anulacion": "Se requiere motivo para anular un ingreso."})

    def momento_pesaje(self):
        from datetime import datetime
        from django.utils.timezone import make_aware
        return make_aware(datetime.combine(self.fecha_pesaje, self.hora_pesaje))

    def save(self, *args, **kwargs):
        self.peso_neto_tn = self.peso_bruto_tn - self.tara_tn
        self.full_clean()
        super().save(*args, **kwargs)
```

Los mensajes de error están en español y **coinciden literalmente** con los criterios de aceptación de las historias (`ARQ-02` §6). Esto convierte a las pruebas en evidencia directa de los CA.

**`services/` — casos de uso (RS). Orquesta, no valida reglas.**

```python
# apps/ingresos/services/registrar_ingreso.py
from django.db import transaction
from django.utils import timezone
from apps.auditoria.services import registrar_evento
from apps.existencias.services import asentar_movimiento

@transaction.atomic
def registrar_ingreso(*, datos, usuario, generador_correlativo, hora_captura_local=None):
    """RS-M03-01. Devuelve el Ingreso persistido con correlativo definitivo."""
    hora_registro = hora_captura_local or timezone.now()   # D-03
    if hora_registro > timezone.now():
        raise ReglaDeNegocioError("La hora de captura no puede ser posterior a la hora del servidor.")

    ingreso = Ingreso(
        **datos,
        usuario_registro=usuario,
        hora_registro=hora_registro,
        correlativo=generador_correlativo(),               # D-02, inyectado (DIP)
        capturado_offline=hora_captura_local is not None,
    )
    ingreso.save()
    asentar_movimiento(ingreso=ingreso)                    # M05: todo ingreso genera un movimiento
    registrar_evento(usuario=usuario, accion="CREAR", instancia=ingreso)  # M08
    return ingreso
```

El generador de correlativo entra **por parámetro**, no importado dentro de la función: es la inversión de dependencias de `ARQ-02` §5 y es lo que permite un correlativo determinista en pruebas.

**`repositories/` — lectura, separada de la escritura (D-09)**

```python
# apps/ingresos/repositories/ingreso.py
class RepositorioIngreso:
    """Solo lectura: ni save, ni create, ni update, ni delete."""

    def listar(self, *, filtros=None):
        return (
            Ingreso.objects
            .select_related("vehiculo", "producto", "usuario_registro")
            .filter(**(filtros or {}))
            .order_by("-hora_registro")
        )

    def por_correlativo(self, correlativo: str) -> Ingreso | None:
        return self.listar().filter(correlativo=correlativo).first()
```

Clase concreta, sin interfaz ni `Protocol`: la abstracción se crea cuando una prueba exige
sustituirla, y aquí no la exige (D-09). Devuelve entidades o `QuerySet`, nunca diccionarios listos
para la respuesta — eso es trabajo del serializer.

**`views/` — solo HTTP (RF)**

```python
# apps/ingresos/views/ingreso.py
class IngresoViewSet(ViewSetBase):          # sin destroy (D-07)
    serializer_class = IngresoSerializer
    permission_classes = [PuedeRegistrarIngreso]
    repositorio = RepositorioIngreso()

    def get_queryset(self):
        return self.repositorio.listar()

    def create(self, request):
        entrada = IngresoSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        ingreso = registrar_ingreso(
            datos=entrada.validated_data,
            usuario=request.user,
            generador_correlativo=correlativo_por_secuencia,
        )
        return Response(IngresoSerializer(ingreso).data, status=201)
```

### 2.6 Respuesta uniforme de error (`ARQ-02` §6)

```python
# utils/manejador_errores.py
from rest_framework.views import exception_handler
from rest_framework.response import Response
from utils.excepciones import ReglaDeNegocioError

def manejador_uniforme(exc, context):
    if isinstance(exc, ReglaDeNegocioError):
        return Response(
            {"codigo": exc.codigo, "mensaje": str(exc), "detalles": exc.detalles},
            status=422,
        )
    respuesta = exception_handler(exc, context)
    if respuesta is not None:
        respuesta.data = {
            "codigo": f"HTTP_{respuesta.status_code}",
            "mensaje": _mensaje_legible(respuesta.data),
            "detalles": respuesta.data,
        }
    return respuesta
```

El frontend puede escribir **un solo** interceptor de errores porque la forma del cuerpo es siempre la misma. Esa es la ganancia concreta de la convención.

### 2.7 ViewSet base sin borrado (D-07)

`ModelViewSet` expone `destroy` por defecto. D-07 dice que nada se borra: la baja de catálogo es
`PATCH .../desactivar/` y la de un ingreso `PATCH .../anular/` con motivo. Se retira **una vez**, en
la clase base, no viewset por viewset:

```python
# utils/vistas.py
from rest_framework import mixins, viewsets

class ViewSetBase(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    """CRUD sin D: ningún endpoint del sistema borra físicamente (D-07)."""
```

Heredar de `ViewSetBase` en lugar de `ModelViewSet` convierte la decisión en algo que no se puede
olvidar por descuido en un módulo nuevo. Si alguien necesita `DELETE`, tiene que escribirlo a mano —
y ahí la revisión lo ve.

### 2.8 Rutas

```python
# config/urls.py
urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/auth/", include("apps.accounts.urls")),
    path("api/v1/catalogo/", include("apps.catalogo.urls")),
    path("api/v1/ingresos/", include("apps.ingresos.urls")),
    path("api/v1/salidas/", include("apps.salidas.urls")),
    path("api/v1/existencias/", include("apps.existencias.urls")),
    path("api/v1/reportes/", include("apps.reportes.urls")),
    path("api/v1/sincronizacion/", include("apps.sincronizacion.urls")),
    path("api/v1/auditoria/", include("apps.auditoria.urls")),
    path("api/v1/busqueda/", include("apps.busqueda.urls")),
    path("api/v1/esquema/", SpectacularAPIView.as_view()),
    path("api/v1/docs/", SpectacularSwaggerView.as_view(url_name="schema")),
]
```

### 2.9 Pruebas

`pytest.ini`:

```ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings.dev
python_files = test_*.py
addopts = -ra --strict-markers
```

Una prueba por criterio de aceptación, nombrada con su código:

```python
# apps/ingresos/tests/test_reglas.py
import pytest
from django.core.exceptions import ValidationError

@pytest.mark.django_db
def test_RN_M03_02_pesaje_posterior_al_registro_es_rechazado(ingreso_factory):
    with pytest.raises(ValidationError) as e:
        ingreso_factory(hora_pesaje="23:59", fecha_pesaje="2026-12-31")
    assert "posterior a la hora de registro" in str(e.value)
```

```bash
pytest -q
```

El nombre de la prueba contiene el código de la regla: la matriz de trazabilidad `RN → prueba` se genera con `pytest --collect-only`, no se mantiene a mano.

### 2.10 Orden de arranque

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

---

## 3. Frontend — Angular

### 3.1 Creación

```bash
cd frontend
npx @angular/cli@17 new logistica-minera \
  --standalone --routing --style=scss --ssr=false --skip-git
cd logistica-minera
ng add @angular/pwa            # M07 desde la semana 1 (D-04)
npm i idb                      # cola offline en IndexedDB
```

`ng add @angular/pwa` se ejecuta **ahora**, no en la semana 4. La D-04 es explícita: el service worker es arquitectura, no una funcionalidad agregable.

### 3.2 Estructura

```
src/app/
  core/                        una sola instancia, cargado al inicio
    interceptors/
      auth.interceptor.ts        adjunta el JWT
      error.interceptor.ts       traduce {codigo, mensaje, detalles}
      offline.interceptor.ts     encola si no hay red (M07)
    services/
      auth.service.ts
      cola-sincronizacion.service.ts
      notificacion.service.ts
    guards/
      sesion.guard.ts
      rol.guard.ts
  shared/                      componentes reutilizables sin estado
    components/  pipes/  directives/
  models/                      interfaces del dominio, espejo del ERD
    ingreso.model.ts  vehiculo.model.ts  producto.model.ts ...
  features/                    una carpeta por módulo, carga diferida
    autenticacion/    M01
    catalogo/         M02
    ingresos/         M03
    salidas/          M04
    existencias/      M05
    reportes/         M06
    auditoria/        M08
    busqueda/         M09
  app.routes.ts
  app.config.ts
environments/
  environment.ts  environment.pre.ts  environment.prod.ts
```

M07 no tiene carpeta propia en `features/`: es transversal y vive en `core/` (interceptor + cola). Esa es la traducción al frontend de la D-04.

### 3.3 Rutas con carga diferida

```typescript
// app.routes.ts
export const routes: Routes = [
  { path: 'login', loadComponent: () => import('./features/autenticacion/login.component').then(m => m.LoginComponent) },
  {
    path: 'ingresos',
    canActivate: [sesionGuard, rolGuard(['ADMINISTRADOR', 'SUPERVISOR'])],
    loadChildren: () => import('./features/ingresos/ingresos.routes').then(m => m.INGRESOS_ROUTES),
  },
  { path: '', redirectTo: 'ingresos', pathMatch: 'full' },
  { path: '**', loadComponent: () => import('./shared/components/no-encontrado.component').then(m => m.NoEncontradoComponent) },
];
```

### 3.4 Modelo y servicio de feature

```typescript
// models/ingreso.model.ts
export interface Ingreso {
  id: number;
  correlativo: string;
  uuidLocal?: string;
  fechaPesaje: string;   // ISO
  horaPesaje: string;    // HH:mm
  horaRegistro: string;
  vehiculoId: number;
  productoId: number;
  pesoBrutoTn: number;
  taraTn: number;
  pesoNetoTn: number;
  numeroTicket: string;
  estado: 'REGISTRADO' | 'ANULADO';
}
```

```typescript
// features/ingresos/ingresos.service.ts
@Injectable({ providedIn: 'root' })
export class IngresosService {
  private http = inject(HttpClient);
  private base = `${environment.apiUrl}/ingresos/`;

  listar(filtros: FiltroIngreso = {}): Observable<Pagina<Ingreso>> {
    return this.http.get<Pagina<Ingreso>>(this.base, { params: toParams(filtros) });
  }

  registrar(payload: NuevoIngreso): Observable<Ingreso> {
    return this.http.post<Ingreso>(this.base, payload);
  }
}
```

Ningún componente inyecta `HttpClient` directamente (`ARQ-02` §4). El componente inyecta el servicio del feature; así el interceptor offline es el único punto que decide entre red y cola.

### 3.5 Estado con signals

```typescript
@Component({ standalone: true, selector: 'app-ingresos-lista', /* ... */ })
export class IngresosListaComponent {
  private servicio = inject(IngresosService);
  ingresos = signal<Ingreso[]>([]);
  cargando = signal(false);
  pendientesDeSincronizar = inject(ColaSincronizacionService).pendientes; // signal

  ngOnInit() {
    this.cargando.set(true);
    this.servicio.listar().subscribe({
      next: p => this.ingresos.set(p.results),
      complete: () => this.cargando.set(false),
    });
  }
}
```

### 3.6 Cola offline (M07)

```typescript
// core/services/cola-sincronizacion.service.ts
@Injectable({ providedIn: 'root' })
export class ColaSincronizacionService {
  pendientes = signal<number>(0);

  async encolar(registro: NuevoIngreso): Promise<void> {
    const db = await openDB('logistica', 1, {
      upgrade: d => d.createObjectStore('cola', { keyPath: 'uuidLocal' }),
    });
    await db.put('cola', {
      ...registro,
      uuidLocal: crypto.randomUUID(),          // D-02: identificador temporal
      horaCapturaLocal: new Date().toISOString(), // D-03
    });
    this.pendientes.update(n => n + 1);
  }

  async sincronizar(): Promise<void> {
    // POST /api/v1/sincronizacion/lote/ ; el servidor asigna el correlativo definitivo
  }
}
```

El cliente genera `uuidLocal` y `horaCapturaLocal`; **nunca** un correlativo. El servidor persiste `horaCapturaLocal` como `hora_registro` y añade `hora_sincronizacion` solo para auditoría. Esta es la implementación literal de D-02 y D-03, y es la que preserva los indicadores I1 e I2.

### 3.7 Regla que no se rompe (D-08)

Angular valida en el formulario para mejorar la experiencia, pero la validación autoritativa está en el backend. Un registro que llega por la cola de sincronización no pasa por el formulario y debe someterse a las mismas reglas. Concretamente: toda validación de `models/` puede duplicarse en un `Validators` de Angular, pero **ninguna** puede existir solo allí.

### 3.8 Comandos

```bash
ng serve            # http://localhost:4200
ng build            # producción
ng test
```

---

## 4. Flujo de trabajo de un módulo, de principio a fin

Para cada módulo Mxx, en este orden. No se salta ningún paso: cada uno produce evidencia citable en la sustentación.

1. `git checkout -b feature/Mxx-nombre` (desde `develop`).
2. Leer `docs/modulos/Mxx-*/requisitos/` — RU, RS, RF, RNF, RN. (M01 y M02 usan `requerimientos/`;
   el resto usa `requisitos/`. Es una inconsistencia conocida de la documentación.)
3. Backend: `models/` (RN) → `repositories/` (lectura) → `services/` (RS) → `serializers/` + `views/`
   (RF) → `permissions.py` (por acción).
4. Migración: `makemigrations` + `migrate`. Revisar el SQL generado con `sqlmigrate` antes de aplicarlo en preproducción.
5. Pruebas: una por criterio de aceptación, nombrada `test_<CODIGO>_<enunciado>`.
6. Frontend: `models/` → servicio del feature → componentes → ruta diferida.
7. Commit por historia: `M03: registra hora de pesaje separada de hora de registro (HU-M03-01)`.
8. Pull request hacia `develop` con la lista de HU cerradas y la salida de `pytest`.

---

## 5. Definición de terminado

Un módulo está terminado cuando, y solo cuando:

- [ ] Cada RN tiene una prueba que falla si se elimina la regla.
- [ ] Cada RF responde en el contrato de rutas de `ARQ-02` §6 y devuelve el cuerpo de error uniforme.
- [ ] Ninguna regla de negocio vive en `views/` ni existe únicamente en Angular.
- [ ] `repositories/` no escribe y `services/` no consulta para presentar.
- [ ] Los permisos están declarados por acción y hay una prueba de rechazo por rol.
- [ ] Las acciones de escritura registran evento en M08 (`CREAR` / `MODIFICAR` / `ANULAR` / `EXPORTAR`).
- [ ] Los índices del `modelo_datos_entidad_relacion.md` §3 que toca el módulo están creados en migración.
- [ ] Ninguna entidad se borra físicamente: la baja es lógica (`activo`) o anulación con motivo (D-07).
- [ ] Los mensajes de error visibles coinciden literalmente con los criterios de aceptación.
- [ ] Los commits referencian su HU.

---

## 6. Errores que invalidan la tesis, no solo el código

| Error | Consecuencia metodológica |
|---|---|
| Poner `auto_now_add` en `hora_registro` | El indicador I1 desaparece; D1 queda sin medición (D-01) |
| Asignar el correlativo en el cliente | Colisiones offline; el ingreso deja de ser identificable (D-02) |
| Usar la hora de sincronización como hora de registro | I1 mide señal de red, no latencia de captura (D-03) |
| Dejar M07 para el final | Obliga a reescribir M03 (D-04) |
| Guardar el tipo de vehículo como texto libre | I2 se vuelve inclasificable (D-06) |
| `DELETE` físico de un ingreso | No se puede demostrar que el postest no fue depurado (D-07) |
| Validar solo en Angular | Los registros de la cola offline entran sin validar (D-08) |
| Desplegar durante la ventana de observación sin registrarlo | Amenaza a la validez interna (`ARQ-02` §7) |

---

## 7. Orden de construcción (semanas)

| Semana | Entregable |
|---|---|
| 1 | Esqueleto backend + Angular PWA + PostgreSQL + M01 |
| 2 | M02 catálogo, inicio de M03 |
| 3 | M03 completo + M08 (eventos de creación) |
| 4 | M07 cola offline y endpoint de lote |
| 5 | M04 salidas + M05 existencias |
| 6 | M09 búsqueda + M08 (exportaciones) |
| 7 | M06 consolidados y reportes |
| 8 | Preproducción, JMeter, corrección de RNF |

Coincide con `ARQ-01` §3. Si una semana se desplaza, se documenta: el porcentaje de módulos implementados sobre planificados es el indicador de la variable independiente.
