# Diagramas de actividades — M03 Registro de ingresos

## A-M03-01 · Registro de un ingreso (RN-M03-01 a RN-M03-08)

```mermaid
flowchart TD
    Start([Supervisor abre formulario de ingreso]) --> C1[Cargar catalogos de producto y vehiculo]
    C1 --> L1[Transcribir datos del ticket de balanza]
    L1 --> CN[Sistema calcula peso neto en pantalla]
    CN --> S1[Usuario confirma el registro]
    S1 --> V1{Campos obligatorios completos?}
    V1 -->|No| E1[Senalar campos faltantes]
    E1 --> L1
    V1 -->|Si| V2{Tara menor que peso bruto?}
    V2 -->|No| E2[Rechazar: La tara no puede ser mayor o igual al peso bruto]
    E2 --> L1
    V2 -->|Si| V3{Fecha y hora de pesaje no futuras?}
    V3 -->|No| E3[Rechazar: No pueden ser posteriores a la hora actual]
    E3 --> L1
    V3 -->|Si| V4{Ticket ya registrado?}
    V4 -->|Si| E4[Rechazar: El ticket ya fue registrado en el ingreso C]
    E4 --> L1
    V4 -->|No| T1[Iniciar transaccion]
    T1 --> A1[Asignar correlativo del servidor]
    A1 --> A2[Asignar hora de registro del servidor]
    A2 --> A3[Recalcular peso neto en servidor]
    A3 --> P1[Persistir ingreso]
    P1 --> P2[Generar movimiento de stock de entrada]
    P2 --> P3[Registrar evento en auditoria]
    P3 --> T2[Confirmar transaccion]
    T2 --> M1[Mostrar: Ingreso registrado con el numero C]
    M1 --> Fin([Fin])
```

## A-M03-02 · Decisión entre editar y anular (RN-M03-09, RN-M03-10)

```mermaid
flowchart TD
    Start([Se detecta un error en un ingreso]) --> D1{El ingreso debio existir?}
    D1 -->|No, fue registrado por error| AN[Anular con motivo obligatorio]
    AN --> AN1[Revertir movimiento de stock]
    AN1 --> AN2[Registrar en auditoria]
    AN2 --> Fin([Fin])
    D1 -->|Si, pero tiene un dato mal| D2{Ingreso esta anulado?}
    D2 -->|Si| E1[Rechazar: No se puede editar un ingreso anulado]
    E1 --> Fin
    D2 -->|No| D3{El campo es editable?}
    D3 -->|No: correlativo u hora de registro| E2[Rechazar: El campo no es editable]
    E2 --> Fin
    D3 -->|Si| ED[Aplicar cambios]
    ED --> D4{Cambio afecta peso o producto?}
    D4 -->|Si| RC[Recalcular movimiento de stock]
    D4 -->|No| AU[Registrar valores anterior y nuevo en auditoria]
    RC --> AU
    AU --> Fin
```

Este diagrama documenta una distinción que el usuario debe entender antes de operar: **editar** corrige un dato de un evento que sí ocurrió; **anular** invalida un registro de un evento que no ocurrió o que se duplicó. Confundirlas produce un histórico inconsistente.

## A-M03-03 · Cálculo del indicador I1 sobre los datos del módulo

```mermaid
flowchart TD
    Start([Ingreso persistido]) --> D1[Leer fecha_pesaje y hora_pesaje]
    D1 --> D2[Leer hora_registro]
    D2 --> C1[Latencia = hora_registro menos fecha y hora de pesaje]
    C1 --> V1{Latencia negativa?}
    V1 -->|Si| AL[Anomalia: revisar RN-M03-02]
    AL --> Fin([Fin])
    V1 -->|No| R1[Registrar latencia en horas para el indicador I1]
    R1 --> Fin
```

Este cálculo no es una función del sistema sino un procedimiento de análisis sobre sus datos. Se documenta aquí porque explicita por qué los dos campos temporales deben permanecer separados y por qué RN-M03-02 existe.
