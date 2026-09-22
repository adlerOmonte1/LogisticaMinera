# Guía definitiva del marco de trabajo

**Documento:** transversal
**Aplica a:** `backend/` (Django 5 + DRF + PostgreSQL 16) y `frontend/` (Angular 17+)
**Depende de:** `../model-c4/ARQ-02_Arquitectura_Tecnica.md`, `convenciones_codigo.md`,
`decisiones_diseno.md`, `modelo_datos_entidad_relacion.md`

Esta guía es operativa: se sigue de arriba abajo una sola vez, al preparar el backend, y deja el
esqueleto listo para que M01…M09 se implementen sin volver a discutir estructura. Todo lo que aquí
se fija ya estaba decidido en los documentos de arquitectura; lo que se agrega es el *cómo*.

---

## 0. Requisitos previos

| Herramienta | Versión | Verificación |
|---|---|---|
| Python | 3.12.x | `python3 --version` |
| Node.js | 20 LTS | `node --version` |
| PostgreSQL | 16 | `psql --version` |
| Angular CLI | 17+ | `npx @angular/cli version` |
| Git | cualquiera | `git --version` |

No se instala Angular CLI globalmente: se usa `npx` para que la versión quede fijada en
`package.json` y el entorno sea reproducible.

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

`timezone = America/Lima` no es cosmético: el ingreso guarda tres marcas de tiempo independientes
—la del ticket y las dos del servidor (D-01)— y un desfase de zona horaria las desalinearía entre
sí sin que ninguna prueba lo note hasta comparar con la hora real de planta.

### 1.2 Tres bases, tres entornos

```
logistica_minera_dev     desarrollo local, datos de prueba
logistica_minera_pre     preproducción, pruebas funcionales y de rendimiento
logistica_minera         producción, donde corre el sistema una vez validado el pretest
```

Nunca se ejecutan pruebas de carga contra producción: alterarían los tiempos de respuesta reales
durante el periodo de operación.

### 1.3 Secuencia del código único (D-02)

El código lo asigna el servidor, nunca el dispositivo. Se implementa con una secuencia nativa de
PostgreSQL, creada en una migración de Django (nunca a mano en el servidor, o el entorno deja de ser
reproducible):

```python
# apps/ingresos/migrations/0002_secuencia_codigo.py
from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [("ingresos", "0001_initial")]
    operations = [
        migrations.RunSQL(
            sql="CREATE SEQUENCE IF NOT EXISTS seq_ingreso_codigo START 1;",
            reverse_sql="DROP SEQUENCE IF EXISTS seq_ingreso_codigo;",
        ),
    ]
```

`MAX(codigo) + 1` está prohibido: dos usuarios confirmando a la vez producirían el mismo número y el
ingreso dejaría de ser identificable de forma única.

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
Pillow==10.*
openpyxl==3.1.*
```

`Pillow` recibe, valida el formato y comprime las fotografías del ticket antes de guardarlas
(RNF-M03-01, RNF-M03-04). La librería o el SDK del motor de reconocimiento **no** va en `base.txt`:
se agrega solo en el adaptador concreto de `apps/reconocimiento/motores/` cuando D-12 se cierre.

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

for m in accounts catalogo ingresos reconocimiento validacion trazabilidad consulta consolidacion auditoria; do
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

**`consulta` (M07) y `consolidacion` (M08) no llevan `models/` ni `migrations/`** (D-10): no aportan
entidad al modelo entidad-relación. El bucle anterior las crea igual que las demás por simplicidad;
esos dos paquetes se retiran a mano después de `startapp`.

Después de `startapp`, en cada `apps/<app>/apps.py` corregir el `name` para que incluya el paquete:

```python
class IngresosConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.ingresos"
    verbose_name = "M03 — Registro de ingresos"
```

El `verbose_name` con el código de módulo hace que el admin de Django sea, sin trabajo extra, una
vista de la trazabilidad módulo → código.

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
      __init__.py  base.py  development.py  preproduction.py  production.py
    urls.py  wsgi.py  asgi.py
  utils/
    excepciones.py          excepciones de dominio (no importan DRF)
    manejador_errores.py    respuesta uniforme {codigo, mensaje, detalles}
    modelos.py              ModeloBase (creado_en, actualizado_en)
    vistas.py               ViewSetBase sin destroy (D-07)
    permisos.py             permisos por acción reutilizables
    paginacion.py           25 por página
    query_builder.py        armado mecánico de Q(), sin reglas de negocio
    serializer_mixin.py
    throttles.py
  apps/
    accounts/         M01
    catalogo/         M02
    ingresos/         M03
    reconocimiento/    M04
    validacion/         M05
    trazabilidad/       M06
    consulta/           M07   sin models/ ni migrations/ (D-10)
    consolidacion/       M08   sin models/ ni migrations/ (D-10)
    auditoria/           M09
```

Y dentro de cada app con entidad propia, paquetes en lugar de archivos sueltos:

```
apps/ingresos/
  migrations/       los índices del modelo entidad-relacion §3, desde la PRIMERA migración
  models/           entidades e invariantes (RN)
  repositories/     LECTURA. No escribe nunca (D-09)
  services/         casos de uso (RS): transacción e inyección de dependencias
  serializers/      dominio <-> JSON, sin reglas de negocio
  views/            solo HTTP (RF)
  permissions.py    por acción: PuedeRegistrarIngreso, PuedeAnularIngreso (ISP)
  filters.py        django-filter
  urls.py
  apps.py           verbose_name = "M03 — Registro de ingresos"
  tests/
```

Cada paquete reexporta en su `__init__.py`:

```python
# apps/catalogo/models/__init__.py
from .vehiculo import Vehiculo
from .tipo_mineral import TipoMineral
from .transportista import Transportista

__all__ = ["Vehiculo", "TipoMineral", "Transportista"]
```

Sin esto Django detecta los modelos igual, pero mover un archivo rompe las migraciones y las
referencias por cadena (`"catalogo.Vehiculo"`).

**M07 y M08 no llevan `models/` ni `migrations/`** (D-10). No aportan entidad al modelo
entidad-relación; agregan y consultan sobre M03, M04, M05 y M06. M08 añade `exportadores/`, una
clase por formato:

```
apps/consulta/         repositories/ services/ serializers/ views/ ...
apps/consolidacion/    repositories/ exportadores/ services/ serializers/ views/ ...
```

Regla general: una app tiene `models/` solo si aporta una entidad al modelo entidad-relación.

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
    "apps.reconocimiento",
    "apps.validacion",
    "apps.trazabilidad",
    "apps.consulta",
    "apps.consolidacion",
    "apps.auditoria",
]

DATABASES = {"default": env.db("DATABASE_URL")}

AUTH_USER_MODEL = "accounts.Usuario"

MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "/media/"
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024   # 10 MB, limite de la imagen del ticket (RS-M03-01)

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

`MEDIA_ROOT` es el valor por defecto para desarrollo. El medio definitivo de almacenamiento de
imágenes —volumen del servidor o almacenamiento de objetos— lo fija D-14; cuando se cierre, esta
sección se actualiza con el backend de `django-storages` correspondiente.

`.env.example` (versionado, sin secretos reales):

```
DJANGO_SETTINGS_MODULE=config.settings.development
DJANGO_SECRET_KEY=cambiar
DEBUG=True
DATABASE_URL=postgres://logistica:cambiar_en_produccion@localhost:5432/logistica_minera_dev
CORS_ALLOWED_ORIGINS=http://localhost:4200
JWT_ACCESS_MINUTES=30
JWT_REFRESH_DAYS=7
```

### 2.5 Las capas, con un ejemplo completo de M03

La regla de asignación de `ARQ-02` §3.1 es la única que hay que memorizar: **si una validación puede
enunciarse sin mencionar HTTP, no vive en `views/`.**

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

    codigo = models.CharField(max_length=20, unique=True, editable=False)
    imagen_ticket = models.ImageField(upload_to="tickets/%Y/%m/")
    fecha_hora_ticket = models.DateTimeField()                     # leida del ticket (D-01)
    hora_inicio_registro = models.DateTimeField(editable=False)    # del servidor (D-01)
    hora_fin_registro = models.DateTimeField(editable=False)       # del servidor (D-01)
    vehiculo = models.ForeignKey("catalogo.Vehiculo", on_delete=models.PROTECT)
    tipo_mineral = models.ForeignKey("catalogo.TipoMineral", on_delete=models.PROTECT)
    peso_bruto_tn = models.DecimalField(max_digits=8, decimal_places=2)
    tara_tn = models.DecimalField(max_digits=8, decimal_places=2)
    peso_neto_tn = models.DecimalField(max_digits=8, decimal_places=2)   # leido, no calculado
    numero_ticket = models.CharField(max_length=20, blank=True)
    justificacion_peso = models.TextField(blank=True)
    lote = models.ForeignKey("trazabilidad.LoteProceso", null=True, blank=True,
                              on_delete=models.PROTECT)
    usuario_registro = models.ForeignKey("accounts.Usuario", on_delete=models.PROTECT,
                                          editable=False)
    estado = models.CharField(max_length=12, choices=Estado.choices, default=Estado.REGISTRADO)
    motivo_anulacion = models.TextField(blank=True)

    class Meta:
        db_table = "ingreso"
        indexes = [
            models.Index(fields=["vehiculo", "fecha_hora_ticket"], name="idx_ingreso_vehiculo_fecha"),
            models.Index(fields=["fecha_hora_ticket", "tipo_mineral"], name="idx_ingreso_fecha_mineral"),
            models.Index(fields=["estado"], name="idx_ingreso_estado"),
        ]

    def clean(self):
        # RN-M03-08: la fecha del ticket no es posterior al inicio del registro
        if self.hora_inicio_registro and self.fecha_hora_ticket > self.hora_inicio_registro:
            raise ValidationError(
                {"fecha_hora_ticket": "La fecha del ticket no puede ser posterior a la fecha de registro."}
            )
        # D-07: la anulacion exige motivo
        if self.estado == self.Estado.ANULADO and not self.motivo_anulacion:
            raise ValidationError({"motivo_anulacion": "Se requiere motivo para anular un ingreso."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
```

`peso_neto_tn` **no** es `editable=False` ni una propiedad calculada: es un dato del ticket
(RN-M03-04). Calcularlo como `peso_bruto_tn - tara_tn` haría que la regla V1 de M05 —que compara
justamente esos dos valores— nunca pudiera detectar un ticket incoherente, porque la comparación
siempre daría cero.

Los mensajes de error están en español y **coinciden literalmente** con los criterios de aceptación
de las historias (`ARQ-02` §6). Esto convierte a las pruebas en evidencia directa de los CA.

**`services/` — casos de uso (RS). Orquesta, no valida reglas.**

```python
# apps/ingresos/services/registrar_ingreso.py
from django.db import transaction
from django.utils import timezone

class ServicioIngreso:
    def __init__(self, reconocedor, validador, generador_codigo, reloj, auditoria):
        self._reconocedor = reconocedor          # ReconocedorTicket, D-12
        self._validador = validador              # ValidadorConsistencia
        self._generador_codigo = generador_codigo
        self._reloj = reloj
        self._auditoria = auditoria

    def iniciar_registro(self, *, imagen, usuario):
        """RS-M03-01, RS-M03-03. No persiste el ingreso: devuelve una propuesta."""
        hora_inicio = self._reloj.ahora()
        resultado = self._reconocedor.reconocer(imagen)
        inconsistencias = self._validador.validar(resultado.datos)
        return Propuesta(hora_inicio=hora_inicio, resultado=resultado,
                          inconsistencias=inconsistencias)

    @transaction.atomic
    def registrar_ingreso(self, *, datos, hora_inicio, usuario):
        """RS-M03-09. Devuelve el Ingreso persistido con su codigo definitivo."""
        inconsistencias = self._validador.validar(datos)
        if any(i.bloqueante for i in inconsistencias):
            raise ReglaDeNegocioError(inconsistencias[0].mensaje)

        ingreso = Ingreso(
            **datos,
            usuario_registro=usuario,
            hora_inicio_registro=hora_inicio,
            hora_fin_registro=self._reloj.ahora(),
            codigo=self._generador_codigo.siguiente(),      # D-02, inyectado (DIP)
        )
        ingreso.save()
        self._auditoria.registrar(usuario=usuario, accion="CREAR", entidad="INGRESO",
                                   id_entidad=ingreso.id, valores_nuevos=datos)
        return ingreso
```

Las cuatro dependencias entran **por inyección**, no importadas dentro de la clase: es la inversión
de dependencias de `ARQ-02` §5 y es lo que permite un motor de reconocimiento y un código
deterministas en pruebas, sin invocar a un servicio externo real.

**`repositories/` — lectura, separada de la escritura (D-09)**

```python
# apps/ingresos/repositories/ingreso.py
class RepositorioIngreso:
    """Solo lectura: ni save, ni create, ni update, ni delete."""

    def listar(self, *, filtros=None):
        return (
            Ingreso.objects
            .select_related("vehiculo", "tipo_mineral", "usuario_registro")
            .filter(**(filtros or {}))
            .order_by("-fecha_hora_ticket")
        )

    def por_codigo(self, codigo: str) -> Ingreso | None:
        return self.listar().filter(codigo=codigo).first()
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
        ingreso = self.servicio.registrar_ingreso(
            datos=entrada.validated_data,
            hora_inicio=request.data["hora_inicio_registro"],
            usuario=request.user,
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

El frontend puede escribir **un solo** interceptor de errores porque la forma del cuerpo es siempre
la misma. Esa es la ganancia concreta de la convención.

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
    """CRUD sin D: ningun endpoint del sistema borra fisicamente (D-07)."""
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
    path("api/v1/reconocimientos/", include("apps.reconocimiento.urls")),
    path("api/v1/lotes/", include("apps.trazabilidad.urls")),
    path("api/v1/consulta/", include("apps.consulta.urls")),
    path("api/v1/consolidacion/", include("apps.consolidacion.urls")),
    path("api/v1/auditoria/", include("apps.auditoria.urls")),
    path("api/v1/esquema/", SpectacularAPIView.as_view()),
    path("api/v1/docs/", SpectacularSwaggerView.as_view(url_name="schema")),
]
```

`apps.validacion` (M05) no expone rutas propias de escritura: se invoca internamente desde M03. Solo
publica la consulta de resultados, que puede montarse bajo `api/v1/ingresos/{id}/validaciones/`
dentro de las rutas de `ingresos`.

### 2.9 Pruebas

`pytest.ini`:

```ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings.development
python_files = test_*.py
addopts = -ra --strict-markers
```

Una prueba por criterio de aceptación, nombrada con su código:

```python
# apps/ingresos/tests/test_reglas.py
import pytest

@pytest.mark.django_db
def test_RN_M03_08_ticket_posterior_al_registro_es_rechazado(ingreso_factory):
    with pytest.raises(ValidationError) as e:
        ingreso_factory(fecha_hora_ticket="2099-12-31T23:59:00Z")
    assert "posterior a la fecha de registro" in str(e.value)
```

```bash
pytest -q
```

El nombre de la prueba contiene el código de la regla: la matriz de trazabilidad `RN → prueba` se
genera con `pytest --collect-only`, no se mantiene a mano.

### 2.10 Orden de arranque

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

---

## 3. Frontend — Angular

> **El frontend vive en su propio repositorio** (`logistica-minera-frontend`, D-11). Esta sección
> queda como referencia rápida; la guía de instalación y la estructura viven en
> `GUIA_FRONTEND_ANGULAR.md`.

### 3.1 Creación

```bash
cd frontend
npx @angular/cli@17 new logistica-minera \
  --standalone --routing --style=scss --ssr=false --skip-git
cd logistica-minera
```

No se agrega `@angular/pwa` ni una librería de almacén de cola: la captura sin señal de red no es un
módulo del sistema (DR-01). Lo único que exige RNF-M03-05 es un borrador guardado en el navegador
mientras dura el registro, que se implementa con el almacenamiento propio del navegador y se
descarta al confirmar — sin service worker ni infraestructura de sincronización en segundo plano.

### 3.2 Estructura

```
src/app/
  core/                        una sola instancia, cargado al inicio
    interceptors/
      auth.interceptor.ts        adjunta el JWT
      error.interceptor.ts       traduce {codigo, mensaje, detalles}
    services/
      auth.service.ts
      borrador-registro.service.ts   conserva imagen y campos mientras no hay señal (RNF-M03-05)
      notificacion.service.ts
    guards/
      sesion.guard.ts
      rol.guard.ts
  shared/                      componentes reutilizables sin estado
    components/  pipes/  directives/
  models/                      interfaces del dominio, espejo del modelo entidad-relacion
    ingreso.model.ts  vehiculo.model.ts  tipo-mineral.model.ts ...
  features/                    una carpeta por módulo con pantalla propia, carga diferida
    auth/              M01
    catalogo/           M02
    ingresos/            M03 (incluye reconocimiento y validacion: M04, M05)
    trazabilidad/        M06
    consulta/            M07
    consolidacion/       M08
    auditoria/           M09
  app.routes.ts
  app.config.ts
environments/
  environment.ts  environment.pre.ts  environment.prod.ts
```

M04 y M05 no tienen carpeta propia: sus pantallas son parte del mismo flujo de registro y viven
dentro de `features/ingresos/`.

### 3.3 Rutas con carga diferida

```typescript
// app.routes.ts
export const routes: Routes = [
  { path: 'login', loadComponent: () => import('./features/auth/login.component').then(m => m.LoginComponent) },
  {
    path: 'ingresos',
    canActivate: [sesionGuard, rolGuard(['ADMINISTRADOR', 'ADMINISTRATIVO', 'SUPERVISOR'])],
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
  codigo: string;
  imagenTicket: string;       // URL del respaldo
  fechaHoraTicket: string;    // ISO
  horaInicioRegistro: string;
  horaFinRegistro: string;
  vehiculoId: number;
  tipoMineralId: number;
  pesoBrutoTn: number;
  taraTn: number;
  pesoNetoTn: number;
  numeroTicket?: string;
  justificacionPeso?: string;
  estado: 'REGISTRADO' | 'ANULADO';
}
```

```typescript
// features/ingresos/ingresos.service.ts
@Injectable({ providedIn: 'root' })
export class IngresosService {
  private http = inject(HttpClient);
  private base = `${environment.apiUrl}/ingresos/`;

  iniciarRegistro(imagen: File): Observable<PropuestaIngreso> {
    const form = new FormData();
    form.append('imagen', imagen);
    return this.http.post<PropuestaIngreso>(`${this.base}borradores/`, form);
  }

  registrar(payload: NuevoIngreso): Observable<Ingreso> {
    return this.http.post<Ingreso>(this.base, payload);
  }

  listar(filtros: FiltroIngreso = {}): Observable<Pagina<Ingreso>> {
    return this.http.get<Pagina<Ingreso>>(this.base, { params: toParams(filtros) });
  }
}
```

Ningún componente inyecta `HttpClient` directamente (`ARQ-02` §4). El componente inyecta el servicio
del feature.

### 3.5 Estado con signals

```typescript
@Component({ standalone: true, selector: 'app-ingresos-lista', /* ... */ })
export class IngresosListaComponent {
  private servicio = inject(IngresosService);
  ingresos = signal<Ingreso[]>([]);
  cargando = signal(false);

  ngOnInit() {
    this.cargando.set(true);
    this.servicio.listar().subscribe({
      next: p => this.ingresos.set(p.results),
      complete: () => this.cargando.set(false),
    });
  }
}
```

### 3.6 Captura de la imagen y pantalla de confirmación (M03, M04, M05)

```typescript
// features/ingresos/registro/captura-ticket.component.ts
@Component({
  standalone: true,
  selector: 'app-captura-ticket',
  template: `
    <input type="file" accept="image/*" capture="environment"
           (change)="onImagenSeleccionada($event)">
  `,
})
export class CapturaTicketComponent {
  private servicio = inject(IngresosService);
  private borrador = inject(BorradorRegistroService);
  propuesta = signal<PropuestaIngreso | null>(null);

  async onImagenSeleccionada(evento: Event) {
    const archivo = (evento.target as HTMLInputElement).files?.[0];
    if (!archivo) return;
    const imagenReducida = await comprimirImagen(archivo);        // RNF-M03-04
    this.borrador.guardar({ imagen: imagenReducida });             // RNF-M03-05
    this.servicio.iniciarRegistro(imagenReducida).subscribe({
      next: p => this.propuesta.set(p),
      error: () => this.propuesta.set(propuestaVacia()),           // CA04, CA05 de HU-M04-01
    });
  }
}
```

`capture="environment"` abre la cámara trasera directamente en el teléfono, sin pantalla intermedia
(RNF-M03-07). La imagen se comprime en el cliente **antes** de enviarse: una fotografía actual supera
con facilidad los 5 MB y casi todo ese peso es irrelevante para leer un ticket impreso.

```typescript
// features/ingresos/registro/confirmar-registro.component.ts
@Component({
  standalone: true,
  selector: 'app-confirmar-registro',
  template: `
    @for (campo of propuesta().campos; track campo.nombre) {
      <app-campo-reconocido [campo]="campo" [dudoso]="campo.confianza < umbral" />
    }
    @for (inconsistencia of propuesta().inconsistencias; track inconsistencia.regla) {
      <app-alerta-inconsistencia [inconsistencia]="inconsistencia" />
    }
  `,
})
export class ConfirmarRegistroComponent {
  propuesta = input.required<PropuestaIngreso>();
  umbral = 0.8;
}
```

Esta pantalla es donde se cumplen HU-M04-01 (campos con su confianza, los dudosos resaltados) y
HU-M05-01 (inconsistencias señaladas junto al campo, con el mensaje literal de la regla). Nada de lo
que muestra se ha persistido todavía: el envío final ocurre solo cuando el usuario confirma
(RN-M03-02, D-13).

### 3.7 Regla que no se rompe (D-08)

Angular puede validar en el formulario para mejorar la experiencia, pero la validación autoritativa
está en el backend. Toda regla de `models/` o de `apps/validacion/reglas/` puede duplicarse en un
`Validators` de Angular para dar respuesta inmediata, pero **ninguna** puede existir solo allí: una
petición que llegue sin pasar por el formulario debe someterse a las mismas reglas.

### 3.8 Comandos

```bash
ng serve            # http://localhost:4200
ng build            # producción
ng test
```

---

## 4. Flujo de trabajo de un módulo, de principio a fin

Para cada módulo Mxx, en este orden. No se salta ningún paso: cada uno produce evidencia citable en
la revisión técnica.

1. `git checkout -b feature/Mxx-nombre` (desde `develop`).
2. Leer `docs/modulos/Mxx-*/requerimientos/` — RU, RS, RF, RNF, RN.
3. Backend: `models/` (RN) → `repositories/` (lectura) → `services/` (RS) → `serializers/` +
   `views/` (RF) → `permissions.py` (por acción).
4. Migración: `makemigrations` + `migrate`. Revisar el SQL generado con `sqlmigrate` antes de
   aplicarlo en preproducción.
5. Pruebas: una por criterio de aceptación, nombrada `test_<CODIGO>_<enunciado>`.
6. Frontend: `models/` → servicio del feature → componentes → ruta diferida.
7. Commit por historia: `M04: reconoce los seis campos del ticket con su confianza (HU-M04-01)`.
8. Pull request hacia `develop` con la lista de HU cerradas y la salida de `pytest`.

---

## 5. Definición de terminado

Un módulo está terminado cuando, y solo cuando:

- [ ] Cada RN tiene una prueba que falla si se elimina la regla.
- [ ] Cada RF responde en el contrato de rutas de `ARQ-02` §6 y devuelve el cuerpo de error uniforme.
- [ ] Ninguna regla de negocio vive en `views/` ni existe únicamente en Angular.
- [ ] `repositories/` no escribe y `services/` no consulta para presentar.
- [ ] Los permisos están declarados por acción y hay una prueba de rechazo por rol.
- [ ] Las acciones de escritura registran evento en M09 (`CREAR` / `MODIFICAR` / `ANULAR` /
      `RECONOCER` / `CORREGIR_DATO` / `EXPORTAR`).
- [ ] Los índices del `modelo_datos_entidad_relacion.md` §3 que toca el módulo están creados en
      migración.
- [ ] Ninguna entidad se borra físicamente: la baja es lógica (`activo`) o anulación con motivo
      (D-07).
- [ ] Los mensajes de error visibles coinciden literalmente con los criterios de aceptación.
- [ ] Los commits referencian su HU.

---

## 6. Errores que comprometen la validez del sistema, no solo el código

| Error | Consecuencia |
|---|---|
| Poner `auto_now_add` en `hora_inicio_registro` o `hora_fin_registro` | Las marcas fijarían el instante de inserción en la base, no el hecho real que describen (D-01) |
| Asignar el código en el cliente | Dos confirmaciones simultáneas producirían el mismo código; el ingreso dejaría de ser identificable (D-02) |
| Calcular `peso_neto_tn` en vez de leerlo del ticket | La regla V1 nunca podría detectar un ticket incoherente, porque la comparación siempre daría cero (RN-M03-04) |
| Persistir un valor reconocido sin confirmación del usuario | Un error del motor se convertiría en dato oficial sin revisión (D-13) |
| Sobrescribir el valor reconocido con el confirmado en la misma columna | Se perdería la única evidencia de si el reconocimiento funciona (RN-M04-02) |
| Invocar el motor de reconocimiento directamente, sin pasar por `ReconocedorTicket` | Cambiar de motor cuando se cierre D-12 obligaría a reescribir el servicio de registro |
| Guardar el tipo de vehículo como texto libre en vez de derivarlo del catálogo | La regla V4 no tendría contra qué contrastar el peso neto (D-06) |
| `DELETE` físico de un ingreso | No se podría demostrar que el histórico no fue depurado (D-07) |
| Validar solo en Angular | Una petición que no pase por el formulario entraría sin validar (D-08) |
| Registrar el evento de auditoría después del `commit` de la operación principal | Un fallo entre ambos pasos dejaría una operación sin su rastro (RN-M09-01) |
| Cambiar el motor o los parámetros de las reglas de validación en medio de la ventana de operación controlada | Los datos de ese periodo dejarían de ser comparables entre sí (D-16) |

---

## 7. Orden de construcción

```
M01, M02  ->  M03  ->  M04, M05  ->  M09  ->  M06, M07, M08
```

El orden lo impone la dependencia, no el calendario: M03 necesita usuario y catálogo; se construye
asumiendo que `ReconocedorTicket` y `ValidadorConsistencia` existen, así que M04 y M05 no pueden
quedar para el final sin obligar a reescribirlo. El cronograma con fechas y semanas vive en
`../01-plan/PLAN_DE_TRABAJO.md`; esta guía solo fija la secuencia de dependencias, que coincide con
`ARQ-01` §6.
