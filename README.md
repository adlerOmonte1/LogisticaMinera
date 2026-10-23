# LogisticaMinera

Sistema web inteligente para el control de inventarios de ingreso de mineral, desarrollado como
proyecto de tesis para la empresa Construcción y Minería (planta de procesamiento de Pillcomarca,
Huánuco). El ticket de balanza se fotografía, sus datos se reconocen automáticamente y se validan
antes de registrarse, con el usuario siempre confirmando lo que el sistema propone.

> **Documentación completa en [`docs/`](docs/).** Este README es el punto de entrada; el detalle de
> cada decisión, requisito e historia vive en la documentación, no aquí.

---

## Estado del proyecto

La documentación del sistema está en su **versión 2**: nueve módulos, 26 historias de usuario, sus
requerimientos y diagramas, reformulados a partir de la revisión del prototipo navegable
([`Mockup/index.html`](Mockup/index.html)) y de las decisiones DR-11 a DR-29. La versión 1 queda en
la etiqueta `docs-v1`. El backend conserva apps de un alcance anterior que se retiran en la
preparación del repositorio, antes de construir los módulos
([`docs/01-plan/PLAN_DE_TRABAJO.md`](docs/01-plan/PLAN_DE_TRABAJO.md) §8).

| Rama | Contenido |
|---|---|
| `main` | Documentación de la versión 2 hasta DR-23; backend con M01 y M02 implementados, bajo el diseño anterior |
| `docs/version-2` | Documentación de la versión 2, reformulada con las decisiones DR-11 a DR-29; preparación del backend en curso |

| Módulo | Responsabilidad | Documentación | Código |
|---|---|---|---|
| M01 | Autenticación y roles | Versión 2 | Implementado; falta ampliar la matriz de permisos al alcance del Supervisor de planta |
| M02 | Catálogo maestro | Versión 2 | Implementado; `Cliente` retirado, pendiente renombrar `Producto` a `TipoMineral` |
| M03 | Registro de ingresos | Versión 2 | Implementado con el diseño anterior; pendiente de refactor |
| M04 | Reconocimiento automático del ticket | Versión 2 | Sin código |
| M05 | Validación automática de consistencia | Versión 2 | Sin código |
| M06 | Trazabilidad del proceso | Versión 2 | Sin código |
| M07 | Consulta de ingresos y respaldo | Versión 2 | Sin código |
| M08 | Consolidación de la producción | Versión 2 | Sin código |
| M09 | Auditoría | Versión 2 | Esqueleto, sin lógica |

La limpieza del backend es la preparación del repositorio de `PLAN_DE_TRABAJO.md` §8 y está en
curso. El 22/10/2026 se retiraron `apps/salidas`, `apps/sincronizacion` y `Cliente`; falta retirar
`apps/existencias`, refactorizar `apps/ingresos` y crear las apps nuevas.

---

## Estructura del repositorio

```
LogisticaMinera/
├── backend/          Django 5 + Django REST Framework, una app por módulo
├── Mockup/           Prototipo navegable de la interfaz, alineado con las decisiones hasta DR-29
├── docs/             Documentación completa del sistema y de la tesis
│   ├── 00-tesis/            Marco de tesis, decisiones de reformulación, plantillas
│   ├── 00-arquitectura/     Decisiones de diseño, modelo de datos, guías, convenciones
│   ├── model-c4/            Módulos (ARQ-01), arquitectura técnica (ARQ-02), modelo C4 (ARQ-03)
│   ├── modulos/             Un paquete por módulo: HU.md, requerimientos/, diagramas/, notas.md
│   ├── 02-trazabilidad/     Matriz HU → RF → indicador → tarea → caso de prueba
│   ├── 01-plan/             Cronograma
│   └── 03-pruebas/          Guías de prueba
├── skills/           Skills del repositorio; contexto-tesis es la fuente para el agente
├── scripts/          verificar_migracion.sh, validar_docs.py, reporte_trazabilidad.py,
│                     indexar_docs.py, generar_pdf_hu.py, generar_pdf_requerimientos.py, md_a_pdf.py
└── CLAUDE.md         Instrucciones para trabajar con un agente de IA en este repositorio
```

El frontend Angular vive en un **repositorio separado** (`logistica-minera-frontend`), por decisión
de diseño D-11: se despliega como archivos estáticos, con un ciclo de vida distinto al de la API.

---

## Por dónde empezar a leer

1. [`CLAUDE.md`](CLAUDE.md) — el principio rector de la documentación y las reglas del repositorio.
2. [`docs/00-tesis/marco_tesis.md`](docs/00-tesis/marco_tesis.md) — variables, indicadores, los 10
   requerimientos funcionales, roles y módulos. Es la fuente de verdad.
3. [`docs/model-c4/ARQ-01_Modulos_del_Sistema.md`](docs/model-c4/ARQ-01_Modulos_del_Sistema.md) —
   por qué existe cada módulo.
4. [`docs/00-arquitectura/decisiones_diseno.md`](docs/00-arquitectura/decisiones_diseno.md) —
   decisiones de diseño vigentes, con qué protegen y qué pasa si se revierten.
5. [`docs/02-trazabilidad/matriz_HU_RF_indicador.md`](docs/02-trazabilidad/matriz_HU_RF_indicador.md)
   — único documento donde el sistema se relaciona con los indicadores de la tesis.

---

## Backend

**Stack:** Python 3.12, Django 5.x, Django REST Framework, PostgreSQL 16, SimpleJWT.

### Requisitos previos

| Herramienta | Versión |
|---|---|
| Python | 3.12.x |
| PostgreSQL | 16 |

### Instalación

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/dev.txt
cp .env.example .env        # completar DJANGO_SECRET_KEY y DATABASE_URL
```

```bash
psql -U postgres -c "CREATE DATABASE logistica_minera_dev ENCODING 'UTF8';"
psql -U postgres -c "CREATE USER logistica WITH PASSWORD 'cambiar_en_produccion';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE logistica_minera_dev TO logistica;"
```

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

La API queda disponible en `http://localhost:8000/api/v1/`.

### Pruebas

```bash
cd backend
pytest -q
```

Las pruebas corren contra SQLite en memoria (`config/settings/test.py`), sin necesidad de un
PostgreSQL levantado.

### Convención de apps

Cada módulo es una app Django con la misma organización interna: `models/` (invariantes de dominio),
`repositories/` (lectura), `services/` (casos de uso), `serializers/`, `views/`, `permissions.py`,
`filters.py`, `tests/`. El detalle completo está en
[`docs/00-arquitectura/GUIA_MARCO_DE_TRABAJO.md`](docs/00-arquitectura/GUIA_MARCO_DE_TRABAJO.md) y
en [`docs/model-c4/ARQ-02_Arquitectura_Tecnica.md`](docs/model-c4/ARQ-02_Arquitectura_Tecnica.md).

---

## Convención de commits y ramas

| Fase | Formato de commit | Rama |
|---|---|---|
| Documentación | `docs(alcance): Asunto` | `docs/{alcance}/{descripcion}` |
| Código | `M03: descripcion (HU-M03-01)` | `feature/M03-ingresos` |

Sin tildes en el mensaje de commit. Un commit por módulo. Los commits de código referencian siempre
la historia de usuario que implementan, para que la trazabilidad `RF → módulo → HU → commit` pueda
reconstruirse desde el historial de git. Detalle completo en
[`docs/00-arquitectura/convenciones_codigo.md`](docs/00-arquitectura/convenciones_codigo.md).

---

## Verificación de la documentación

```bash
bash scripts/verificar_migracion.sh
```

Detecta conceptos del alcance anterior (stock, kardex, captura sin conexión, indicadores antiguos,
formato `RF-01`) que no deberían sobrevivir en `docs/` ni en `skills/`. Se ejecuta antes de cada
commit de documentación.

```bash
python3 scripts/validar_docs.py
```

Comprueba las reglas de Mermaid, los enlaces, que toda referencia (HU, RN, RS, RU, RNF, D, DR)
exista y que las historias coincidan entre cada `HU.md`, el índice y la matriz de trazabilidad.

Ambas corren en el CI de GitHub Actions junto con el lint, las migraciones y las pruebas del
backend sobre PostgreSQL. El pipeline completo está en
[`docs/01-plan/PLAN_DE_TRABAJO.md`](docs/01-plan/PLAN_DE_TRABAJO.md) §6.6.

---

## Alcance

Solo el ingreso de mineral óxido a la planta de Pillcomarca. Quedan explícitamente fuera: salidas y
ventas, inventario de producto terminado, reportes normativos periódicos, facturación, contabilidad,
actividad en la mina, integración directa con la balanza, predicción de demanda, aplicación móvil
nativa, operación sin señal de red (salvo la conservación de un borrador) y operación multiempresa.
Detalle en [`docs/00-tesis/marco_tesis.md`](docs/00-tesis/marco_tesis.md#10-fuera-de-alcance).
