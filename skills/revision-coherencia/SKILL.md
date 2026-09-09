---
name: revision-coherencia
description: Verifica la coherencia y la trazabilidad cruzada de la documentación de la tesis minera — que cada HU tenga requisitos y diagramas, que los códigos RN, RNF, RU, RS y RF referenciados existan, que las rutas relativas resuelvan y que los módulos no se contradigan entre sí. Úsala antes de un commit de documentación, al terminar un módulo, o cuando se pida revisar, auditar o validar la documentación o buscar inconsistencias entre módulos.
---

# Revisión de coherencia

Carga antes `contexto-tesis`. Esta skill **no reescribe**: detecta, clasifica y reporta. Solo corrige
cuando el autor lo pide explícitamente, y nunca resuelve por su cuenta una divergencia entre dos
documentos que afirman cosas distintas — esa decisión es del autor de la tesis.

## Ejecución

Trabaja desde la raíz del repositorio. Las comprobaciones son acumulativas: no pares en la primera.

### 1. Códigos referenciados que no existen

Todo código citado en un documento debe estar definido en alguna tabla.

```bash
grep -rhoE "(RN|RNF|RU|RS)-M[0-9]{2}-[0-9]{2}" docs --include=*.md | sort -u > /tmp/citados.txt
grep -rhoE "^\| (RN|RNF|RU|RS)-M[0-9]{2}-[0-9]{2}" docs --include=*.md | tr -d '| ' | sort -u > /tmp/definidos.txt
comm -23 /tmp/citados.txt /tmp/definidos.txt
```

Lo que salga está **citado pero no definido**. Es el error más frecuente al ampliar un módulo: se
añade una regla en un diagrama y no se registra en `reglas_negocio.md`.

### 2. Historias sin cobertura

Cada `HU-M{nn}-{nn}` debe aparecer, además de en su `HU.md`, en `requisitos/funcionales.md` y en al
menos un diagrama. Recorre las historias del módulo y comprueba en qué carpetas aparece cada una;
la que no figure en requisitos o en diagramas está incompleta.

### 3. Numeración con saltos o duplicados

```bash
grep -rhoE "HU-M[0-9]{2}-[0-9]{2}" docs/modulos/*/HU.md | sort | uniq -c
```

Un identificador que aparece dos veces como encabezado `##` es un duplicado real. Un salto en la
serie solo es aceptable si una historia se retiró, y debe estar dicho en el módulo.

### 4. Tildes dentro de bloques Mermaid

Regla estricta del repositorio: ningún carácter acentuado, `ñ`, `¿` o `¡` dentro de un bloque de
código mermaid. Localiza los bloques y revisa su contenido; cada carácter acentuado que sobreviva
rompe el renderizado en la exportación del documento de tesis.

### 5. Rutas relativas rotas

Los documentos se enlazan entre sí con rutas relativas, y varias apuntan a carpetas que aún no
existen (`00-arquitectura/`, `03-pruebas/`).

```bash
grep -rnoE '\.\./[^` )]+\.md' docs --include=*.md | sort -u
```

Comprueba cada destino. Los que faltan **no son errores de escritura**: son trabajo pendiente.
Repórtalos en su propia lista y no los borres de los documentos.

### 6. Contradicciones entre módulos

La comprobación que ninguna herramienta hace por ti. Para cada módulo, contrasta lo que declara con
lo que otros módulos afirman de él, leyendo las tablas «Depende de» y «Es requerido por» de los
`notas.md`.

Si M03 declara que M08 registra los eventos de creación, modificación y anulación, la documentación
de M08 **debe** ofrecer exactamente eso. Una dependencia declarada por un módulo y no honrada por el
otro es un defecto de la tesis, no del código.

### 7. Backlog global contra módulos

`docs/HistoriasUsuario.md` es el backlog maestro y ya diverge de los `HU.md`. Divergencia
comprobada: `HU-M02-04` es «Desactivación de elementos del catálogo» en el backlog global y
«Gestión de clientes» en el módulo.

Compara los títulos de historia de ambos orígenes. Los `HU.md` por módulo son la versión más
reciente. **Reporta las divergencias; no las resuelvas.** Reescribir el backlog global sin decidirlo
el autor puede alterar el recuento de historias que ya figura en el documento de tesis.

### 8. Coherencia con el diseño de la investigación

Revisión de fondo, la que decide si la documentación sirve. Para cada módulo:

- [ ] La cabecera de `HU.md` declara RF, indicador, semana y número de historias, y ese número
      coincide con las historias efectivamente escritas.
- [ ] Ningún documento admite eliminación física de un registro.
- [ ] Ningún documento colapsa `hora_pesaje` y `hora_registro`.
- [ ] Todo RNF tiene característica ISO/IEC 25010:2023 y método de verificación.
- [ ] Toda operación restringida por rol tiene un criterio de aceptación que verifica el rechazo.
- [ ] Cada módulo explica en algún punto qué medición se pierde si se implementa mal.
- [ ] La semana asignada no precede a la de un módulo del que este depende.

## Formato del informe

```markdown
## Revisión de coherencia — {alcance}

### Bloqueantes
Contradicen el diseño de la investigación o rompen la trazabilidad.
- {archivo}:{línea} — {qué} — {qué indicador o regla compromete}

### Inconsistencias
Divergencias entre documentos que exigen decisión del autor.
- {qué dice A} vs. {qué dice B} — {por qué importa}

### Pendientes
Referencias a material que aún no existe.
- {archivo} remite a `{ruta}`, no creado

### Menores
Formato, tildes en Mermaid, numeración.
```

Ordena siempre por gravedad y **no mezcles categorías**: una tilde en un diagrama y una regla de
negocio que contradice a otro módulo no son el mismo tipo de problema, y presentarlas en la misma
lista hace que la segunda pase desapercibida.
