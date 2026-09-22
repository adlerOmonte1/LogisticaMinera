# Historias de usuario — M02 Catálogo maestro

**RF asociado:** RF06 (soporte) · **Historias:** 3

> Módulo de soporte. Mantiene los datos que el registro de ingresos referencia y no digita:
> vehículos con su titularidad y capacidad, tipos de mineral y transportistas. Sin este catálogo, el
> tipo de vehículo se capturaría como texto libre y la capacidad no existiría para contrastarla
> contra la regla V4.

---

## HU-M02-01 — Gestión del catálogo de vehículos

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M02-01 |
| **Épica** | Catálogo maestro |
| **Prioridad** | Crítica |

**Historia**

Como administrativo, quiero registrar y mantener los volquetes indicando si son propios o de un
transportista externo, y su capacidad de carga, para que el registro de ingresos derive el tipo de
vehículo del catálogo y pueda contrastar el peso contra su capacidad.

**Descripción**

Cada vehículo se identifica por placa, única en el catálogo. La titularidad es obligatoria y admite
únicamente dos valores: PROPIO o EXTERNO. Un vehículo externo debe asociarse a un transportista
registrado; uno propio no lleva transportista. La capacidad de carga se declara en toneladas y es la
que la regla V4 usa para señalar un peso neto fuera de rango.

**Detalles**
- Placa: obligatoria, única, formato de placa peruana.
- Titularidad: obligatoria, PROPIO o EXTERNO.
- Capacidad de carga: obligatoria, decimal positivo, en toneladas.
- Transportista: obligatorio si la titularidad es EXTERNO; no se admite si es PROPIO.
- Baja: lógica; un vehículo con ingresos asociados se desactiva, nunca se elimina.

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

> **CA07.** Dado que un vehículo está desactivado, cuando se abre el formulario de registro de un
> ingreso, entonces no aparece entre las placas seleccionables.

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
