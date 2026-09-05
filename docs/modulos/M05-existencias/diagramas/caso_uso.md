# Diagrama de casos de uso — M05 Existencias

```mermaid
flowchart LR
    ADM(("Administrador"))
    ADV(("Administrativo"))
    SUP(("Supervisor"))

    UC1["Consultar existencias"]
    UC2["Consultar kardex"]
    UC3["Registrar ajuste de inventario"]
    UC4["Listar ajustes"]

    ADM --> UC1
    ADM --> UC2
    ADM --> UC3
    ADM --> UC4
    ADV --> UC1
    ADV --> UC2
    ADV --> UC4
    SUP --> UC1
```

## Casos de uso

| Caso | HU | Actores | Nota |
|---|---|---|---|
| Consultar existencias | HU-M05-01 | Los tres roles | Vista predeterminada del Administrativo |
| Consultar kardex | HU-M05-02 | Administrador, Administrativo | Detalle cronológico con saldo resultante |
| Registrar ajuste | HU-M05-03 | Administrador | Exclusivo: es la evidencia del indicador I4 |
| Listar ajustes | HU-M05-03 | Administrador, Administrativo | Histórico de desviaciones |

**No existe** un caso de uso "modificar existencias". Su ausencia es deliberada y corresponde a RN-M05-02.
