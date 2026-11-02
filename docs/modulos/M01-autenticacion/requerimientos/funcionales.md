# Requerimientos funcionales — M01 Autenticación y roles

**RF asociado:** **RF10** — Gestionar usuarios y roles de acceso.

| Función | Descripción | HU | Endpoint |
|---|---|---|---|
| Iniciar sesión | Autenticar y emitir token | HU-M01-01 | `POST /api/v1/auth/login/` |
| Refrescar token | Renovar la sesión sin recredenciales | HU-M01-01 | `POST /api/v1/auth/refresh/` |
| Cerrar sesión | Invalidar el token vigente | HU-M01-01 | `POST /api/v1/auth/logout/` |
| Listar usuarios | Consultar usuarios registrados | HU-M01-02 | `GET /api/v1/usuarios/` |
| Crear usuario | Alta de usuario con rol | HU-M01-02 | `POST /api/v1/usuarios/` |
| Editar usuario | Modificar datos y rol | HU-M01-02 | `PATCH /api/v1/usuarios/{id}/` |
| Desactivar usuario | Baja lógica; rechaza la propia cuenta | HU-M01-02 | `PATCH /api/v1/usuarios/{id}/desactivar/` |
| Reactivar usuario | Devuelve el acceso a un usuario inactivo, con su mismo rol | HU-M01-02 | `PATCH /api/v1/usuarios/{id}/reactivar/` |
| Restablecer contraseña | Genera una contraseña temporal de cambio obligatorio | HU-M01-02 | `POST /api/v1/usuarios/{id}/restablecer-clave/` |
| Cambiar contraseña propia | El usuario cambia su propia clave, también la temporal | HU-M01-01, HU-M01-02 | `POST /api/v1/usuarios/cambiar-clave/` |
| Controlar el acceso por rol | Concede o niega cada operación de los demás módulos según el rol, en el servidor, y registra el rechazo | HU-M01-03 | (transversal: clases de `apps/accounts/permissions.py`) |

## Responsabilidad y límites

M01 es el dueño de las entidades `USUARIO` y `ROL`. Identifica a quien opera el sistema y decide,
para cada solicitud, si el rol del usuario autoriza la operación pedida. No sabe qué hace cada
módulo con esa autorización: solo la concede o la niega.

## Permisos por función

| Función | Administrador | Administrativo | Supervisor de planta |
|---|:---:|:---:|:---:|
| Iniciar y cerrar sesión | Sí | Sí | Sí |
| Gestionar usuarios: alta, edición, desactivación y reactivación | Sí | No | No |
| Restablecer la contraseña de otro usuario | Sí | No | No |
| Cambiar contraseña propia | Sí | Sí | Sí |

## Permisos generales por módulo

Referencia rápida de qué rol accede a cada módulo; el detalle vive en el `funcionales.md` de cada
uno.

| Módulo | Administrador | Administrativo | Supervisor de planta |
|---|:---:|:---:|:---:|
| M02 Catálogo maestro | Sí | Sí, salvo modificar una tara ya registrada | Consulta; alta del vehículo desde el registro y primera tara |
| M03 Registro de ingresos | Sí | Sí, salvo anular | Registro con foto o sin ella, destare y consulta; no corrige ni anula |
| M04 Reconocimiento | Sí | Sí | Dentro del registro, y consulta en el detalle del ingreso (DR-31) |
| M05 Validación | Sí | Sí | Dentro del registro, con justificación de V1 y V4, y consulta en el detalle del ingreso (DR-31) |
| M06 Trazabilidad | Sí | Sí, salvo cerrar el lote con su destino | Paso por etapa, secado de un ingreso tardío, bigbags y consulta |
| M07 Consulta | Sí | Sí | Sí, salvo exportar el listado de ingresos |
| M08 Consolidación | Sí | Sí | No |
| M09 Auditoría | Sí | Historial de un ingreso | Historial de un ingreso |

El alcance del Supervisor de planta sigue DR-17: registra en planta lo que ocurre en planta
(ingresos, vehículos nuevos, destares y etapas) y consulta, incluidos el reconocimiento y la
validación de cada ingreso (DR-31). El cierre del lote con su destino es
exclusivo del Administrador (DR-14). Si esta tabla y la sección «Permisos» de un módulo difieren,
prevalece la del módulo y la diferencia se reporta.

## Dependencias

| Es requerido por | Para |
|---|---|
| M02 a M09 | Autenticación y control de acceso de toda operación |
