# Reglas de negocio — M05 Validación automática de consistencia

> Ubicación en el código: `apps/validacion/reglas/` (una clase por regla) y
> `apps/validacion/services/` (la composición y el registro del resultado). Ninguna de estas reglas
> vive en `views/` ni en un componente Angular (D-08).

| Código | Regla | Consecuencia si se viola |
|---|---|---|
| RN-M05-01 | Las reglas V1 a V5 se ejecutan en el servidor; el cliente solo muestra el resultado | Una petición que no pase por el formulario entraría sin validar, y el histórico contendría datos que el sistema declara imposibles |
| RN-M05-02 | Un ingreso no se confirma con una regla bloqueante incumplida | Se registrarían toneladas que el ticket no respalda |
| RN-M05-03 | V4 no bloquea, pero exige justificación escrita para confirmar | Una sobrecarga quedaría registrada sin explicación y sería indistinguible de un error de lectura |
| RN-M05-04 | Las cinco reglas se evalúan siempre; ninguna se omite porque otra ya haya fallado | El usuario corregiría un error por intento, y un trabajo de segundos se convertiría en varios ciclos |
| RN-M05-05 | Las reglas se aplican sobre los datos propuestos y de nuevo sobre los confirmados | Un error introducido por el usuario al corregir entraría sin comprobarse |
| RN-M05-06 | El resultado de cada regla aplicada se persiste junto al ingreso, con su momento y su resolución | No se podría reconstruir qué se revisó, ni quién justificó una advertencia ni con qué explicación |
| RN-M05-07 | Una regla cuyos datos necesarios faltan no se evalúa ni se reporta como incumplida | Un campo vacío produciría dos mensajes contradictorios: uno que pide el dato y otro que lo declara incoherente |
| RN-M05-08 | El mensaje de cada regla es literal y no se reformula en la interfaz | Las pruebas que comprueban el texto exacto dejarían de valer y el usuario vería mensajes distintos según la pantalla |
| RN-M05-09 | Las reglas y sus parámetros no cambian durante la ventana de operación controlada (D-16) | Dos ingresos del mismo periodo habrían sido evaluados con criterios distintos |
| RN-M05-10 | V4 toma la capacidad del vehículo del catálogo, nunca un valor fijo en el código | Un vehículo con capacidad distinta se evaluaría contra un límite que no le corresponde |
| RN-M05-11 | Añadir una regla nueva no modifica las existentes ni el servicio que las compone | Cada regla añadida arriesgaría romper las anteriores, y el conjunto se volvería frágil |

## Nota sobre RN-M05-03

Es la única regla que no bloquea, y la excepción es deliberada. Una sobrecarga puede ser un hecho
real: el volquete efectivamente trajo más carga de la que declara su capacidad. Bloquear el registro
obligaría al usuario a falsear el peso para poder continuar, que es exactamente lo contrario de lo
que el sistema busca. Exigir la justificación conserva el hecho y su explicación.

## Nota sobre RN-M05-04 y RN-M05-07

Ambas gobiernan qué se le muestra al usuario y cuándo. RN-M05-04 evita el ciclo de corregir un error
por intento. RN-M05-07 evita el ruido contrario: señalar como incoherente un dato que sencillamente
no está. La combinación de las dos es lo que hace que la lista de inconsistencias sea accionable —
todo lo que aparece es algo que el usuario puede arreglar ahora.

## Nota sobre RN-M05-11

Las cinco reglas actuales provienen del instrumento de la investigación, pero el sistema debe poder
incorporar otras —una placa que no está en el catálogo, un tipo de mineral incompatible con el
vehículo— sin rehacer lo existente. Por eso cada regla es una clase independiente que se registra en
una colección, y el servicio recorre esa colección sin conocer sus miembros. Durante la ventana de
operación controlada, sin embargo, el conjunto queda congelado (RN-M05-09).
