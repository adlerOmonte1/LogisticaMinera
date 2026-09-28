# Historias de usuario — M02 Catálogo maestro

**RF asociado:** RF06 (soporte) · **Historias:** 3

> Módulo de soporte. Mantiene los datos que el registro de ingresos referencia y no digita:
> vehículos con su titularidad, capacidad y tara, tipos de mineral y transportistas. Sin este
> catálogo, el tipo de vehículo se capturaría como texto libre, la capacidad no existiría para
> contrastarla contra la regla V4 y el peso neto no podría calcularse, porque el ticket de balanza
> solo imprime el peso bruto.

---

## HU-M02-01 — Gestión del catálogo de vehículos

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M02-01 |
| **Épica** | Catálogo maestro |
| **Prioridad** | Crítica |

**Historia**

Como administrativo, quiero registrar y mantener los volquetes indicando si son propios o de un
transportista externo, su capacidad de carga y su tara, para que el registro de ingresos derive el
tipo de vehículo del catálogo, calcule el peso neto y pueda contrastarlo contra la capacidad.

**Descripción**

Cada vehículo se identifica por placa, única en el catálogo. La titularidad es obligatoria y admite
únicamente dos valores: PROPIO o EXTERNO. Un vehículo externo debe asociarse a un transportista
registrado; uno propio no lleva transportista. La capacidad de carga se declara en toneladas y es la
que la regla V4 usa para señalar un peso neto fuera de rango.

La tara es el peso del vehículo vacío. No se captura al dar de alta el vehículo: se obtiene en el
destare de su primer viaje y la registra el usuario desde el ingreso que quedó En proceso
(HU-M03-04). Hasta entonces el vehículo figura como pendiente de destare. Una vez registrada, la tara
se mantiene por decisión de la Gerencia: solo el Administrador puede modificarla, indicando el
motivo, y el cambio no altera los ingresos ya registrados, que conservan la tara que se les aplicó.

Un vehículo puede darse de alta desde este catálogo o desde la pantalla de registro de un ingreso,
cuando la placa del ticket no está registrada (HU-M03-01). En ambos casos se aplican las mismas
reglas: el alta desde el registro no es un camino con menos controles.

**Detalles**
- Placa: obligatoria, única, formato de placa peruana.
- Titularidad: obligatoria, PROPIO o EXTERNO.
- Capacidad de carga: obligatoria, decimal positivo, en toneladas.
- Tara: sin valor al dar de alta; decimal positivo en toneladas, registrada en el destare del primer
  viaje, con su fecha y el usuario que la registró. Solo el Administrador la modifica, con motivo.
- Transportista: obligatorio si la titularidad es EXTERNO; no se admite si es PROPIO.
- Baja: lógica; un vehículo con ingresos asociados se desactiva, nunca se elimina.
- Alta: desde el catálogo o desde el registro de un ingreso, con las mismas reglas.

**Criterios de aceptación**

> **CA01.** Dado que el usuario completa placa, titularidad y capacidad, cuando guarda, entonces el
> sistema registra el vehículo en estado activo.

> **CA02.** Dado que la placa ya está registrada, cuando el usuario intenta guardar, entonces el
> sistema rechaza la operación mostrando "La placa ya está registrada".

> **CA03.** Dado que la placa no cumple el formato de placa vehicular peruana, cuando el usuario
> intenta guardar, entonces el sistema la rechaza mostrando "El formato de la placa no es válido".

> **CA04.** Dado que el usuario marca la titularidad como EXTERNO, cuando intenta guardar sin
> seleccionar transportista, entonces el sistema rechaza la operación mostrando "Debe indicar el
> transportista para un vehículo externo".

> **CA05.** Dado que el usuario marca la titularidad como PROPIO, cuando guarda, entonces el sistema
> acepta el registro sin transportista asociado.

> **CA06.** Dado que un vehículo tiene ingresos asociados, cuando el usuario intenta eliminarlo,
> entonces el sistema lo desactiva en lugar de eliminarlo y muestra "El vehículo se desactivó porque
> tiene ingresos registrados".

> **CA07.** Dado que un vehículo está desactivado, cuando se registra un ingreso nuevo, entonces el
> sistema no permite asociarlo a ese ingreso.

> **CA08.** Dado que el usuario da de alta un vehículo, cuando guarda, entonces el sistema lo registra
> sin tara y lo muestra como pendiente de destare.

> **CA09.** Dado que un vehículo ya tiene tara, cuando un usuario que no es Administrador intenta
> modificarla, entonces el sistema rechaza la operación mostrando "Solo el Administrador puede
> modificar la tara del vehículo".

> **CA10.** Dado que el Administrador modifica la tara de un vehículo, cuando intenta guardar sin
> indicar el motivo, entonces el sistema rechaza la operación mostrando "Debe indicar el motivo del
> cambio de tara".

> **CA11.** Dado que el Administrador modifica la tara con motivo, cuando guarda, entonces el sistema
> actualiza la tara, registra en auditoría el valor anterior, el nuevo y el motivo, y los ingresos ya
> registrados de ese vehículo conservan el peso neto con que se registraron.

> **CA12.** Dado que la placa de un ticket no está en el catálogo, cuando el usuario da de alta el
> vehículo desde la pantalla de registro, entonces el sistema aplica las mismas validaciones que el
> alta desde el catálogo y devuelve al registro con el vehículo ya asociado.

---

## HU-M02-02 — Gestión del catálogo de tipos de mineral

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M02-02 |
| **Épica** | Catálogo maestro |
| **Prioridad** | Crítica |

**Historia**

Como administrativo, quiero registrar y mantener los tipos de mineral que procesa la planta, para
que los ingresos y la consolidación mensual se clasifiquen de forma consistente.

**Descripción**

Es un solo catálogo, usado tanto al registrar el ingreso como al consolidar la producción del mes.
Sus valores concretos se definen con la empresa; lo que fija esta historia es el mecanismo, no la
lista final. Cada tipo tiene código único, nombre y la unidad de medida, siempre toneladas.

**Detalles**
- Código: obligatorio, único.
- Nombre: obligatorio.
- Unidad de medida: toneladas.
- Baja: lógica; un tipo de mineral con ingresos asociados se desactiva, nunca se elimina.

**Criterios de aceptación**

> **CA01.** Dado que el usuario completa código y nombre, cuando guarda, entonces el sistema
> registra el tipo de mineral en estado activo.

> **CA02.** Dado que el código ya existe, cuando el usuario intenta guardar, entonces el sistema
> rechaza la operación mostrando "El código ya está registrado".

> **CA03.** Dado que un tipo de mineral tiene ingresos asociados, cuando el usuario intenta
> eliminarlo, entonces el sistema lo desactiva en lugar de eliminarlo y muestra "El tipo de mineral
> se desactivó porque tiene ingresos registrados".

> **CA04.** Dado que un tipo de mineral está desactivado, cuando se abre el formulario de registro
> de un ingreso, entonces no aparece entre las opciones seleccionables.

---

## HU-M02-03 — Gestión de transportistas

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M02-03 |
| **Épica** | Catálogo maestro |
| **Prioridad** | Media |

**Historia**

Como administrativo, quiero registrar los transportistas externos, para asociarlos a sus vehículos.

**Descripción**

Cada transportista se identifica por su RUC, único en el catálogo, y su razón social. Es el catálogo
del que depende un vehículo con titularidad externa.

**Detalles**
- Razón social: obligatoria.
- RUC: obligatorio, once dígitos, único.
- Baja: lógica; un transportista con vehículos asociados se desactiva, nunca se elimina.

**Criterios de aceptación**

> **CA01.** Dado que el usuario completa razón social y RUC, cuando guarda, entonces el sistema
> registra el transportista en estado activo.

> **CA02.** Dado que el RUC no tiene once dígitos, cuando el usuario intenta guardar, entonces el
> sistema lo rechaza mostrando "El RUC debe tener once dígitos".

> **CA03.** Dado que un transportista tiene vehículos asociados, cuando el usuario intenta
> eliminarlo, entonces el sistema lo desactiva y muestra "El transportista se desactivó porque tiene
> vehículos asociados".
