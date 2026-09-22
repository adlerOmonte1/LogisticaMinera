# Historias de usuario — M05 Validación automática de consistencia

**RF asociado:** RF03 · **Historias:** 1

> Módulo que decide si los datos de un ticket son coherentes entre sí y con el catálogo. Aplica las
> cinco reglas V1 a V5 en el servidor, primero sobre lo que propone el reconocimiento y otra vez
> sobre lo que el usuario confirma, y conserva el resultado de cada evaluación. No lee la imagen ni
> persiste el ingreso: devuelve una lista de inconsistencias y quien decide qué hacer con ella es M03.

---

## HU-M05-01 — Detección y resolución de inconsistencias del ticket

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M05-01 |
| **Épica** | Validación automática de consistencia |
| **Prioridad** | Crítica |

**Historia**

Como supervisor de planta, quiero que el sistema señale automáticamente los datos del ticket que no
son coherentes, para corregirlos antes de que el ingreso quede registrado y no descubrirlos cuando
el volquete ya se fue.

**Descripción**

El validador aplica cinco reglas sobre los datos del ticket: que el peso neto coincida con el bruto
menos la tara, que la tara sea menor que el bruto, que la placa tenga un formato válido, que el peso
neto esté dentro del rango de carga del vehículo y que la fecha del ticket no sea posterior al
momento del registro.

Las reglas se ejecutan dos veces: sobre los valores que propone el reconocimiento, para señalar de
inmediato lo que no cuadra, y de nuevo sobre los valores que el usuario confirma, porque entre una y
otra el usuario pudo haber introducido un error nuevo. Se ejecutan siempre en el servidor: la
interfaz solo muestra el resultado.

Cuatro de las cinco reglas bloquean la confirmación. La quinta, la del rango de carga, no bloquea
porque una sobrecarga real puede ocurrir, pero exige una justificación escrita: el sistema no
impide registrar el hecho, impide registrarlo sin explicación.

Al confirmarse el ingreso, el sistema guarda el resultado de cada regla aplicada y la justificación
si la hubo, de modo que después pueda saberse qué se revisó y cómo se resolvió.

**Detalles**

| Regla | Condición que señala | Mensaje | Efecto |
|---|---|---|---|
| V1 | El peso neto difiere del bruto menos la tara en más de la tolerancia | "El peso neto no coincide con el peso bruto menos la tara" | Bloquea |
| V2 | La tara es mayor o igual que el peso bruto | "La tara no puede ser mayor o igual que el peso bruto" | Bloquea |
| V3 | La placa no corresponde al patrón de placa peruana | "La placa no tiene un formato válido" | Bloquea |
| V4 | El peso neto supera la capacidad del vehículo o no es positivo | "El peso neto está fuera del rango de carga del vehículo {placa}" | Exige justificación |
| V5 | La fecha del ticket es posterior al momento del registro | "La fecha del ticket no puede ser posterior a la fecha de registro" | Bloquea |

- Tolerancia de V1: 0,01 toneladas.
- Capacidad de V4: la declarada para el vehículo en el catálogo.
- Justificación de V4: texto obligatorio para poder confirmar.
- Las reglas no se evalúan sobre campos vacíos: un campo sin dato lo reclama el registro, no el
  validador.

**Criterios de aceptación**

> **CA01.** Dado que los datos incumplen una regla bloqueante, cuando el sistema los valida,
> entonces señala el campo afectado con el mensaje literal de esa regla.

> **CA02.** Dado que el peso neto queda fuera del rango de carga del vehículo, cuando el usuario
> intenta confirmar sin justificación, entonces el sistema rechaza la operación mostrando "Debe
> indicar la justificación del peso fuera de rango".

> **CA03.** Dado que el usuario escribe la justificación del peso fuera de rango, cuando confirma el
> ingreso, entonces el sistema lo acepta y conserva la justificación.

> **CA04.** Dado que el usuario corrige un dato señalado, cuando el sistema vuelve a validar,
> entonces retira la alerta si la regla ya se cumple.

> **CA05.** Dado que los datos incumplen varias reglas a la vez, cuando el sistema los valida,
> entonces informa todas las inconsistencias, no solo la primera.

> **CA06.** Dado que todos los datos cumplen las cinco reglas, cuando el sistema los valida,
> entonces no muestra alertas y habilita la confirmación.

> **CA07.** Dado que una petición llega sin pasar por el formulario, cuando el sistema la procesa,
> entonces aplica las mismas cinco reglas y la rechaza si incumple alguna bloqueante.

> **CA08.** Dado que el ingreso se confirma, cuando el sistema lo persiste, entonces guarda el
> resultado de cada una de las cinco reglas y la justificación, si la hubo.

> **CA09.** Dado que un campo requerido está vacío, cuando el sistema valida, entonces no lo señala
> como inconsistencia: la ausencia del dato la reclama el registro.
