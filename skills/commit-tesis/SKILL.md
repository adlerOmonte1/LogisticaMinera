---
name: commit-tesis
description: Prepara la rama y el commit de la documentación de un módulo de la tesis minera con el formato exacto del repositorio. Úsala cuando se pida confirmar, commitear, guardar o subir la documentación de un módulo, o al cerrar el trabajo de un M**. Impone un commit por módulo, el formato docs(alcance) sin tildes y el nombre de rama del proyecto.
---

# Commit de documentación y de código

Este repositorio tiene **dos convenciones**, una por fase. Comprueba qué estás confirmando antes de
redactar el mensaje.

| Fase | Formato | Ramas |
|---|---|---|
| Documentación (actual) | `docs(alcance): Asunto` | `docs/{alcance}/{descripcion}` |
| Código (a partir de la semana 1) | `M03: descripcion (HU-M03-01)` | `feature/M03-ingresos` sobre `develop` |

La convención de código está fijada en `docs/00-arquitectura/convenciones_codigo.md` §4:

```
main                      Código desplegable
develop                   Integración
feature/M03-ingresos      Una rama por módulo
```

```
M03: registra hora de pesaje separada de hora de registro (HU-M03-01)
```

**Referencia siempre la historia de usuario** en el commit de código. Es lo que permite reconstruir
la trazabilidad `Indicador -> RF -> Módulo -> HU -> Caso de prueba -> Commit` desde el historial de
git, y es evidencia utilizable en sustentación. Un commit de código sin `HU-` rompe el último eslabón
de esa cadena.

---

## Convención de documentación — observada en el repositorio

```
docs(autenticacion): Definicion de las Historias de Usuario, requisitos y diagramas
docs(catalogo): Definicion de las Historias de Usuario, requisitos y diagramas
```

Reglas que se deducen del historial y deben mantenerse:

| Elemento | Regla |
|---|---|
| Tipo | `docs` mientras el repositorio solo contenga documentación |
| Alcance | El slug del módulo **sin el prefijo `M{nn}-`**: `autenticacion`, `catalogo`, `ingresos` |
| Asunto | Empieza en **mayúscula**, sin punto final |
| Tildes | **Ninguna** en el mensaje de commit: `Definicion`, no `Definición` |
| Granularidad | **Un commit por módulo.** Nunca varios módulos en un mismo commit |

Asunto estándar cuando se entrega el paquete completo de un módulo:

```
Definicion de las Historias de Usuario, requisitos y diagramas
```

Para entregas parciales, describe lo que efectivamente entra, con el mismo estilo:

```
docs(ingresos): Correccion de los criterios de aceptacion de HU-M03-02
docs(existencias): Diagramas de secuencia del kardex
```

## Ramas

```
docs/{alcance}/definicion-historias-de-usuario-diagramas
```

Ejemplo existente: `docs/catalogo/definicion-historias-de-usuario-diagramas`.
Minúsculas, guiones, sin tildes. Para trabajo parcial, describe el cambio:
`docs/ingresos/correccion-criterios-aceptacion`.

## Procedimiento

1. **Revisar antes de confirmar.** Ejecuta `revision-coherencia` sobre lo que va a entrar. No se
   commitea documentación con hallazgos bloqueantes sin decírselo al autor.

2. **Comprobar el estado real:**

```bash
git status --short
```

3. **Rama.** Si `git branch --show-current` devuelve `main`, crea la rama del módulo antes de nada.
   Si ya estás en la rama de otro módulo y vas a confirmar uno distinto, crea la suya: una rama por
   módulo, igual que un commit por módulo.

4. **Añadir solo el módulo que se confirma:**

```bash
git add docs/modulos/M03-ingresos
```

   Nunca `git add -A` con varios módulos pendientes. En este repositorio suele haber varias carpetas
   de módulo sin seguimiento a la vez (M03 a M07 lo estuvieron); un `add` indiscriminado los mezcla
   en un commit y deshace la trazabilidad por módulo.

5. **Confirmar:**

```bash
git commit -m "docs(ingresos): Definicion de las Historias de Usuario, requisitos y diagramas"
```

   Cuando el commit lo genera Claude, cierra el mensaje con la línea de atribución:

```
Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
```

6. **Repetir** para cada módulo pendiente, uno a uno.

## Límites

- No hagas `push` ni abras un *pull request* salvo petición explícita.
- No confirmes en `main`.
- No incluyas en el mismo commit cambios de documentación y cambios de configuración
  (`.claude/`, `.gitignore`): van por separado, con alcance propio.
- Ante un conflicto o un `rebase` en curso, detente y describe la situación en lugar de resolverla.
