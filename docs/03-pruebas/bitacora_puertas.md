# Bitácora de puertas de fase

Una fila por cada ejecución de la puerta de una fase de
[`PLAN_IMPLEMENTACION.md`](../01-plan/PLAN_IMPLEMENTACION.md) §5, también las observadas: la bitácora
muestra cuántas veces se intentó cada puerta y por qué no pasó. El implementador completa las
columnas técnicas; el supervisor, el resultado y las observaciones.

| Fase | Fecha | Commit | pytest | Newman | Trazabilidad | Resultado | Supervisor | Observaciones |
|---|---|---|---|---|---|---|---|---|
| F0 | 25/10/2026 | `9e5c600` | 71 aprobadas sobre PostgreSQL 16 del Compose, 0 fallos; cobertura 94 % | 9 solicitudes, 32 aserciones, 0 fallos, contra el Compose | Estricto, sin códigos huérfanos | Aprobada | Autor, en el chat del 25/10/2026 | Repetida sobre PostgreSQL 16 tras la primera ejecución en SQLite del 24/10/2026 |
| F1 | 25/10/2026 | Sin commit; rama `feature/M01-autenticacion` | 85 aprobadas sobre PostgreSQL 16, 0 fallos; cobertura 94 % | 41 solicitudes (F0 y F1), 123 aserciones, 0 fallos | Estricto; M01 al 94 % (faltan HU-M01-01 CA08 y HU-M01-03 CA01, de interfaz) | Pendiente de supervisión | — | Respaldo y restauración probados (D-20) |
