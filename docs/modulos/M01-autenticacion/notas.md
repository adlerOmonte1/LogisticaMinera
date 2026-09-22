# Notas de implementación — M01 Autenticación y roles

## Backend (Django)

**App:** `apps/accounts/` — implementada y con pruebas (`models/`, `services/`, `serializers/`,
`views/`, `permissions.py`, `tests/`). Sin cambios de fondo en esta reformulación: el módulo ya
respondía a RF10 con el diseño anterior.

### Modelo

`Usuario` extiende el modelo de autenticación de Django y añade `id_rol`, `activo`,
`intentos_fallidos` y `ultimo_acceso`. `Rol` es un catálogo de tres valores:
`ADMINISTRADOR`, `ADMINISTRATIVO`, `SUPERVISOR`.

### Servicio de autenticación

`apps/accounts/services/autenticacion.py` concentra el bloqueo temporal (RN-M01-07) y la emisión del
token; `apps/accounts/services/usuarios.py` concentra el alta, la edición, la desactivación y el
cambio de contraseña.

### Permisos por rol

`apps/accounts/permissions.py` define las clases de permiso que reutilizan los demás módulos. Cada
app declara qué clase de permiso exige cada `ViewSet`; ninguna app reimplementa la lógica de rol por
su cuenta.

## Frontend (Angular)

**Feature:** `features/auth/`

- El token se guarda en memoria, no en `localStorage`, para reducir la superficie de un robo de
  sesión mediante un script inyectado.
- El interceptor adjunta la cabecera `Authorization` en cada solicitud y redirige a la pantalla de
  inicio de sesión ante un 401.
- El menú se construye a partir del rol devuelto por el login, no de una lista fija en el cliente.

## Riesgo de implementación identificado

**El riesgo principal es que un módulo nuevo implemente su propio control de rol en lugar de
reutilizar `apps/accounts/permissions.py`.**

Cuantos más módulos definan su propia lógica de «si el rol es tal, entonces...», más probable es que
una de esas copias quede desactualizada cuando cambien los roles o sus alcances. La defensa es de
revisión de código, no de prueba automática: todo `ViewSet` nuevo debe declarar una clase de permiso
importada de `apps/accounts/permissions.py`, nunca una comprobación de rol escrita en la vista.

## Dependencias

| Es requerido por | Para |
|---|---|
| M02 a M09 | Autenticación y control de acceso de toda operación |
