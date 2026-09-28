---
name: backend-auth-permisos
description: Implementa la autenticación JWT y la autorización por rol del sistema web inteligente de ingreso de mineral (módulo M01) — SimpleJWT, los tres roles Administrador, Administrativo y Supervisor de planta, permisos declarados por acción, bloqueo por intentos fallidos y validación en servidor. Úsala al trabajar en apps/accounts, en permissions.py de cualquier app, en guards o interceptores de rol, y cuando se mencione login, JWT, token, sesión, roles o permisos.
---

# Autenticación y permisos

Carga antes `contexto-tesis` y `solid-proyecto`. Fuente: `docs/modulos/M01-autenticacion/`.

## Los tres roles

Son exactamente estos. No hay «Operador de balanza» ni «Gerencia»: las historias de usuario y el
modelo entidad-relación están escritos sobre estos tres nombres y cambiarlos obliga a reescribir M01
completo.

| Rol | Alcance |
|---|---|
| **Administrador** | Todo, incluida gestión de usuarios, catálogos, anulaciones y ajustes |
| **Administrativo** | Registro, corrección, consultas, consolidación y exportación |
| **Supervisor de planta** | Registro y consulta |

El rol se modela como entidad `ROL` con FK desde `USUARIO`, no como un campo de texto ni como grupos
de Django sin respaldo en el modelo entidad-relación.

## JWT

`djangorestframework-simplejwt`. Sesión sin estado en el servidor.

```
POST /api/v1/auth/login/     -> access + refresh
POST /api/v1/auth/refresh/
POST /api/v1/auth/logout/    -> invalida el refresh
```

Duración de sesión configurable, por defecto ocho horas (HU-M01-01). Expiración por inactividad
configurable, con aviso antes de expirar y opción de extender. El aviso es del cliente; la
invalidación es del servidor — si solo lo hace el cliente, no es control de sesión.

## Permisos por acción — no un objeto monolítico

Segregación de interfaces aplicada (ver `solid-proyecto`, ISP):

```python
class PuedeRegistrarIngreso(BasePermission): ...       # Administrador, Administrativo, Supervisor de planta
class PuedeCorregirIngreso(BasePermission): ...        # Administrador, Administrativo
class PuedeAnularIngreso(BasePermission): ...          # solo Administrador
class PuedeGestionarCatalogo(BasePermission): ...      # Administrador, Administrativo
class PuedeGestionarUsuarios(BasePermission): ...      # solo Administrador
class PuedeConsolidar(BasePermission): ...             # Administrador, Administrativo
class PuedeConsultarAuditoria(BasePermission): ...     # solo Administrador
```

Un permiso por acción, no `IsAdminUser` genérico. El Supervisor de planta no debe recibir la
interfaz de gestión de usuarios ni la de consolidación.

## La validación de servidor es obligatoria

Una solicitud **directa** a un módulo fuera del rol —por ejemplo, un Supervisor de planta que
invoca el endpoint de anulación— debe recibir rechazo del servidor y quedar constancia en auditoría.
Ocultar el botón en Angular no es control de acceso, es cosmética.

Regla operativa: **por cada opción que el frontend oculta según el rol, debe existir un permiso del
backend que rechace la misma operación**, y una prueba que lo verifique. Si solo existe lo primero,
el control no existe.

Toda solicitud rechazada por autorización se registra en auditoría (M09) con usuario, acción
intentada, fecha y dirección IP. El mensaje devuelto es exactamente `"Acción no autorizada"`.

## Reglas de cuenta

| Regla | Detalle |
|---|---|
| Contraseñas | Hash siempre; mínimo ocho caracteres; nunca en texto plano ni en logs |
| Intentos fallidos | Bloqueo temporal de quince minutos tras cinco fallos consecutivos; el contador vive en `USUARIO.intentos_fallidos` |
| Mensaje de credenciales | `"Usuario o contraseña incorrectos"` — **sin** precisar cuál de los dos falló |
| Cuenta inactiva | `"La cuenta se encuentra inactiva"` |
| Baja de usuario | Lógica (`activo = false`). Nunca se elimina: se perdería la atribución de los registros históricos y el rastro de auditoría |
| Cambio de contraseña propia | Cualquier rol, sobre su propia cuenta, exigiendo la contraseña actual |
| Cambio de rol | Se aplica en la siguiente sesión del usuario |

## Atribución

Cada operación de escritura guarda el usuario responsable de forma **permanente e inmutable**
(`usuario_registro`, `editable=False`). Un evento de auditoría con autor distinto al que ejecutó la
operación invalidaría la atribución de todo el histórico (RN-M09-06).

## Verificación

- [ ] Cada endpoint declara su permiso; ninguno queda con el permiso por defecto del proyecto.
- [ ] Existe una prueba de rechazo por rol para cada criterio de aceptación que lo exige.
- [ ] El mensaje de credenciales inválidas no revela si el usuario existe.
- [ ] Ningún endpoint expone `DELETE` sobre usuarios ni sobre ninguna otra entidad.
- [ ] Los rechazos por autorización llegan a auditoría (M09).
- [ ] El cambio de la propia contraseña no exige el permiso de gestión de usuarios.
