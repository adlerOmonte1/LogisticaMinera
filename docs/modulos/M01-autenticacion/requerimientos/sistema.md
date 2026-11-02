# Requerimientos de sistema — M01 Autenticación y roles

| Código | Requerimiento | Deriva de |
|---|---|---|
| RS-M01-01 | El sistema autentica mediante par usuario/contraseña y emite un token con vigencia configurable (por defecto 8 horas) | RU-M01-01 |
| RS-M01-02 | El sistema almacena contraseñas con función de derivación de clave (PBKDF2 con sal); nunca en texto plano ni con hash reversible | RU-M01-01 |
| RS-M01-03 | El sistema incrementa un contador de intentos fallidos por usuario y lo reinicia tras un acceso exitoso o transcurrido el bloqueo | RU-M01-02 |
| RS-M01-04 | El sistema bloquea el acceso durante 15 minutos al alcanzar 5 intentos fallidos consecutivos | RU-M01-02 |
| RS-M01-05 | El sistema valida el token en cada solicitud a un endpoint protegido y devuelve 401 si es inválido o expiró | RU-M01-02 |
| RS-M01-06 | El sistema evalúa los permisos del rol en el servidor antes de ejecutar cualquier operación, con independencia de lo que muestre el cliente | RU-M01-03 |
| RS-M01-07 | El sistema aplica baja lógica a los usuarios: `activo` pasa a falso y el registro persiste; la reactivación lo devuelve a verdadero con el mismo rol | RU-M01-04 |
| RS-M01-08 | El sistema registra en auditoría los eventos de inicio de sesión, cierre de sesión, cambio de rol, desactivación, reactivación, restablecimiento de contraseña y acceso rechazado | RU-M01-01 |
| RS-M01-09 | El sistema permite a cualquier usuario autenticado cambiar su propia contraseña, sin exigir el permiso de gestión de usuarios | RU-M01-05 |
| RS-M01-10 | El sistema concede al Supervisor de planta los permisos de registro de ingreso, alta de vehículo desde el registro, registro de destare, registro del paso por etapa y consulta —incluidos el reconocimiento y la validación de un ingreso (DR-31)—, y le niega la gestión de catálogos, la corrección, la anulación, la composición de lotes, la consolidación y la gestión de usuarios | RU-M01-03, RU-M01-06 |
| RS-M01-11 | El sistema autoriza el cierre del lote con su destino únicamente al rol Administrador | RU-M01-07 |
| RS-M01-12 | El sistema restablece la contraseña de un usuario generando una contraseña temporal aleatoria, que muestra una sola vez al Administrador, almacena con la misma función de derivación y marca la cuenta con `debe_cambiar_clave` | RU-M01-08 |
| RS-M01-13 | El sistema exige el cambio de contraseña a la cuenta marcada con `debe_cambiar_clave` antes de atender cualquier otra operación, y retira la marca al completarse el cambio | RU-M01-08 |
| RS-M01-14 | El sistema rechaza que un usuario desactive su propia cuenta | RU-M01-04 |
