---
name: backend-auth-permisos
description: Implementa la autenticación JWT y la autorización por rol del sistema de control de producción y existencias (módulo M01) — SimpleJWT, los tres roles Administrador, Administrativo y Supervisor, permisos declarados por acción, bloqueo por intentos fallidos y validación en servidor. Úsala al trabajar en apps/accounts, en permissions.py de cualquier app, en guards o interceptores de rol, y cuando se mencione login, JWT, token, sesión, roles o permisos.
---

# Autenticación y permisos

Carga antes `contexto-tesis` y `solid-proyecto`. Fuente: `docs/modulos/M01-autenticacion/`.

## Los tres roles

Son exactamente estos. No hay «Operador de balanza» ni «Gerencia»: las 34 historias de usuario y el
modelo ER están escritos sobre estos tres nombres y cambiarlos obliga a reescribir M01 completo.

| Rol | Alcance |
|---|---|
| **Administrador** | Todo, incluida gestión de usuarios, catálogos, anulaciones y ajustes |
| **Administrativo** | Ingresos, salidas, consultas, reportes y exportaciones |
| **Supervisor** | Registro de ingresos y consulta de existencias |

El rol se modela como entidad `ROL` con FK desde `USUARIO`, no como un campo de texto ni como grupos
de Django sin respaldo en el modelo ER.

## JWT

`djangorestframework-simplejwt`. Sesión sin estado en el servidor, y no por moda: es **indispensable
para la operación sin conexión de M07**. Un token que el dispositivo conserva permite validar
localmente que hay sesión activa mientras no hay red.

```
POST /api/v1/auth/login/     -> access + refresh
POST /api/v1/auth/refresh/
POST /api/v1/auth/logout/    -> invalida el refresh
```

Duración de sesión configurable, por defecto ocho horas (HU-M01-01). Expiración por inactividad a los
treinta minutos, con aviso dos minutos antes y opción de extender (HU-M01-02). El aviso es del
cliente; la invalidación es del servidor — si solo lo hace el cliente, no es control de sesión.

Ajusta la vida del `access` a la ventana offline prevista: si expira mientras el supervisor está sin
señal, la cola de M07 no puede enviarse al recuperar conexión y el ingreso queda retenido. Es un
fallo que degrada I1 justo en el escenario que M07 existe para resolver.

## Permisos por acción — no un objeto monolítico

Segregación de interfaces aplicada (ver `solid-proyecto`, ISP):

```python
class PuedeRegistrarIngreso(BasePermission): ...     # Administrador, Administrativo, Supervisor
class PuedeEditarIngreso(BasePermission): ...        # Administrador, Administrativo
class PuedeAnularIngreso(BasePermission): ...        # solo Administrador
class PuedeGestionarCatalogo(BasePermission): ...    # Administrador, Administrativo
class PuedeGestionarUsuarios(BasePermission): ...    # solo Administrador
class PuedeGenerarReportes(BasePermission): ...      # Administrador, Administrativo
class PuedeConsultarExistencias(BasePermission): ... # los tres
```

Un permiso por acción, no `IsAdminUser` genérico. El Supervisor no debe recibir la interfaz de
gestión de usuarios ni la de reportes.

## La validación de servidor es obligatoria

HU-M01-04 CA02, literal: un supervisor que envía una solicitud **directa** al módulo de reportes debe
recibir rechazo del servidor y quedar constancia en auditoría. Ocultar el botón en Angular no es
control de acceso, es cosmética.

Regla operativa: **por cada opción que el frontend oculta según el rol, debe existir un permiso del
backend que rechace la misma operación**, y una prueba que lo verifique. Si solo existe lo primero,
el control no existe.

Toda solicitud rechazada por autorización se registra en auditoría (M08) con usuario, acción
intentada, fecha y dirección IP. El mensaje devuelto es exactamente `"Acción no autorizada"`.

## Reglas de cuenta

| Regla | Detalle |
|---|---|
| Contraseñas | Hash siempre; mínimo ocho caracteres; nunca en texto plano ni en logs |
| Intentos fallidos | Bloqueo temporal de quince minutos tras cinco fallos consecutivos; el contador vive en `USUARIO.intentos_fallidos` |
| Mensaje de credenciales | `"Usuario o contraseña incorrectos"` — **sin** precisar cuál de los dos falló |
| Cuenta inactiva | `"La cuenta se encuentra inactiva"` |
| Baja de usuario | Lógica (`activo = false`). Nunca se elimina: se perdería la atribución de los registros históricos y el rastro de auditoría |
| Primer acceso | Cambio de contraseña obligatorio; ninguna otra operación permitida hasta completarlo |
| Cambio de rol | Se aplica en la siguiente sesión del usuario (HU-M01-04 CA03) |

## Atribución

Cada operación de escritura guarda el usuario responsable de forma **permanente e inmutable**
(`id_usuario_registro`, `editable=False`). Esto sostiene RNF-M03-08 (no repudio) y es lo que permite
demostrar ante el jurado que los registros del postest son atribuibles. Un ingreso sin usuario
asociado es un dato inservible para la tesis, aunque el sistema funcione.

## Verificación

- [ ] Cada endpoint declara su permiso; ninguno queda con el permiso por defecto del proyecto.
- [ ] Existe una prueba de rechazo por rol para cada criterio de aceptación que lo exige.
- [ ] El mensaje de credenciales inválidas no revela si el usuario existe.
- [ ] Ningún endpoint expone `DELETE` sobre usuarios.
- [ ] Los rechazos por autorización llegan a auditoría.
- [ ] La vida del token cubre la ventana offline prevista para M07.
