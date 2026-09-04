# Historias de usuario — M01 Autenticación y control de acceso

**RF asociado:** RF-08 · **Indicador de tesis:** — (habilitante) · **Semana:** 1 · **Historias:** 5

---

## HU-M01-01 — Inicio de sesión en el sistema

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M01-01 |
| **Épica** | Autenticación y control de acceso |
| **Prioridad** | Crítica |
| **Estado** | Pendiente |

**Historia**

Como usuario del sistema, quiero iniciar sesión con mis credenciales, para acceder a las funciones que corresponden a mi rol.

**Descripción**

El sistema autentica mediante nombre de usuario y contraseña, emite un token JWT y dirige al usuario a la pantalla principal de su rol. Las contraseñas se almacenan cifradas. Tras cinco intentos fallidos consecutivos la cuenta se bloquea temporalmente quince minutos.

**Criterios de aceptación**

> **CA01.** Dado que un usuario activo ingresa credenciales válidas, cuando confirma el inicio de sesión, entonces el sistema establece la sesión y lo dirige a la pantalla principal correspondiente a su rol.

> **CA02.** Dado que un usuario ingresa credenciales inválidas, cuando envía el formulario, entonces el sistema rechaza el acceso mostrando "Usuario o contraseña incorrectos", sin indicar cuál de los dos campos falló.

> **CA03.** Dado que un usuario acumula cinco intentos fallidos consecutivos, cuando intenta un sexto acceso, entonces el sistema bloquea la cuenta por quince minutos y muestra "Cuenta bloqueada temporalmente. Intente nuevamente en 15 minutos".

> **CA04.** Dado que un usuario existe pero está inactivo, cuando ingresa credenciales correctas, entonces el sistema rechaza el acceso mostrando "La cuenta se encuentra inactiva. Contacte al administrador".

> **CA05.** Dado que el inicio de sesión es exitoso, cuando se establece la sesión, entonces el sistema registra el evento en auditoría con usuario, fecha, hora y dirección IP.

---

## HU-M01-02 — Cierre de sesión

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M01-02 |
| **Prioridad** | Alta |

**Historia**

Como usuario autenticado, quiero cerrar mi sesión, para impedir que otra persona use el sistema con mi identidad en un equipo compartido.

**Criterios de aceptación**

> **CA01.** Dado que un usuario tiene sesión activa, cuando selecciona cerrar sesión, entonces el sistema invalida el token y lo redirige a la pantalla de inicio de sesión.

> **CA02.** Dado que un usuario cerró sesión, cuando intenta acceder a una ruta protegida mediante el historial del navegador, entonces el sistema lo redirige a la pantalla de inicio de sesión.

> **CA03.** Dado que la sesión supera la duración configurada sin actividad, cuando el usuario realiza una acción, entonces el sistema cierra la sesión y muestra "Su sesión ha expirado. Ingrese nuevamente".

---

## HU-M01-03 — Registro y gestión de usuarios

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M01-03 |
| **Prioridad** | Crítica |

**Historia**

Como administrador, quiero registrar, editar y desactivar usuarios, para controlar quién accede al sistema.

**Criterios de aceptación**

> **CA01.** Dado que el administrador completa nombres, apellidos, nombre de usuario, contraseña y rol, cuando guarda, entonces el sistema crea el usuario en estado activo.

> **CA02.** Dado que el nombre de usuario ya existe, cuando el administrador intenta guardar, entonces el sistema rechaza la operación mostrando "El nombre de usuario ya está registrado".

> **CA03.** Dado que un usuario tiene registros asociados, cuando el administrador intenta eliminarlo, entonces el sistema no lo elimina físicamente sino que lo desactiva, preservando el histórico.

> **CA04.** Dado que un usuario con rol distinto de administrador intenta acceder a la gestión de usuarios, cuando envía la solicitud, entonces el sistema la rechaza respondiendo "Acción no autorizada".

---

## HU-M01-04 — Control de acceso por rol

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M01-04 |
| **Prioridad** | Alta |

**Historia**

Como administrador, quiero que cada rol acceda únicamente a las funciones que le competen, para que la responsabilidad sobre cada registro sea atribuible.

**Descripción**

Tres roles: Administrador (acceso total), Administrativo (registro de ingresos y salidas, consultas, reportes y exportaciones) y Supervisor (registro de ingresos y consulta de existencias).

**Criterios de aceptación**

> **CA01.** Dado que un usuario con rol Supervisor inicia sesión, cuando se carga el menú, entonces el sistema muestra únicamente las opciones de registro de ingreso y consulta de existencias.

> **CA02.** Dado que un usuario invoca directamente un endpoint fuera de su rol, cuando el servidor recibe la solicitud, entonces la rechaza con código 403 y mensaje "Acción no autorizada", sin ejecutar la operación.

> **CA03.** Dado que el administrador cambia el rol de un usuario, cuando ese usuario realiza su siguiente acción, entonces el sistema aplica los permisos del nuevo rol.

---

## HU-M01-05 — Cambio de contraseña

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M01-05 |
| **Prioridad** | Media |

**Historia**

Como usuario autenticado, quiero cambiar mi contraseña, para mantener el control sobre mi propia cuenta.

**Criterios de aceptación**

> **CA01.** Dado que el usuario ingresa su contraseña actual correcta y una nueva contraseña válida repetida dos veces, cuando confirma, entonces el sistema actualiza la contraseña y solicita iniciar sesión nuevamente.

> **CA02.** Dado que la contraseña actual ingresada es incorrecta, cuando el usuario confirma, entonces el sistema rechaza la operación mostrando "La contraseña actual no es correcta".

> **CA03.** Dado que la nueva contraseña tiene menos de ocho caracteres, cuando el usuario confirma, entonces el sistema la rechaza mostrando "La contraseña debe tener al menos ocho caracteres".
