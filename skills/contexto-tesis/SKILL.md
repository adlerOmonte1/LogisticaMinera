---
name: contexto-tesis
description: Carga el contexto de la tesis minera antes de redactar, ampliar o revisar cualquier documento de docs/ (historias de usuario, requisitos, diagramas, notas de implementación). Aporta las variables de investigación, los indicadores I1 a I6, los roles, los requerimientos funcionales globales RF-01 a RF-10, el mapa de módulos y las reglas de nomenclatura. Úsala como primer paso de toda tarea de documentación del Sistema de Control de Producción y Existencias, y siempre que aparezcan siglas como HU-M, RN-M, RNF-M, RU-M, RS-M o los indicadores I1 a I6.
---

# Contexto de la tesis

Cárgalo antes de escribir una sola línea en `docs/`. Sin él, se producen documentos correctos
como software y **inútiles como tesis**.

## Qué se está documentando

Un sistema web (Django REST + Angular, PWA con captura sin conexión) para una empresa minera en
proceso de formalización bajo la **Ley 32213**. El diagnóstico encontró que:

- El dato del ticket de balanza tarda **horas o días** en llegar a un registro consultable, porque
  se anota en papel y se transcribe después en la oficina.
- Los **volquetes propios se registran peor que los externos** — hallazgo central del diagnóstico.
- La empresa **tenía** un consolidado mensual de producción y lo perdió por falta de tiempo.
- El stock se estima **a ojo**, por apreciación visual de la cancha.

## Variables e indicadores

**Variable independiente:** el sistema, evaluado con **ISO/IEC 25010:2023** (adecuación funcional,
eficiencia de desempeño, usabilidad, fiabilidad, seguridad).
**Variable dependiente:** el control de producción y existencias.

| Indicador | Qué mide |
|---|---|
| **I1** | Latencia entre el pesaje y la disponibilidad del dato |
| **I2** | Cobertura de registro por tipo de vehículo (propio vs. externo) |
| **I3** | Tiempo de determinación del stock por producto |
| **I4** | Desviación entre stock declarado y stock estimado |
| **I5** | Tiempo de recuperación del dato de un ingreso concreto — por padrón, fecha, placa o producto (ver D-05) |
| **I6** | Porcentaje de meses con consolidado de producción disponible |

Diseño **preexperimental con pretest y postest**: durante la ventana de observación **ningún registro
puede desaparecer ni el sistema puede cambiar de condiciones**. De ahí tres exigencias que atraviesan
todo el repositorio:

1. **Nada se elimina.** Baja lógica y anulación con motivo; jamás `DELETE` físico.
2. **Todo queda atribuido.** Usuario y marca de tiempo en cada operación.
3. **Las dos marcas de tiempo son distintas.** `hora_pesaje` la ingresa el usuario; `hora_registro`
   la asigna el servidor. Colapsarlas «para simplificar» destruye I1.

## Roles

| Rol | Alcance |
|---|---|
| Administrador | Acceso total, incluida gestión de usuarios, catálogos, anulaciones y ajustes |
| Administrativo | Ingresos, salidas, consultas, reportes y exportaciones |
| Supervisor | Registro de ingresos y consulta de existencias |

## Requerimientos funcionales globales

| RF | Descripción | Módulo |
|---|---|---|
| RF-01 | Registrar el ingreso de volquete con los datos del ticket de balanza | M03 |
| RF-02 | Calcular automáticamente el peso neto del ingreso | M03 |
| RF-03 | Gestión de catálogos maestros | M02 |
| RF-04 | Determinar las existencias por producto a partir de los movimientos | M05 |
| RF-05 | Registrar salidas de producto y movimientos internos | M04 |
| RF-06 | Generar el consolidado mensual de producción | M06 |
| RF-07 | Exportar los reportes en formatos de uso externo | M06 |
| RF-08 | Control de acceso mediante autenticación y roles diferenciados | M01 |
| RF-09 | (asociado a M03) | M03 |
| RF-10 | Captura sin conexión y sincronización | M07 |
| RF-11 | Búsqueda de ingresos por criterios | M09 |
| RF-12 | Registro de eventos de auditoría | M08 |

Los RF son **globales** porque muchos cruzan más de un módulo y son los que aparecen en la tesis.
RNF, RN, RU y RS se numeran **por módulo** porque su alcance es local.

## Mapa de módulos

| Módulo | Nombre | RF | Indicadores | Semana | HU | Estado |
|---|---|---|---|---|---|---|
| M01 | Autenticación y control de acceso | RF-08 | — (habilitante) | 1 | 5 | Documentado |
| M02 | Catálogo maestro | RF-03 | I2 | 2 | 4 | Documentado |
| M03 | Registro de ingresos | RF-01, RF-02, RF-09 | I1, I2, I5 | 2–3 | 7 | Documentado |
| M04 | Salidas y movimientos | RF-05 | I4 | 5 | 3 | Documentado |
| M05 | Existencias por producto | RF-04 | I3, I4 | 5 | 3 | Documentado |
| M06 | Consolidados y reportes | RF-06, RF-07 | I6 | 7 | 3 | Documentado |
| M07 | Captura sin conexión (PWA) | RF-10 | I1, I2 | 4 | 5 | Documentado |
| M08 | Auditoría | RF-12 | — (trazabilidad) | 3 y 6 | — | **Sin documentar** |
| M09 | Búsqueda | RF-11 | I5 | 6 | — | **Sin documentar** |

**Total planificado: 9 módulos.** Esa cifra es el denominador del indicador «porcentaje de módulos
implementados sobre planificados» de la variable independiente: toda ampliación posterior lo baja, y
toda reducción debe documentarse **antes** de firmar la ficha técnica.

Aún no existen: `docs/02-trazabilidad/matriz_HU_RF_indicador.md` (referenciada por ARQ-01 §8) y
`docs/03-pruebas/plan_de_pruebas.md`.

## Cronograma de ocho semanas

| Semana | Foco | Entregable verificable |
|---|---|---|
| 1 | Arquitectura, modelo de datos, **esqueleto PWA**, M01 | Login funcional con roles |
| 2 | M02 y arranque de M03 | Catálogo operativo; formulario con validaciones |
| 3 | M03 completo y M08 | Alta, edición, listado e histórico con registro de eventos |
| 4 | M07 sobre M03 | Registro sin conexión y sincronización verificada |
| 5 | M04 y M05 | Stock coincidente con el cálculo manual |
| 6 | M09 y kardex | Búsqueda de un ingreso por padrón en menos de un minuto |
| 7 | M06 | Consolidado mensual y declaración semestral exportables |
| 8 | Pruebas funcionales y de carga, corrección, despliegue | Acta de pruebas y protocolo de carga |

La semana 8 es de estabilización, **no de desarrollo**: es donde se llenan los instrumentos de la
variable independiente.

## Stack

PostgreSQL 16 · Django 5.x + Django REST Framework · SimpleJWT · Angular 17+ (standalone, signals) ·
Angular Service Worker + IndexedDB · openpyxl / ReportLab · pytest-django · Apache JMeter.
Detalle en `docs/00-arquitectura/ARQ-02_Arquitectura_Tecnica.md`.

## Decisiones cerradas

Reabrir cualquiera exige justificación escrita: todas condicionan un indicador o la integridad del
dominio. Están en `docs/00-arquitectura/decisiones_diseno.md`.

| ID | Decisión |
|---|---|
| D-01 | La hora de pesaje y la hora de registro son campos independientes (I1) |
| D-02 | El correlativo lo asigna el servidor, nunca el dispositivo |
| D-03 | La hora de registro de un ingreso offline es la de **captura local**, no la de sincronización (I1, I2) |
| D-04 | La captura sin conexión se decide en la semana 1; no se añade al final |
| D-05 | M09-Búsqueda existe porque el indicador I5 lo exige; se incorporó como RF-11 |
| D-06 | La titularidad del vehículo es un atributo del catálogo, no texto libre (I2) |
| D-07 | El sistema no borra ingresos: los anula |
| D-08 | Las reglas de negocio no se replican en el cliente como fuente de verdad |

> **Contradicción conocida:** D-01 afirma que `hora_registro` es `auto_now_add`; D-03 y el `notas.md`
> de M03 exigen lo contrario, porque en offline el valor correcto es la hora de captura local.
> **D-03 es el que vale.** Está pendiente de corregir en `decisiones_diseno.md`.

## Pendientes que bloquean decisiones

| Pendiente | Bloquea | Fecha límite |
|---|---|---|
| Criterio de estimación de merma por humedad | M04, indicador I4 | Antes de la semana 5 |
| Formato oficial de declaración semestral | M06 | Antes de la semana 7 |
| Confirmación del tamaño de muestra para D3 con la asesora | Análisis inferencial | Antes de cerrar el capítulo III |

## Fuera de alcance — declarado

Facturación, cobranza y precios · fletes a transportistas · contabilidad y planillas · actividad en la
concesión · geolocalización · predicción de demanda o aprendizaje automático · aplicación móvil nativa
· operación multiempresa · balance metalúrgico y leyes.

Se declara explícitamente para proteger el cronograma y para poder responderlo en sustentación.
**Antes de añadir cualquier funcionalidad, comprueba que no esté en esta lista.**

## Nomenclatura

| Elemento | Formato | Ejemplo |
|---|---|---|
| Historia de usuario | `HU-M{módulo}-{nn}` | HU-M03-01 |
| Criterio de aceptación | `CA{nn}` dentro de la HU | CA01 |
| Requerimiento funcional global | `RF-{nn}` | RF-03 |
| Requerimiento de usuario | `RU-M{módulo}-{nn}` | RU-M03-01 |
| Requerimiento de sistema | `RS-M{módulo}-{nn}` | RS-M03-01 |
| Requerimiento no funcional | `RNF-M{módulo}-{nn}` | RNF-M03-06 |
| Regla de negocio | `RN-M{módulo}-{nn}` | RN-M03-05 |
| Diagrama de secuencia | `S-M{módulo}-{nn}` | S-M03-01 |
| Diagrama de actividades | `A-M{módulo}-{nn}` | A-M03-02 |
| Caso de prueba | `CP-{historia}-{nn}` | CP-HU-M03-01-01 |
| Decisión de diseño | `D-{nn}` | D-03 |

**Prioridades:** Crítica · Alta · Media · Baja.
**Unidad de medida:** toneladas. **Productos vigentes:** Saranda y Molido (el sulfuro queda fuera
de alcance por decisión documentada). **Titularidad:** `PROPIO` / `EXTERNO`.

## Estructura de un módulo

```
docs/modulos/M{nn}-{slug}/
├── HU.md
├── notas.md                    (M03 en adelante)
├── requisitos/                 ← M03 en adelante
│   ├── usuario.md
│   ├── sistema.md
│   ├── funcionales.md
│   ├── no_funcionales.md
│   └── reglas_negocio.md
└── diagramas/
    ├── caso_uso.md
    ├── secuencia.md
    └── actividades.md
```

> **Inconsistencia conocida:** M01 y M02 usan la carpeta `requerimientos/`; M03 a M07 usan
> `requisitos/`. Al crear un módulo nuevo sigue a la mayoría (`requisitos/`) y menciónale al autor
> que la unificación sigue pendiente. No la renombres por iniciativa propia: rompería los enlaces
> relativos de los documentos ya versionados.

## Registro maestro

`docs/HistoriasUsuario.md` es el backlog global (34 historias, 9 módulos) y **no siempre coincide**
con los `HU.md` por módulo — los archivos de módulo son la versión más reciente y detallada.
Cuando detectes una divergencia, repórtala; no la corrijas en silencio en ambos lados.

## Tono

Español académico formal, sin anglicismos evitables, sin marketing y sin adjetivos entusiastas.
Cada archivo cierra con una sección que explica **qué se rompe en la tesis si esto se implementa mal**
(«Relación con el indicador I…», «Nota sobre RN-…», «Contexto del diagnóstico»). Esa sección es
obligatoria: es lo que distingue esta documentación de una especificación cualquiera.
