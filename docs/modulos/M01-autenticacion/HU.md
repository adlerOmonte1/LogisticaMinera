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

---

## HU-M01-02 — Gestión de usuarios

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M01-02 |
| **Épica** | Autenticación y roles |
| **Prioridad** | Crítica |

**Historia**

Como administrador, quiero registrar, editar, desactivar usuarios y permitir que cada uno cambie su
propia contraseña, para controlar quién accede al sistema y que cada cuenta permanezca bajo el
control de su titular.

**Descripción**

El administrador da de alta, edita el rol y desactiva usuarios; ningún usuario se elimina, solo se
desactiva. Cualquier usuario autenticado puede cambiar su propia contraseña, independientemente de
su rol, sin que esa operación requiera el permiso de administración de usuarios.

**Detalles**
- Alta: nombres, apellidos, nombre de usuario, contraseña inicial y rol; obligatorios.
- Nombre de usuario: único.
- Baja: lógica, nunca física.
- Cambio de contraseña: exige la contraseña actual; la nueva tiene ocho caracteres como mínimo.
- Roles autorizados para gestionar usuarios: Administrador. El cambio de la propia contraseña lo
  hace cualquier rol sobre su propia cuenta.

**Criterios de aceptación**

> **CA01.** Dado que el administrador completa nombres, apellidos, nombre de usuario, contraseña y
> rol, cuando guarda, entonces el sistema crea el usuario en estado activo.

> **CA02.** Dado que el nombre de usuario ya existe, cuando el administrador intenta guardar,
> entonces el sistema rechaza la operación mostrando "El nombre de usuario ya está registrado".

> **CA03.** Dado que un usuario tiene registros asociados, cuando el administrador intenta
> eliminarlo, entonces el sistema no lo elimina físicamente: lo desactiva y preserva el histórico.

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

Tres roles: Administrador (acceso total, incluidos usuarios, catálogos y anulaciones), Administrativo
(registro, corrección, consultas, consolidación y exportación) y Supervisor de planta (registro y
consulta). El control se aplica en el servidor, no solo en la interfaz: ocultar un botón no es un
control de acceso.

**Criterios de aceptación**

> **CA01.** Dado que un usuario con rol Supervisor de planta inicia sesión, cuando se carga el menú,
> entonces el sistema muestra únicamente las opciones de registro de ingreso y consulta.

> **CA02.** Dado que un usuario invoca directamente un endpoint fuera de las operaciones de su rol,
> cuando el servidor recibe la solicitud, entonces la rechaza con código 403 y el mensaje "Acción no
> autorizada", sin ejecutar la operación.

> **CA03.** Dado que el administrador cambia el rol de un usuario, cuando ese usuario realiza su
> siguiente acción, entonces el sistema aplica los permisos del nuevo rol.

> **CA04.** Dado que una operación se rechaza por falta de autorización, cuando concluye el rechazo,
> entonces el sistema registra el evento en auditoría con el usuario y la operación intentada.
