# Historias de usuario — M02 Catálogo maestro

**RF asociado:** RF-03 · **Indicador:** I2 · **Semana:** 2 · **Historias:** 4

> Este módulo sostiene el indicador I2 (cobertura de registro por tipo de vehículo). Sin un catálogo de vehículos con titularidad clasificada, el hallazgo central del diagnóstico —que los volquetes propios se registran peor que los externos— no puede demostrarse con datos.

---

## HU-M02-01 — Gestión de productos

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M02-01 |
| **Épica** | Catálogo maestro |
| **Prioridad** | Crítica |

**Historia**

Como administrativo, quiero registrar y mantener los productos que maneja la planta, para que los ingresos y salidas se clasifiquen de forma consistente.

**Descripción**

Los productos vigentes son Saranda y Molido. El sulfuro queda fuera de alcance por decisión documentada. Cada producto tiene código único, nombre y unidad de medida (toneladas).

**Criterios de aceptación**

> **CA01.** Dado que el usuario completa código, nombre y unidad de medida, cuando guarda, entonces el sistema registra el producto en estado activo.

> **CA02.** Dado que el código de producto ya existe, cuando el usuario intenta guardar, entonces el sistema rechaza la operación mostrando "El código de producto ya está registrado".

> **CA03.** Dado que un producto tiene movimientos asociados, cuando el usuario intenta eliminarlo, entonces el sistema lo desactiva en lugar de eliminarlo y muestra "El producto se desactivó porque tiene movimientos registrados".

> **CA04.** Dado que un producto está desactivado, cuando el usuario abre el formulario de registro de ingreso, entonces el producto no aparece entre las opciones seleccionables.

---

## HU-M02-02 — Gestión de vehículos con clasificación de titularidad

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M02-02 |
| **Épica** | Catálogo maestro |
| **Prioridad** | Crítica |

**Historia**

Como administrativo, quiero registrar los volquetes indicando si son propios o de un transportista externo, para que el sistema pueda diferenciar la cobertura de registro entre ambos tipos.

**Descripción**

Cada vehículo se identifica por placa. El campo de titularidad es obligatorio y admite únicamente dos valores: PROPIO o EXTERNO. Si es externo, debe asociarse a un transportista registrado.

**Criterios de aceptación**

> **CA01.** Dado que el usuario completa placa, titularidad y capacidad, cuando guarda, entonces el sistema registra el vehículo en estado activo.

> **CA02.** Dado que la placa ya está registrada, cuando el usuario intenta guardar, entonces el sistema rechaza la operación mostrando "La placa ya está registrada".

> **CA03.** Dado que el usuario marca la titularidad como EXTERNO, cuando intenta guardar sin seleccionar transportista, entonces el sistema rechaza la operación mostrando "Debe indicar el transportista para un vehículo externo".

> **CA04.** Dado que el usuario marca la titularidad como PROPIO, cuando guarda, entonces el sistema acepta el registro sin transportista asociado.

> **CA05.** Dado que la placa no cumple el formato de placa vehicular peruana, cuando el usuario intenta guardar, entonces el sistema la rechaza mostrando "El formato de la placa no es válido".

---

## HU-M02-03 — Gestión de transportistas

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M02-03 |
| **Prioridad** | Alta |

**Historia**

Como administrativo, quiero registrar los transportistas externos, para asociarlos a sus vehículos y poder analizar la cobertura por proveedor.

**Criterios de aceptación**

> **CA01.** Dado que el usuario completa razón social y RUC, cuando guarda, entonces el sistema registra el transportista en estado activo.

> **CA02.** Dado que el RUC no tiene once dígitos, cuando el usuario intenta guardar, entonces el sistema lo rechaza mostrando "El RUC debe tener once dígitos".

> **CA03.** Dado que un transportista tiene vehículos asociados, cuando el usuario intenta eliminarlo, entonces el sistema lo desactiva y muestra "El transportista se desactivó porque tiene vehículos asociados".

---

## HU-M02-04 — Gestión de clientes

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M02-04 |
| **Prioridad** | Media |

**Historia**

Como administrativo, quiero registrar los clientes que reciben producto, para clasificar correctamente las salidas por venta.

**Criterios de aceptación**

> **CA01.** Dado que el usuario completa razón social y RUC, cuando guarda, entonces el sistema registra el cliente en estado activo.

> **CA02.** Dado que un cliente tiene salidas asociadas, cuando el usuario intenta eliminarlo, entonces el sistema lo desactiva en lugar de eliminarlo.

> **CA03.** Dado que un cliente está desactivado, cuando el usuario registra una salida, entonces el cliente no aparece entre las opciones seleccionables.
