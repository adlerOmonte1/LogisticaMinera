# Bitácora de puertas de fase

Una fila por cada ejecución de la puerta de una fase de
[`PLAN_IMPLEMENTACION.md`](../01-plan/PLAN_IMPLEMENTACION.md) §5, también las observadas: la bitácora
muestra cuántas veces se intentó cada puerta y por qué no pasó. El implementador completa las
columnas técnicas; el supervisor, el resultado y las observaciones.

| Fase | Fecha | Commit | pytest | Newman | Trazabilidad | Resultado | Supervisor | Observaciones |
|---|---|---|---|---|---|---|---|---|
| F0 | 24/10/2026 | Sin commit; rama `chore/F0-preparacion-backend` | 71 aprobadas, 0 fallos; cobertura 94 % | 9 solicitudes, 32 aserciones, 0 fallos | Estricto, sin códigos huérfanos | Pendiente de supervisión | — | Newman ejecutado sobre SQLite porque Docker Desktop estaba en pausa; falta repetirlo sobre el PostgreSQL 16 del Compose |
