# Requerimientos de sistema — M01 Autenticación

> Traducción técnica de los RU. Especifican qué debe hacer el sistema, no cómo se ve.

| Código | Requerimiento | Deriva de |
|---|---|---|
| RS-M01-01 | El sistema autentica mediante par usuario/contraseña y emite un token JWT con vigencia configurable (por defecto 8 horas) | RU-M01-01 |
| RS-M01-02 | El sistema almacena contraseñas con función de derivación de clave (PBKDF2 con sal, configuración por defecto de Django); nunca en texto plano ni con hash reversible | RU-M01-01 |
| RS-M01-03 | El sistema incrementa un contador de intentos fallidos por usuario y lo reinicia tras un acceso exitoso | RU-M01-02 |
| RS-M01-04 | El sistema bloquea el acceso durante 15 minutos al alcanzar 5 intentos fallidos consecutivos | RU-M01-02 |
| RS-M01-05 | El sistema valida el token en cada solicitud a un endpoint protegido y devuelve 401 si es inválido o expiró | RU-M01-02 |
| RS-M01-06 | El sistema evalúa los permisos del rol en el servidor antes de ejecutar cualquier operación, con independencia de lo que muestre el cliente | RU-M01-03 |
| RS-M01-07 | El sistema aplica baja lógica a los usuarios: el campo `activo` pasa a falso y el registro persiste | RU-M01-04 |
| RS-M01-08 | El sistema registra en auditoría los eventos de inicio de sesión, cierre de sesión y cambio de rol | RU-M01-01 |
