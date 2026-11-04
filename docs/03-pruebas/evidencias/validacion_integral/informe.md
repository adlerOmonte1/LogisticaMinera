# Informe de validación integral del backend (F0 a F7)

**Fecha:** 02/11/2026 · **Rama:** `feature/M03-registro-ingresos` · **Alcance:** módulos M01 a M09 del backend,
colección Postman, documentación y scripts de verificación.

## 1. Propósito

Comprobar, antes de cerrar la fase de construcción del backend, que el sistema se instala desde cero, que
sus pruebas y verificaciones pasan en un entorno equivalente al CI, que la API cumple las decisiones de
diseño transversales y que los tiempos de respuesta están dentro de los RNF. Los hallazgos se corrigen
cuando son defectos del código y se registran como riesgo cuando requieren una decisión.

## 2. Verificaciones ejecutadas

| # | Verificación | Método | Resultado |
|---|---|---|---|
| 1 | Instalación desde cero | Base `logistica_validacion` vacía: 46 migraciones, semilla ejecutada dos veces | Correcto; la semilla es idempotente |
| 2 | Reversibilidad de migraciones | `migrate <app> zero` y reaplicación en trazabilidad, validacion y reconocimiento | Correcto |
| 3 | Paridad con el CI | Contenedor `python:3.12-slim` limpio, variables del CI, sin `.env` | ruff sin hallazgos, `makemigrations --check` limpio, 524 pruebas aprobadas |
| 4 | Suite completa en el entorno de desarrollo | `pytest` con cobertura | 524 aprobadas, 0 fallidas, 0 `ResourceWarning` |
| 5 | Trazabilidad de pruebas | `reporte_trazabilidad.py --estricto` | M02 a M09 al 100 %; M01 al 94 % (dos criterios de interfaz) |
| 6 | Coherencia documental | `verificar_migracion.sh` y `validar_docs.py` | Sin hallazgos |
| 7 | Colección Postman | Newman 6.2.1, carpetas 00 y F0 a F7, dos corridas sobre la base nueva y una sobre la de desarrollo | 265 peticiones, 858 aserciones, 0 fallos |
| 8 | Esquema OpenAPI | `spectacular --validate` | 0 errores, 60 rutas documentadas |
| 9 | Configuración de producción | `check --deploy` con `config.settings.prod` | Solo `security.W021` (HSTS *preload*) |
| 10 | Superficie de la API | Recorrido de las 105 rutas registradas | Ningún `DELETE` ni `PUT` (D-07, D-22); `AllowAny` solo en inicio y cierre de sesión |
| 11 | Revisión estática de riesgos | Búsqueda de fechas ingenuas, SQL crudo, `print` y `except` amplios | Sin hallazgos; los `except` amplios son intencionales y registran el evento |
| 12 | Rendimiento | 5028 ingresos y 308 lotes sintéticos | Todos los RNF de tiempo cumplidos (tabla 3) |
| 13 | Respaldo y restauración | `pg_dump` y restauración en base nueva | Conteos idénticos; el cambio testigo se revirtió |

## 3. Tiempos de respuesta con volumen

| Operación | Tiempo medido | Umbral del RNF |
|---|---:|---:|
| Búsqueda y listado de ingresos | 161 ms | 2 s |
| Pantalla de inicio | 251 ms | 2 s |
| Detalle de ingreso | 16 ms | 2 s |
| Confirmación del registro | 14 ms | 2 s |
| Validación de las cinco reglas | 1 ms | 200 ms |
| Consolidado mensual | 5 ms | 3 s |
| Exportación XLSX | 17 ms | 5 s |
| Exportación CSV | 41 ms | 5 s |

El detalle de lote ejecuta 12 consultas y el listado 4, sin crecimiento con el número de filas.

## 4. Defectos corregidos durante la validación

| Id | Defecto | Corrección |
|---|---|---|
| DEF-006 | La variable `DJANGO_SETTINGS_MODULE` del contenedor prevalecía sobre `config.settings.test` al ejecutar `pytest` | `backend/pytest.ini` fuerza `--ds=config.settings.test` |
| DEF-009 | Trece vistas `APIView` de M06, M07 y M08 no declaraban su respuesta y el esquema OpenAPI emitía errores | `@extend_schema(responses=OpenApiTypes.OBJECT)` en cada `get` |
| DEF-010 | Dos pruebas abrían la imagen del ticket sin cerrarla (`ResourceWarning`) | Cierre explícito del archivo en `test_hu_m03_03_ca05` y `test_hu_m07_01_ca03` |

## 5. Riesgos y pendientes

| Riesgo | Consecuencia en el dominio | Acción propuesta |
|---|---|---|
| Fases F4 a F7 sin *commit*; la preparación parcial depende de objetos de git sueltos que `git gc` elimina en unas dos semanas | Pérdida del historial por módulo | Registrar los *commits* de la lista entregada antes del 16/11/2026 |
| Rama obsoleta `feature/M03-ingresos` (DEF-008) | Confusión al integrar | Eliminarla tras fusionar `feature/M03-registro-ingresos` |
| `backend/.env` local apunta a SQLite (no versionado; Compose lo sobrescribe) | Ejecución fuera de Docker contra una base distinta | Alinearlo con `.env.example` |
| Clave JWT de producción menor de 32 bytes | Tokens con firma débil | Exigir una clave de 32 bytes o más en el despliegue (F8) |
| HSTS *preload* sin decidir | Advertencia `security.W021` | Decidir en F8 con el dominio definitivo |
| Sin limitación de intentos por IP en el inicio de sesión (solo bloqueo por cuenta, D-23) | Enumeración de cuentas por fuerza bruta distribuida | Evaluar `ScopedRateThrottle` como decisión D nueva |
| D-12 y D-15 pendientes del ensayo con 20 a 30 tickets reales | Motor de reconocimiento sin calibrar con datos de planta | Ejecutar `piloto_motores` con los tickets de la empresa |
| Catálogo de DR-03 provisional | Tipos de mineral por confirmar | Confirmarlo con la empresa antes de producción |
| Interfaz web sin iniciar | Dos criterios de M01 y la parte B del plan sin verificar | Iniciar el *frontend* sobre la API validada |

## 6. Conclusión

El backend se instala desde cero, pasa sus 524 pruebas en un entorno equivalente al CI, responde a las
265 peticiones de la colección sin fallos y cumple los RNF de tiempo con un volumen superior al de un
año de operación. No quedan defectos abiertos en el código; los riesgos de la sección 5 dependen de
decisiones de despliegue, de datos reales de la empresa o de la construcción de la interfaz.

## Dependencias, permisos y riesgo de implementación

- **Dependencias:** Docker Compose (PostgreSQL 16), Newman 6.2.1, entorno `postman/entornos/local.postman_environment.json`.
- **Permisos:** las corridas usan las cuentas de prueba de `cargar_datos_prueba`, que se niega a ejecutarse sin `DEBUG`.
- **Riesgo de implementación:** este informe vale para el estado de la rama en la fecha indicada; cualquier
  cambio posterior en modelos o reglas exige repetir las verificaciones 3, 4, 5 y 7.
