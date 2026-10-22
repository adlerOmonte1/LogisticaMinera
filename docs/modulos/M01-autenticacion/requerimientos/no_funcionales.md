# Requerimientos no funcionales — M01 Autenticación y roles

| Código | Característica ISO/IEC 25010:2023 | Requerimiento | Verificación |
|---|---|---|---|
| RNF-M01-01 | Seguridad — confidencialidad | Las contraseñas se almacenan con PBKDF2 y sal única por usuario | Inspección de la base de datos: ningún campo contiene la contraseña legible |
| RNF-M01-02 | Seguridad — autenticidad | Todo endpoint distinto de login y refresh exige token válido | Prueba automatizada: solicitud sin token devuelve 401 |
| RNF-M01-03 | Seguridad — integridad | El token se firma con clave secreta del servidor y su alteración lo invalida | Prueba automatizada: token modificado devuelve 401 |
| RNF-M01-04 | Eficiencia de desempeño — comportamiento temporal | El inicio de sesión responde en menos de 2 segundos con 20 usuarios concurrentes | Prueba de carga con datos sintéticos |
| RNF-M01-05 | Usabilidad — accesibilidad | El formulario de inicio de sesión es operable desde un teléfono en campo, con campos de al menos 44 px de alto | Inspección en dispositivo real |
| RNF-M01-06 | Fiabilidad — tolerancia a fallos | La expiración de sesión no provoca pérdida de datos no guardados en un formulario a medio llenar | Prueba manual: expirar sesión con el formulario de registro a medio llenar |

## Nota sobre RNF-M01-04

La carga esperada en planta es baja —el personal administrativo y algunos supervisores— pero el
umbral se mantiene como referencia técnica para la ventana de estabilización previa al uso en
producción.
