# Historias de usuario — M06 Consolidados y reportes

**RF asociados:** RF-06, RF-07 · **Indicador de tesis:** I6 · **Semana:** 7 · **Historias:** 3

> El indicador I6 mide el porcentaje de meses con reporte de producción consolidado disponible. La empresa tuvo ese reporte y lo perdió por falta de tiempo; este módulo lo restituye de forma automática.

---

## HU-M06-01 — Consolidado mensual de producción

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M06-01 |
| **Épica** | Consolidados y reportes |
| **Prioridad** | Crítica |

**Historia**

Como administrativo, quiero generar el consolidado mensual de producción con un clic, para que el reporte exista todos los meses y no dependa de que alguien tenga tiempo de armarlo.

**Descripción**

El consolidado agrupa los ingresos del mes por producto, mostrando cantidad de viajes, toneladas totales y desagregación por titularidad del vehículo. Incluye las salidas y el saldo de cierre.

**Criterios de aceptación**

> **CA01.** Dado que el usuario selecciona un mes y confirma, cuando el sistema procesa la solicitud, entonces genera el consolidado con toneladas ingresadas por producto, cantidad de viajes y desagregación entre vehículos propios y externos.

> **CA02.** Dado que el mes seleccionado no tiene ingresos registrados, cuando se genera el consolidado, entonces el sistema lo produce igualmente con valores en cero y una nota que lo indica, en lugar de fallar.

> **CA03.** Dado que existen ingresos anulados en el mes, cuando se genera el consolidado, entonces el sistema los excluye del cálculo y reporta su cantidad por separado.

> **CA04.** Dado que el consolidado se genera, cuando el usuario lo consulta, entonces muestra también las salidas del mes por tipo de movimiento y el saldo de cierre por producto.

> **CA05.** Dado que el usuario genera un consolidado, cuando concluye la operación, entonces el sistema registra el evento en auditoría con el periodo consultado.

---

## HU-M06-02 — Exportación de reportes

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M06-02 |
| **Prioridad** | Alta |

**Historia**

Como administrativo, quiero exportar el consolidado a Excel y PDF, para enviarlo o archivarlo fuera del sistema.

**Criterios de aceptación**

> **CA01.** Dado que el consolidado está en pantalla, cuando el usuario solicita la exportación a Excel, entonces el sistema genera un archivo con los mismos datos, encabezados legibles y valores numéricos como números, no como texto.

> **CA02.** Dado que el consolidado está en pantalla, cuando el usuario solicita la exportación a PDF, entonces el sistema genera un archivo con el periodo, la fecha de generación y el usuario que lo generó en el encabezado.

> **CA03.** Dado que la exportación se completa, cuando concluye la operación, entonces el sistema registra el evento EXPORTAR en auditoría.

> **CA04.** Dado que el usuario tiene rol Supervisor, cuando intenta exportar, entonces el sistema rechaza la operación respondiendo "Acción no autorizada".

---

## HU-M06-03 — Formato de declaración semestral

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M06-03 |
| **Prioridad** | Media |

**Historia**

Como administrador, quiero obtener los datos de producción en el formato de la declaración semestral, para no tener que rearmarlos manualmente cada vez que corresponde presentarla.

**Descripción**

El sistema agrupa la producción del semestre según la estructura del formato oficial vigente. No presenta la declaración ni se conecta con ninguna entidad: produce el archivo que el responsable revisa y presenta.

**Criterios de aceptación**

> **CA01.** Dado que el usuario selecciona un semestre, cuando confirma, entonces el sistema genera el consolidado semestral con la estructura del formato oficial.

> **CA02.** Dado que el semestre seleccionado está incompleto respecto a la fecha actual, cuando se genera, entonces el sistema lo produce con los datos disponibles e indica de forma visible que el periodo aún no ha concluido.

> **CA03.** Dado que un usuario con rol distinto de Administrador intenta generar la declaración, cuando envía la solicitud, entonces el sistema la rechaza respondiendo "Acción no autorizada".

> **CA04.** Dado que la declaración se genera, cuando concluye, entonces el sistema registra en auditoría el periodo y el responsable.
