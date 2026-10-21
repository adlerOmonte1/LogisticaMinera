---
name: diagramas-uml
description: Escribe o corrige los diagramas Mermaid de un módulo del sistema web inteligente de ingreso de mineral — casos de uso, secuencia y actividades — en docs/modulos/M**/diagramas/. Úsala cuando se pida un diagrama, un flujo, un caso de uso, un diagrama de secuencia o de actividades, o cuando aparezcan identificadores S-M** o A-M**. Impone la regla de etiquetas sin tildes, la nomenclatura de participantes (ReconocedorTicket, ValidadorConsistencia, Auditoria) y la tabla de casos de uso que acompaña al diagrama.
---

# Diagramas Mermaid

Carga antes `contexto-tesis`. Referencia de estilo: `docs/modulos/M03-ingresos/diagramas/` (en
reescritura para el sistema web inteligente; donde su versión actual contradiga esta skill, manda
la skill).

## Regla que no se negocia: etiquetas sin tildes ni eñes

Dentro de un bloque ```mermaid, **todo texto de nodo, participante, etiqueta de flecha o rama va sin
tildes, sin eñes y sin signos `¿` `¡`**. El repositorio entero lo cumple: `Validacion`, `vehiculo`,
`auditoria`, `transaccion`, `Senalar campos faltantes`, `codigo`.

Es deliberado: evita fallos de renderizado en los visores de Markdown y en la exportación a Word del
documento de tesis. La prosa que rodea al diagrama —títulos, tablas, notas— **sí lleva tildes
normales**. La regla aplica exclusivamente al interior del bloque de código.

Otras restricciones dentro del bloque:

- Sin paréntesis, comas ni comillas dentro de `[...]` o `{...}`. Usa guiones o reescribe.
- Sin `<br/>` ni HTML.
- Los identificadores de nodo son cortos y mnemotécnicos: `V1`, `E2`, `UC3`, `SRV`, `DB`.
- El signo `?` final en un rombo de decisión sí se admite: `{Imagen legible?}`.

---

## `caso_uso.md`

```markdown
# Diagrama de casos de uso — M{nn} {Nombre}

```mermaid
flowchart LR
    SUP(("Supervisor de planta"))
    ADV(("Administrativo"))
    ADM(("Administrador"))
    MOT[["Motor de reconocimiento"]]

    UC1["Reconocer datos del ticket"]
    UC2["Revisar campos de baja confianza"]
    UC3["Consultar resultado del reconocimiento"]

    SUP --> UC1
    SUP --> UC2
    ADV --> UC1
    ADV --> UC2
    ADV --> UC3
    ADM --> UC3
    MOT -.-> UC1
```

## Casos de uso

| Caso | HU | Actores | Nota |
|---|---|---|---|
| Reconocer datos del ticket | HU-M04-01 | Supervisor de planta, Administrativo | El resultado es una propuesta; no se persiste sin confirmación |
| Revisar campos de baja confianza | HU-M04-01 | Supervisor de planta, Administrativo | Umbral por defecto de 0,80 |

Los actores se definen en `../../M01-autenticacion/diagramas/caso_uso.md` y no se redefinen aquí.
```

- `flowchart LR`, actores como círculos `(("Nombre"))`, casos como cajas `["Verbo objeto"]`.
  Un sistema externo (el motor de reconocimiento cuando D-12 elija un servicio) se dibuja como
  `[["Nombre"]]` y se une con línea discontinua `-.->`.
- Identificadores fijos de actor: `ADM`, `ADV`, `SUP`. Casos: `UC1`, `UC2`, …
- El caso de uso se nombra con **verbo en infinitivo + objeto**: «Gestionar vehiculos»,
  «Registrar ingreso», «Vincular ingreso con etapa».
- La **tabla es obligatoria** y es donde vive el detalle con tildes: HU asociada, actores y el matiz
  que el dibujo no puede expresar («La placa debe existir en el catálogo», «El Supervisor de planta
  no anula»).
- Cierra siempre con la línea que remite a M01 para la definición de actores.

---

## `secuencia.md`

Uno o más diagramas, cada uno titulado `## S-M{nn}-{nn} · {Escenario} (HU-M{nn}-{nn})`.

```markdown
## S-M03-01 · Registro de un ingreso con reconocimiento y validación (HU-M03-01)

```mermaid
sequenceDiagram
    actor S as Supervisor de planta
    participant NG as Angular
    participant API as Django REST
    participant SRV as ServicioIngreso
    participant REC as ReconocedorTicket M04
    participant VAL as ValidadorConsistencia M05
    participant COR as GeneradorCodigo
    participant IMG as Almacen de imagenes
    participant DB as PostgreSQL
    participant AUD as Auditoria M09

    S->>NG: Captura la foto del ticket
    NG->>NG: Reduce la imagen RNF-M03-04
    NG->>API: POST /api/v1/ingresos/borradores/
    API->>SRV: iniciar_registro(imagen, usuario)

    alt Formato o tamano no admitido
        SRV-->>API: Error de validacion RNF-M03-01
        API-->>NG: 400 La imagen debe estar en formato JPG o PNG
    else Imagen admitida
        SRV->>IMG: Guardar imagen
        SRV->>DB: Registrar hora de inicio del registro
        SRV->>REC: reconocer(imagen)
        REC-->>SRV: Placa fecha y peso bruto con su confianza
        SRV->>SRV: Proponer la hora actual como hora del pesaje
        SRV->>VAL: validar(datos propuestos)
        VAL-->>SRV: Lista de inconsistencias
        SRV-->>API: Propuesta sin persistir RN-M03-02
        API-->>NG: 200 con campos confianza hora propuesta e inconsistencias
        NG-->>S: Resalta baja confianza e inconsistencias
    end

    S->>NG: Corrige datos ajusta la hora del pesaje y elige tipo de mineral
    opt Placa sin registrar en el catalogo
        NG-->>S: Formulario de alta del vehiculo en la misma pantalla
        S->>NG: Completa titularidad y capacidad
        NG->>API: POST /api/v1/catalogo/vehiculos/
        API-->>NG: 201 vehiculo creado sin tara
    end
    opt Tipo de mineral nuevo y rol Administrativo o Administrador
        NG->>API: POST /api/v1/catalogo/tipos-mineral/
        API-->>NG: 201 tipo de mineral creado y elegido
    end
    NG->>API: POST /api/v1/ingresos/
    API->>SRV: registrar_ingreso(datos confirmados, usuario)
    SRV->>DB: Leer vehiculo vigente con su tara RN-M03-08
    SRV->>VAL: validar(datos confirmados)

    alt Vehiculo dado de baja
        SRV-->>API: Rechazo RN-M03-08
        API-->>NG: 400 El vehiculo esta dado de baja
    else Regla bloqueante o advertencia sin justificar
        VAL-->>SRV: Rechazo con mensaje literal
        SRV-->>API: Error de dominio RN-M03-05
        API-->>NG: 400 con el campo afectado
        NG-->>S: Mensaje junto al campo
    else Datos coherentes
        SRV->>DB: BEGIN TRANSACTION
        SRV->>COR: obtener_siguiente_codigo()
        COR-->>SRV: Codigo asignado RN-M03-09
        alt Vehiculo con tara
            SRV->>SRV: Calcular peso neto como bruto menos tara RN-M03-04
            SRV->>DB: Persistir ingreso Registrado con tara aplicada y hora de fin
        else Vehiculo sin tara
            SRV->>DB: Persistir ingreso En proceso sin neto y hora de fin RN-M03-17
        end
        SRV->>DB: Persistir valor reconocido y confirmado por campo
        SRV->>AUD: Registrar evento CREAR
        SRV->>DB: COMMIT
        SRV-->>API: Ingreso persistido
        API-->>NG: 201 con el codigo y el estado
        NG-->>S: Ingreso registrado o pendiente de destare
    end
```
```

**Participantes canónicos.** Reutiliza estos nombres en todo el repositorio; no inventes variantes:

| Alias | Participante |
|---|---|
| `NG` | Angular |
| `API` | Django REST |
| `SRV` | `Servicio{Entidad}` |
| `DOM` | `Modelo {Entidad}` |
| `DB` | PostgreSQL |
| `REC` | `ReconocedorTicket M04` (interfaz; el motor concreto lo fija D-12) |
| `VAL` | `ValidadorConsistencia M05` |
| `COR` | `GeneradorCodigo` |
| `IMG` | `Almacen de imagenes` |
| `LOT` | `ServicioLote M06` |
| `AUD` | `Auditoria M09` |

El actor se declara con `actor`, el resto con `participant`. Los módulos externos llevan su código
(`M04`, `M05`, `M09`) en el nombre para que la dependencia sea visible. `REC` y `VAL` son
interfaces inyectadas en el servicio de registro: el diagrama nunca nombra el motor concreto.

**Contenido obligatorio de todo diagrama de escritura:**

1. Bloque `alt … else …` con la rama de error **antes** de la de éxito.
2. `BEGIN TRANSACTION` … `COMMIT` explícitos cuando la operación toca más de una tabla.
3. La llamada a `AUD` dentro de la transacción.
4. Los códigos HTTP reales en las respuestas al cliente: `201`, `400`, `403`, `409`.
5. Las reglas de negocio citadas por código en la flecha de validación.
6. En los flujos que persisten datos reconocidos, la confirmación del usuario como paso explícito
   entre la propuesta y la persistencia.

Los mensajes describen **qué se hace**, no cómo: `obtener_siguiente_codigo()`,
`Persistir hora_fin_registro del servidor`.

---

## `actividades.md`

Uno o más diagramas, titulados `## A-M{nn}-{nn} · {Proceso} ({reglas que verifica})`.

```markdown
## A-M03-01 · Registro de un ingreso a partir del ticket (RN-M03-01 a RN-M03-09, RN-M03-16, RN-M03-17, RN-M03-21, RN-M03-22, RN-M03-24)

```mermaid
flowchart TD
    I([Supervisor junto a la balanza]) --> D0{Hay ticket para fotografiar?}
    D0 -->|Si| C1[Capturar foto del ticket]
    C1 --> V1{Formato y tamano admitidos?}
    V1 -->|No| E1[Rechazar: La imagen debe estar en formato JPG o PNG y no superar los 10 MB]
    E1 --> C1
    V1 -->|Si| A1[Guardar imagen y asignar hora de inicio]
    A1 --> R1[Reconocer placa fecha y peso bruto]
    R1 --> D1{Imagen legible?}
    D1 -->|No| L1[Ingresar placa fecha y peso bruto manualmente]
    D1 -->|Si| C2[Mostrar campos con su confianza]
    D0 -->|No| S1[Elegir registro sin foto y asignar hora de inicio]
    S1 --> S2[Elegir el motivo de la lista]
    S2 --> S3[Ingresar placa fecha y peso bruto]
    L1 --> H1[Proponer la hora actual como hora del pesaje]
    C2 --> H1
    S3 --> H1
    H1 --> L2[Revisar corregir datos y ajustar la hora]
    L2 --> D2{Placa en el catalogo?}
    D2 -->|No| L4[Dar de alta el vehiculo en la misma pantalla]
    D2 -->|De baja| E3[Rechazar: El vehiculo esta dado de baja]
    E3 --> L2
    D2 -->|Si| L5{Tipo de mineral en el catalogo?}
    L4 --> L5
    L5 -->|No| D5{Rol Administrativo o Administrador?}
    D5 -->|Si| L6[Dar de alta el tipo de mineral en la misma pantalla]
    D5 -->|No| E4[Indicar que lo registre un administrativo]
    E4 --> F2([Registro detenido sin perder lo capturado])
    L6 --> L7[Elegir tipo de mineral]
    L5 -->|Si| L7
    L7 --> V2[Validar reglas V1 a V5]
    V2 --> D3{Inconsistencia sin resolver?}
    D3 -->|Si| E2[Senalar campo con el mensaje de la regla]
    E2 --> L2
    D3 -->|No| T1[Iniciar transaccion]
    T1 --> A2[Asignar codigo y hora de fin]
    A2 --> D4{El vehiculo tiene tara?}
    D4 -->|Si| A3[Calcular peso neto con la tara del vehiculo]
    A3 --> P1[Persistir ingreso Registrado con la tara aplicada]
    D4 -->|No| P2[Persistir ingreso En proceso sin peso neto]
    P1 --> P3[Guardar valores reconocidos y confirmados y auditar]
    P2 --> P3
    P3 --> T2[Confirmar transaccion]
    T2 --> F([Ingreso con su codigo])
```
```

- `flowchart TD`. Inicio y fin con `([...])`, acciones con `[...]`, decisiones con `{...?}`.
- Ramas etiquetadas `|Si|` y `|No|` — sin tilde en «Si».
- **Toda rama de error retorna al paso de captura o corrección** (`E1 --> L2`), no muere en un
  nodo suelto.
- Prefijos: `V` validacion, `R` reconocimiento, `E` error, `T` transaccion, `P` persistencia,
  `A` asignacion, `C` carga, `L` captura o correccion del usuario, `D` decision.
- Los nodos de rechazo llevan el mensaje literal del criterio de aceptación, sin tildes.

Además del flujo principal, incluye los diagramas de **decisión de negocio** que el módulo necesite
—«Decisión entre corregir y anular», «Resolución de una inconsistencia V4 con justificación»,
«Asignación de un ingreso a un lote de proceso»—.

---

## Diagramas de arquitectura (C4 y entidad-relación)

Viven en `docs/model-c4/` y `docs/00-arquitectura/`, no en un módulo, y siguen las mismas reglas de
etiquetas sin tildes.

**C4 nivel 1 (contexto):** la balanza no se integra; su ticket se fotografía y se reconoce. Si D-12
elige un servicio en la nube, el motor de reconocimiento aparece como sistema externo.
**C4 nivel 2 (contenedores):** exactamente los contenedores reales del despliegue: SPA Angular, API
Django REST, PostgreSQL, almacén de imágenes y motor de reconocimiento (externo o local según D-12).
**C4 nivel 3 (componentes):** solo para M03, M04 y M05, que son los que se explican en
sustentación; muestra `ReconocedorTicket` y `ValidadorConsistencia` inyectados en el servicio de
registro.

No inventes contenedores que el despliegue no tiene ni omitas los que sí tiene: un diagrama que
promete más o menos de lo implementado se contradice con la lista de control cuando el jurado lo
contrasta.

**Modelo entidad-relación:** `erDiagram` de Mermaid, con la cardinalidad explícita
(`INGRESO ||--o| RECONOCIMIENTO_TICKET : produce`). La fuente única es
`docs/00-arquitectura/modelo_datos_entidad_relacion.md`; si tu diagrama y esa tabla discrepan, la
tabla manda.

---

## Verificación final

- [ ] Ningún carácter acentuado, `ñ`, `¿` o `¡` dentro de un bloque ```mermaid.
- [ ] Sin paréntesis ni comas dentro de `[...]` y `{...}`.
- [ ] Todo diagrama titulado con su código `S-M**-**` o `A-M**-**` y la HU o RN que representa.
- [ ] `caso_uso.md` cierra con la remisión a M01.
- [ ] Los diagramas de escritura muestran transacción, auditoría, rama de error y, si aplica,
      la confirmación del usuario antes de persistir datos reconocidos.
- [ ] Ningún diagrama nombra el motor de reconocimiento concreto: solo `ReconocedorTicket`.
