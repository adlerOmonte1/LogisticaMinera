# Diagrama de casos de uso — M04 Salidas y movimientos

```mermaid
flowchart LR
    ADV(("Administrativo"))
    ADM(("Administrador"))
    SUP(("Supervisor"))

    UC1["Registrar salida por venta"]
    UC2["Registrar traslado interno"]
    UC3["Registrar merma"]
    UC4["Consultar salidas"]
    UC5["Anular salida"]

    ADV --> UC1
    ADV --> UC2
    ADV --> UC3
    ADV --> UC4
    ADV --> UC5

    ADM --> UC1
    ADM --> UC2
    ADM --> UC3
    ADM --> UC4
    ADM --> UC5

    SUP --> UC4
```

## Casos de uso

| Caso | HU | Actores | Precondición |
|---|---|---|---|
| Registrar salida por venta | HU-M04-01 | Administrativo, Administrador | Cliente y producto vigentes en catálogo |
| Registrar traslado interno | HU-M04-02 | Administrativo, Administrador | Producto vigente |
| Registrar merma | HU-M04-02 | Administrativo, Administrador | Producto vigente; motivo obligatorio |
| Consultar salidas | HU-M04-03 | Los tres roles | Sesión activa |
| Anular salida | HU-M04-03 | Administrativo, Administrador | Salida en estado REGISTRADO |

El Supervisor aparece únicamente en la consulta, coherente con la matriz de permisos de `../requerimientos/funcionales.md`.
