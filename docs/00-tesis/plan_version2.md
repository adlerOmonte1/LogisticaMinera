# Plan de reformulación de la documentación a la versión 2

Repositorio: `adlerOmonte1/LogisticaMinera`. La versión 2 **reemplaza** a la 1 en los mismos archivos; no se crean carpetas paralelas. La versión 1 queda guardada en el historial con la etiqueta `docs-v1`. No se tocan `00-arquitectura/`, `model-c4/` ni `backend/`.

Fuentes: `docs/00-tesis/marco_tesis.md`, `docs/00-tesis/decisiones_reformulacion.md` (DR-01 a DR-18) y `CLAUDE.md`.

## Cómo se trabaja

- **Este chat** valida decisiones y resuelve dudas de alcance o de la tesis.
- **Claude Code**, abierto en la carpeta del repositorio, aplica los cambios. Lee los archivos directamente y no hay que copiarlos al chat, así se gastan menos tokens. Los chats no se enlazan entre sí: el traspaso se hace con este archivo y con `decisiones_reformulacion.md` dentro del repositorio.
- **Un entregable por sesión**, en una rama propia, con un *pull request* que revisas antes del siguiente.
- Antes de cada commit se ejecuta `bash scripts/verificar_migracion.sh`. Los commits siguen la convención `docs(alcance): Asunto`.

## Fase 0. Preparación (sesión corta)

- Etiqueta `docs-v1` sobre la rama actual de documentación y rama de trabajo `docs/version-2`.
- Copiar este plan a `docs/00-tesis/plan_version2.md`.
- **Entregable:** rama y etiqueta creadas. **Revisas:** que `docs-v1` apunte al último commit de la versión 1.

## Fase 1. Fuentes de verdad y limpieza (PR 1)

- `decisiones_reformulacion.md`: DR-11 a DR-18, a partir del bloque de decisiones nuevas registrado en ese mismo archivo.
- `marco_tesis.md`: I6 por ruta decidida (§4), rol Supervisor (§8) y la excepción de registro sin foto.
- **Mapa de limpieza:** tabla con cada archivo de `docs/` y su destino (conservar, fusionar o eliminar). Cubre notas obsoletas, PDFs generados que quedarán desactualizados, duplicados y restos de la migración.
- Revisar si las plantillas de `skills/` siguen sirviendo para la versión 2.
- **Entregable:** PR 1 con el marco, las decisiones y el mapa de limpieza. **Revisas:** las decisiones y qué se elimina. Aún no se borra nada.

## Fase 2. Módulos por lotes (un PR por lote)

En cada módulo: `HU.md` → los cinco archivos de `requerimientos/` → los tres diagramas → `notas.md`. También se aplica la limpieza aprobada en el mapa.

| PR | Módulos | Contenido principal |
|---|---|---|
| 2 | M03, M04, M05 | Placa editable, alta de vehículo y de tipo de mineral desde el registro, registro manual de respaldo, tres marcas de tiempo, V1 a V5 |
| 3 | M06 | Lote con nombre, rutas, división por proporción, ingresos agregados después del cierre, bigbags y horas de molienda (datos descriptivos), cierre del lote con destino |
| 4 | M07, M09 | Consulta con trazabilidad, calendario de llegadas, historial visible para los tres roles |
| 5 | M01, M02, M08 | Matriz de roles, catálogos y verificación de que la consolidación no cambia |

**Revisas en cada PR:**
- que cada HU tenga su RF, su indicador y criterios Dado/cuando/entonces;
- que los mensajes coincidan entre HU y requerimientos;
- que no haya nada fuera de alcance (ventas, guías, inventario);
- que los diagramas reflejen el flujo del mockup.

## Fase 3. Documentos transversales (PR 6)

- `02-trazabilidad`: matriz HU → RF → indicador, con I6 reformulado.
- `03-pruebas`: casos de prueba de las HU nuevas y modificadas.
- `HistoriasUsuario.md` (índice) y `README.md`.
- PDFs regenerados con `scripts/` o retirados si no se regeneran.
- Reporte de contradicciones con `decisiones_diseno.md` (D-nn), sin modificar la arquitectura.
- **Revisas:** la matriz completa y el reporte.

## Fase 4. Cierre

- Revisión de coherencia en todo `docs/` con la skill `revision-coherencia`.
- *Merge* a la rama principal de documentación y etiqueta `docs-v2`.

## Pendientes que conviene resolver antes de la Fase 3

1. Si el ingreso que llega después del secado se reparte por proporción. Se propone usar por defecto las fracciones del lote, editables.
2. Actualizar el Anexo 02 con la Hoja 4 nueva antes del juicio de expertos.
3. Ajustes del mockup (opcional, aparte de la documentación): hora del pesaje editable, quitar el número de ticket, cierre con destino y división por fracciones.

## Prompt para Claude Code (una fase por sesión)

> Lee `CLAUDE.md` y `docs/00-tesis/plan_version2.md`. Ejecuta solo la **Fase N**. Trabaja en la rama `docs/version-2`, haz los commits según la convención y detente al terminar con un resumen de lo que cambió y lo que debo revisar.