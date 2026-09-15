---
name: historias-usuario
description: Redacta, amplía o corrige historias de usuario y criterios de aceptación para el sistema de control de producción y existencias de la tesis minera. Úsala cuando se pida escribir una HU, añadir o revisar criterios de aceptación, completar el archivo HU.md de un módulo, o cuando aparezcan identificadores HU-M** y CA**. Impone el formato de tabla de cabecera, la redacción Como/quiero/para y los criterios en forma Dado/Cuando/Entonces con los mensajes de error literales.
---

# Historias de usuario

Antes de escribir, carga `contexto-tesis`. Toma como referencia de estilo
`docs/modulos/M03-ingresos/HU.md`, que es el módulo mejor trabajado.

## Cabecera del archivo

```markdown
# Historias de usuario — M{nn} {Nombre del módulo}

**RF asociado:** RF-{nn} · **Indicador de tesis:** I{n} · **Semana:** {n} · **Historias:** {n}

> Una o dos frases que expliquen qué indicador sostiene el módulo y qué deja de ser demostrable
> si el módulo no existe. Esta cita es obligatoria.

---
```

Si hay varios: `**RF asociados:**` e `**Indicadores de tesis:**`, en plural.

## Plantilla de una historia

```markdown
## HU-M{nn}-{nn} — {Título en infinitivo o sustantivo, sin punto final}

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M{nn}-{nn} |
| **Épica** | {Nombre del módulo} |
| **Prioridad** | Crítica \| Alta \| Media \| Baja |

**Historia**

Como {rol}, quiero {capacidad}, para {beneficio operativo o metodológico}.

**Descripción**

Uno o dos párrafos. Qué hace el sistema, qué restricciones aplica y —cuando corresponda— por qué
esta historia sostiene un indicador. Aquí va el razonamiento, no en los criterios.

**Detalles**
- Campo (obligatorio/opcional, regla de validación en palabras).
- ...

**Criterios de aceptación**

> **CA01.** Dado que {contexto}, cuando {acción}, entonces {resultado observable}.

> **CA02.** Dado que {contexto de error}, cuando {acción}, entonces el sistema rechaza la operación
> mostrando "{mensaje literal}".

---
```

`Detalles` es opcional en historias simples (ver HU-M02-03). La tabla, la historia y los criterios
no lo son.

## Reglas de redacción

**El rol es uno de los tres definidos.** Administrador, Administrativo o Supervisor. La única
excepción admitida es `Como investigador`, reservada a las historias que existen para hacer medible
un indicador (HU-M03-02, HU-M03-03, HU-M05-03). Úsala con parsimonia y justifícala en la descripción.

**El «para» es una consecuencia real, no una repetición del «quiero».**
Mal: «...para poder registrar el ingreso». Bien: «...para que la información de producción quede
disponible de inmediato y no dependa de anotaciones dispersas».

**Cada criterio es verificable por observación.** Un CA que no se puede convertir en caso de prueba
`CP-HU-M{nn}-{nn}-{nn}` está mal escrito. Prohibido: «el sistema es rápido», «la interfaz es
intuitiva», «se maneja adecuadamente». Eso pertenece a `no_funcionales.md` con su método de
verificación.

**Los mensajes de error van entre comillas y en su forma literal**, porque las pruebas los verifican
por igualdad exacta y las notas de implementación exigen que la interfaz los reproduzca sin
reformular. Redáctalos como los ya existentes: impersonales, sin culpar al usuario, sin exclamaciones.

- «El producto ya se encuentra registrado»
- «La tara debe ser menor que el peso bruto»
- «Acción no autorizada»
- «Debe indicar el motivo de la corrección»

**Un criterio, un escenario.** No encadenes dos comportamientos con «y además». Divide.

**Cobertura mínima de cada historia:** el camino feliz, el rechazo por dato inválido o faltante, y
el rechazo por rol no autorizado cuando la operación esté restringida. Las historias que alimentan
un indicador añaden el criterio que protege la medición (por ejemplo, HU-M03-01 CA05: la hora de
pesaje y la hora de registro se muestran como dos valores distintos).

## Lo que nunca debe aparecer

| Prohibido | Por qué |
|---|---|
| Eliminación física de cualquier registro | Rompe la auditabilidad exigida por el diseño preexperimental |
| Peso neto como campo de entrada | Se calcula siempre como bruto − tara (RN-M03-04) |
| Una sola marca de tiempo en el ingreso | Destruye el indicador I1 |
| Precios, montos o importes | Están fuera de alcance por decisión documentada |
| Nombres de componentes, tablas o clases | Eso vive en `notas.md`, no en la historia |

## Numeración

Correlativa dentro del módulo y **estable**. Si se añade una historia intermedia, va al final con el
siguiente número libre; no se renumeran las existentes, porque `requisitos/`, `diagramas/` y
`docs/HistoriasUsuario.md` las referencian por identificador.

## Al terminar

Verifica que cada HU nueva aparezca también en `requisitos/funcionales.md` (columna HU) y en al
menos un diagrama. Si no, el paquete del módulo está incompleto: continúa con `requisitos-modulo`
y `diagramas-uml`, o avísalo explícitamente.
