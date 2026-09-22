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
| Desactivar usuario | Baja lógica | HU-M01-02 | `PATCH /api/v1/usuarios/{id}/desactivar/` |
| Cambiar contraseña propia | El usuario cambia su propia clave | HU-M01-02 | `POST /api/v1/usuarios/cambiar-clave/` |

## Responsabilidad y límites

M01 es el dueño de las entidades `USUARIO` y `ROL`. Identifica a quien opera el sistema y decide,
para cada solicitud, si el rol del usuario autoriza la operación pedida. No sabe qué hace cada
módulo con esa autorización: solo la concede o la niega.

## Permisos por función

| Función | Administrador | Administrativo | Supervisor de planta |
|---|:---:|:---:|:---:|
| Iniciar y cerrar sesión | Sí | Sí | Sí |
| Gestionar usuarios | Sí | No | No |
| Cambiar contraseña propia | Sí | Sí | Sí |

## Permisos generales por módulo

Referencia rápida de qué rol accede a cada módulo; el detalle vive en el `funcionales.md` de cada
uno.

| Módulo | Administrador | Administrativo | Supervisor de planta |
|---|:---:|:---:|:---:|
| M02 Catálogo maestro | Sí | Sí | Consulta |
| M03 Registro de ingresos | Sí | Sí | Sí |
| M04 Reconocimiento | Sí | Sí | Sí |
| M05 Validación | Sí | Sí | Sí |
| M06 Trazabilidad | Sí | Sí | Registro de etapa |
| M07 Consulta | Sí | Sí | Sí |
| M08 Consolidación | Sí | Sí | No |
| M09 Auditoría | Sí | No | No |

## Dependencias

| Es requerido por | Para |
|---|---|
| M02 a M09 | Autenticación y control de acceso de toda operación |
