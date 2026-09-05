# Diagrama de casos de uso — M07 Captura sin conexión

```mermaid
flowchart LR
    SUP(("Supervisor"))
    ADV(("Administrativo"))
    SYS[["Sistema<br/>(actor temporal:<br/>deteccion de red)"]]

    UC1["Registrar ingreso sin conexion"]
    UC2["Consultar pendientes locales"]
    UC3["Sincronizar manualmente"]
    UC4["Corregir ingreso rechazado"]
    UC5["Sincronizar automaticamente"]
    UC6["Consultar ingresos capturados offline"]

    SUP --> UC1
    SUP --> UC2
    SUP --> UC3
    SUP --> UC4
    SYS --> UC5
    ADV --> UC6
```

## Nota sobre el actor Sistema

La sincronización automática (UC5) no la inicia una persona sino la detección de un evento de red. Se representa como actor temporal porque el disparador es externo a la voluntad del usuario. Es la diferencia esencial con UC3, que sí es una acción deliberada.

## Casos de uso

| Caso | HU | Actor | Precondición |
|---|---|---|---|
| Registrar ingreso sin conexión | HU-M07-02 | Supervisor | Aplicación instalada; catálogos en local |
| Consultar pendientes locales | HU-M07-02, HU-M07-05 | Supervisor | — |
| Sincronizar manualmente | HU-M07-03 | Supervisor | Conexión disponible; cola no vacía |
| Corregir ingreso rechazado | HU-M07-04 | Supervisor | Elemento en estado rechazado |
| Sincronizar automáticamente | HU-M07-03 | Sistema | Recuperación de conectividad; cola no vacía |
| Consultar ingresos capturados offline | HU-M07-05 | Administrativo | Conexión disponible |
