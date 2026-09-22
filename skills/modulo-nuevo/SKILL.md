---
name: modulo-nuevo
description: Crea el paquete documental completo de un módulo del sistema web inteligente de ingreso de mineral — carpeta docs/modulos/M**-slug/ con HU.md, requerimientos/, diagramas/ y notas.md — siguiendo las convenciones de los módulos ya versionados. Úsala cuando se pida documentar, crear o completar un módulo nuevo (por ejemplo M04 reconocimiento, M05 validación o M06 trazabilidad), o cuando se pida "toda la documentación" de una parte del sistema. Orquesta las skills historias-usuario, requisitos-modulo y diagramas-uml en el orden correcto.
---

# Paquete documental de un módulo

Carga primero `contexto-tesis`. Este es el procedimiento completo, de la carpeta vacía al commit.

## 1. Determinar la identidad del módulo

Antes de crear nada, deja fijado y por escrito:

| Dato | Cómo se obtiene |
|---|---|
| Código y slug | `M{nn}-{slug-en-minúsculas-con-guiones}`, del mapa de módulos de `contexto-tesis` |
| Nombre | El que ya usan los demás módulos al referenciarlo (`grep -rn "M04" docs/modulos`) |
| Responsabilidad | Una frase: qué contexto del dominio cubre este módulo y ningún otro |
| RF principal | De la tabla RF01 a RF10 de `contexto-tesis`, o `— (transversal)` si no tiene |
| Interfaces que expone o consume | `ReconocedorTicket`, `ValidadorConsistencia`, `GeneradorCodigo`, servicios de otro módulo |
| Número de historias | Entre 3 y 7 |

El módulo se define por su **responsabilidad**, no por el indicador que sostiene: la relación con
la tesis se registra únicamente en `docs/02-trazabilidad/matriz_HU_RF_indicador.md`. Tampoco se le
asigna semana: el cronograma vive en `docs/01-plan/`.

**El paso previo obligatorio** es recolectar lo que los módulos ya escritos esperan de este:

```bash
grep -rn "M04" docs/modulos --include=*.md
```

Si M03 ya declara que invoca `ReconocedorTicket` para obtener seis campos con su nivel de
confianza, esa dependencia declarada **es un requisito vinculante**, no una sugerencia. Documentar
un módulo contradiciendo lo que otro ya afirma de él invalida la trazabilidad del documento entero.

Si la responsabilidad o el RF no se deducen del material existente, pregúntalo antes de escribir.
Inventarlos contamina la lista de control validada por expertos.

## 2. Crear la estructura

```bash
M=M04-reconocimiento
mkdir -p "docs/modulos/$M/requerimientos" "docs/modulos/$M/diagramas"
```

Todos los módulos usan `requerimientos/`. No emplees `requisitos/`: rompería los enlaces relativos
de los documentos ya versionados.

## 3. Redactar, en este orden

El orden importa: cada artefacto se apoya en el anterior y reescribir hacia atrás cuesta más.

| Paso | Archivo | Skill |
|---|---|---|
| 1 | `requerimientos/usuario.md` | `requisitos-modulo` |
| 2 | `HU.md` | `historias-usuario` |
| 3 | `requerimientos/sistema.md` | `requisitos-modulo` |
| 4 | `requerimientos/reglas_negocio.md` | `requisitos-modulo` |
| 5 | `requerimientos/funcionales.md` | `requisitos-modulo` |
| 6 | `requerimientos/no_funcionales.md` | `requisitos-modulo` |
| 7 | `diagramas/caso_uso.md` | `diagramas-uml` |
| 8 | `diagramas/actividades.md` | `diagramas-uml` |
| 9 | `diagramas/secuencia.md` | `diagramas-uml` |
| 10 | `notas.md` | esta skill, sección 4 |
| 11 | Filas en `docs/02-trazabilidad/matriz_HU_RF_indicador.md` | esta skill, sección 5 |

Se empieza por la voz del usuario y se termina por la nota técnica. Nunca al revés: un módulo
escrito desde el modelo de datos produce historias que describen la base de datos en lugar del
trabajo real de la planta.

## 4. `notas.md`

Es el puente entre la documentación y el código, y el lugar donde se registran los riesgos de
implementación. Existe en todo módulo que tenga o vaya a tener código. Estructura:

```markdown
# Notas de implementación — M{nn} {Nombre}

## Backend (Django)

**App:** `apps/{app}/`

### Modelo

```python
class Entidad(models.Model):
    codigo = models.CharField(max_length=20, unique=True, editable=False)
    # ... resto de campos
```

Explicación de las decisiones no obvias del modelo, cada una remitida a su `D-{nn}`.

### Servicio

Cómo se compone la operación, qué se inyecta (`ReconocedorTicket`, `ValidadorConsistencia`), qué
ocurre dentro de `transaction.atomic()` y qué regla de negocio se rompería si algo quedara fuera
de la transacción.

## Frontend (Angular)

**Feature:** `features/{feature}/`

- Decisiones de formulario y de estado, cada una citando la HU o el RNF que las obliga.

## Riesgo de implementación identificado

El punto más probable de fallo, cómo probarlo y por qué no basta con la prueba obvia.

## Dependencias

| Depende de | Para |
|---|---|
| M01 | Autenticación y atribución del registro al usuario |
| M04 | Propuesta de los seis campos del ticket |

| Es requerido por | Para |
|---|---|
| M08 | Total acumulado mensual por producto |
```

Convenciones técnicas del proyecto que deben respetarse en las notas:

- App Django `apps/{nombre}/` con la estructura por capas del repositorio: `models/` (invariantes),
  `services/` (escritura), `repositories/` (lectura, D-09), `serializers/`, `views/`. Las reglas
  **nunca** en `views/` ni en un componente Angular (D-08).
- Feature Angular `features/{nombre}/`.
- Cantidades en toneladas con **decimal, jamás punto flotante**: el error acumulado se confundiría
  con diferencias reales entre el ticket y lo registrado.
- Los campos asignados por el servidor van `editable=False`: el código único, la hora de inicio y
  la hora de fin del registro.
- Los campos de solo lectura en formularios se marcan `readonly`, **no** `disabled`: los
  deshabilitados no viajan en el payload.
- **El valor reconocido y el valor confirmado de cada campo se guardan por separado** (D-13): el
  primero pertenece al resultado del reconocimiento, el segundo al ingreso. Sobrescribir uno con
  otro hace imposible distinguir lo que leyó el motor de lo que corrigió el usuario.
- El motor concreto no aparece en el código de negocio: se inyecta detrás de `ReconocedorTicket`
  (D-12), igual que el generador de código único.
- Los índices declarados se crean **desde la primera migración**; añadirlos a mitad de la ventana
  de observación altera las condiciones de medición.

La sección **Riesgo de implementación identificado** es obligatoria y debe nombrar un riesgo
concreto y verificable, no una precaución genérica.

## 5. Cerrar el paquete

1. Añade una fila por historia a `docs/02-trazabilidad/matriz_HU_RF_indicador.md`: HU, título, rol,
   prioridad, RF, indicador, tarea y caso de prueba previsto. Es el único lugar donde este módulo
   se relaciona con la tesis.
2. Ejecuta `revision-coherencia` sobre el módulo nuevo.
3. Añade el módulo a la tabla de mapa de módulos de `skills/contexto-tesis/SKILL.md`.
4. Si el módulo aporta historias que no están en `docs/HistoriasUsuario.md`, añádelas al índice o
   señálalo al autor.
5. Confirma con `commit-tesis`.

## Criterio de módulo terminado

Un módulo está completo cuando cada historia aparece en `requerimientos/funcionales.md`, está
protegida por al menos una regla de negocio, se ve en al menos un diagrama y tiene fila en la
matriz de trazabilidad. Si falta cualquiera de esas cuatro cosas, el paquete está incompleto aunque
los diez archivos existan.
