---
name: historias-usuario
description: Redacta, amplía o corrige historias de usuario y criterios de aceptación del sistema web inteligente para el control de inventarios de ingreso de mineral. Úsala cuando se pida escribir una HU, añadir o revisar criterios de aceptación, completar el archivo HU.md de un módulo, o cuando aparezcan identificadores HU-M** y CA**. Impone el formato de tabla de cabecera, la redacción Como/quiero/para, los criterios en forma Dado/Cuando/Entonces con los mensajes de error literales y la confirmación previa de todo dato reconocido.
---

# Historias de usuario

Antes de escribir, carga `contexto-tesis`. Toma como referencia de estilo
`docs/modulos/M03-ingresos/HU.md`, que es el módulo mejor trabajado y el primero que se reescribe
para el sistema web inteligente: donde su versión actual contradiga esta skill, manda la skill.

## Cabecera del archivo

```markdown
# Historias de usuario — M{nn} {Nombre del módulo}

**RF asociado:** RF{nn} · **Historias:** {n}

> Una o dos frases que expliquen la responsabilidad del módulo dentro del sistema: qué hace,
> qué recibe de otros módulos y qué entrega. Esta cita es obligatoria.

---
```

Si hay varios: `**RF asociados:** RF01, RF04, RF05`. La cabecera no lleva indicadores de la tesis ni
semanas del cronograma: lo primero vive en la matriz de trazabilidad y lo segundo en `docs/01-plan/`.

## Plantilla de una historia

```markdown
## HU-M{nn}-{nn} — {Título en infinitivo o sustantivo, sin punto final}

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M{nn}-{nn} |
| **Épica** | {Nombre del módulo} |
| **Prioridad** | Crítica \| Alta \| Media \| Baja |

**Historia**

Como {rol}, quiero {capacidad}, para {beneficio operativo}.

**Descripción**

Uno o dos párrafos. Qué hace el sistema, qué restricciones aplica y —cuando corresponda— qué
módulo o interfaz interviene (`ReconocedorTicket`, `ValidadorConsistencia`). Aquí va el
razonamiento, no en los criterios.

**Detalles**
- Campo (obligatorio/opcional, origen: reconocido, editable, derivado o asignado por el servidor;
  regla de validación en palabras).
- ...

**Criterios de aceptación**

> **CA01.** Dado que {contexto}, cuando {acción}, entonces {resultado observable}.

> **CA02.** Dado que {contexto de error}, cuando {acción}, entonces el sistema rechaza la operación
> mostrando "{mensaje literal}".

---
```

`Detalles` es opcional en historias simples (ver HU-M02-03). La tabla, la historia y los criterios
no lo son.

## Granularidad: una historia por capacidad, no por operación

**Un CRUD completo es una sola historia.** Dar de alta, editar, listar y desactivar una entidad de
catálogo son cuatro operaciones del mismo trabajo y se cubren con criterios de aceptación distintos
dentro de una historia, no con cuatro historias. Escribir «Registrar producto», «Editar producto»,
«Listar productos» y «Desactivar producto» infla el backlog sin añadir información.

Merece historia propia lo que tiene **lógica dedicada**: un flujo con decisiones, una regla de
dominio que solo aplica ahí, un contrato con otro módulo o un rol distinto. El reconocimiento
automático, la detección de inconsistencias, la anulación con motivo o la exportación son historias
propias; «editar» un catálogo, no.

| Caso | Cómo se documenta |
|---|---|
| CRUD de una entidad de catálogo | Una historia, con un criterio por operación |
| Alta con reglas propias y consulta simple del mismo recurso | Una historia, salvo que los roles difieran |
| Capacidad con flujo propio (reconocer, validar, anular, exportar) | Historia propia |
| Misma operación para dos roles con alcance distinto | Una historia, con un criterio de rechazo por rol |

Entre 1 y 4 historias por módulo es lo normal en este sistema. Si un módulo supera cinco, comprueba
que no estés fragmentando un CRUD.

## Reglas de redacción

**El rol es uno de los tres definidos.** Administrador, Administrativo o Supervisor de planta. No
hay otros: una historia que solo existe «para medir algo» no es una historia. Lo que protege una
medición se expresa como criterio de aceptación de una historia real. Ejemplo: en el registro de
un ingreso, el criterio que exige que la fecha y hora del ticket, el inicio del registro y el fin
del registro se muestren como tres valores distintos y que los dos últimos no sean editables.

**El «para» es una consecuencia real, no una repetición del «quiero».**
Mal: «...para poder registrar el ingreso». Bien: «...para que el dato y su respaldo queden
disponibles sin transcripción posterior en la oficina».

**Cada criterio es verificable por observación.** Un CA que no se puede convertir en caso de prueba
`CP-HU-M{nn}-{nn}-{nn}` está mal escrito. Prohibido: «el sistema es rápido», «la interfaz es
intuitiva», «se maneja adecuadamente». Eso pertenece a `no_funcionales.md` con su método de
verificación.

**Los mensajes de error van entre comillas y en su forma literal**, porque las pruebas los verifican
por igualdad exacta y las notas de implementación exigen que la interfaz los reproduzca sin
reformular. Redáctalos como los ya existentes: impersonales, sin culpar al usuario, sin exclamaciones.

- «Debe adjuntar la imagen del ticket de balanza»
- «El peso neto no coincide con el peso bruto menos la tara» (V1)
- «La tara no puede ser mayor o igual que el peso bruto» (V2)
- «La placa no tiene un formato válido» (V3)
- «El peso neto está fuera del rango de carga del vehículo {placa}» (V4)
- «La fecha del ticket no puede ser posterior a la fecha de registro» (V5)
- «Verifique este dato: lectura con baja confianza»
- «No fue posible leer el ticket. Tome una nueva fotografía o ingrese los datos manualmente»
- «La placa {placa} no está registrada en el catálogo de vehículos»
- «Debe corregir o justificar las inconsistencias señaladas»
- «Acción no autorizada»

**Un criterio, un escenario.** No encadenes dos comportamientos con «y además». Divide.

**Escenarios mínimos de cada historia:** el camino feliz, el rechazo por dato inválido o faltante,
y el rechazo por rol no autorizado cuando la operación esté restringida. Las historias que persisten
datos reconocidos añaden el criterio de confirmación previa: el sistema no guarda ningún valor
propuesto por el reconocimiento hasta que el usuario lo revisa y confirma, y conserva por separado
el valor reconocido y el confirmado.

## Lo que nunca debe aparecer

| Prohibido | Por qué |
|---|---|
| Eliminación física de cualquier registro | Rompe la auditabilidad exigida por el diseño preexperimental (D-07) |
| Persistir un dato reconocido sin confirmación del usuario | El reconocimiento es una propuesta; el peso neto se lee del ticket, es editable antes de confirmar y se valida con V1 (D-13) |
| Menos de tres marcas de tiempo en el ingreso, o alguna de las del servidor editable | Fecha y hora del ticket, inicio y fin del registro son independientes; colapsarlas o editarlas hace falsificable el registro (D-01) |
| Secciones o cabeceras que citen indicadores de la tesis | La relación con la tesis vive en la matriz de trazabilidad, no en el módulo |
| Precios, montos o importes | Están fuera de alcance por decisión documentada |
| Nombres de componentes, tablas o clases | Eso vive en `notas.md`, no en la historia |

## Numeración

Correlativa dentro del módulo y **estable**. Si se añade una historia intermedia, va al final con el
siguiente número libre; no se renumeran las existentes, porque `requerimientos/`, `diagramas/`,
`docs/HistoriasUsuario.md` y la matriz de trazabilidad las referencian por identificador.

## Al terminar

Verifica que cada HU nueva aparezca también en `requerimientos/funcionales.md` (columna HU), en al
menos un diagrama y en `docs/02-trazabilidad/matriz_HU_RF_indicador.md`. Si no, el paquete del
módulo está incompleto: continúa con `requisitos-modulo` y `diagramas-uml`, o avísalo
explícitamente.
