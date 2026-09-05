# Diagramas de actividades — M04 Salidas y movimientos

## A-M04-01 · Registro de salida según tipo de movimiento (RN-M04-02 a RN-M04-06)

```mermaid
flowchart TD
    Start([Usuario abre formulario de salida]) --> S1[Selecciona tipo de movimiento]
    S1 --> D1{Tipo?}
    D1 -->|VENTA| V1{Cliente indicado?}
    V1 -->|No| E1[Rechazar: Debe indicar el cliente]
    E1 --> S1
    V1 -->|Si| C1[Continuar]
    D1 -->|TRASLADO_INTERNO| C1
    D1 -->|MERMA| V2{Motivo indicado?}
    V2 -->|No| E2[Rechazar: Debe indicar el motivo de la merma]
    E2 --> S1
    V2 -->|Si| C1
    C1 --> V3{Cantidad mayor que cero?}
    V3 -->|No| E3[Rechazar: La cantidad debe ser mayor que cero]
    E3 --> S1
    V3 -->|Si| Q1[Consultar saldo vigente del producto]
    Q1 --> V4{Cantidad supera el saldo?}
    V4 -->|Si| W1[Advertir y solicitar confirmacion]
    W1 --> D2{Usuario confirma?}
    D2 -->|No| Fin([Fin sin registrar])
    D2 -->|Si| T1[Iniciar transaccion]
    V4 -->|No| T1
    T1 --> P1[Asignar correlativo y persistir salida]
    P1 --> P2[Generar movimiento de stock de salida]
    P2 --> P3[Registrar evento en auditoria]
    P3 --> T2[Confirmar transaccion]
    T2 --> M1[Confirmar: Salida registrada]
    M1 --> Fin
```

## A-M04-02 · Composición del indicador I4

```mermaid
flowchart TD
    Start([Corte de inventario del periodo]) --> A1[Stock estimado = ingresos menos salidas registradas]
    A1 --> A2[Stock declarado = medicion fisica en planta]
    A2 --> C1[Desviacion = stock declarado menos stock estimado]
    C1 --> C2[Desviacion porcentual sobre stock estimado]
    C2 --> D1{Existen mermas registradas en el periodo?}
    D1 -->|Si| I1[Desviacion parcialmente explicada por mermas]
    D1 -->|No| I2[Desviacion sin explicacion registrada]
    I1 --> Fin([Registrar indicador I4 con su interpretacion])
    I2 --> Fin
```

Este diagrama documenta por qué el tipo MERMA existe como categoría separada: sin él, toda desviación sería indistinguible de un error de registro. La rama I1 solo puede recorrerse si el criterio de merma por humedad está definido, pendiente registrado en `../requisitos/reglas_negocio.md`.
