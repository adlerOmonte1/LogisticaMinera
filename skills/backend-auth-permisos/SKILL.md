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
| **Administrador** | Todo, incluida gestión de usuarios —con su reactivación y el restablecimiento de contraseñas—, catálogos, modificación de una tara ya registrada, anulaciones, cierre del lote con su destino y auditoría completa (DR-14, DR-30) |
| **Administrativo** | Registro, corrección y reversión, consultas, consolidación y exportaciones —consolidado y listado—; gestión de catálogos, con su reactivación, y composición de lotes (DR-23, DR-30) |
| **Supervisor de planta** | Registro de ingresos con foto o sin ella, alta del vehículo nuevo desde el registro, destare, paso del lote por las etapas y consulta, incluidos el reconocimiento y la validación de cada ingreso (DR-17, DR-31) |

El permiso se concede por operación, no por módulo (RN-M01-09): el Supervisor registra ingresos, pero
no los corrige ni los anula; registra el paso por etapa, pero no compone ni cierra lotes. La matriz
completa está en `docs/modulos/M01-autenticacion/notas.md`.

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
# Los tres roles
class PuedeConsultar(BasePermission): ...              # M04, M05, M06, M07 y el historial de M09
class PuedeRegistrarIngreso(BasePermission): ...       # registro con foto o sin ella (M03)
class PuedeRegistrarDestare(BasePermission): ...       # destare y primera tara (M03, M02)
class PuedeDarAltaVehiculo(BasePermission): ...        # alta del vehiculo desde el registro (M02)
class PuedeRegistrarEtapa(BasePermission): ...         # etapas, secado de un tardio y bigbags (M06)
# Administrador y Administrativo
class PuedeCorregirIngreso(BasePermission): ...        # correccion y reversion de la ultima (M03)
class PuedeGestionarCatalogo(BasePermission): ...      # alta, edicion, baja, reactivacion; tipo de mineral desde el registro (M02)
class PuedeComponerLote(BasePermission): ...           # abrir, minerales, asignar, retirar, iniciar, dividir (M06)
class PuedeExportarListado(BasePermission): ...        # CSV del listado (M07)
class PuedeConsolidar(BasePermission): ...             # consolidado y su exportacion (M08)
# Solo Administrador
class PuedeAnularIngreso(BasePermission): ...          # M03
class PuedeModificarTara(BasePermission): ...          # tara ya registrada, con motivo (M02)
class PuedeCerrarLote(BasePermission): ...             # cierre con destino (M06)
class PuedeGestionarUsuarios(BasePermission): ...      # alta, edicion, baja, reactivacion, restablecer contrasena (M01)
class PuedeConsultarAuditoria(BasePermission): ...     # auditoria completa (M09)
# Global
class RequiereClaveDefinitiva(BasePermission): ...     # con debe_cambiar_clave solo admite cambiar la clave y cerrar sesion
```

Un permiso por acción, no `IsAdminUser` genérico. La matriz que estas clases implementan está en
`docs/modulos/M01-autenticacion/notas.md`; si difieren, manda la matriz y la diferencia se reporta.
El Supervisor de planta no debe recibir la interfaz de gestión de usuarios ni la de consolidación.

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
| Baja de usuario | Lógica (`activo = false`) y reactivable. Nunca se elimina: se perdería la atribución de los registros históricos y el rastro de auditoría. Nadie desactiva su propia cuenta: `"No puede desactivar su propia cuenta"` |
| Restablecimiento | Solo el Administrador. Contraseña temporal generada con `secrets`, mostrada una vez, guardada con `set_password()` y con `debe_cambiar_clave = true`; nunca entra en auditoría ni en los registros del servidor |
| Cambio de contraseña propia | Cualquier rol, sobre su propia cuenta, exigiendo la contraseña actual; retira `debe_cambiar_clave` |
| Cambio de rol | Se aplica en la **siguiente acción** del usuario (HU-M01-03 CA03): el rol se lee de la base en cada solicitud y no se guarda como dato del token |

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
- [ ] Una cuenta con `debe_cambiar_clave` solo puede cambiar su contraseña o cerrar sesión.
- [ ] Un cambio de rol se aplica en la siguiente solicitud del usuario, sin esperar a que expire su
      token.
