---
name: requisitos-modulo
description: Redacta o revisa los cinco archivos de requerimientos de un módulo del sistema web inteligente de ingreso de mineral — usuario.md, sistema.md, funcionales.md, no_funcionales.md y reglas_negocio.md en docs/modulos/M**/requerimientos/. Úsala cuando se pidan requerimientos funcionales o no funcionales, reglas de negocio, requerimientos de usuario o de sistema, o cuando aparezcan identificadores RU-M**, RS-M**, RNF-M**, RN-M** o RF01 a RF10. Impone el formato de tabla, la trazabilidad entre niveles y la sección de responsabilidad y límites del módulo.
---

# Requerimientos de un módulo

Carga antes `contexto-tesis`. La referencia de estilo es `docs/modulos/M03-ingresos/requerimientos/`
(en reescritura para el sistema web inteligente; donde su versión actual contradiga esta skill,
manda la skill).

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
| RU-M{nn}-01 | Quiero sacarle una foto al ticket apenas el volquete sale de la balanza y que el sistema lea los datos |
| RU-M{nn}-02 | Si el sistema lee mal un número, quiero corregirlo ahí mismo antes de guardar |
| RU-M{nn}-03 | Quiero elegir de una lista qué tipo de mineral trajo el volquete |
| RU-M{nn}-04 | Cuando busque un ingreso, quiero ver la foto del ticket, no solo los números |

## Contexto del diagnóstico

Qué problema documentado en el diagnóstico responde cada RU relevante (transcripción posterior en
la oficina, respaldo en papel difícil de recuperar, total mensual reconstruido a mano).
```

Entre cuatro y ocho requerimientos. Si suenan a especificación («el sistema deberá…»), están mal:
reescríbelos como lo diría el supervisor de planta.

---

## `sistema.md`

La traducción técnica. Nombres de campo en `código`, comportamiento observable, sin decidir aún la
implementación.

```markdown
# Requerimientos de sistema — M{nn} {Nombre}

| Código | Requerimiento | Deriva de |
|---|---|---|
| RS-M{nn}-01 | El sistema conserva la `imagen_ticket` asociada al ingreso y asigna `hora_inicio_registro` al recibirla | RU-M{nn}-01 |
| RS-M{nn}-02 | El sistema presenta los seis campos reconocidos con su `confianza` y permite editarlos antes de confirmar | RU-M{nn}-02 |
| RS-M{nn}-05 | El sistema asigna `codigo` y `hora_fin_registro` dentro de la misma transacción | — (integridad con M05) |
```

Cuando un RS no nace de un RU sino de una necesidad de integridad entre módulos, la columna
*Deriva de* lleva `— (integridad con M05)`. Se admite, pero debe estar explícito.

Empieza siempre por «El sistema…» y en presente de indicativo. Nunca «deberá».

---

## `funcionales.md`

El contrato de la API. Es el puente entre la historia y el código.

```markdown
# Requerimientos funcionales — M{nn} {Nombre}

**RF asociado:** RF{nn} — {descripción del RF global}

| Función | Descripción | HU | Endpoint |
|---|---|---|---|
| Reconocer ticket | Recibe la imagen y devuelve los seis campos con su confianza | HU-M04-01 | `POST /api/v1/reconocimientos/` |
| Validar datos propuestos | Aplica V1 a V5 y devuelve las inconsistencias | HU-M05-01 | `POST /api/v1/validaciones/` |
| Registrar ingreso | Persiste los datos confirmados con código y hora de fin | HU-M03-01 | `POST /api/v1/ingresos/` |
| Anular ingreso | Baja lógica con motivo | HU-M03-07 | `PATCH /api/v1/ingresos/{id}/anular/` |

## Responsabilidad y límites

Qué hace este módulo, qué delega a otro y a través de qué interfaz. Por ejemplo: M03 no lee la
imagen ni aplica reglas; invoca `ReconocedorTicket` (M04) y `ValidadorConsistencia` (M05) y decide
con su resultado. Una función que no encaja en la responsabilidad declarada pertenece a otro módulo.

## Permisos

| Función | Administrador | Administrativo | Supervisor de planta |
|---|:---:|:---:|:---:|
| Consultar | Sí | Sí | Sí |
| Registrar y corregir | Sí | Sí | Sí |
| Anular | Sí | No | No |
```

**Convención de rutas:** `/api/v1/{recurso}/`, plural, con barra final. Acciones no CRUD como
sub-ruta explícita: `.../{id}/desactivar/`, `.../{id}/anular/`. La baja es `PATCH`, nunca `DELETE`.
Cuando el CRUD completo no aporta detalle, basta una fila con la ruta base
(`/api/v1/catalogo/vehiculos/`).

La tabla de permisos es obligatoria en todo módulo con operaciones de escritura. La sección
«Responsabilidad y límites» es obligatoria en todo módulo.

---

## `no_funcionales.md`

Cada RNF se clasifica bajo una característica de **ISO/IEC 25010:2023** —usada solo como taxonomía
de clasificación, no como instrumento de la tesis— y **declara su método de verificación**. Un RNF
que no se puede verificar no es un requisito: es un deseo.

```markdown
# Requerimientos no funcionales — M{nn} {Nombre}

| Código | Característica ISO/IEC 25010:2023 | Requerimiento | Verificación |
|---|---|---|---|
| RNF-M{nn}-01 | Eficiencia de desempeño — comportamiento temporal | El reconocimiento de un ticket devuelve resultado en menos de 5 segundos con imágenes de hasta 10 MB | Cronometraje sobre el conjunto de tickets de prueba |
| RNF-M{nn}-02 | Adecuación funcional — corrección | La imagen se acepta en JPG o PNG hasta 10 MB y se rechaza cualquier otro formato | Prueba automatizada con archivos de muestra |
| RNF-M{nn}-03 | Fiabilidad — tolerancia a fallos | El borrador del registro (imagen y campos editados) se conserva en el dispositivo ante pérdida de conexión y se reanuda al recuperarla | Inspección en dispositivo real con la red desactivada |
| RNF-M{nn}-04 | Seguridad — no repudio | La imagen del ticket se conserva sin modificación mientras exista el ingreso | Consulta de verificación sobre el almacén de imágenes |
| RNF-M{nn}-05 | Usabilidad — protección contra errores del usuario | Los campos con confianza inferior al umbral se resaltan antes de confirmar | Inspección en dispositivo real |
```

Características utilizadas en el repositorio: *Adecuación funcional — corrección* · *Eficiencia de
desempeño — comportamiento temporal* · *Usabilidad — operabilidad* · *Usabilidad — protección contra
errores del usuario* · *Fiabilidad — tolerancia a fallos* · *Seguridad — no repudio*.

Todo umbral es numérico y va con su condición de medición: «menos de 3 segundos **con 1000 ingresos
en base**». Un umbral sin carga declarada no es medible.

Métodos de verificación admitidos: prueba automatizada con datos de muestra, cronometraje sobre
el conjunto de prueba, observación cronometrada en campo, inspección en dispositivo real, consulta
de verificación sobre la base o el almacén de imágenes, inspección de código o configuración.

---

## `reglas_negocio.md`

Invariantes del dominio. Lo que sigue siendo cierto sin importar qué interfaz lo invoque.

```markdown
# Reglas de negocio — M{nn} {Nombre}

> Ubicación en el código: `apps/{app}/models/` (invariantes de la entidad) y
> `apps/{app}/services/` (reglas de proceso). Ninguna de estas reglas vive en `views/` ni en
> un componente Angular (D-08).

| Código | Regla | Consecuencia si se viola |
|---|---|---|
| RN-M{nn}-01 | El peso neto confirmado no difiere de bruto menos tara en más de 0,01 t (V1) | Se registrarían toneladas que el ticket no respalda |
| RN-M{nn}-02 | La tara es estrictamente menor que el peso bruto (V2) | El peso neto sería cero o negativo |
| RN-M{nn}-03 | La fecha del ticket no es posterior a la fecha de registro (V5) | El ingreso quedaría fechado en el futuro y el orden de los registros dejaría de ser reconstruible |
| RN-M{nn}-04 | `hora_inicio_registro` y `hora_fin_registro` las asigna el servidor y ningún rol las modifica | Las marcas de tiempo serían falsificables y el registro dejaría de ser atribuible |
| RN-M{nn}-05 | Ningún valor reconocido se persiste como dato del ingreso sin confirmación del usuario | Un error del motor se convertiría en dato oficial sin que nadie lo revisara |

## Nota sobre RN-M{nn}-{nn}

Los matices que la tabla no admite: por qué la regla se acota como se acota, qué caso límite
resuelve y en qué decisión `D-{nn}` está registrada cuando aplique.
```

**La columna *Consecuencia si se viola* no es decorativa.** Se redacta en condicional y describe el
daño concreto al dato, a su integridad o a su atribución; nunca un genérico «se produciría un
error» ni una referencia a la tesis. Compara:

- Mal: «El sistema fallaría».
- Mal: «El indicador dejaría de ser medible».
- Bien: «Se contarían dos veces las mismas toneladas».
- Bien: «Dos ingresos serían indistinguibles entre sí».

Entre ocho y doce reglas por módulo con operaciones de escritura. Si salen menos de cinco, faltan
invariantes; revisa qué asume cada criterio de aceptación sin decirlo.

---

## Verificación final

- [ ] Todo RU tiene al menos un RS que lo realiza.
- [ ] Toda función de `funcionales.md` referencia una HU existente.
- [ ] Todo RNF tiene característica ISO/IEC 25010:2023 y método de verificación.
- [ ] Toda RN tiene consecuencia concreta redactada en condicional, en términos del dominio.
- [ ] `funcionales.md` declara la responsabilidad y los límites del módulo.
- [ ] Cada función de `funcionales.md` tiene fila en `docs/02-trazabilidad/matriz_HU_RF_indicador.md`
      a través de su HU.
