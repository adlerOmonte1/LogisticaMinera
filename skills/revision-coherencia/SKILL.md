---
name: revision-coherencia
description: Verifica la coherencia y la trazabilidad cruzada de la documentación del sistema web inteligente de ingreso de mineral — que cada HU tenga requerimientos, diagramas y fila en la matriz de trazabilidad, que los códigos RN, RNF, RU, RS y RF referenciados existan, que las rutas relativas resuelvan, que no sobrevivan conceptos del sistema anterior y que los módulos no se contradigan entre sí. Úsala antes de un commit de documentación, al terminar un módulo, o cuando se pida revisar, auditar o validar la documentación o buscar inconsistencias entre módulos.
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

Para los requerimientos funcionales globales, el formato vigente es `RF01` **sin guion**. Toda
aparición del formato con guion es un residuo del sistema anterior y se reporta como bloqueante:

```bash
grep -rnE "RF-[0-9]{2}" docs skills --include=*.md
grep -rhoE "\bRF[0-9]{2}\b" docs --include=*.md | sort -u
```

La segunda orden no debe devolver ningún código fuera del rango RF01 a RF10.

### 2. Historias sin cobertura

Cada `HU-M{nn}-{nn}` debe aparecer, además de en su `HU.md`, en `requerimientos/funcionales.md`, en
al menos un diagrama y en `docs/02-trazabilidad/matriz_HU_RF_indicador.md`. Recorre las historias
del módulo y comprueba en qué archivos aparece cada una; la que no figure en los cuatro está
incompleta.

### 3. Numeración con saltos o duplicados

```bash
grep -rhoE "HU-M[0-9]{2}-[0-9]{2}" docs/modulos/*/HU.md | sort | uniq -c
```

Un identificador que aparece dos veces como encabezado `##` es un duplicado real. Un salto en la
serie solo es aceptable si una historia se retiró, y debe estar dicho en el módulo.

### 4. Tildes dentro de bloques Mermaid

Regla estricta del repositorio: ningún carácter acentuado, `ñ`, `¿` o `¡` dentro de un bloque de
código mermaid. Localiza los bloques y revisa su contenido; cada carácter acentuado que sobreviva
rompe el renderizado en la exportación del documento de tesis. Comprueba también que ningún
diagrama nombre el motor de reconocimiento concreto en lugar de `ReconocedorTicket` (D-12).

### 5. Rutas relativas rotas

Los documentos se enlazan entre sí con rutas relativas, y varias apuntan a carpetas que aún no
existen (`02-trazabilidad/`, `03-pruebas/`).

```bash
grep -rnoE '\.\./[^` )]+\.md' docs --include=*.md | sort -u
```

Comprueba cada destino. Los que faltan **no son errores de escritura**: son trabajo pendiente.
Repórtalos en su propia lista y no los borres de los documentos. Atención especial a los enlaces
que apunten a carpetas de módulo retiradas en la renumeración: esos sí son errores.

### 6. Contradicciones entre módulos

La comprobación que ninguna herramienta hace por ti. Para cada módulo, contrasta lo que declara con
lo que otros módulos afirman de él, leyendo las tablas «Depende de» y «Es requerido por» de los
`notas.md` y la sección «Responsabilidad y límites» de cada `funcionales.md`.

Si M03 declara que invoca `ValidadorConsistencia` para aplicar V1 a V5 y que M09 registra los
eventos de creación, corrección y anulación, la documentación de M05 y de M09 **debe** ofrecer
exactamente eso. Una dependencia declarada por un módulo y no honrada por el otro es un defecto de
la documentación, no del código.

### 7. Índice global contra módulos

`docs/HistoriasUsuario.md` es un **índice** generado desde los `HU.md`: identificador, título, rol,
prioridad y enlace, sin criterios de aceptación. La divergencia que se reporta es de **lista**: una
historia que está en un `HU.md` y falta en el índice, o al revés, o un título que no coincide. No
compares criterios de aceptación: el índice no los contiene por diseño.

Los `HU.md` por módulo son la versión más reciente. **Reporta las divergencias; no las resuelvas.**
Reescribir el índice sin decidirlo el autor puede alterar el recuento de historias que ya figura en
el documento de tesis.

### 8. Coherencia con el diseño del sistema

Revisión de fondo, la que decide si la documentación sirve. Para cada módulo:

- [ ] La cabecera de `HU.md` declara los RF asociados y el número de historias, y ese número
      coincide con las historias efectivamente escritas.
- [ ] Ningún documento admite eliminación física de un registro.
- [ ] El ingreso conserva tres marcas de tiempo independientes, y las dos asignadas por el servidor
      (inicio y fin del registro) no son editables por ningún rol.
- [ ] Ningún criterio de aceptación persiste un dato reconocido sin confirmación del usuario, ni
      omite guardar por separado el valor reconocido y el confirmado.
- [ ] Ningún archivo de `docs/modulos/` cita indicadores de la tesis ni contiene secciones que
      relacionen el módulo con la medición; el patrón exacto lo detecta el script de la
      comprobación 9.
- [ ] Cada HU tiene fila en `docs/02-trazabilidad/matriz_HU_RF_indicador.md`.
- [ ] Cada `funcionales.md` declara la responsabilidad y los límites del módulo, y ninguna función
      excede esa responsabilidad.
- [ ] Todo RNF tiene característica ISO/IEC 25010:2023 y método de verificación.
- [ ] Toda operación restringida por rol tiene un criterio de aceptación que verifica el rechazo.

### 9. Conceptos del sistema anterior

El repositorio documentó antes otro alcance, retirado en la reformulación del 21/09/2026. Ningún
término de aquel sistema debe sobrevivir en la documentación vigente. El patrón de búsqueda está
centralizado en un solo lugar —`scripts/verificar_migracion.sh`, Anexo F del plan de migración—
para no duplicarlo ni reintroducir los términos retirados en esta skill:

```bash
bash scripts/verificar_migracion.sh
```

El script excluye los documentos que describen la propia migración, porque esos sí deben conservar
la terminología antigua. Cualquier otra coincidencia es un residuo: repórtala como bloqueante
indicando archivo y línea. Si el script aún no existe, toma su patrón del Anexo F del plan y
ejecútalo tal cual, sin transcribirlo a este archivo.

Revisa además que no se citen las carpetas de módulo retiradas en la renumeración ni sus historias,
y que los módulos M01 a M09 correspondan al mapa de `contexto-tesis`.

## Formato del informe

```markdown
## Revisión de coherencia — {alcance}

### Bloqueantes
Contradicen el diseño del sistema o rompen la trazabilidad.
- {archivo}:{línea} — {qué} — {qué regla, dependencia o contrato compromete}

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
