# Diagrama de casos de uso — M02 Catálogo maestro

```mermaid
flowchart LR
    ADM(("Administrador"))
    ADV(("Administrativo"))
    SUP(("Supervisor"))

    UC1["Gestionar productos"]
    UC2["Gestionar vehiculos"]
    UC3["Gestionar transportistas"]
    UC4["Gestionar clientes"]
    UC5["Consultar catalogos"]

    ADM --> UC1
    ADM --> UC2
    ADM --> UC3
    ADM --> UC4
    ADV --> UC1
    ADV --> UC2
    ADV --> UC3
    ADV --> UC4
    SUP --> UC5
```

## Casos de uso

| Caso | HU | Actores | Nota |
|---|---|---|---|
| Gestionar productos | HU-M02-01 | Administrador, Administrativo | Incluye alta, edición y baja lógica |
| Gestionar vehículos | HU-M02-02 | Administrador, Administrativo | La titularidad es obligatoria |
| Gestionar transportistas | HU-M02-03 | Administrador, Administrativo | |
| Gestionar clientes | HU-M02-04 | Administrador, Administrativo | |
| Consultar catálogos | HU-M02-01 a 04 | Los tres roles | El Supervisor solo consulta, para poder seleccionar en el formulario de ingreso |

Los actores se definen en `../../M01-autenticacion/diagramas/caso_uso.md` y no se redefinen aquí.
