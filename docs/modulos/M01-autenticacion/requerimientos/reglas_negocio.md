# Reglas de negocio — M01 Autenticación

> Invariantes del dominio. En el código viven en `apps/accounts/models/` y validadores asociados, nunca en las vistas ni en los componentes Angular.

| Código | Regla | Consecuencia si se viola |
|---|---|---|
| RN-M01-01 | El nombre de usuario es único en todo el sistema | Dos personas podrían compartir identidad y la atribución de registros se rompe |
| RN-M01-02 | Todo usuario pertenece a exactamente un rol | Los permisos se vuelven indeterminados |
| RN-M01-03 | Un usuario con registros asociados nunca se elimina físicamente; solo se desactiva | Se perderían ingresos del histórico y el indicador I2 quedaría subestimado |
| RN-M01-04 | La contraseña tiene un mínimo de ocho caracteres | Riesgo de acceso no autorizado en un equipo compartido en planta |
| RN-M01-05 | Un usuario inactivo no puede autenticarse aunque sus credenciales sean correctas | Personal desvinculado seguiría registrando |
| RN-M01-06 | Solo el rol Administrador crea, modifica o desactiva usuarios | La segregación de funciones desaparece |
| RN-M01-07 | El contador de intentos fallidos se reinicia únicamente tras un acceso exitoso o transcurrido el bloqueo | El bloqueo sería evadible esperando entre intentos |

**Ubicación en el código:** `apps/accounts/models/` (RN-M01-01, 02, 04, 05), `apps/accounts/services/` (RN-M01-03, 07), `apps/accounts/permissions.py` (RN-M01-06).
