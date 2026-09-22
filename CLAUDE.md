# Instrucciones para el agente — LogisticaMinera

Este repositorio documenta e implementa un **sistema web inteligente para el control de inventarios
de ingreso de mineral** (tesis 2027, empresa Construcción y Minería, Huánuco). Hasta el 21/09/2026
documentaba un sistema distinto, de control de producción y existencias; esa migración está en curso.

## Fuentes de verdad, en este orden

1. `docs/00-tesis/marco_tesis.md` — variables, indicadores, RF01 a RF10, reglas V1 a V5, módulos.
2. `docs/00-tesis/decisiones_reformulacion.md` — decisiones DR-01 a DR-08, ya cerradas.
3. `docs/00-tesis/ejemplos_plantilla.md` — patrón de historias, requerimientos y diagramas.
4. `docs/REFORMULACION.md` — análisis de impacto: qué cambia, dónde y por qué.
5. `docs/PLAN_TRABAJO.md` — plan de migración por fases, con su estado.

Si dos documentos se contradicen, gana el de orden más alto y la contradicción **se reporta**.

## Principio rector

**La documentación describe un sistema, no una tesis.**

- Los módulos se definen por su **responsabilidad** en el dominio, no por el indicador que sostienen.
- Ningún archivo de `docs/modulos/` cita indicadores (I1 a I6, ERA, TDI, SUS, TCA, RFC, CPS) ni
  contiene secciones «Relación con el indicador», «Indicador de tesis» o «qué se rompe en la tesis». <!-- migracion:ok -->
- La relación tesis ↔ sistema vive en **un solo lugar**:
  `docs/02-trazabilidad/matriz_HU_RF_indicador.md`.
- Lo que antes se justificaba «porque protege un indicador» se expresa como regla de negocio o RNF,
  con su consecuencia en términos del dominio (dato incoherente, registro no atribuible, respaldo
  irrecuperable, marca de tiempo falsificable) y su método de verificación.
- Las reglas V1 a V5 **sí** se citan en los módulos: son reglas del sistema, no de la tesis.
- El cronograma vive solo en `docs/01-plan/`. Ningún documento de módulo asigna semanas.

## Reglas

- Carga la skill `contexto-tesis` antes de escribir en `docs/`. Es el resumen operativo del marco.
- No inventes RF, indicadores, tareas, reglas ni decisiones que no estén en las fuentes. Si falta
  algo, márcalo `[PENDIENTE: …]` y repórtalo; no lo supongas.
- Los indicadores I1 a I6 del sistema anterior significaban otra cosa. Usa solo los del marco.
- Formato de RF: `RF01`, sin guion. `RF-01` es un residuo y se corrige. <!-- migracion:ok -->
- Nunca persistas un dato reconocido sin confirmación del usuario (D-13). Nunca borres registros:
  se anulan (D-07).
- El ingreso guarda tres marcas de tiempo independientes: fecha y hora del ticket, inicio del
  registro y fin del registro. Las dos últimas las asigna el servidor y nadie las edita (D-01).
- Mermaid: sin tildes, eñes ni signos de apertura dentro del bloque; sin paréntesis ni comas dentro
  de `[ ]` o `{ }`; sin HTML.
- Español académico formal. Cada archivo cierra con la sección que **el sistema** necesita:
  dependencias, permisos, consecuencia de violar una regla, riesgo de implementación.
- Un módulo por sesión y por commit. Al terminar, lista los archivos cambiados y las dudas.
- No toques `backend/` salvo en la fase que lo indique.

## Estructura

```
docs/00-tesis/        Marco, decisiones y plantillas (fuente de verdad)
docs/00-arquitectura/ Decisiones de diseño, modelo de datos, convenciones y guías
docs/model-c4/        ARQ-01 modulos · ARQ-02 arquitectura tecnica · ARQ-03 modelo C4
docs/modulos/M{nn}-{slug}/  HU.md · requerimientos/ (5) · diagramas/ (3) · notas.md
docs/02-trazabilidad/ Matriz HU → RF → indicador → tarea → caso de prueba
docs/03-pruebas/      Plan de pruebas y guías de prueba manual
skills/               Skills del repositorio; contexto-tesis es la fuente para el agente
backend/              Django 5 + DRF, una app por módulo
scripts/              verificar_migracion.sh
```

Todos los módulos usan la carpeta `requerimientos/`, nunca `requisitos/`.

## Convención de commits

| Fase | Formato | Rama |
|---|---|---|
| Documentación | `docs(alcance): Asunto` | `docs/{alcance}/{descripcion}` |
| Código | `M03: descripcion (HU-M03-01)` | `feature/M03-ingresos` |

Sin tildes en el mensaje. Un commit por módulo. Referencia siempre la historia de usuario en los
commits de código.

## Verificación

```bash
bash scripts/verificar_migracion.sh
```

Detecta conceptos del sistema anterior en `docs/` y `skills/`. Debe pasar sin hallazgos antes de
cada commit de documentación.
