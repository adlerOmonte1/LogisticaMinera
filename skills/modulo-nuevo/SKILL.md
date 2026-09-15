---
name: modulo-nuevo
description: Crea el paquete documental completo de un módulo del sistema de la tesis minera — carpeta docs/modulos/M**-slug/ con HU.md, requisitos/, diagramas/ y notas.md — siguiendo las convenciones de los módulos ya versionados. Úsala cuando se pida documentar, crear o completar un módulo nuevo (por ejemplo M08 auditoría o M09 búsqueda), o cuando se pida "toda la documentación" de una parte del sistema. Orquesta las skills historias-usuario, requisitos-modulo y diagramas-uml en el orden correcto.
---

# Paquete documental de un módulo

Carga primero `contexto-tesis`. Este es el procedimiento completo, de la carpeta vacía al commit.

## 1. Determinar la identidad del módulo

Antes de crear nada, deja fijado y por escrito:

| Dato | Cómo se obtiene |
|---|---|
| Código y slug | `M{nn}-{slug-en-minúsculas-con-guiones}`, continuando la numeración existente |
| Nombre | El que ya usan los demás módulos al referenciarlo (`grep -rn "M08" docs/`) |
| RF global asociado | De la tabla RF-01 a RF-10 de `contexto-tesis` |
| Indicador de tesis | I1 a I6, o `— (habilitante)` si el módulo solo da soporte |
| Semana del cronograma | Coherente con las dependencias: un módulo no puede preceder a aquel del que depende |
| Número de historias | Entre 3 y 7 |

**El paso previo obligatorio** es recolectar lo que los módulos ya escritos esperan de este:

```bash
grep -rn "M08" docs/modulos --include=*.md
```

M08 y M09 ya están referenciados por M03, M05 y otros: sus dependencias declaradas
(«Registro de eventos de creación, modificación y anulación») **son requisitos vinculantes**, no
sugerencias. Documentar un módulo contradiciendo lo que otro ya afirma de él invalida la
trazabilidad del documento entero.

Si el indicador o la semana no se deducen del material existente, pregúntalo antes de escribir.
Inventarlos contamina la tabla de trazabilidad de la tesis.

## 2. Crear la estructura

```bash
M=M08-auditoria
mkdir -p "docs/modulos/$M/requisitos" "docs/modulos/$M/diagramas"
```

Usa `requisitos/` (no `requerimientos/`): es lo que emplean M03 a M07. Ver la nota sobre esta
inconsistencia en `contexto-tesis`.

## 3. Redactar, en este orden

El orden importa: cada artefacto se apoya en el anterior y reescribir hacia atrás cuesta más.

| Paso | Archivo | Skill |
|---|---|---|
| 1 | `requisitos/usuario.md` | `requisitos-modulo` |
| 2 | `HU.md` | `historias-usuario` |
| 3 | `requisitos/sistema.md` | `requisitos-modulo` |
| 4 | `requisitos/reglas_negocio.md` | `requisitos-modulo` |
| 5 | `requisitos/funcionales.md` | `requisitos-modulo` |
| 6 | `requisitos/no_funcionales.md` | `requisitos-modulo` |
| 7 | `diagramas/caso_uso.md` | `diagramas-uml` |
| 8 | `diagramas/actividades.md` | `diagramas-uml` |
| 9 | `diagramas/secuencia.md` | `diagramas-uml` |
| 10 | `notas.md` | esta skill, sección 4 |

Se empieza por la voz del usuario y se termina por la nota técnica. Nunca al revés: un módulo
escrito desde el modelo de datos produce historias que describen la base de datos en lugar del
trabajo real de la planta.

## 4. `notas.md`

Es el puente entre la documentación y el código, y el lugar donde se registran los riesgos de
implementación. Solo existe de M03 en adelante. Estructura:

```markdown
# Notas de implementación — M{nn} {Nombre}

## Backend (Django)

**App:** `apps/{app}/`

### Modelo

```python
class Entidad(models.Model):
    campo = models.CharField(max_length=20, unique=True, editable=False)
    # ... resto de campos
```

Explicación de las decisiones no obvias del modelo, cada una remitida a su `D-{nn}`.

### Servicio

Cómo se compone la operación, qué ocurre dentro de `transaction.atomic()` y qué regla de negocio
se rompería si algo quedara fuera de la transacción.

## Frontend (Angular)

**Feature:** `features/{feature}/`

- Decisiones de formulario y de estado, cada una citando la HU o el RNF que las obliga.

## Riesgo de implementación identificado

El punto más probable de fallo, cómo probarlo y por qué no basta con la prueba obvia.

## Dependencias

| Depende de | Para |
|---|---|
| M01 | Autenticación y atribución del registro al usuario |

| Es requerido por | Para |
|---|---|
| M05 | Cálculo de existencias |
```

Convenciones técnicas del proyecto que deben respetarse en las notas:

- App Django `apps/{nombre}/`, con `models.py` (invariantes), `services.py` (escritura),
  `selectors.py` (lectura). Las reglas **nunca** en `views.py`.
- Feature Angular `features/{nombre}/`.
- Cantidades en toneladas con **decimal, jamás punto flotante**: el error acumulado se confundiría
  con desviación real de inventario y contaminaría I4.
- Los campos calculados o asignados por el servidor van `editable=False`.
- Los campos de solo lectura en formularios se marcan `readonly`, **no** `disabled`: los
  deshabilitados no viajan en el payload.
- Los índices declarados se crean **desde la primera migración**; añadirlos a mitad de la ventana de
  observación altera las condiciones de medición de I5.

La sección **Riesgo de implementación identificado** es obligatoria y debe nombrar un riesgo
concreto y verificable, no una precaución genérica.

## 5. Cerrar el paquete

1. Ejecuta `revision-coherencia` sobre el módulo nuevo.
2. Añade el módulo a la tabla de mapa de módulos de `.claude/skills/contexto-tesis/SKILL.md`.
3. Si el módulo aporta historias que no están en `docs/HistoriasUsuario.md`, señálalo al autor —
   ese archivo es el backlog global y ya arrastra divergencias; no lo edites sin decirlo.
4. Confirma con `commit-tesis`.

## Criterio de módulo terminado

Un módulo está completo cuando cada historia aparece en `funcionales.md`, está protegida por al
menos una regla de negocio, se ve en al menos un diagrama, y el archivo explica en algún punto qué
indicador de la tesis deja de ser medible si el módulo se implementa mal. Si falta cualquiera de
esas cuatro cosas, el paquete está incompleto aunque los diez archivos existan.
