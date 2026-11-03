# Notas de implementación — M01 Autenticación y roles

## Backend (Django)

**App:** `apps/accounts/` — implementada y con pruebas (`models/`, `services/`, `serializers/`,
`views/`, `permissions.py`, `tests/`). El modelo y la autenticación no cambian; sí cambia la matriz
de permisos, que debe ampliarse al alcance del Supervisor de planta (DR-17) y reservar el cierre del
lote al Administrador (DR-14).

### Modelo

`Usuario` extiende el modelo de autenticación de Django y añade `id_rol`, `activo`,
`intentos_fallidos`, `ultimo_acceso` y `debe_cambiar_clave`. `Rol` es un catálogo de tres valores:
`ADMINISTRADOR`, `ADMINISTRATIVO`, `SUPERVISOR`.

### Servicio de autenticación

`apps/accounts/services/autenticacion.py` concentra el bloqueo temporal (RN-M01-07) y la emisión del
token; `apps/accounts/services/usuarios.py` concentra el alta, la edición, la desactivación, la
reactivación, el restablecimiento y el cambio de contraseña.

El restablecimiento genera la contraseña temporal con `secrets` —no con `random`—, la guarda con
`set_password()` y pone `debe_cambiar_clave` en verdadero (RS-M01-12). Mientras la marca esté activa,
una clase de permiso global solo admite el cambio de contraseña y el cierre de sesión (RS-M01-13). La
contraseña temporal viaja una sola vez en la respuesta y nunca entra en `EVENTO_AUDITORIA`
(RNF-M01-07).

### Permisos por rol

`apps/accounts/permissions.py` define las clases de permiso que reutilizan los demás módulos. Cada
app declara qué clase de permiso exige cada `ViewSet`; ninguna app reimplementa la lógica de rol por
su cuenta.

Hoy el archivo solo contiene `PuedeGestionarUsuarios`. Con la matriz de la versión 2 hacen falta, al
menos, permisos por acción para:

| Permiso | Roles | Módulo que lo usa |
|---|---|---|
| Registrar ingreso, con foto o sin ella | Los tres | M03 |
| Corregir ingreso y revertir su última corrección | Administrador, Administrativo | M03 |
| Anular ingreso | Administrador | M03 |
| Dar de alta un vehículo desde el registro y registrar su destare | Los tres | M02, M03 |
| Gestionar catálogos, incluida la reactivación de registros dados de baja | Administrador, Administrativo | M02 |
| Modificar una tara ya registrada | Administrador | M02 |
| Consultar el reconocimiento y la validación de un ingreso | Los tres | M04, M05 |
| Componer lotes: abrir, agregar o quitar minerales, asignar, retirar, iniciar el recorrido y dividir | Administrador, Administrativo | M06 |
| Registrar el paso por etapa, el secado de un ingreso tardío y los bigbags | Los tres | M06 |
| Cerrar el lote con su destino | Administrador | M06 |
| Exportar el listado de ingresos | Administrador, Administrativo | M07 |
| Consolidar y exportar | Administrador, Administrativo | M08 |
| Gestionar usuarios y restablecer contraseñas | Administrador | M01 |
| Consultar la auditoría del sistema | Administrador | M09 |

Los nombres de las clases se fijan al implementar cada módulo; lo que no cambia es que se definen
aquí y no en la app que las usa (RN-M01-09).

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
