# Requerimientos de usuario — M01 Autenticación y roles

| Código | Requerimiento |
|---|---|
| RU-M01-01 | Necesito entrar al sistema con mi propio usuario, para que quede claro quién registró cada cosa |
| RU-M01-02 | No quiero que cualquiera pueda entrar desde la computadora de la planta si me olvido de salir |
| RU-M01-03 | El supervisor no debería poder crear usuarios ni tocar la consolidación de producción |
| RU-M01-04 | Si alguien deja la empresa, quiero desactivarlo sin perder lo que ya registró |
| RU-M01-05 | Quiero poder cambiar mi contraseña cuando quiera, sin pedírselo a nadie |

## Contexto del diagnóstico

| Requerimiento | Situación que resuelve |
|---|---|
| RU-M01-01 | Sin sesión propia por persona, un ingreso o una corrección no tendrían un responsable claro |
| RU-M01-02 | La planta comparte equipos entre turnos; una sesión que no expira queda abierta para cualquiera |
| RU-M01-03, RU-M01-04 | Sin roles diferenciados, cualquier persona podría alcanzar operaciones que no le corresponden |
