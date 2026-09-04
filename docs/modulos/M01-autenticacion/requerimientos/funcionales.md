# Requerimientos funcionales — M01 Autenticación

**RF global asociado:** RF-08 — Control de acceso mediante autenticación y roles diferenciados

| Función | Descripción | HU | Endpoint |
|---|---|---|---|
| Iniciar sesión | Autenticar y emitir token | HU-M01-01 | `POST /api/v1/auth/login/` |
| Refrescar token | Renovar la sesión sin recredenciales | HU-M01-02 | `POST /api/v1/auth/refresh/` |
| Cerrar sesión | Invalidar el token vigente | HU-M01-02 | `POST /api/v1/auth/logout/` |
| Listar usuarios | Consultar usuarios registrados | HU-M01-03 | `GET /api/v1/usuarios/` |
| Crear usuario | Alta de usuario con rol | HU-M01-03 | `POST /api/v1/usuarios/` |
| Editar usuario | Modificar datos y rol | HU-M01-03, HU-M01-04 | `PATCH /api/v1/usuarios/{id}/` |
| Desactivar usuario | Baja lógica | HU-M01-03 | `PATCH /api/v1/usuarios/{id}/desactivar/` |
| Cambiar contraseña | Contraseña propia | HU-M01-05 | `POST /api/v1/usuarios/cambiar-clave/` |

## Matriz de permisos por rol

| Función | Administrador | Administrativo | Supervisor |
|---|:---:|:---:|:---:|
| Iniciar/cerrar sesión | Sí | Sí | Sí |
| Gestionar usuarios | Sí | No | No |
| Cambiar contraseña propia | Sí | Sí | Sí |
| Registrar ingreso (M03) | Sí | Sí | Sí |
| Registrar salida (M04) | Sí | Sí | No |
| Consultar existencias (M05) | Sí | Sí | Sí |
| Generar reportes (M06) | Sí | Sí | No |
| Consultar auditoría (M08) | Sí | No | No |
| Gestionar catálogo (M02) | Sí | Sí | No |
