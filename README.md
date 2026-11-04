# LogisticaMinera

Sistema web inteligente para el control de inventarios de ingreso de mineral, desarrollado como
proyecto de tesis para la empresa Construcción y Minería (planta de procesamiento de Pillcomarca,
Huánuco). El ticket de balanza se fotografía, sus datos se reconocen automáticamente y se validan
antes de registrarse, con el usuario siempre confirmando lo que el sistema propone.

> **Documentación completa en [`docs/`](docs/).** Este README es el punto de entrada; el detalle de
> cada decisión, requisito e historia vive en la documentación, no aquí. El índice de todos los
> documentos está en [`docs/INDICE.md`](docs/INDICE.md).

---

## Estado del proyecto

**Documentación.** Versión 2.1: nueve módulos, 27 historias de usuario, sus requerimientos y
diagramas. La fase documental quedó cerrada el 23/10/2026
([`docs/01-plan/ACTA_CIERRE_FASE_DOCUMENTAL.md`](docs/01-plan/ACTA_CIERRE_FASE_DOCUMENTAL.md)); desde
entonces, cada cambio entra como decisión nueva (D-24 a D-28 durante la implementación).

**Backend.** Las fases F0 a F7 de
[`docs/01-plan/PLAN_IMPLEMENTACION.md`](docs/01-plan/PLAN_IMPLEMENTACION.md) están construidas y su
puerta técnica pasa; la supervisión de cada puerta se registra en
[`docs/03-pruebas/bitacora_puertas.md`](docs/03-pruebas/bitacora_puertas.md). La validación integral
del 02/11/2026 ([`informe`](docs/03-pruebas/evidencias/validacion_integral/informe.md)) obtuvo:

| Verificación | Resultado |
|---|---|
| Pruebas automatizadas sobre PostgreSQL 16 | 524 aprobadas, 0 fallidas |
| Colección Postman, carpetas F0 a F7 | 265 peticiones, 858 aserciones, 0 fallos |
| Trazabilidad de reglas y criterios con prueba | M02 a M09 al 100 %; M01 al 94 % (dos criterios de interfaz) |
| Tiempos de respuesta con 5028 ingresos | Todos los RNF cumplidos |
| Instalación desde cero, respaldo y restauración | Correctos |

| Módulo | Responsabilidad | Fase | Estado del backend |
|---|---|---|---|
| M01 | Autenticación y roles | F1 | Implementado |
| M02 | Catálogo maestro | F2 | Implementado |
| M03 | Registro de ingresos | F3 | Implementado: registro, corrección, reversión, anulación y destare |
| M04 | Reconocimiento automático del ticket | F3, F7 | Implementado con el motor local provisional (Tesseract); el piloto con tickets reales que elige el motor definitivo está pendiente (D-12, D-15) |
| M05 | Validación automática de consistencia | F3 | Implementado: reglas V1 a V5 |
| M06 | Trazabilidad del proceso | F5 | Implementado: lotes, recorrido, división, bigbags y cierre |
| M07 | Consulta de ingresos y respaldo | F6 | Implementado: búsqueda, listado, detalle, calendario, exportación, inicio y avisos |
| M08 | Consolidación de la producción | F7 | Implementado: consolidado mensual y exportación XLSX |
| M09 | Auditoría | F4 | Implementado: eventos, historial del ingreso y consulta de la auditoría |

**Lo que sigue.** F8 (estabilización en preproducción y congelamiento del motor y las reglas) y F9
(despliegue para la presentación) dependen del piloto de motores con 20 a 30 tickets reales y de un
servidor de preproducción. La interfaz web (la «Parte B» de cada fase) se construye en el
repositorio del frontend.

### Ramas

| Rama | Contenido |
|---|---|
| `main` | Línea estable; recibe cada fase cuando su puerta queda aprobada |
| `docs/version-2` | Documentación de la versión 2.1 |
| `chore/F0-preparacion-backend` | F0: retiro del alcance anterior y preparación del backend |
| `feature/M01-autenticacion`, `feature/M02-catalogo` | F1 y F2 |
| `feature/M03-registro-ingresos` | F3 (M03, M04 y M05) y F4 (M09) |
| `feature/M06-trazabilidad` | F5 |

`feature/M03-ingresos` es una rama del alcance anterior y no debe fusionarse (DEF-008).

---

## Estructura del repositorio

```
LogisticaMinera/
├── backend/            Django 5 + Django REST Framework, una app por módulo
│   └── apps/           accounts (M01), catalogo (M02), ingresos (M03), reconocimiento (M04),
│                       validacion (M05), trazabilidad (M06), consulta (M07),
│                       consolidacion (M08), auditoria (M09)
├── postman/            Colección de validación por fase, entorno local y archivos de prueba
├── Mockup/             Prototipo navegable de la interfaz, alineado con las decisiones hasta DR-31
├── docs/               Documentación completa del sistema y de la tesis
│   ├── 00-tesis/            Marco de tesis, decisiones de reformulación, plantillas
│   ├── 00-arquitectura/     Decisiones de diseño, modelo de datos, guías, convenciones
│   ├── model-c4/            Módulos (ARQ-01), arquitectura técnica (ARQ-02), modelo C4 (ARQ-03)
│   ├── modulos/             Un paquete por módulo: HU.md, requerimientos/, diagramas/, notas.md
│   ├── 01-plan/             Plan de trabajo, plan de implementación y acta de cierre documental
│   ├── 02-trazabilidad/     Matriz HU → RF → indicador → tarea → caso de prueba
│   └── 03-pruebas/          Plan de pruebas, bitácora de puertas y evidencias por fase
├── skills/             Skills del repositorio; contexto-tesis es la fuente para el agente
├── scripts/            verificar_migracion.sh, validar_docs.py, reporte_trazabilidad.py,
│                       indexar_docs.py, generar_pdf_hu.py, generar_pdf_requerimientos.py, md_a_pdf.py
├── docker-compose.yml  PostgreSQL 16 y backend para desarrollo
└── CLAUDE.md           Instrucciones para trabajar con un agente de IA en este repositorio
```

El frontend Angular vive en un **repositorio separado**,
[`LogisticaMineraFront`](https://github.com/adlerOmonte1/LogisticaMineraFront), por decisión de diseño
D-11: se despliega como archivos estáticos, con un ciclo de vida distinto al de la API. El contrato
entre ambos es el esquema OpenAPI que publica el backend.

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

**Stack:** Python 3.12, Django 5.0, Django REST Framework, SimpleJWT, drf-spectacular,
PostgreSQL 16 y Tesseract OCR, todo dentro de Docker Compose.

### Puesta en marcha

Requisito: Docker con Docker Compose. Desde la raíz del repositorio:

```bash
docker compose up -d --build
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py cargar_datos_prueba
```

`cargar_datos_prueba` crea las cuentas de prueba de los tres roles y el catálogo inicial; solo corre
con `DEBUG` activo. Las credenciales de prueba están en el entorno de Postman, nunca credenciales
reales.

| Servicio | Dirección |
|---|---|
| API | `http://localhost:8000/api/v1/` |
| Documentación interactiva (Swagger) | `http://localhost:8000/api/v1/docs/` |
| Esquema OpenAPI | `http://localhost:8000/api/v1/esquema/` |
| PostgreSQL | `localhost:5433`, base `logistica_minera_dev` |

Para ejecutar el backend fuera de Docker contra la base del Compose, copia
`backend/.env.example` a `backend/.env` y usa el `DATABASE_URL` del puerto 5433 que trae.

### Pruebas

```bash
docker compose exec backend pytest -q
```

Las pruebas usan `config.settings.test` sobre PostgreSQL (la auditoría y el registro usan funciones
que SQLite no tiene) y el motor de reconocimiento determinista. Para ver qué regla o criterio de
aceptación cubre cada prueba:

```bash
python3 scripts/reporte_trazabilidad.py --estricto
```

### Validación en Postman

La colección [`postman/`](postman/README.md) tiene una carpeta por fase y se puede repetir el mismo
día. Con el backend levantado y los datos de prueba cargados:

```bash
npx --yes newman@6.2.1 run postman/LogisticaMinera.postman_collection.json -e postman/entornos/local.postman_environment.json
```

### Convención de apps

Cada módulo es una app Django con la misma organización interna: `models/` (invariantes de dominio),
`repositories/` (lectura), `services/` (casos de uso), `serializers/`, `views/`, `permissions.py`,
`filters.py`, `tests/`. Ningún endpoint borra registros (se anulan, D-07) y todos los errores
responden con el cuerpo `{codigo, mensaje, detalles}` (D-23). El detalle completo está en
[`docs/00-arquitectura/GUIA_MARCO_DE_TRABAJO.md`](docs/00-arquitectura/GUIA_MARCO_DE_TRABAJO.md) y
en [`docs/model-c4/ARQ-02_Arquitectura_Tecnica.md`](docs/model-c4/ARQ-02_Arquitectura_Tecnica.md).

---

## Convención de commits y ramas

| Tipo | Formato de commit | Rama |
|---|---|---|
| Documentación | `docs(alcance): Asunto` | `docs/{alcance}/{descripcion}` |
| Código | `M03: descripcion (HU-M03-01)` | `feature/M03-registro-ingresos` |
| Mantenimiento | `chore(alcance): Asunto` | `chore/{alcance}/{descripcion}` |

Sin tildes en el mensaje de commit. Una historia por commit y una fase por PR. Los commits de código
referencian siempre la historia de usuario que implementan, para que la trazabilidad
`RF → módulo → HU → commit` pueda reconstruirse desde el historial de git. Detalle completo en
[`docs/00-arquitectura/convenciones_codigo.md`](docs/00-arquitectura/convenciones_codigo.md).

---

## Verificación

```bash
bash scripts/verificar_migracion.sh
```

Detecta conceptos del alcance anterior (stock, kardex, captura sin conexión, indicadores antiguos,
formato `RF-01`) que no deberían sobrevivir en `docs/` ni en `skills/`.

```bash
python3 scripts/validar_docs.py
```

Comprueba las reglas de Mermaid, los enlaces, que toda referencia (HU, RN, RS, RU, RNF, D, DR)
exista y que las historias coincidan entre cada `HU.md`, el índice y la matriz de trazabilidad.

Ambas se ejecutan antes de cada commit de documentación. El CI de GitHub Actions
(`.github/workflows/docs.yml` y `backend.yml`) las repite en cada PR junto con ruff, la comprobación
de migraciones, las pruebas del backend sobre PostgreSQL y el reporte estricto de trazabilidad
([`docs/01-plan/PLAN_DE_TRABAJO.md`](docs/01-plan/PLAN_DE_TRABAJO.md) §6.6).

---

## Alcance

Solo el ingreso de mineral óxido a la planta de Pillcomarca. Quedan explícitamente fuera: salidas y
ventas, inventario de producto terminado, reportes normativos periódicos, facturación, contabilidad,
actividad en la mina, integración directa con la balanza, predicción de demanda, aplicación móvil
nativa, operación sin señal de red (salvo la conservación de un borrador) y operación multiempresa.
Detalle en [`docs/00-tesis/marco_tesis.md`](docs/00-tesis/marco_tesis.md#10-fuera-de-alcance).
