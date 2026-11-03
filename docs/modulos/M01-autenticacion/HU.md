# Historias de usuario — M01 Autenticación y roles

**RF asociado:** RF10 · **Historias:** 3

> Módulo habilitante. Identifica al usuario y limita cada operación según su rol. Sin control de
> acceso, ninguna operación de los demás módulos puede atribuirse a un responsable y el registro de
> eventos de M09 carece de a quién imputar los cambios.

---

## HU-M01-01 — Inicio y cierre de sesión

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M01-01 |
| **Épica** | Autenticación y roles |
| **Prioridad** | Crítica |

**Historia**

Como usuario del sistema, quiero iniciar y cerrar sesión con mis credenciales, para acceder a las
funciones de mi rol y evitar que otra persona use el sistema con mi identidad en un equipo
compartido.

**Descripción**

El sistema autentica mediante nombre de usuario y contraseña, y emite un token de sesión. Tras cinco
intentos fallidos consecutivos, la cuenta se bloquea quince minutos. El cierre de sesión invalida el
token de inmediato; la sesión también expira por inactividad tras el tiempo configurado.

**Detalles**
- Usuario y contraseña: obligatorios.
- Bloqueo temporal: cinco intentos fallidos, quince minutos.
- Expiración por inactividad: configurable.
- Contraseñas almacenadas cifradas, nunca en texto plano.
- Contraseña olvidada: no hay recuperación automática; la restablece el Administrador con una
  contraseña temporal (HU-M01-02), que el usuario cambia al iniciar sesión.

**Criterios de aceptación**

> **CA01.** Dado que un usuario activo ingresa credenciales válidas, cuando confirma el inicio de
> sesión, entonces el sistema establece la sesión y lo dirige a la pantalla principal de su rol.

> **CA02.** Dado que un usuario ingresa credenciales inválidas, cuando envía el formulario, entonces
> el sistema rechaza el acceso mostrando "Usuario o contraseña incorrectos", sin indicar cuál de los
> dos campos falló.

> **CA03.** Dado que un usuario acumula cinco intentos fallidos consecutivos, cuando intenta un
> sexto acceso, entonces el sistema bloquea la cuenta por quince minutos y muestra "Cuenta bloqueada
> temporalmente. Intente nuevamente en 15 minutos".

> **CA04.** Dado que un usuario existe pero está inactivo, cuando ingresa credenciales correctas,
> entonces el sistema rechaza el acceso mostrando "La cuenta se encuentra inactiva. Contacte al
> administrador".

> **CA05.** Dado que un usuario tiene sesión activa, cuando selecciona cerrar sesión, entonces el
> sistema invalida el token y lo redirige a la pantalla de inicio de sesión.

> **CA06.** Dado que la sesión supera el tiempo de inactividad configurado, cuando el usuario
> realiza una acción, entonces el sistema la cierra y muestra "Su sesión ha expirado. Ingrese
> nuevamente".

> **CA07.** Dado que un inicio o un cierre de sesión ocurre, cuando concluye la operación, entonces
> el sistema registra el evento en auditoría con usuario, fecha, hora y dirección IP.

> **CA08.** Dado que un usuario olvidó su contraseña, cuando elige «¿Olvidó su contraseña?» en la
> pantalla de inicio de sesión, entonces el sistema le indica que solo el Administrador puede
> restablecerla con una contraseña temporal, sin revelar si el nombre de usuario existe.

> **CA09.** Dado que un usuario inicia sesión con una contraseña temporal, cuando el sistema
> establece la sesión, entonces le exige cambiarla antes de permitirle cualquier otra operación, y
> rechaza las demás mostrando "Debe cambiar la contraseña temporal antes de continuar".

---

## HU-M01-02 — Gestión de usuarios

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M01-02 |
| **Épica** | Autenticación y roles |
| **Prioridad** | Alta |

**Historia**

Como administrador, quiero registrar, editar, desactivar y reactivar usuarios, restablecer la
contraseña de quien la olvidó y permitir que cada uno cambie la suya, para controlar quién accede al
sistema y que cada cuenta permanezca bajo el control de su titular.

**Descripción**

El administrador da de alta, edita el rol, desactiva y reactiva usuarios; ningún usuario se elimina,
solo se desactiva, y la reactivación le devuelve el acceso con su mismo historial. El administrador
no puede desactivar su propia cuenta: el sistema quedaría sin quien administre los usuarios (DR-30).

Si un usuario olvida su contraseña, el administrador la restablece: el sistema genera una contraseña
temporal, la muestra una sola vez para que se entregue a la persona y exige cambiarla en el siguiente
inicio de sesión. El administrador nunca conoce la contraseña definitiva de otro usuario.

Cualquier usuario autenticado puede cambiar su propia contraseña, independientemente de su rol, sin
que esa operación requiera el permiso de administración de usuarios.

**Detalles**
- Alta: nombres, apellidos, nombre de usuario, contraseña inicial y rol; obligatorios.
- Nombre de usuario: único.
- Baja: lógica, nunca física. Reactivable por el Administrador.
- Restablecimiento: contraseña temporal generada por el sistema, mostrada una sola vez y de cambio
  obligatorio en el siguiente inicio de sesión.
- Propia cuenta: el Administrador no la desactiva.
- Cambio de contraseña: exige la contraseña actual; la nueva tiene ocho caracteres como mínimo.
- Roles autorizados para gestionar usuarios: Administrador. El cambio de la propia contraseña lo
  hace cualquier rol sobre su propia cuenta.

**Criterios de aceptación**

> **CA01.** Dado que el administrador completa nombres, apellidos, nombre de usuario, contraseña y
> rol, cuando guarda, entonces el sistema crea el usuario en estado activo.

> **CA02.** Dado que el nombre de usuario ya existe, cuando el administrador intenta guardar,
> entonces el sistema rechaza la operación mostrando "El nombre de usuario ya está registrado".

> **CA03.** Dado que el administrador desactiva un usuario, cuando confirma la operación, entonces el
> sistema lo marca inactivo, conserva sus registros y su historial, impide su acceso y muestra
> "Usuario desactivado". Ninguna operación elimina físicamente un usuario.

> **CA04.** Dado que un usuario con rol distinto de Administrador intenta acceder a la gestión de
> usuarios, cuando envía la solicitud, entonces el sistema la rechaza mostrando "Acción no
> autorizada".

> **CA05.** Dado que el usuario ingresa su contraseña actual correcta y una nueva contraseña válida
> repetida dos veces, cuando confirma, entonces el sistema actualiza la contraseña y solicita
> iniciar sesión nuevamente.

> **CA06.** Dado que la contraseña actual ingresada es incorrecta, cuando el usuario confirma el
> cambio, entonces el sistema rechaza la operación mostrando "La contraseña actual no es correcta".

> **CA07.** Dado que la nueva contraseña tiene menos de ocho caracteres, cuando el usuario confirma
> el cambio, entonces el sistema la rechaza mostrando "La contraseña debe tener al menos ocho
> caracteres".

> **CA08.** Dado que un usuario olvidó su contraseña, cuando el administrador la restablece, entonces
> el sistema genera una contraseña temporal, la muestra una sola vez, marca la cuenta para exigir el
> cambio en el siguiente inicio de sesión y registra el restablecimiento en auditoría, sin guardar la
> contraseña legible.

> **CA09.** Dado que el administrador intenta desactivar su propia cuenta, cuando confirma la
> operación, entonces el sistema la rechaza mostrando "No puede desactivar su propia cuenta".

> **CA10.** Dado que un usuario está inactivo, cuando el administrador lo reactiva, entonces el
> sistema le devuelve el acceso con su mismo rol, registra el evento en auditoría y muestra "Usuario
> reactivado".

> **CA11.** Dado que la nueva contraseña y su repetición no coinciden, cuando el usuario confirma el
> cambio, entonces el sistema lo rechaza mostrando "Las contraseñas no coinciden".

---

## HU-M01-03 — Control de acceso por rol

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M01-03 |
| **Épica** | Autenticación y roles |
| **Prioridad** | Crítica |

**Historia**

Como administrador, quiero que cada rol acceda únicamente a las funciones que le competen, para que
la responsabilidad sobre cada registro sea siempre atribuible.

**Descripción**

Tres roles:

- **Administrador:** acceso total, incluidos la gestión de usuarios, los catálogos, la modificación
  de una tara ya registrada, las anulaciones y el cierre del lote con su destino.
- **Administrativo:** registro, corrección, consultas, consolidación y exportación; además gestiona
  los catálogos y la composición de los lotes (apertura, asignación y retiro de ingresos, inicio del
  recorrido y división), según el catálogo y la trazabilidad (DR-23).
- **Supervisor de planta:** registro de ingresos, con foto o sin ella; alta del vehículo nuevo desde
  el registro; registro del destare; paso del lote por las etapas; y consulta, incluidos el
  reconocimiento y la validación de cada ingreso (DR-17, DR-31).

Solo el Administrador cierra un lote con su destino, porque decide a dónde se entrega el mineral
(DR-14). El control se aplica en el servidor, no solo en la interfaz: ocultar un botón no es un
control de acceso.

**Detalles**
- La matriz de permisos por acción se define una sola vez, en el servidor (RN-M01-09).
- El detalle de cada operación vive en la sección «Permisos» del `funcionales.md` de su módulo; la
  tabla general de `requerimientos/funcionales.md` de este módulo los resume.

**Criterios de aceptación**

> **CA01.** Dado que un usuario con rol Supervisor de planta inicia sesión, cuando se carga el menú,
> entonces el sistema muestra únicamente el inicio, los ingresos —con su registro, el registro de
> destares y el calendario—, la trazabilidad con el registro del paso por las etapas y la consulta, y
> no muestra los catálogos, el cierre de lotes, la consolidación ni la administración.

> **CA02.** Dado que un usuario invoca directamente un endpoint fuera de las operaciones de su rol,
> cuando el servidor recibe la solicitud, entonces la rechaza con código 403 y el mensaje "Acción no
> autorizada", sin ejecutar la operación.

> **CA03.** Dado que el administrador cambia el rol de un usuario, cuando ese usuario realiza su
> siguiente acción, entonces el sistema aplica los permisos del nuevo rol.

> **CA04.** Dado que una operación se rechaza por falta de autorización, cuando concluye el rechazo,
> entonces el sistema registra el evento en auditoría con el usuario y la operación intentada.

> **CA05.** Dado que un supervisor de planta registra un ingreso cuya placa no está en el catálogo,
> cuando da de alta el vehículo desde el registro o registra después su destare, entonces el sistema
> permite la operación aunque el rol no gestione el catálogo.

> **CA06.** Dado que un usuario con rol Administrativo o Supervisor de planta solicita cerrar un lote
> con su destino, cuando el servidor recibe la solicitud, entonces la rechaza mostrando "Acción no
> autorizada", sin modificar el lote.
