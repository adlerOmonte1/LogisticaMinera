# Diagrama de casos de uso — M02 Catálogo maestro

```mermaid
flowchart LR
    ADM(("Administrador"))
    ADV(("Administrativo"))
    SUP(("Supervisor de planta"))

    UC1["Gestionar vehiculos"]
    UC2["Gestionar tipos de mineral"]
    UC3["Gestionar transportistas"]
    UC4["Consultar catalogos"]
    UC5["Modificar tara de un vehiculo"]
    UC6["Dar de alta vehiculo desde el registro"]

    ADM --> UC1
    ADM --> UC2
    ADM --> UC3
    ADV --> UC1
    ADV --> UC2
    ADV --> UC3
    ADM --> UC5
    SUP --> UC4
    SUP --> UC6
    ADV --> UC6
```

## Casos de uso

| Caso | HU | Actores | Nota |
|---|---|---|---|
| Gestionar vehículos | HU-M02-01 | Administrador, Administrativo | La titularidad y la capacidad son obligatorias; el vehículo nace sin tara |
| Modificar tara de un vehículo | HU-M02-01 | Administrador | Con motivo obligatorio; los ingresos ya registrados conservan su tara |
| Dar de alta vehículo desde el registro | HU-M02-01, HU-M03-01 | Los tres roles | Mismas reglas que el alta desde el catálogo; es el primer viaje del vehículo |
| Gestionar tipos de mineral | HU-M02-02 | Administrador, Administrativo | Catálogo único, usado al registrar y al consolidar |
| Gestionar transportistas | HU-M02-03 | Administrador, Administrativo | Del que depende un vehículo con titularidad externa |
| Consultar catálogos | HU-M02-01 a 03 | Los tres roles | El Supervisor de planta solo consulta, para seleccionar en el registro de ingresos |

Los actores se definen en `../../M01-autenticacion/diagramas/caso_uso.md` y no se redefinen aquí.
