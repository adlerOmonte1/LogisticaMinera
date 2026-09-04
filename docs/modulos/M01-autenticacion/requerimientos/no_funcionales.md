# Requerimientos no funcionales — M01 Autenticación

> Modelo de calidad: ISO/IEC 25010:2023

| Código | Característica | Requerimiento | Verificación |
|---|---|---|---|
| RNF-M01-01 | Seguridad — confidencialidad | Las contraseñas se almacenan con PBKDF2 y sal única por usuario | Inspección de la base de datos: ningún campo contiene la contraseña legible |
| RNF-M01-02 | Seguridad — autenticidad | Todo endpoint distinto de login y refresh exige token válido | Prueba: solicitud sin token devuelve 401 |
| RNF-M01-03 | Seguridad — integridad | El token se firma con clave secreta del servidor y su alteración lo invalida | Prueba: token modificado devuelve 401 |
| RNF-M01-04 | Eficiencia de desempeño | El inicio de sesión responde en menos de 2 segundos con 20 usuarios concurrentes | Prueba de carga con JMeter (semana 8) |
| RNF-M01-05 | Usabilidad | El formulario de inicio de sesión es operable desde un teléfono en campo, con campos de al menos 44 px de alto | Inspección en dispositivo real |
| RNF-M01-06 | Fiabilidad | La expiración de sesión no provoca pérdida de datos no guardados en el formulario de ingreso | Prueba manual: expirar sesión con formulario a medio llenar |

**Nota sobre el indicador de la variable independiente:** RNF-M01-04 forma parte de la evidencia de *eficiencia de desempeño* bajo ISO/IEC 25010:2023, dimensión declarada en el capítulo II de la tesis. El protocolo de carga se documenta en `../../03-pruebas/`.
