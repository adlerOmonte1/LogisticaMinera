# Historias de usuario — M08 Consolidación de la producción

**RF asociado:** RF09 · **Historias:** 2

> Módulo de lectura que agrega los ingresos por mes y tipo de mineral. Restituye el total mensual de
> producción que la empresa llevaba antes y dejó de calcular por falta de tiempo. No tiene entidad
> propia: agrega sobre `INGRESO`, que pertenece a M03.

---

## HU-M08-01 — Total acumulado mensual por tipo de mineral

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M08-01 |
| **Épica** | Consolidación de la producción |
| **Prioridad** | Crítica |

**Historia**

Como administrativo, quiero obtener el total de toneladas ingresadas en un mes, separado por tipo de
mineral, para reportar la producción sin sumar los tickets a mano.

**Descripción**

La consolidación toma un mes y un año, y devuelve, por cada tipo de mineral que tuvo ingresos en ese
periodo, el número de ingresos y la suma de sus pesos netos. Los ingresos anulados quedan fuera del
cálculo: el total describe lo que efectivamente ingresó, no lo que se intentó registrar.

El cálculo se hace a demanda sobre los ingresos existentes, no sobre un acumulado que se actualiza
en cada registro. Un acumulado guardado se desincroniza en cuanto un ingreso se corrige o se anula
después de calculado, y el error pasaría inadvertido hasta que alguien comparara ambos números.

**Detalles**
- Periodo: mes y año, obligatorios.
- Agrupación: por tipo de mineral.
- Por cada tipo: número de ingresos y suma de toneladas.
- Excluye ingresos anulados.
- Un mes sin ingresos para un tipo de mineral no aparece en el resultado, no aparece con total cero.
- Roles autorizados: Administrativo y Administrador.

**Criterios de aceptación**

> **CA01.** Dado que el usuario indica un mes y un año con ingresos registrados, cuando solicita la
> consolidación, entonces el sistema muestra el total de toneladas por cada tipo de mineral que tuvo
> ingresos en ese periodo.

> **CA02.** Dado que un ingreso del periodo está anulado, cuando se calcula el total, entonces el
> sistema no lo incluye en la suma ni en el conteo.

> **CA03.** Dado que el mes indicado no tiene ningún ingreso, cuando se solicita la consolidación,
> entonces el sistema muestra "No hay ingresos registrados para el periodo indicado".

> **CA04.** Dado que el usuario indica un periodo futuro, cuando solicita la consolidación, entonces
> el sistema rechaza la operación mostrando "No se puede consolidar un periodo futuro".

> **CA05.** Dado que se corrige el peso neto de un ingreso ya consolidado en un cálculo anterior,
> cuando se vuelve a solicitar la consolidación de ese mismo periodo, entonces el sistema devuelve el
> total actualizado con la corrección.

> **CA06.** Dado que el usuario tiene rol de Supervisor de planta, cuando intenta solicitar la
> consolidación, entonces el sistema rechaza la operación mostrando "Acción no autorizada".

---

## HU-M08-02 — Exportación del total acumulado mensual

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M08-02 |
| **Épica** | Consolidación de la producción |
| **Prioridad** | Alta |

**Historia**

Como administrativo, quiero exportar el total mensual a un archivo, para entregarlo o archivarlo sin
tener que transcribirlo de la pantalla.

**Descripción**

La exportación toma el mismo cálculo de HU-M08-01 y lo entrega como archivo descargable, con el
periodo, la fecha de generación y el detalle por tipo de mineral. El formato inicial es hoja de
cálculo; el diseño admite añadir otros formatos sin modificar el cálculo que los alimenta.

**Detalles**
- Formatos: hoja de cálculo (XLSX) en la primera versión.
- Contenido: periodo consolidado, fecha de generación, total por tipo de mineral, número de ingresos
  por tipo.
- El archivo exportado usa los mismos totales que muestra la consulta en pantalla.
- Roles autorizados: Administrativo y Administrador.

**Criterios de aceptación**

> **CA01.** Dado que el usuario solicita exportar un periodo con ingresos, cuando el sistema genera
> el archivo, entonces lo entrega con el total por tipo de mineral y el número de ingresos de cada
> uno.

> **CA02.** Dado que el usuario solicita exportar un periodo sin ingresos, cuando el sistema procesa
> la solicitud, entonces rechaza la operación mostrando "No hay ingresos registrados para el periodo
> indicado".

> **CA03.** Dado que se genera el archivo, cuando el usuario lo abre, entonces el total de cada tipo
> de mineral coincide exactamente con el que muestra la consulta en pantalla para el mismo periodo.

> **CA04.** Dado que el usuario tiene rol de Supervisor de planta, cuando intenta exportar, entonces
> el sistema rechaza la operación mostrando "Acción no autorizada".

> **CA05.** Dado que la exportación se genera, cuando concluye la operación, entonces el sistema
> registra el evento en auditoría con el periodo exportado y el usuario responsable.
