# Mapa de limpieza de la documentación — versión 2

| Campo | Valor |
|---|---|
| Documento | Mapa de limpieza para la reformulación a la versión 2 |
| Fase | Fase 1 de `plan_version2.md` |
| Fecha | 21/10/2026 |
| Fuentes | `marco_tesis.md`, `decisiones_reformulacion.md` (DR-01 a DR-18) y el mockup del sistema |
| Estado | Propuesta para revisión. **Nada de lo listado se ha eliminado todavía** |

Cada archivo de `docs/` recibe uno de cinco destinos:

| Destino | Significado |
|---|---|
| Conservar | Sigue vigente sin cambios de contenido |
| Actualizar | Se mantiene y se reescribe en la fase indicada |
| Fusionar | Su contenido útil pasa a otro archivo y el original se elimina |
| Regenerar | Es un producto generado por `scripts/`; se vuelve a generar al final |
| Eliminar | No describe el sistema ni sirve a la tesis; se retira, y queda en el historial de git |

---

## 1. Fuentes de verdad y documentos transversales

| Archivo | Destino | Fase | Motivo |
|---|---|---|---|
| `00-tesis/marco_tesis.md` | Actualizar | 1 (hecho) | I6 por ruta, rol Supervisor, registro sin foto, M06 y fuera de alcance según DR-11 a DR-18 |
| `00-tesis/decisiones_reformulacion.md` | Actualizar | 1 (hecho) | DR-11 a DR-18 integradas con redacción formal; pendientes P-01 a P-04 |
| `00-tesis/plan_version2.md` | Conservar | — | Guía de la reformulación. Se propone eliminarlo en la Fase 4, igual que el plan de migración anterior, porque no describe el sistema |
| `00-tesis/mapa_limpieza_v2.md` | Eliminar | 4 | Este archivo. Cumple su función al aplicarse la limpieza |
| `01-plan/PLAN_DE_TRABAJO.md` | Actualizar | 3 | El cronograma y la plantilla de caso de prueba asumen un lote que se abre, se cierra y recorre las cuatro etapas; faltan la ruta, la división por fracciones y el cierre con destino (DR-14, DR-16, DR-18) |
| `02-trazabilidad/matriz_HU_RF_indicador.md` | Actualizar | 3 | I6 reformulado (DR-16) y las historias nuevas o modificadas de M03 y M06 |
| `03-pruebas/plan_de_pruebas.md` | Actualizar | 3 | CP07 asume las cuatro etapas en orden fijo; CP01 y CP06 citan la hora del pesaje digitada; faltan casos para el registro sin foto (DR-13) y el cierre con destino (DR-14) |
| `HistoriasUsuario.md` | Actualizar | 3 | Índice de historias; cambiará el número de historias de M03 y M06 |
| `Historias_de_Usuario.pdf` | Regenerar | 3 | Generado por `scripts/generar_pdf_hu.py`; queda desactualizado en cuanto cambien las HU |
| `Requerimientos_y_Diagramas.pdf` | Regenerar | 3 | Generado por `scripts/generar_pdf_requerimientos.py`; mismo motivo |
| `Historias_de_Usuario_v1.1.docx` | **Decidir** | 3 | No es reproducible: su generador no está en el repositorio. Opciones: incorporar el generador a `scripts/` y regenerarlo, o eliminarlo y usar el PDF como documento formal |

## 2. Módulos

Todos los archivos de cada módulo —`HU.md`, los cinco de `requerimientos/`, los tres de `diagramas/` y
`notas.md`— se **conservan y actualizan** en el lote de la Fase 2 que les corresponde. La tabla
indica qué cambia en cada uno y qué contenido obsoleto se retira.

| Módulo | PR | Cambio por decisión | Contenido obsoleto que se retira |
|---|---|---|---|
| M03 Registro de ingresos | 2 | DR-11: hora del pesaje propuesta con la hora actual y editable. DR-12: sin número de ticket. DR-13: registro sin foto con motivo y marca «sin respaldo fotográfico». Alta de tipo de mineral desde el registro (plan, PR 2) | RNF-M03-14 y su nota exigen la hora **sin valor precargado**, lo contrario de DR-11. El número de ticket aparece en `HU.md`, `reglas_negocio.md`, `actividades.md` y `notas.md`. `notas.md` abre con una nota sobre la refactorización de la app anterior, que ya figura en `PLAN_DE_TRABAJO.md` §8 |
| M04 Reconocimiento | 2 | Sin cambio de alcance. Revisar el flujo del registro sin foto: no hay reconocimiento | — |
| M05 Validación | 2 | Sin cambio de reglas. V5 compara con la hora del pesaje, que ahora es propuesta y editable | — |
| M06 Trazabilidad | 3 | DR-14, DR-15, DR-16, DR-18: lote con nombre, ruta por lote o parte, división por fracciones, ingresos agregados después del cierre, bigbags y horas de molienda como datos descriptivos, cierre con destino | Toda regla que impone las cuatro etapas en orden fijo y el estado ABIERTO/CERRADO como único ciclo de vida, en los nueve archivos del módulo |
| M07 Consulta | 4 | Consulta con trazabilidad, calendario de llegadas, ingresos marcados sin respaldo fotográfico (DR-13) | — |
| M09 Auditoría | 4 | Historial visible para los tres roles | `notas.md` dice que la app «se completa en la fase de» un plan ya retirado |
| M01 Autenticación | 5 | DR-17: el Supervisor registra ingresos, vehículos nuevos, destares y etapas. DR-14: solo el Administrador cierra el lote con destino | `diagramas/caso_uso.md` describe al Supervisor como «Registro y consulta» |
| M02 Catálogo | 5 | Catálogos según el mockup | `notas.md` conserva tareas de la migración: retirar `Cliente` y renombrar `Producto`. Ya figuran en `PLAN_DE_TRABAJO.md` §8; se **fusionan** allí y se retiran de las notas |
| M08 Consolidación | 5 | Verificar que la consolidación no cambia | — |

## 3. Documentos que el plan deja fuera y que contradicen la versión 2

El plan de la versión 2 excluye `00-arquitectura/`, `model-c4/` y `backend/`, y en la Fase 3 solo
reporta contradicciones con las decisiones D-nn. Pero varios de esos archivos contradicen ya las
decisiones nuevas, y los módulos remiten a ellos:

| Archivo | Contradicción | Propuesta |
|---|---|---|
| `00-arquitectura/modelo_datos_entidad_relacion.md` | `INGRESO.numero_ticket` (DR-12); no existe la marca de ingreso sin respaldo fotográfico (DR-13); `LOTE_PROCESO` solo tiene estado ABIERTO/CERRADO, sin nombre, ruta, partes, fracciones, bigbags ni destino (DR-14, DR-15, DR-16, DR-18) | **Actualizar** en la Fase 2, junto con M03 y M06. Las notas de los módulos describen sus entidades según este modelo; si no se actualiza, las notas nuevas lo contradirán |
| `00-arquitectura/decisiones_diseno.md` | D-01 dice que la hora del pesaje la digita el usuario; DR-11 la hace propuesta y editable | Ajustar D-01 o registrarlo en el reporte de la Fase 3 |
| `00-arquitectura/GUIA_MARCO_DE_TRABAJO.md` | El código de ejemplo del modelo `Ingreso` incluye `numero_ticket` y la hora sin propuesta | Actualizar el ejemplo, o **fusionar** la guía en las skills `backend-django` y `solid-proyecto`, que ya repiten buena parte de su contenido |
| `00-arquitectura/GUIA_FRONTEND_ANGULAR.md` | La pantalla de confirmación pide la hora «en un campo sin valor precargado» | Actualizar ese párrafo |
| `00-arquitectura/convenciones_codigo.md` | Ninguna | Conservar |
| `model-c4/ARQ-01_Modulos_del_Sistema.md` | Responsabilidad de M06 sin ruta ni cierre con destino | Actualizar la fila de M06 con el texto del marco |
| `model-c4/ARQ-02_Arquitectura_Tecnica.md` | Ninguna verificada | Conservar |
| `model-c4/ARQ-03_Modelo_C4.md` | Menciona las cuatro etapas como recorrido fijo | Revisar en la Fase 3 |

## 4. Fuera de `docs/`

| Elemento | Destino | Motivo |
|---|---|---|
| `Mockup/index.html` (raíz, sin versionar) | **Decidir** | Es la fuente de las decisiones DR-11 a DR-18 y el plan pide revisar que los diagramas reflejen su flujo. Se propone versionarlo en `docs/mockup/` para que la revisión de cada PR sea reproducible. Contiene usuarios y contraseñas de demostración, no reales |
| `scripts/verificar_migracion.sh` | Conservar | Sigue impidiendo que reaparezcan conceptos del alcance anterior |
| `scripts/generar_pdf_hu.py`, `scripts/generar_pdf_requerimientos.py` | Conservar | Regeneran los PDF en la Fase 3 |

## 5. Revisión de las skills

| Skill | ¿Sirve para la versión 2? | Ajuste necesario | Fase y PR |
|---|---|---|---|
| `contexto-tesis` | Sí | Alineada con el marco en esta fase: I6, roles, DR-11 a DR-18, fuera de alcance | Fase 1 (hecho) |
| `historias-usuario` | Sí | Plantilla genérica; sin contenido de dominio afectado | — |
| `requisitos-modulo` | Sí | Plantilla genérica | — |
| `diagramas-uml` | Sí, con ajuste | Su ejemplo copia el A-M03-01 vigente, que incluye «Numero de ticket ya registrado» (DR-12). Debe volver a copiarse después de reescribir M03 | Fase 2, PR 2 |
| `revision-coherencia` | Sí | Se usa en la Fase 4 | — |
| `modulo-nuevo` | Sí | Sin cambios | — |
| `commit-tesis` | Sí | Sin cambios | — |
| `base-datos-postgresql` | Sí, con ajuste | Índice de unicidad parcial de `numero_ticket` (DR-12) | Fase 2, PR 2, si se actualiza el modelo de datos |
| `backend-auth-permisos` | Sí, con ajuste | La tabla de roles describe al Supervisor como «Registro y consulta» (DR-17) | Fase 2, PR 5 |
| `solid-proyecto` | Sí, con ajuste | Dice que el Supervisor «obtiene únicamente registro y consulta» (DR-17) | Fase 2, PR 5 |
| `reconocimiento-validacion` | Sí | Revisar que el registro sin foto (DR-13) no invoque el reconocimiento | Fase 2, PR 2 |
| `backend-django`, `frontend-angular`, `pruebas-y-desempeno`, `despliegue-docker` | Sí | Sin contradicciones encontradas | — |

## 6. Decisiones que se necesitan del autor

1. Si se levanta la exclusión de `00-arquitectura/` y `model-c4/` al menos para el modelo de datos, la
   decisión D-01 y la fila de M06 de ARQ-01 (sección 3).
2. Qué hacer con `Historias_de_Usuario_v1.1.docx` (sección 1).
3. Si se versiona el mockup en `docs/mockup/` (sección 4).
4. Los pendientes P-01 a P-04 de `decisiones_reformulacion.md`.
