---
name: requisitos-modulo
description: Redacta o revisa los cinco archivos de requisitos de un módulo de la tesis minera — usuario.md, sistema.md, funcionales.md, no_funcionales.md y reglas_negocio.md. Úsala cuando se pidan requerimientos funcionales o no funcionales, reglas de negocio, requerimientos de usuario o de sistema, cuando se mencione ISO/IEC 25010, o cuando aparezcan identificadores RU-M**, RS-M**, RNF-M** o RN-M**. Impone el formato de tabla, la trazabilidad entre niveles y la sección de relación con el indicador de tesis.
---

# Requisitos de un módulo

Carga antes `contexto-tesis`. La referencia de estilo es `docs/modulos/M03-ingresos/requisitos/`.

Los cinco archivos forman **una cadena de trazabilidad**, y se escriben en este orden:

```
usuario.md      →  sistema.md      →  funcionales.md   (qué se expone)
   (RU)              (RS)                (endpoints)
                        ↓
                 no_funcionales.md  ·  reglas_negocio.md
                        (RNF)                (RN)
```

Cada RS declara de qué RU deriva. Cada función declara a qué HU sirve. Un RS sin RU de origen es un
requisito inventado; un RU sin RS que lo realice es una promesa incumplida.

---

## `usuario.md`

La voz del usuario de planta, **en su propio registro**: coloquial, en primera persona, sin
vocabulario técnico. Es el único archivo del repositorio donde eso es correcto.

```markdown
# Requerimientos de usuario — M{nn} {Nombre}

| Código | Requerimiento |
|---|---|
| RU-M{nn}-01 | Quiero registrar el volquete apenas baje de la balanza, ahí mismo en la planta |
| RU-M{nn}-02 | No quiero sacar la cuenta del neto a mano, que lo haga el sistema |

## Contexto del diagnóstico

Qué problema documentado en el Capítulo I responde cada RU relevante y qué indicador lo mide.
```

Entre cuatro y ocho requerimientos. Si suenan a especificación («el sistema deberá…»), están mal:
reescríbelos como lo diría el supervisor.

---

## `sistema.md`

La traducción técnica. Nombres de campo en `código`, comportamiento observable, sin decidir aún la
implementación.

```markdown
# Requerimientos de sistema — M{nn} {Nombre}

| Código | Requerimiento | Deriva de |
|---|---|---|
| RS-M{nn}-01 | El sistema persiste ... con `campo_a` y `campo_b` | RU-M{nn}-01 |
| RS-M{nn}-05 | El sistema genera ... dentro de la misma transacción | — (integridad con M{nn}) |
```

Cuando un RS no nace de un RU sino de una necesidad de integridad entre módulos, la columna
*Deriva de* lleva `— (integridad con M05)`. Se admite, pero debe estar explícito.

Empieza siempre por «El sistema…» y en presente de indicativo. Nunca «deberá».

---

## `funcionales.md`

El contrato de la API. Es el puente entre la historia y el código.

```markdown
# Requerimientos funcionales — M{nn} {Nombre}

**RF global asociado:** RF-{nn} — {descripción del RF global}

| Función | Descripción | HU | Endpoint |
|---|---|---|---|
| Listar productos | Consulta con filtro por vigencia | HU-M02-01 | `GET /api/v1/catalogo/productos/` |
| Crear producto | Alta | HU-M02-01 | `POST /api/v1/catalogo/productos/` |
| Desactivar producto | Baja lógica | HU-M02-01 | `PATCH /api/v1/catalogo/productos/{id}/desactivar/` |

## Relación con el indicador I{n}

Qué endpoint o filtro concreto alimenta el cálculo del indicador y qué se pierde sin él.

## Permisos

| Función | Administrador | Administrativo | Supervisor |
|---|:---:|:---:|:---:|
| Consultar | Sí | Sí | Sí (solo lectura) |
| Crear y editar | Sí | Sí | No |
```

**Convención de rutas:** `/api/v1/{recurso}/`, plural, con barra final. Acciones no CRUD como
sub-ruta explícita: `.../{id}/desactivar/`, `.../{id}/anular/`. La baja es `PATCH`, nunca `DELETE`.
Cuando el CRUD completo no aporta detalle, basta una fila con la ruta base
(`/api/v1/catalogo/clientes/`).

La tabla de permisos es obligatoria en todo módulo con operaciones de escritura.

---

## `no_funcionales.md`

Cada RNF se clasifica bajo una característica de **ISO/IEC 25010:2023** y **declara su método de
verificación**. Un RNF que no se puede verificar no es un requisito: es un deseo.

```markdown
# Requerimientos no funcionales — M{nn} {Nombre}

| Código | Característica ISO/IEC 25010:2023 | Requerimiento | Verificación |
|---|---|---|---|
| RNF-M{nn}-01 | Eficiencia de desempeño — comportamiento temporal | El alta responde en menos de 2 segundos con 20 usuarios concurrentes | Prueba de carga JMeter (semana 8) |
| RNF-M{nn}-04 | Usabilidad — protección contra errores del usuario | Los campos numéricos abren teclado numérico en móviles | Inspección en dispositivo real |

## Relación con la variable independiente

Qué RNF constituyen la evidencia de qué dimensión de ISO/IEC 25010:2023.

## Relación con el indicador I{n}

Por qué el incumplimiento de un RNF concreto devolvería el indicador a los valores del pretest.
```

Características utilizadas en el repositorio: *Adecuación funcional — corrección* · *Eficiencia de
desempeño — comportamiento temporal* · *Usabilidad — operabilidad* · *Usabilidad — protección contra
errores del usuario* · *Fiabilidad — tolerancia a fallos* · *Seguridad — no repudio*.

Todo umbral es numérico y va con su condición de medición: «menos de 3 segundos **con 1000 ingresos
en base**». Un umbral sin carga declarada no es medible.

Métodos de verificación admitidos: prueba de carga con datos sintéticos, observación cronometrada en
campo, inspección en dispositivo real, consulta de verificación sobre la base, inspección de código
o configuración.

---

## `reglas_negocio.md`

Invariantes del dominio. Lo que sigue siendo cierto sin importar qué interfaz lo invoque.

```markdown
# Reglas de negocio — M{nn} {Nombre}

> Ubicación en el código: `apps/{app}/models.py` (invariantes de la entidad) y
> `apps/{app}/services.py` (reglas de proceso). Ninguna de estas reglas vive en `views.py` ni en
> un componente Angular.

| Código | Regla | Consecuencia si se viola |
|---|---|---|
| RN-M{nn}-01 | La tara debe ser estrictamente menor que el peso bruto | El peso neto sería cero o negativo |

## Nota sobre RN-M{nn}-{nn}

Los matices que la tabla no admite: por qué la regla se acota como se acota.

## Nota sobre RN-M{nn}-{nn} y la validez de la tesis

Para las reglas que sostienen un indicador. Debe decir explícitamente qué medición desaparece si
alguien «simplifica» la regla durante la implementación, y en qué decisión `D-{nn}` está registrada.
```

**La columna *Consecuencia si se viola* no es decorativa.** Se redacta en condicional y describe el
daño concreto al dato o a la medición, no un genérico «se produciría un error». Compara:

- Mal: «El sistema fallaría».
- Bien: «Se contarían dos veces las mismas toneladas».
- Bien: «Dos ingresos serían indistinguibles como unidad de análisis».

Entre ocho y doce reglas por módulo con operaciones de escritura. Si salen menos de cinco, faltan
invariantes; revisa qué asume cada criterio de aceptación sin decirlo.

---

## Verificación final

- [ ] Todo RU tiene al menos un RS que lo realiza.
- [ ] Toda función de `funcionales.md` referencia una HU existente.
- [ ] Todo RNF tiene característica ISO/IEC 25010:2023 y método de verificación.
- [ ] Toda RN tiene consecuencia concreta redactada en condicional.
- [ ] Al menos un archivo del módulo explica su relación con el indicador de tesis.
