# Reglas de negocio — M01 Autenticación y roles

> Ubicación en el código: `apps/accounts/models/` (invariantes de usuario y rol),
> `apps/accounts/services/` (bloqueo temporal y desactivación) y `apps/accounts/permissions.py`
> (control de acceso por rol). Ninguna de estas reglas vive en `views/` ni en un componente Angular
> (D-08).

| Código | Regla | Consecuencia si se viola |
|---|---|---|
| RN-M01-01 | El nombre de usuario es único en todo el sistema | Dos personas podrían compartir identidad y la atribución de cada registro se rompería |
| RN-M01-02 | Todo usuario pertenece a exactamente un rol | Los permisos quedarían indeterminados |
| RN-M01-03 | Un usuario con registros asociados nunca se elimina físicamente; solo se desactiva | Se perderían ingresos del histórico atribuidos a ese usuario |
| RN-M01-04 | La contraseña tiene un mínimo de ocho caracteres | Una contraseña corta facilitaría el acceso no autorizado en un equipo compartido en planta |
| RN-M01-05 | Un usuario inactivo no puede autenticarse aunque sus credenciales sean correctas | Personal desvinculado seguiría pudiendo registrar operaciones |
| RN-M01-06 | Solo el rol Administrador crea, modifica o desactiva usuarios | La segregación entre quien administra y quien opera desaparecería |
| RN-M01-07 | El contador de intentos fallidos se reinicia únicamente tras un acceso exitoso o transcurrido el bloqueo | El bloqueo sería evadible esperando entre intentos sin agotar el conteo |
| RN-M01-08 | El cambio de la propia contraseña exige la contraseña actual | Cualquiera con una sesión abierta y sin vigilancia podría apropiarse de la cuenta |
