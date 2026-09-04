# Diagrama de casos de uso — M01 Autenticación

```mermaid
flowchart LR
    ADM(("Administrador"))
    ADV(("Administrativo"))
    SUP(("Supervisor"))

    UC1["Iniciar sesion"]
    UC2["Cerrar sesion"]
    UC3["Cambiar contrasena propia"]
    UC4["Gestionar usuarios"]
    UC5["Asignar rol"]

    ADM --> UC1
    ADM --> UC2
    ADM --> UC3
    ADM --> UC4
    ADM --> UC5

    ADV --> UC1
    ADV --> UC2
    ADV --> UC3

    SUP --> UC1
    SUP --> UC2
    SUP --> UC3
```

## Actores

| Actor | Descripción |
|---|---|
| Administrador | Personal con responsabilidad sobre la configuración del sistema. Acceso total |
| Administrativo | Personal de oficina. Registra ingresos y salidas, consulta y exporta |
| Supervisor | Personal de planta. Registra ingresos y consulta existencias, típicamente desde teléfono |

Los tres actores son transversales al sistema y se referencian desde los demás módulos sin volver a definirse.

## Casos de uso

| Caso | HU | Actores |
|---|---|---|
| Iniciar sesión | HU-M01-01 | Los tres |
| Cerrar sesión | HU-M01-02 | Los tres |
| Cambiar contraseña propia | HU-M01-05 | Los tres |
| Gestionar usuarios | HU-M01-03 | Administrador |
| Asignar rol | HU-M01-04 | Administrador |
