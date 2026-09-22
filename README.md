# LogisticaMinera

Sistema web inteligente para el control de inventarios de ingreso de mineral, desarrollado como
proyecto de tesis para la empresa Construcción y Minería (planta de procesamiento de Pillcomarca,
Huánuco). El ticket de balanza se fotografía, sus datos se reconocen automáticamente y se validan
antes de registrarse, con el usuario siempre confirmando lo que el sistema propone.

> **Documentación completa en [`docs/`](docs/).** Este README es el punto de entrada; el detalle de
> cada decisión, requisito e historia vive en la documentación, no aquí.

---

## Estado del proyecto

El repositorio está en migración de un alcance anterior (control de producción y existencias) al
sistema web inteligente descrito arriba. La reformulación se documenta en
[`docs/REFORMULACION.md`](docs/REFORMULACION.md) y se ejecuta por fases según
[`docs/PLAN_TRABAJO.md`](docs/PLAN_TRABAJO.md).

| Rama | Contenido |
|---|---|
| `main` | Última versión estable: backend con M01 y M02 implementados, bajo el diseño anterior |
| `docs/reformulacion/sistema-inteligente` | Documentación reescrita para el sistema nuevo (fases 0 a 8 completas); el backend todavía no se tocó |

| Módulo | Responsabilidad | Documentación | Código |
|---|---|---|---|
| M01 | Autenticación y roles | Reescrita | Implementado, sin cambios de fondo |
| M02 | Catálogo maestro | Reescrita | Implementado; pendiente retirar `Cliente` y renombrar `Producto` a `TipoMineral` |
| M03 | Registro de ingresos | Reescrita | Implementado con el diseño anterior; pendiente de refactor |
| M04 | Reconocimiento automático del ticket | Escrita | Sin código |
| M05 | Validación automática de consistencia | Escrita | Sin código |
| M06 | Trazabilidad del proceso | Escrita | Sin código |
| M07 | Consulta de ingresos y respaldo | Escrita | Sin código |
| M08 | Consolidación de la producción | Escrita | Sin código |
| M09 | Auditoría | Escrita | Esqueleto, sin lógica |

La limpieza del backend (retirar `apps/salidas`, `apps/existencias`, `apps/sincronizacion`, refactorizar
`apps/ingresos`, crear las apps nuevas) es la Fase 10 del plan y todavía no se ejecutó.

---

## Estructura del repositorio

```
LogisticaMinera/
├── backend/          Django 5 + Django REST Framework, una app por módulo
├── docs/             Documentación completa del sistema y de la tesis
│   ├── 00-tesis/            Marco de tesis, decisiones de reformulación, plantillas
│   ├── 00-arquitectura/     Decisiones de diseño, modelo de datos, guías, convenciones
│   ├── model-c4/            Módulos (ARQ-01), arquitectura técnica (ARQ-02), modelo C4 (ARQ-03)
│   ├── modulos/             Un paquete por módulo: HU.md, requerimientos/, diagramas/, notas.md
│   ├── 02-trazabilidad/     Matriz HU → RF → indicador → tarea → caso de prueba
│   ├── 01-plan/             Cronograma
│   └── 03-pruebas/          Guías de prueba
├── skills/           Skills del repositorio; contexto-tesis es la fuente para el agente
├── scripts/          verificar_migracion.sh, generar_pdf_hu.py
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

---

## Alcance

Solo el ingreso de mineral óxido a la planta de Pillcomarca. Quedan explícitamente fuera: salidas y
ventas, inventario de producto terminado, reportes normativos periódicos, facturación, contabilidad,
actividad en la mina, integración directa con la balanza, predicción de demanda, aplicación móvil
nativa, operación sin señal de red (salvo la conservación de un borrador) y operación multiempresa.
Detalle en [`docs/00-tesis/marco_tesis.md`](docs/00-tesis/marco_tesis.md#10-fuera-de-alcance).
