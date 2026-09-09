# Historias de Usuario — Sistema de Control de Producción y Existencias

**Documento:** HU-01 · Backlog de historias de usuario
**Versión:** 1.0
**Estado:** Pendiente de aprobación
**Alcance:** 34 historias distribuidas en 9 módulos

---

## Convenciones

| Elemento | Formato | Ejemplo |
|---|---|---|
| Historia | `HU-M{módulo}-{correlativo}` | HU-M03-01 |
| Requerimiento | `RF-{correlativo}` | RF-01 |
| Caso de prueba | `CP-{historia}-{correlativo}` | CP-HU-M03-01-01 |

**Roles del sistema**

| Rol | Alcance |
|---|---|
| Administrador | Acceso total, incluida la gestión de usuarios y catálogos |
| Administrativo | Registro de ingresos y salidas, consultas, reportes y exportaciones |
| Supervisor | Registro de ingresos y consulta de existencias |

**Prioridades:** Crítica (bloquea a otras historias) · Alta (afecta a un indicador operativo) · Media (mejora la operación) · Baja (deseable)

---

# M01 · Autenticación y control de acceso

## HU-M01-01 — Inicio de sesión en el sistema

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M01-01 |
| **Épica** | Autenticación y control de acceso |
| **Nombre** | Inicio de sesión en el sistema |
| **Prioridad** | Crítica |
| **Estado** | Pendiente |

**Historia de Usuario**

Como usuario del sistema, quiero iniciar sesión con mis credenciales, para acceder a las funciones que corresponden a mi rol.

**Descripción**

El sistema debe autenticar al usuario mediante nombre de usuario y contraseña, establecer una sesión y dirigirlo a la pantalla principal correspondiente a su rol. Las contraseñas se almacenan cifradas y nunca en texto plano. Tras cinco intentos fallidos consecutivos la cuenta se bloquea temporalmente.

**Detalles**
- Nombre de usuario (obligatorio, único).
- Contraseña (obligatoria, mínimo ocho caracteres).
- Sesión con duración configurable, por defecto ocho horas.
- Bloqueo temporal de quince minutos tras cinco intentos fallidos.

**Criterios de Aceptación**

> **CA01.** Dado que un usuario activo ingresa credenciales válidas, cuando confirma el inicio de sesión, entonces el sistema establece la sesión y lo dirige a la pantalla principal correspondiente a su rol.

> **CA02.** Dado que un usuario ingresa una contraseña incorrecta, cuando confirma el inicio de sesión, entonces el sistema rechaza el acceso mostrando "Usuario o contraseña incorrectos", sin precisar cuál de los dos es erróneo.

> **CA03.** Dado que un usuario ha fallado cinco intentos consecutivos, cuando intenta iniciar sesión nuevamente, entonces el sistema bloquea la cuenta durante quince minutos e informa el tiempo restante.

> **CA04.** Dado que un usuario ha sido desactivado por el administrador, cuando intenta iniciar sesión con credenciales válidas, entonces el sistema rechaza el acceso mostrando "La cuenta se encuentra inactiva".

---

## HU-M01-02 — Cierre de sesión y expiración automática

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M01-02 |
| **Épica** | Autenticación y control de acceso |
| **Nombre** | Cierre de sesión y expiración automática |
| **Prioridad** | Alta |
| **Estado** | Pendiente |

**Historia de Usuario**

Como usuario del sistema, quiero cerrar mi sesión de forma manual o que expire por inactividad, para evitar que otra persona registre operaciones a mi nombre.

**Descripción**

El sistema debe permitir el cierre manual de sesión desde cualquier pantalla e invalidar automáticamente la sesión tras un periodo de inactividad. Esta historia sostiene la atribución de responsabilidad exigida por el registro de auditoría.

**Detalles**
- Opción de cierre de sesión visible en todas las pantallas.
- Expiración automática tras treinta minutos de inactividad.
- Aviso al usuario dos minutos antes de la expiración, con opción de extender.

**Criterios de Aceptación**

> **CA01.** Dado que un usuario con sesión activa selecciona la opción de cierre de sesión, cuando confirma la acción, entonces el sistema invalida la sesión y lo dirige a la pantalla de inicio de sesión.

> **CA02.** Dado que una sesión permanece treinta minutos sin actividad, cuando el usuario intenta realizar una operación, entonces el sistema rechaza la solicitud y lo dirige a la pantalla de inicio de sesión.

> **CA03.** Dado que una sesión está próxima a expirar, cuando restan dos minutos de inactividad, entonces el sistema muestra un aviso con la opción de extender la sesión.

---

## HU-M01-03 — Registro de cuentas de usuario

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M01-03 |
| **Épica** | Autenticación y control de acceso |
| **Nombre** | Registro de cuentas de usuario |
| **Prioridad** | Crítica |
| **Estado** | Pendiente |

**Historia de Usuario**

Como administrador, quiero registrar las cuentas de los usuarios del sistema, para que cada persona acceda con una identidad propia y sus operaciones queden atribuidas.

**Descripción**

El sistema debe permitir al administrador dar de alta cuentas indicando nombre completo, documento de identidad, nombre de usuario, rol y contraseña inicial. Las cuentas no se eliminan: se desactivan, para preservar la integridad del registro de auditoría.

**Detalles**
- Nombre completo (obligatorio).
- Documento de identidad (obligatorio, único).
- Nombre de usuario (obligatorio, único).
- Rol (obligatorio, uno de los tres definidos).
- Contraseña inicial (obligatoria, debe cambiarse en el primer acceso).
- Estado activo o inactivo.

**Criterios de Aceptación**

> **CA01.** Dado que un administrador completa el formulario con todos los campos obligatorios, cuando confirma el registro, entonces el sistema crea la cuenta en estado activo y la muestra en el listado de usuarios.

> **CA02.** Dado que el nombre de usuario o el documento de identidad ya existen, cuando el administrador intenta guardar, entonces el sistema rechaza la operación mostrando "El usuario o el documento ya se encuentran registrados".

> **CA03.** Dado que un administrador desactiva una cuenta, cuando confirma la acción, entonces el sistema impide el acceso de ese usuario pero conserva todos sus registros históricos y su rastro en la auditoría.

> **CA04.** Dado que un usuario con rol distinto a administrador intenta acceder a la gestión de usuarios, cuando envía la solicitud, entonces el sistema la rechaza respondiendo "Acción no autorizada".

---

## HU-M01-04 — Restricción de acceso por rol

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M01-04 |
| **Épica** | Autenticación y control de acceso |
| **Nombre** | Restricción de acceso por rol |
| **Prioridad** | Crítica |
| **Estado** | Pendiente |

**Historia de Usuario**

Como administrador, quiero que cada rol acceda únicamente a los módulos que le corresponden, para que la información sensible del negocio no quede expuesta a todo el personal.

**Descripción**

El sistema debe validar los permisos tanto en la interfaz, ocultando las opciones no autorizadas, como en el servidor, rechazando las solicitudes directas. La validación del servidor es obligatoria: ocultar un botón no constituye control de acceso.

**Detalles**
- Administrador: todos los módulos.
- Administrativo: ingresos, salidas, existencias, reportes, búsqueda.
- Supervisor: ingresos y consulta de existencias.
- Toda solicitud no autorizada se registra en la auditoría.

**Criterios de Aceptación**

> **CA01.** Dado que un usuario con rol supervisor inicia sesión, cuando accede a la pantalla principal, entonces el sistema muestra únicamente las opciones de registro de ingresos y consulta de existencias.

> **CA02.** Dado que un usuario con rol supervisor envía una solicitud directa al módulo de reportes, cuando el servidor la recibe, entonces la rechaza respondiendo "Acción no autorizada" y deja constancia del intento en el registro de auditoría.

> **CA03.** Dado que un administrador modifica el rol de un usuario, cuando ese usuario inicia una nueva sesión, entonces el sistema aplica los permisos del nuevo rol.

---

## HU-M01-05 — Cambio de contraseña

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M01-05 |
| **Épica** | Autenticación y control de acceso |
| **Nombre** | Cambio de contraseña |
| **Prioridad** | Media |
| **Estado** | Pendiente |

**Historia de Usuario**

Como usuario del sistema, quiero cambiar mi contraseña, para mantener el control sobre el acceso a mi cuenta.

**Descripción**

El sistema debe exigir el cambio de contraseña en el primer acceso y permitirlo en cualquier momento posterior, solicitando siempre la contraseña vigente como verificación.

**Detalles**
- Contraseña actual (obligatoria).
- Contraseña nueva (obligatoria, mínimo ocho caracteres, distinta de la actual).
- Confirmación de la contraseña nueva (obligatoria, debe coincidir).
- Cambio obligatorio en el primer inicio de sesión.

**Criterios de Aceptación**

> **CA01.** Dado que un usuario ingresa correctamente su contraseña actual y una nueva contraseña válida y confirmada, cuando confirma el cambio, entonces el sistema actualiza la credencial y solicita un nuevo inicio de sesión.

> **CA02.** Dado que la contraseña actual ingresada es incorrecta, cuando el usuario confirma el cambio, entonces el sistema rechaza la operación mostrando "La contraseña actual es incorrecta".

> **CA03.** Dado que un usuario inicia sesión por primera vez, cuando accede al sistema, entonces este lo dirige obligatoriamente a la pantalla de cambio de contraseña y no permite otra operación hasta completarla.

---

# M02 · Catálogo maestro

## HU-M02-01 — Registro de productos

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M02-01 |
| **Épica** | Catálogo maestro |
| **Nombre** | Registro de productos |
| **Prioridad** | Crítica |
| **Estado** | Pendiente |

**Historia de Usuario**

Como administrador, quiero registrar los productos que resultan del procesamiento del mineral, para poder clasificar cada ingreso y determinar las existencias por producto.

**Descripción**

El sistema debe permitir el alta de productos con nombre y unidad de medida. Los productos iniciales son Saranda y Molido, pero el catálogo debe ser extensible. Un producto con movimientos asociados no puede eliminarse, solo desactivarse.

**Detalles**
- Nombre del producto (obligatorio, único).
- Unidad de medida (obligatoria, por defecto toneladas).
- Descripción (opcional).
- Estado activo o inactivo.

**Criterios de Aceptación**

> **CA01.** Dado que un administrador completa el nombre y la unidad de medida, cuando confirma el registro, entonces el sistema crea el producto en estado activo y lo hace seleccionable en el formulario de ingresos.

> **CA02.** Dado que ya existe un producto con el mismo nombre, cuando el administrador intenta guardarlo, entonces el sistema rechaza la operación mostrando "El producto ya se encuentra registrado".

> **CA03.** Dado que un producto tiene movimientos asociados, cuando el administrador intenta eliminarlo, entonces el sistema rechaza la operación mostrando "El producto tiene movimientos registrados y solo puede desactivarse".

> **CA04.** Dado que un producto se encuentra inactivo, cuando un usuario abre el formulario de registro de ingresos, entonces el sistema no lo ofrece entre las opciones seleccionables.

---

## HU-M02-02 — Registro de vehículos con su condición de titularidad

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M02-02 |
| **Épica** | Catálogo maestro |
| **Nombre** | Registro de vehículos con su condición de titularidad |
| **Prioridad** | Crítica |
| **Estado** | Pendiente |

**Historia de Usuario**

Como administrador, quiero registrar los vehículos indicando si son propios o de servicio externo, para que el sistema pueda diferenciar la cobertura del registro según su titularidad.

**Descripción**

El sistema debe mantener el padrón de vehículos que ingresan a planta, distinguiendo los de propiedad de la empresa de los contratados por viaje. Esta distinción es la base de uno de los indicadores operativos y no puede quedar como texto libre: debe ser un campo controlado.

**Detalles**
- Placa (obligatoria, única, formato validado).
- Condición: propio o de servicio externo (obligatoria).
- Transportista asociado (obligatorio si la condición es de servicio externo).
- Capacidad de carga en toneladas (opcional).
- Estado activo o inactivo.

**Criterios de Aceptación**

> **CA01.** Dado que un administrador registra un vehículo con placa válida y condición seleccionada, cuando confirma el registro, entonces el sistema crea el vehículo en estado activo y lo hace seleccionable en el formulario de ingresos.

> **CA02.** Dado que la condición seleccionada es de servicio externo y no se indicó transportista, cuando el administrador intenta guardar, entonces el sistema rechaza la operación mostrando "Debe asociar un transportista a los vehículos de servicio externo".

> **CA03.** Dado que la placa ingresada ya se encuentra registrada, cuando el administrador intenta guardar, entonces el sistema rechaza la operación mostrando "La placa ya se encuentra registrada".

> **CA04.** Dado que un vehículo tiene ingresos registrados, cuando el administrador intenta eliminarlo, entonces el sistema rechaza la operación mostrando "El vehículo tiene ingresos registrados y solo puede desactivarse".

---

## HU-M02-03 — Registro de transportistas

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M02-03 |
| **Épica** | Catálogo maestro |
| **Nombre** | Registro de transportistas |
| **Prioridad** | Media |
| **Estado** | Pendiente |

**Historia de Usuario**

Como administrador, quiero registrar a los transportistas que prestan servicio a la empresa, para asociarlos a los vehículos externos y poder consultar los ingresos por transportista.

**Descripción**

El sistema debe mantener el listado de transportistas con sus datos de identificación y contacto. Un transportista puede tener asociados uno o varios vehículos.

**Detalles**
- Nombre o razón social (obligatorio).
- Documento de identidad o RUC (obligatorio, único).
- Teléfono de contacto (opcional).
- Estado activo o inactivo.

**Criterios de Aceptación**

> **CA01.** Dado que un administrador completa el nombre y el documento, cuando confirma el registro, entonces el sistema crea el transportista en estado activo y lo hace seleccionable al registrar vehículos externos.

> **CA02.** Dado que el documento ingresado ya se encuentra registrado, cuando el administrador intenta guardar, entonces el sistema rechaza la operación mostrando "El documento ya se encuentra registrado".

> **CA03.** Dado que un transportista tiene vehículos activos asociados, cuando el administrador intenta desactivarlo, entonces el sistema advierte "El transportista tiene vehículos activos asociados" y solicita confirmación antes de proceder.

---

## HU-M02-04 — Desactivación de elementos del catálogo

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M02-04 |
| **Épica** | Catálogo maestro |
| **Nombre** | Desactivación de elementos del catálogo |
| **Prioridad** | Alta |
| **Estado** | Pendiente |

**Historia de Usuario**

Como administrador, quiero desactivar productos, vehículos o transportistas en lugar de eliminarlos, para que los registros históricos conserven su integridad y sigan siendo auditables.

**Descripción**

El sistema no debe permitir la eliminación física de ningún elemento del catálogo que tenga movimientos asociados. La desactivación lo retira de las listas de selección sin afectar a los registros que ya lo referencian. Esta historia sostiene la exigencia de auditabilidad declarada en los aspectos éticos del proyecto.

**Detalles**
- La desactivación no altera los registros históricos.
- Un elemento desactivado puede reactivarse.
- La operación queda registrada en la auditoría con usuario y fecha.

**Criterios de Aceptación**

> **CA01.** Dado que un elemento del catálogo tiene movimientos asociados, cuando el administrador solicita su eliminación, entonces el sistema rechaza la operación y ofrece la desactivación como alternativa.

> **CA02.** Dado que un elemento ha sido desactivado, cuando un usuario consulta un registro histórico que lo referencia, entonces el sistema muestra el elemento con normalidad, señalando su condición de inactivo.

> **CA03.** Dado que un administrador desactiva o reactiva un elemento, cuando confirma la acción, entonces el sistema registra el evento en la auditoría indicando usuario, fecha y hora.

---

# M03 · Registro de ingresos de mineral

## HU-M03-01 — Registro de un ingreso de volquete

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M03-01 |
| **Épica** | Registro de ingresos de mineral |
| **Nombre** | Registro de un ingreso de volquete |
| **Prioridad** | Crítica |
| **Estado** | Pendiente |

**Historia de Usuario**

Como supervisor de planta, quiero registrar el ingreso de un volquete con los datos del ticket de balanza, para que la información de producción quede disponible de inmediato y no dependa de anotaciones dispersas.

**Descripción**

Es la historia central del sistema. El formulario debe reproducir los campos del ticket de balanza y permitir su captura en el punto de pesaje. El sistema registra dos marcas de tiempo distintas: la hora de pesaje, que ingresa el usuario desde el ticket, y la hora de registro, que genera automáticamente. La diferencia entre ambas es el indicador de latencia de registro.

**Detalles**
- Fecha de pesaje (obligatoria, no puede ser posterior a la fecha actual).
- Hora de pesaje según el ticket (obligatoria, formato de 24 horas).
- Vehículo (obligatorio, seleccionado del catálogo).
- Producto (obligatorio, seleccionado del catálogo).
- Peso bruto en toneladas (obligatorio, mayor que cero).
- Tara en toneladas (obligatoria, mayor que cero y menor que el peso bruto).
- Peso neto (calculado, no editable).
- Número de ticket de balanza (opcional).
- Observaciones (opcional).
- Hora de registro y usuario responsable (automáticos, no editables).

**Criterios de Aceptación**

> **CA01.** Dado que un supervisor o administrativo completa todos los campos obligatorios con valores válidos, cuando confirma el registro, entonces el sistema almacena el ingreso, le asigna un número correlativo de padrón y lo muestra de inmediato en el listado de ingresos.

> **CA02.** Dado que el formulario carece de fecha de pesaje, hora de pesaje, vehículo, producto, peso bruto o tara, cuando el usuario intenta guardarlo, entonces el sistema rechaza la operación mostrando "Debe completar los campos obligatorios" e indicando cuáles faltan.

> **CA03.** Dado que el usuario ingresa un peso bruto y una tara, cuando ambos valores son válidos, entonces el sistema calcula y muestra el peso neto como la diferencia entre ambos, sin permitir su edición manual.

> **CA04.** Dado que la tara ingresada es mayor o igual que el peso bruto, cuando el usuario intenta guardar, entonces el sistema rechaza la operación mostrando "La tara debe ser menor que el peso bruto".

> **CA05.** Dado que un ingreso ha sido registrado, cuando se consulta su detalle, entonces el sistema muestra la hora de pesaje y la hora de registro como dos valores distintos e independientes.

---

## HU-M03-02 — Validación de la fecha y hora de pesaje

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M03-02 |
| **Épica** | Registro de ingresos de mineral |
| **Nombre** | Validación de la fecha y hora de pesaje |
| **Prioridad** | Crítica |
| **Estado** | Pendiente |

**Historia de Usuario**

Como responsable del sistema, quiero que el sistema exija y valide la fecha y hora de pesaje, para que la latencia entre el pesaje y la disponibilidad del dato pueda medirse de forma confiable.

**Descripción**

La hora de pesaje es el dato del que depende uno de los indicadores operativos. El sistema debe impedir que quede vacía, que sea posterior al momento del registro o que corresponda a una fecha futura. Cuando la antigüedad supera las setenta y dos horas, el sistema solicita una confirmación explícita, para distinguir el registro tardío legítimo del error de digitación.

**Detalles**
- Campo obligatorio, sin valor por defecto.
- No admite fechas ni horas futuras.
- Antigüedad superior a setenta y dos horas: requiere confirmación del usuario.
- Antigüedad superior a treinta días: requiere rol administrativo o administrador.

**Criterios de Aceptación**

> **CA01.** Dado que el usuario deja vacía la hora de pesaje, cuando intenta guardar el ingreso, entonces el sistema rechaza la operación mostrando "Debe indicar la hora de pesaje consignada en el ticket".

> **CA02.** Dado que el usuario ingresa una fecha y hora de pesaje posteriores al momento actual, cuando intenta guardar, entonces el sistema rechaza la operación mostrando "La hora de pesaje no puede ser posterior a la hora actual".

> **CA03.** Dado que la fecha y hora de pesaje tienen más de setenta y dos horas de antigüedad, cuando el usuario intenta guardar, entonces el sistema solicita confirmación explícita antes de registrar el ingreso.

> **CA04.** Dado que un supervisor intenta registrar un ingreso con más de treinta días de antigüedad, cuando confirma la operación, entonces el sistema la rechaza respondiendo "Acción no autorizada para su rol".

---

## HU-M03-03 — Asignación del número correlativo de padrón

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M03-03 |
| **Épica** | Registro de ingresos de mineral |
| **Nombre** | Asignación del número correlativo de padrón |
| **Prioridad** | Crítica |
| **Estado** | Pendiente |

**Historia de Usuario**

Como responsable del sistema, quiero que cada ingreso reciba un número correlativo único e inmutable, para disponer de un padrón auditable y poder identificar cualquier ingreso de forma inequívoca.

**Descripción**

El número correlativo es el identificador que vincula el registro del sistema con el padrón de control de la empresa, con las solicitudes de recuperación de datos y con la verificación en el consolidado. Lo asigna el servidor, es secuencial sin saltos y no puede editarse ni reutilizarse.

**Detalles**
- Formato: `ING-{año}-{correlativo de cinco dígitos}`, por ejemplo ING-2027-00001.
- Asignado por el servidor en el momento de la persistencia.
- Secuencial y sin saltos dentro de cada año.
- No editable ni reutilizable, incluso si el ingreso se anula.
- Los ingresos capturados sin conexión lo reciben en el momento de la sincronización.

**Criterios de Aceptación**

> **CA01.** Dado que se registra un ingreso, cuando el sistema lo persiste, entonces le asigna el siguiente número correlativo disponible del año en curso y lo muestra en el detalle del ingreso.

> **CA02.** Dado que un ingreso ya tiene número correlativo asignado, cuando un usuario edita cualquiera de sus campos, entonces el sistema conserva el correlativo sin modificarlo.

> **CA03.** Dado que un ingreso es anulado, cuando se registra un nuevo ingreso, entonces el sistema no reutiliza el correlativo del ingreso anulado.

> **CA04.** Dado que dos ingresos se registran de forma simultánea, cuando el sistema los persiste, entonces asigna a cada uno un correlativo distinto sin duplicaciones.

---

## HU-M03-04 — Edición de un ingreso registrado

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M03-04 |
| **Épica** | Registro de ingresos de mineral |
| **Nombre** | Edición de un ingreso registrado |
| **Prioridad** | Alta |
| **Estado** | Pendiente |

**Historia de Usuario**

Como administrativo, quiero corregir los datos de un ingreso mal registrado, para que la información refleje lo consignado en el ticket de balanza.

**Descripción**

El sistema debe permitir la corrección de los ingresos conservando el rastro del cambio. Los campos generados automáticamente no son editables. Toda edición queda registrada en la auditoría con los valores anteriores y los nuevos.

**Detalles**
- Campos editables: fecha y hora de pesaje, vehículo, producto, peso bruto, tara, número de ticket y observaciones.
- Campos no editables: número correlativo, hora de registro, usuario que registró.
- El peso neto se recalcula automáticamente al modificar el peso bruto o la tara.
- Toda edición exige un motivo de al menos diez caracteres.

**Criterios de Aceptación**

> **CA01.** Dado que un administrativo modifica campos editables de un ingreso e indica el motivo, cuando confirma la edición, entonces el sistema actualiza el registro, recalcula el peso neto y deja constancia del cambio en la auditoría.

> **CA02.** Dado que el usuario no indica el motivo de la edición, cuando intenta guardar, entonces el sistema rechaza la operación mostrando "Debe indicar el motivo de la corrección".

> **CA03.** Dado que un usuario intenta modificar el número correlativo o la hora de registro, cuando envía la solicitud, entonces el sistema la rechaza respondiendo "El campo no es editable".

> **CA04.** Dado que un supervisor intenta editar un ingreso registrado por otro usuario, cuando envía la solicitud, entonces el sistema la rechaza respondiendo "Acción no autorizada".

---

## HU-M03-05 — Listado y filtrado de ingresos

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M03-05 |
| **Épica** | Registro de ingresos de mineral |
| **Nombre** | Listado y filtrado de ingresos |
| **Prioridad** | Alta |
| **Estado** | Pendiente |

**Historia de Usuario**

Como administrativo, quiero consultar los ingresos filtrándolos por fecha, vehículo, producto y condición de titularidad, para revisar la producción de un periodo sin recorrer registros dispersos.

**Descripción**

El listado es la vista principal del módulo. Debe presentar los ingresos ordenados por fecha de pesaje descendente, permitir filtros combinables y mostrar totales del conjunto filtrado.

**Detalles**
- Filtros: rango de fechas, vehículo, condición propio o externo, producto, usuario que registró.
- Columnas: correlativo, fecha y hora de pesaje, placa, condición, producto, peso neto, hora de registro.
- Totales del conjunto filtrado: número de ingresos y suma de peso neto.
- Paginación de veinticinco registros por página.

**Criterios de Aceptación**

> **CA01.** Dado que un administrativo accede al listado, cuando la pantalla carga, entonces el sistema muestra los ingresos del mes en curso ordenados por fecha y hora de pesaje descendente.

> **CA02.** Dado que el usuario aplica uno o varios filtros combinados, cuando confirma la consulta, entonces el sistema muestra únicamente los ingresos que cumplen todas las condiciones y actualiza los totales.

> **CA03.** Dado que ningún ingreso cumple los criterios del filtro, cuando el sistema procesa la consulta, entonces muestra el mensaje "No se encontraron ingresos con los criterios indicados" sin error.

> **CA04.** Dado que el usuario filtra por condición de titularidad, cuando confirma la consulta, entonces el sistema muestra por separado el número de ingresos de vehículos propios y de servicio externo.

---

## HU-M03-06 — Consulta del histórico de ingresos por vehículo

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M03-06 |
| **Épica** | Registro de ingresos de mineral |
| **Nombre** | Consulta del histórico de ingresos por vehículo |
| **Prioridad** | Media |
| **Estado** | Pendiente |

**Historia de Usuario**

Como administrativo, quiero consultar todos los ingresos de un vehículo determinado en un rango de fechas, para verificar los viajes realizados y sustentar la liquidación con el transportista.

**Descripción**

El sistema debe ofrecer una vista por vehículo que reúna sus ingresos, con el total de viajes y de tonelaje transportado en el periodo consultado.

**Detalles**
- Selección del vehículo desde el catálogo.
- Rango de fechas (obligatorio).
- Resultado: listado de ingresos, número total de viajes y suma de peso neto.

**Criterios de Aceptación**

> **CA01.** Dado que un administrativo selecciona un vehículo y un rango de fechas, cuando confirma la consulta, entonces el sistema muestra todos los ingresos de ese vehículo en el periodo, con el total de viajes y el tonelaje acumulado.

> **CA02.** Dado que el vehículo no registra ingresos en el periodo consultado, cuando el sistema procesa la consulta, entonces muestra el mensaje "El vehículo no registra ingresos en el periodo indicado".

> **CA03.** Dado que el usuario no indica el rango de fechas, cuando intenta ejecutar la consulta, entonces el sistema la rechaza mostrando "Debe indicar el rango de fechas".

---

## HU-M03-07 — Anulación de un ingreso

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M03-07 |
| **Épica** | Registro de ingresos de mineral |
| **Nombre** | Anulación de un ingreso |
| **Prioridad** | Media |
| **Estado** | Pendiente |

**Historia de Usuario**

Como administrador, quiero anular un ingreso registrado por error, para que deje de afectar a las existencias sin que desaparezca del registro histórico.

**Descripción**

El sistema no debe permitir la eliminación física de un ingreso. La anulación lo marca como tal, lo excluye del cálculo de existencias y de los consolidados, y conserva su correlativo y su rastro de auditoría.

**Detalles**
- Solo el rol administrador puede anular.
- Motivo de anulación obligatorio, mínimo veinte caracteres.
- El ingreso anulado se muestra en el listado con marca visible.
- El correlativo se conserva y no se reutiliza.

**Criterios de Aceptación**

> **CA01.** Dado que un administrador anula un ingreso indicando el motivo, cuando confirma la acción, entonces el sistema marca el ingreso como anulado, lo excluye del cálculo de existencias y registra el evento en la auditoría.

> **CA02.** Dado que un ingreso ha sido anulado, cuando se genera el consolidado del periodo, entonces el sistema no lo incluye en los totales pero sí lo lista en el detalle señalando su condición.

> **CA03.** Dado que un usuario con rol distinto a administrador intenta anular un ingreso, cuando envía la solicitud, entonces el sistema la rechaza respondiendo "Acción no autorizada".

> **CA04.** Dado que el motivo de anulación tiene menos de veinte caracteres, cuando el administrador intenta confirmar, entonces el sistema rechaza la operación mostrando "Debe indicar el motivo de la anulación".

---

# M04 · Registro de salidas y movimientos

## HU-M04-01 — Registro de una salida por venta

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M04-01 |
| **Épica** | Registro de salidas y movimientos |
| **Nombre** | Registro de una salida por venta |
| **Prioridad** | Crítica |
| **Estado** | Pendiente |

**Historia de Usuario**

Como administrativo, quiero registrar la salida de mineral por venta, para que las existencias reflejen la cantidad realmente disponible en planta.

**Descripción**

Sin el registro de salidas, el stock calculado solo se incrementa y la desviación frente al stock real crece de forma artificial. El sistema debe permitir registrar salidas indicando producto, cantidad y fecha, validando que exista stock suficiente.

**Detalles**
- Fecha de salida (obligatoria, no futura).
- Producto (obligatorio).
- Cantidad en toneladas (obligatoria, mayor que cero).
- Referencia o guía (opcional).
- Observaciones (opcional).
- Usuario y hora de registro (automáticos).
- No se registran precios ni montos.

**Criterios de Aceptación**

> **CA01.** Dado que un administrativo registra una salida con producto, cantidad y fecha válidos, cuando confirma la operación, entonces el sistema la almacena y descuenta la cantidad del stock del producto.

> **CA02.** Dado que la cantidad indicada excede el stock disponible del producto a esa fecha, cuando el usuario intenta guardar, entonces el sistema rechaza la operación mostrando "La cantidad excede el stock disponible" e indica el stock actual.

> **CA03.** Dado que la cantidad ingresada es cero o negativa, cuando el usuario intenta guardar, entonces el sistema rechaza la operación mostrando "La cantidad debe ser mayor que cero".

> **CA04.** Dado que se registra una salida, cuando se consulta el kardex del producto, entonces el movimiento aparece con su tipo, fecha, cantidad y saldo resultante.

---

## HU-M04-02 — Registro de merma por secado

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M04-02 |
| **Épica** | Registro de salidas y movimientos |
| **Nombre** | Registro de merma por secado |
| **Prioridad** | Alta |
| **Estado** | Pendiente |

**Historia de Usuario**

Como supervisor de planta, quiero registrar la pérdida de peso del mineral por secado, para que el stock calculado no quede sobrestimado frente al material realmente disponible.

**Descripción**

La merma por humedad es una causa documentada de la diferencia entre el stock declarado y el calculado. El sistema debe registrarla como un movimiento propio, distinto de la salida por venta, indicando el criterio de estimación aplicado. Esta separación es la que permite interpretar el indicador de desviación de inventario.

**Detalles**
- Fecha de la merma (obligatoria, no futura).
- Producto (obligatorio).
- Cantidad estimada en toneladas (obligatoria, mayor que cero).
- Criterio de estimación aplicado (obligatorio, seleccionable: porcentaje sobre ingresos del periodo, diferencia de pesaje, u otro con descripción).
- Observaciones (opcional).

**Criterios de Aceptación**

> **CA01.** Dado que un supervisor registra una merma con producto, cantidad, fecha y criterio de estimación, cuando confirma la operación, entonces el sistema la almacena como movimiento de tipo merma y descuenta la cantidad del stock del producto.

> **CA02.** Dado que el usuario no selecciona el criterio de estimación, cuando intenta guardar, entonces el sistema rechaza la operación mostrando "Debe indicar el criterio de estimación de la merma".

> **CA03.** Dado que se selecciona el criterio "otro", cuando el usuario intenta guardar sin describirlo, entonces el sistema rechaza la operación mostrando "Debe describir el criterio de estimación aplicado".

> **CA04.** Dado que se consulta el kardex de un producto, cuando este contiene mermas registradas, entonces el sistema las presenta diferenciadas de las salidas por venta.

---

## HU-M04-03 — Registro de ajuste manual de existencias

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M04-03 |
| **Épica** | Registro de salidas y movimientos |
| **Nombre** | Registro de ajuste manual de existencias |
| **Prioridad** | Media |
| **Estado** | Pendiente |

**Historia de Usuario**

Como administrador, quiero registrar un ajuste manual de existencias con su motivo, para corregir diferencias detectadas en un conteo físico sin alterar los registros de ingresos ni de salidas.

**Descripción**

El ajuste es el mecanismo que permite reconciliar el stock del sistema con un conteo físico sin modificar los movimientos originales. Debe ser una operación excepcional, restringida al administrador y siempre justificada.

**Detalles**
- Fecha del ajuste (obligatoria, no futura).
- Producto (obligatorio).
- Tipo: incremento o decremento (obligatorio).
- Cantidad en toneladas (obligatoria, mayor que cero).
- Motivo (obligatorio, mínimo veinte caracteres).

**Criterios de Aceptación**

> **CA01.** Dado que un administrador registra un ajuste con todos sus campos válidos, cuando confirma la operación, entonces el sistema la almacena como movimiento de tipo ajuste, modifica el stock según el tipo indicado y registra el evento en la auditoría.

> **CA02.** Dado que el motivo tiene menos de veinte caracteres, cuando el administrador intenta guardar, entonces el sistema rechaza la operación mostrando "Debe justificar el ajuste con un motivo de al menos veinte caracteres".

> **CA03.** Dado que un usuario con rol distinto a administrador intenta registrar un ajuste, cuando envía la solicitud, entonces el sistema la rechaza respondiendo "Acción no autorizada".

> **CA04.** Dado que un decremento dejaría el stock del producto en un valor negativo, cuando el administrador intenta confirmar, entonces el sistema rechaza la operación mostrando "El ajuste dejaría el stock en valor negativo".

---

# M05 · Existencias por producto

## HU-M05-01 — Consulta del stock disponible por producto

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M05-01 |
| **Épica** | Existencias por producto |
| **Nombre** | Consulta del stock disponible por producto |
| **Prioridad** | Crítica |
| **Estado** | Pendiente |

**Historia de Usuario**

Como supervisor de planta, quiero consultar el stock disponible de cada producto, para conocer con exactitud cuánto material hay en cancha sin recurrir a la apreciación visual.

**Descripción**

Es la historia que sustituye la práctica actual de estimar el stock a ojo. La consulta debe ser inmediata y presentar el stock de todos los productos activos en una sola pantalla, con el detalle de cómo se compone cada saldo.

**Detalles**
- Stock por producto calculado como: ingresos menos salidas, menos mermas, más o menos ajustes.
- Presentación de todos los productos activos en una sola vista.
- Detalle desplegable por producto: total ingresado, total vendido, total mermado y ajustes.
- Fecha y hora de la última actualización del saldo.

**Criterios de Aceptación**

> **CA01.** Dado que un supervisor accede al módulo de existencias, cuando la pantalla carga, entonces el sistema muestra el stock disponible de todos los productos activos con la fecha y hora del último movimiento registrado.

> **CA02.** Dado que se registra un ingreso, una salida, una merma o un ajuste, cuando el usuario consulta el stock del producto afectado, entonces el saldo refleja el movimiento sin requerir ninguna acción adicional de actualización.

> **CA03.** Dado que un usuario despliega el detalle de un producto, cuando el sistema presenta la composición del saldo, entonces muestra por separado el total ingresado, el total vendido, el total mermado y el resultado de los ajustes.

> **CA04.** Dado que un producto no registra movimientos, cuando se consulta su stock, entonces el sistema muestra el valor cero y no un mensaje de error.

---

## HU-M05-02 — Consulta del kardex de movimientos

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M05-02 |
| **Épica** | Existencias por producto |
| **Nombre** | Consulta del kardex de movimientos |
| **Prioridad** | Alta |
| **Estado** | Pendiente |

**Historia de Usuario**

Como administrativo, quiero consultar el detalle cronológico de los movimientos de un producto con su saldo acumulado, para verificar cómo se formó el stock actual y localizar el origen de cualquier diferencia.

**Descripción**

El kardex presenta todos los movimientos de un producto ordenados en el tiempo, con el saldo resultante después de cada uno. Es la herramienta que permite auditar el cálculo del stock.

**Detalles**
- Selección del producto y rango de fechas.
- Columnas: fecha, tipo de movimiento, referencia, entrada, salida, saldo.
- Tipos de movimiento diferenciados: ingreso, venta, merma, ajuste.
- Saldo inicial del periodo y saldo final.

**Criterios de Aceptación**

> **CA01.** Dado que un administrativo selecciona un producto y un rango de fechas, cuando confirma la consulta, entonces el sistema muestra todos los movimientos del periodo ordenados cronológicamente, con el saldo resultante después de cada uno.

> **CA02.** Dado que el kardex se genera, cuando el sistema calcula el saldo final del periodo, entonces este coincide exactamente con el stock disponible mostrado en la consulta de existencias a esa fecha.

> **CA03.** Dado que un movimiento corresponde a un ingreso de volquete, cuando se muestra en el kardex, entonces su referencia es el número correlativo de padrón del ingreso.

> **CA04.** Dado que el producto no registra movimientos en el periodo, cuando el sistema procesa la consulta, entonces muestra el saldo inicial y final sin líneas de detalle, y no un mensaje de error.

---

## HU-M05-03 — Consulta del stock a una fecha de corte

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M05-03 |
| **Épica** | Existencias por producto |
| **Nombre** | Consulta del stock a una fecha de corte |
| **Prioridad** | Alta |
| **Estado** | Pendiente |

**Historia de Usuario**

Como responsable del sistema, quiero consultar el stock que tenía cada producto en una fecha pasada, para poder contrastarlo con la cifra declarada por el supervisor en esa misma fecha.

**Descripción**

Esta historia habilita directamente el indicador de desviación de inventario. El sistema debe reconstruir el saldo de cualquier producto a una fecha determinada, considerando únicamente los movimientos ocurridos hasta esa fecha.

**Detalles**
- Fecha de corte (obligatoria, no futura).
- Producto o todos los productos.
- El cálculo considera la fecha del movimiento y no la fecha de su registro en el sistema.
- Los ingresos anulados quedan excluidos del cálculo.

**Criterios de Aceptación**

> **CA01.** Dado que un usuario indica una fecha de corte y un producto, cuando confirma la consulta, entonces el sistema muestra el saldo del producto considerando exclusivamente los movimientos con fecha igual o anterior a la de corte.

> **CA02.** Dado que un ingreso fue registrado con posterioridad pero con fecha de pesaje anterior a la de corte, cuando se consulta el stock a esa fecha, entonces el sistema lo incluye en el cálculo.

> **CA03.** Dado que un ingreso se encuentra anulado, cuando se consulta el stock a cualquier fecha, entonces el sistema lo excluye del cálculo.

> **CA04.** Dado que la fecha de corte indicada es futura, cuando el usuario intenta ejecutar la consulta, entonces el sistema la rechaza mostrando "La fecha de corte no puede ser posterior a la fecha actual".

---

# M06 · Consolidados y reportes

## HU-M06-01 — Generación del consolidado mensual de producción

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M06-01 |
| **Épica** | Consolidados y reportes |
| **Nombre** | Generación del consolidado mensual de producción |
| **Prioridad** | Crítica |
| **Estado** | Pendiente |

**Historia de Usuario**

Como administrativo, quiero generar el consolidado de producción de un mes, para disponer de la información agregada del periodo sin reconstruirla manualmente a partir de registros dispersos.

**Descripción**

El consolidado es el documento que la empresa dejó de producir y cuya ausencia motiva este proyecto. Debe generarse a demanda, en el momento, y presentar el total ingresado, su desagregación por producto y el stock de cierre. Incluye además el detalle de los ingresos del periodo con su número correlativo, condición necesaria para verificar la trazabilidad de cada ingreso.

**Detalles**
- Selección del mes y año.
- Cabecera: periodo, fecha de generación, usuario que lo generó.
- Resumen: total de ingresos, total de toneladas, desagregación por producto, desagregación por condición de vehículo.
- Existencias: stock de cierre por producto.
- Detalle: listado de todos los ingresos del periodo con correlativo, fecha, placa, condición, producto y peso neto.
- Los ingresos anulados se listan en el detalle pero no se suman en los totales.

**Criterios de Aceptación**

> **CA01.** Dado que un administrativo selecciona un mes con ingresos registrados, cuando solicita el consolidado, entonces el sistema lo genera mostrando el total de toneladas ingresadas, su desagregación por producto y el stock de cierre de cada producto.

> **CA02.** Dado que el consolidado se genera, cuando se revisa su sección de detalle, entonces cada ingreso del periodo aparece identificado por su número correlativo de padrón.

> **CA03.** Dado que el periodo contiene ingresos anulados, cuando el sistema calcula los totales, entonces los excluye, pero los presenta en el detalle señalando su condición de anulados.

> **CA04.** Dado que el mes seleccionado no registra ingresos, cuando el usuario solicita el consolidado, entonces el sistema lo genera con totales en cero y el mensaje "El periodo no registra ingresos".

> **CA05.** Dado que el consolidado se genera, cuando se compara el total por producto con el kardex del mismo periodo, entonces ambos valores coinciden.

---

## HU-M06-02 — Generación del formato de declaración semestral

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M06-02 |
| **Épica** | Consolidados y reportes |
| **Nombre** | Generación del formato de declaración semestral |
| **Prioridad** | Alta |
| **Estado** | Pendiente |

**Historia de Usuario**

Como administrativo, quiero generar la declaración semestral de producción en el formato exigido por la normativa, para cumplir la obligación del proceso de formalización sin reconstruir la información manualmente.

**Descripción**

El sistema debe consolidar la producción de los semestres de enero a junio y de julio a diciembre en la estructura requerida por la Ley 32213 y su reglamento. Esta historia es la que conecta el sistema con la justificación social del proyecto.

**Detalles**
- Selección del semestre y año.
- Estructura conforme al formato oficial vigente.
- Totales de producción del semestre desagregados por producto y por mes.
- Advertencia si algún mes del semestre carece de ingresos registrados.
- Exportación en formato descargable.

**Criterios de Aceptación**

> **CA01.** Dado que un administrativo selecciona un semestre con ingresos registrados, cuando solicita la declaración, entonces el sistema la genera con los totales de producción desagregados por producto y por mes.

> **CA02.** Dado que uno o más meses del semestre no registran ingresos, cuando el sistema genera la declaración, entonces incluye una advertencia identificando los meses sin registros.

> **CA03.** Dado que la declaración ha sido generada, cuando el usuario solicita su descarga, entonces el sistema entrega un archivo que conserva íntegramente la información presentada en pantalla.

> **CA04.** Dado que un usuario con rol supervisor intenta generar la declaración, cuando envía la solicitud, entonces el sistema la rechaza respondiendo "Acción no autorizada".

---

## HU-M06-03 — Exportación de reportes

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M06-03 |
| **Épica** | Consolidados y reportes |
| **Nombre** | Exportación de reportes |
| **Prioridad** | Media |
| **Estado** | Pendiente |

**Historia de Usuario**

Como administrativo, quiero descargar los reportes generados por el sistema, para archivarlos, compartirlos con la gerencia o presentarlos ante terceros.

**Descripción**

El sistema debe permitir la descarga de los consolidados, el kardex y los listados filtrados en un formato de uso general, conservando exactamente la información visualizada.

**Detalles**
- Reportes exportables: consolidado mensual, declaración semestral, kardex y listado de ingresos filtrado.
- Formato de descarga con encabezado que identifique la empresa, el reporte, el periodo y la fecha de generación.
- La exportación queda registrada en la auditoría.

**Criterios de Aceptación**

> **CA01.** Dado que un reporte se encuentra generado en pantalla, cuando el usuario solicita su descarga, entonces el sistema entrega un archivo cuyo contenido coincide con el visualizado.

> **CA02.** Dado que se descarga un reporte, cuando se abre el archivo, entonces su encabezado identifica el reporte, el periodo cubierto, la fecha de generación y el usuario que lo generó.

> **CA03.** Dado que un usuario exporta un reporte, cuando la descarga se completa, entonces el sistema registra el evento en la auditoría indicando reporte, periodo, usuario y fecha.

---

# M07 · Captura sin conexión y sincronización

## HU-M07-01 — Instalación de la aplicación en el dispositivo

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M07-01 |
| **Épica** | Captura sin conexión y sincronización |
| **Nombre** | Instalación de la aplicación en el dispositivo |
| **Prioridad** | Alta |
| **Estado** | Pendiente |

**Historia de Usuario**

Como supervisor de planta, quiero instalar la aplicación en mi teléfono desde el navegador, para acceder al registro de ingresos sin depender de una computadora.

**Descripción**

El sistema debe ofrecerse como aplicación web progresiva instalable, de modo que el supervisor la abra desde el icono del dispositivo y pueda usarla en el punto de pesaje. No requiere tienda de aplicaciones ni proceso de publicación.

**Detalles**
- Manifiesto con nombre, icono y color de la aplicación.
- Aviso de instalación al ingresar desde un navegador compatible.
- Funcionamiento a pantalla completa, sin barra de navegación.
- Almacenamiento en caché de los recursos necesarios para el formulario de ingreso.

**Criterios de Aceptación**

> **CA01.** Dado que un usuario accede al sistema desde un navegador compatible, cuando la aplicación carga por primera vez, entonces el sistema ofrece la opción de instalarla en el dispositivo.

> **CA02.** Dado que el usuario ha instalado la aplicación, cuando la abre desde el icono del dispositivo, entonces esta se ejecuta a pantalla completa sin la barra de direcciones del navegador.

> **CA03.** Dado que la aplicación está instalada y el dispositivo carece de conexión, cuando el usuario la abre, entonces el formulario de registro de ingresos carga y queda operativo.

---

## HU-M07-02 — Registro de un ingreso sin conexión

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M07-02 |
| **Épica** | Captura sin conexión y sincronización |
| **Nombre** | Registro de un ingreso sin conexión |
| **Prioridad** | Alta |
| **Estado** | Pendiente |

**Historia de Usuario**

Como supervisor de planta, quiero registrar el ingreso de un volquete aunque no haya conexión en ese momento, para que el dato se capture en el punto de pesaje y no quede pendiente de anotación posterior.

**Descripción**

Esta es la historia que ataca la causa raíz identificada en el diagnóstico: los volquetes llegan fuera del horario administrativo y en un entorno con conectividad intermitente. El sistema debe almacenar el ingreso localmente y encolarlo para su envío posterior, aplicando las mismas validaciones que en el modo conectado.

**Detalles**
- El formulario opera sin conexión con los catálogos almacenados en caché.
- Las validaciones de campos obligatorios y de peso se aplican localmente.
- El ingreso recibe un identificador local único generado en el dispositivo.
- El número correlativo de padrón lo asigna el servidor en la sincronización.
- El ingreso pendiente se muestra en una bandeja local con marca visible.

**Criterios de Aceptación**

> **CA01.** Dado que el dispositivo carece de conexión, cuando el supervisor completa y confirma el formulario de ingreso, entonces el sistema lo almacena localmente e informa "Ingreso guardado. Se enviará al recuperar la conexión".

> **CA02.** Dado que el dispositivo carece de conexión y el formulario está incompleto, cuando el supervisor intenta guardarlo, entonces el sistema aplica las mismas validaciones del modo conectado y rechaza la operación con el mismo mensaje.

> **CA03.** Dado que existen ingresos almacenados localmente sin enviar, cuando el supervisor accede a la aplicación, entonces el sistema los muestra en una bandeja de pendientes indicando cuántos son.

> **CA04.** Dado que un ingreso fue capturado sin conexión, cuando se sincroniza, entonces el sistema conserva la hora de pesaje ingresada por el usuario y registra como hora de registro la del momento de la captura local, no la de la sincronización.

---

## HU-M07-03 — Sincronización automática al recuperar la conexión

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M07-03 |
| **Épica** | Captura sin conexión y sincronización |
| **Nombre** | Sincronización automática al recuperar la conexión |
| **Prioridad** | Alta |
| **Estado** | Pendiente |

**Historia de Usuario**

Como supervisor de planta, quiero que los ingresos guardados sin conexión se envíen solos cuando vuelva la señal, para no tener que recordar hacerlo manualmente.

**Descripción**

El sistema debe detectar la recuperación de la conexión y enviar la cola de pendientes en el orden en que fueron capturados, informando el resultado de cada envío. Si alguno falla, permanece en la cola y no bloquea a los demás.

**Detalles**
- Detección automática del cambio de estado de conexión.
- Envío en orden cronológico de captura.
- Reintento automático hasta tres veces por elemento.
- Los elementos con error permanecen en la cola con el motivo del fallo.
- Opción de forzar la sincronización manualmente.

**Criterios de Aceptación**

> **CA01.** Dado que existen ingresos en la cola local y el dispositivo recupera la conexión, cuando el sistema detecta el cambio de estado, entonces envía automáticamente los ingresos pendientes en orden cronológico de captura.

> **CA02.** Dado que un ingreso se sincroniza correctamente, cuando el servidor lo confirma, entonces el sistema le asigna el número correlativo de padrón, lo retira de la cola local e informa el resultado al usuario.

> **CA03.** Dado que el envío de un ingreso falla, cuando se agotan los tres reintentos, entonces el sistema lo conserva en la cola indicando el motivo del fallo y continúa con los siguientes elementos.

> **CA04.** Dado que el usuario selecciona la opción de sincronizar manualmente, cuando existe conexión disponible, entonces el sistema procesa la cola sin esperar a la detección automática.

---

## HU-M07-04 — Indicador de estado de conexión y de cola pendiente

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M07-04 |
| **Épica** | Captura sin conexión y sincronización |
| **Nombre** | Indicador de estado de conexión y de cola pendiente |
| **Prioridad** | Media |
| **Estado** | Pendiente |

**Historia de Usuario**

Como supervisor de planta, quiero ver en todo momento si estoy conectado y cuántos ingresos me faltan enviar, para saber si la información ya llegó al sistema.

**Descripción**

La confianza en el modo sin conexión depende de que el usuario sepa qué está ocurriendo. El sistema debe mostrar de forma permanente el estado de la conexión y el número de elementos pendientes de envío.

**Detalles**
- Indicador visible en todas las pantallas de la aplicación.
- Tres estados: conectado y sincronizado, conectado con envíos en curso, sin conexión.
- Contador de elementos pendientes.
- Acceso directo a la bandeja de pendientes desde el indicador.

**Criterios de Aceptación**

> **CA01.** Dado que el dispositivo tiene conexión y no hay elementos en cola, cuando el usuario navega por la aplicación, entonces el indicador muestra el estado de sincronizado.

> **CA02.** Dado que el dispositivo carece de conexión, cuando el usuario navega por la aplicación, entonces el indicador muestra el estado sin conexión junto con el número de ingresos pendientes de envío.

> **CA03.** Dado que el usuario selecciona el indicador, cuando existen elementos pendientes, entonces el sistema abre la bandeja mostrando cada ingreso en cola con su fecha y hora de captura.

---

## HU-M07-05 — Prevención de duplicados en la sincronización

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M07-05 |
| **Épica** | Captura sin conexión y sincronización |
| **Nombre** | Prevención de duplicados en la sincronización |
| **Prioridad** | Alta |
| **Estado** | Pendiente |

**Historia de Usuario**

Como responsable del sistema, quiero que un ingreso capturado sin conexión no pueda registrarse dos veces, para que el padrón no contenga duplicados que invaliden el conteo de ingresos.

**Descripción**

Un envío repetido por reintento, por doble sincronización o por reinstalación de la aplicación no debe generar dos registros. El servidor debe reconocer el identificador local del dispositivo y descartar los envíos ya procesados. Esta historia protege la integridad del padrón de ingresos.

**Detalles**
- Cada ingreso capturado localmente recibe un identificador único generado en el dispositivo.
- El servidor almacena ese identificador junto con el ingreso.
- Un envío con identificador ya existente se descarta y se responde con el registro original.
- El sistema advierte además cuando se registra un ingreso con la misma placa y hora de pesaje que otro ya existente.

**Criterios de Aceptación**

> **CA01.** Dado que un ingreso se envía dos veces con el mismo identificador local, cuando el servidor recibe el segundo envío, entonces lo descarta y responde con el registro creado en el primer envío, sin generar un duplicado.

> **CA02.** Dado que el usuario reinstala la aplicación tras sincronizar, cuando la cola local se restablece vacía, entonces el sistema no reenvía ingresos ya procesados.

> **CA03.** Dado que se intenta registrar un ingreso con la misma placa y la misma hora de pesaje que otro ya existente, cuando el usuario confirma la operación, entonces el sistema advierte "Ya existe un ingreso con la misma placa y hora de pesaje" y solicita confirmación explícita antes de guardarlo.

> **CA04.** Dado que se consulta el padrón de ingresos, cuando se verifican los identificadores locales, entonces no existe más de un registro por identificador.

---

# M08 · Auditoría y trazabilidad

## HU-M08-01 — Registro automático de eventos

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M08-01 |
| **Épica** | Auditoría y trazabilidad |
| **Nombre** | Registro automático de eventos |
| **Prioridad** | Alta |
| **Estado** | Pendiente |

**Historia de Usuario**

Como responsable del sistema, quiero que el sistema registre automáticamente quién realizó cada operación y cuándo, para que los datos registrados sean verificables por un tercero.

**Descripción**

El registro de eventos es la evidencia que sostiene la gestión del conflicto de interés declarada en los aspectos éticos del proyecto. Debe generarse sin intervención del usuario, no debe poder desactivarse y no debe admitir modificación ni eliminación.

**Detalles**
- Se registra: alta, edición, anulación, desactivación de catálogos, exportación de reportes e intentos de acceso no autorizado.
- Cada evento almacena: entidad, identificador del registro, acción, usuario, fecha y hora del servidor.
- Las ediciones almacenan además el valor anterior y el nuevo de cada campo modificado.
- El registro no admite edición ni eliminación desde ninguna interfaz.

**Criterios de Aceptación**

> **CA01.** Dado que un usuario ejecuta cualquier operación de alta, edición o anulación, cuando el sistema la procesa, entonces genera un evento de auditoría con entidad, identificador, acción, usuario, fecha y hora del servidor.

> **CA02.** Dado que se edita un ingreso, cuando el sistema registra el evento, entonces almacena el valor anterior y el nuevo de cada campo modificado.

> **CA03.** Dado que un usuario intenta acceder a un módulo no autorizado para su rol, cuando el servidor rechaza la solicitud, entonces registra el intento en la auditoría.

> **CA04.** Dado que un usuario, incluido el administrador, intenta modificar o eliminar un evento de auditoría, cuando envía la solicitud, entonces el sistema la rechaza respondiendo "El registro de auditoría no es modificable".

---

## HU-M08-02 — Consulta del registro de auditoría

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M08-02 |
| **Épica** | Auditoría y trazabilidad |
| **Nombre** | Consulta del registro de auditoría |
| **Prioridad** | Media |
| **Estado** | Pendiente |

**Historia de Usuario**

Como administrador, quiero consultar el registro de eventos filtrando por usuario, fecha y tipo de operación, para verificar el origen de cualquier dato cuando sea necesario.

**Descripción**

El sistema debe ofrecer una vista de consulta del registro de auditoría, de solo lectura, con filtros que permitan localizar un evento concreto. Esta vista es la que permite a un tercero contrastar los datos reportados a la gerencia.

**Detalles**
- Filtros: rango de fechas, usuario, entidad, tipo de acción.
- Columnas: fecha y hora, usuario, entidad, identificador, acción.
- Detalle desplegable con los valores anteriores y nuevos en el caso de las ediciones.
- Acceso restringido al rol administrador.

**Criterios de Aceptación**

> **CA01.** Dado que un administrador aplica filtros de fecha, usuario o acción, cuando confirma la consulta, entonces el sistema muestra los eventos que cumplen todas las condiciones, ordenados del más reciente al más antiguo.

> **CA02.** Dado que un evento corresponde a una edición, cuando el administrador despliega su detalle, entonces el sistema muestra los valores anteriores y nuevos de los campos modificados.

> **CA03.** Dado que un usuario con rol distinto a administrador intenta acceder al registro de auditoría, cuando envía la solicitud, entonces el sistema la rechaza respondiendo "Acción no autorizada".

---

# M09 · Búsqueda y recuperación de ingresos

## HU-M09-01 — Búsqueda de un ingreso por número de padrón

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M09-01 |
| **Épica** | Búsqueda y recuperación de ingresos |
| **Nombre** | Búsqueda de un ingreso por número de padrón |
| **Prioridad** | Alta |
| **Estado** | Pendiente |

**Historia de Usuario**

Como administrativo, quiero localizar un ingreso concreto indicando su número de padrón, para recuperar sus datos de inmediato cuando alguien me los solicite.

**Descripción**

Esta historia habilita directamente el indicador de tiempo de recuperación del dato. La operación actual consiste en buscar entre fotografías y hojas de cálculo; el sistema debe reducirla a una consulta directa que devuelva el detalle completo del ingreso.

**Detalles**
- Campo de búsqueda accesible desde la pantalla principal.
- Admite el correlativo completo o solo su parte numérica.
- Resultado: detalle completo del ingreso con todos sus campos y su estado.
- Tiempo de respuesta objetivo inferior a dos segundos.

**Criterios de Aceptación**

> **CA01.** Dado que un administrativo ingresa un número de padrón existente, cuando confirma la búsqueda, entonces el sistema muestra el detalle completo del ingreso: correlativo, fecha y hora de pesaje, placa, condición del vehículo, producto, peso bruto, tara, peso neto, usuario que registró y hora de registro.

> **CA02.** Dado que el número de padrón ingresado no existe, cuando el sistema procesa la búsqueda, entonces muestra el mensaje "No se encontró ningún ingreso con el número indicado".

> **CA03.** Dado que el usuario ingresa únicamente la parte numérica del correlativo, cuando confirma la búsqueda, entonces el sistema la interpreta como perteneciente al año en curso y devuelve el ingreso correspondiente.

> **CA04.** Dado que el ingreso localizado se encuentra anulado, cuando el sistema muestra su detalle, entonces indica su condición de anulado junto con el motivo registrado.

---

## HU-M09-02 — Búsqueda de ingresos por criterios combinados

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M09-02 |
| **Épica** | Búsqueda y recuperación de ingresos |
| **Nombre** | Búsqueda de ingresos por criterios combinados |
| **Prioridad** | Media |
| **Estado** | Pendiente |

**Historia de Usuario**

Como administrativo, quiero buscar ingresos combinando fecha, placa y producto, para localizar un registro cuando no dispongo de su número de padrón.

**Descripción**

No siempre se conoce el correlativo del ingreso que se busca. El sistema debe permitir localizarlo a partir de los datos que la persona sí recuerda, que habitualmente son la fecha aproximada y la placa del vehículo.

**Detalles**
- Criterios combinables: rango de fechas, placa, producto, condición del vehículo.
- Al menos un criterio es obligatorio.
- Resultado ordenado por fecha y hora de pesaje descendente.
- Selección de un resultado para ver su detalle completo.

**Criterios de Aceptación**

> **CA01.** Dado que un administrativo indica uno o varios criterios de búsqueda, cuando confirma la consulta, entonces el sistema muestra los ingresos que cumplen todas las condiciones, ordenados por fecha y hora de pesaje descendente.

> **CA02.** Dado que el usuario no indica ningún criterio, cuando intenta ejecutar la búsqueda, entonces el sistema la rechaza mostrando "Debe indicar al menos un criterio de búsqueda".

> **CA03.** Dado que la búsqueda devuelve resultados, cuando el usuario selecciona uno de ellos, entonces el sistema muestra el detalle completo de ese ingreso.

> **CA04.** Dado que ningún ingreso cumple los criterios indicados, cuando el sistema procesa la búsqueda, entonces muestra el mensaje "No se encontraron ingresos con los criterios indicados".

---

# Trazabilidad

| Historia | RF | Indicador operativo | Semana |
|---|---|---|---|
| HU-M01-01 a HU-M01-05 | RF-08 | — | 1 |
| HU-M02-01 a HU-M02-04 | RF-03 | I2 | 2 |
| HU-M03-01, HU-M03-02 | RF-01, RF-02 | I1 | 2–3 |
| HU-M03-03 | RF-01 | I2, I5 | 3 |
| HU-M03-04 a HU-M03-07 | RF-09 | I2 | 3 |
| HU-M07-01 a HU-M07-05 | RF-10 | I1, I2 | 4 |
| HU-M04-01 a HU-M04-03 | RF-05 | I4 | 5 |
| HU-M05-01 a HU-M05-03 | RF-04 | I3, I4 | 5 |
| HU-M09-01, HU-M09-02 | RF-11 | I5 | 6 |
| HU-M06-01 a HU-M06-03 | RF-06, RF-07 | I6 | 7 |
| HU-M08-01, HU-M08-02 | RF-12 | — | 3 y 6 |

---

# Resumen

| Módulo | Historias | Críticas | Altas | Medias |
|---|---|---|---|---|
| M01 Autenticación | 5 | 2 | 2 | 1 |
| M02 Catálogo maestro | 4 | 2 | 1 | 1 |
| M03 Ingresos | 7 | 3 | 2 | 2 |
| M04 Salidas y movimientos | 3 | 1 | 1 | 1 |
| M05 Existencias | 3 | 1 | 2 | 0 |
| M06 Consolidados y reportes | 3 | 1 | 1 | 1 |
| M07 Sin conexión | 5 | 0 | 4 | 1 |
| M08 Auditoría | 2 | 0 | 1 | 1 |
| M09 Búsqueda | 2 | 0 | 1 | 1 |
| **Total** | **34** | **10** | **15** | **9** |