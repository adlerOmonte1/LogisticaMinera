# Diagramas de secuencia — M04 Salidas y movimientos

## S-M04-01 · Registro de salida con advertencia de stock (HU-M04-01, CA02)

```mermaid
sequenceDiagram
    actor A as Administrativo
    participant NG as Angular
    participant API as Django REST
    participant SRV as ServicioSalida
    participant STK as ServicioStock M05
    participant DB as PostgreSQL
    participant AUD as Auditoria M08

    A->>NG: Selecciona producto y cantidad
    NG->>API: GET /api/v1/existencias/?producto=X
    API->>STK: obtener_saldo(producto)
    STK-->>API: Saldo vigente
    API-->>NG: Saldo disponible

    alt Cantidad supera el saldo
        NG-->>A: La cantidad supera el stock disponible. Desea continuar?
        A->>NG: Confirma continuar
    end

    NG->>API: POST /api/v1/salidas/
    API->>SRV: registrar_salida(datos, usuario)
    SRV->>SRV: Validar RN-M04-01 a RN-M04-04

    alt Validacion falla
        SRV-->>API: Error de dominio
        API-->>NG: 400 con detalle del campo
    else Validacion correcta
        SRV->>DB: BEGIN TRANSACTION
        SRV->>DB: Asignar correlativo y persistir salida
        SRV->>STK: generar_movimiento_salida(salida)
        STK->>DB: Insertar movimiento y saldo resultante
        SRV->>AUD: Registrar evento CREAR
        SRV->>DB: COMMIT
        API-->>NG: 201 Salida registrada
    end
    NG-->>A: Mensaje correspondiente
```

## S-M04-02 · Anulación con reversión de stock (HU-M04-03, CA02)

```mermaid
sequenceDiagram
    actor A as Administrativo
    participant API as Django REST
    participant SRV as ServicioSalida
    participant STK as ServicioStock M05
    participant DB as PostgreSQL
    participant AUD as Auditoria M08

    A->>API: POST /api/v1/salidas/{id}/anular/ con motivo
    API->>SRV: anular_salida(id, motivo, usuario)
    SRV->>DB: Consultar estado actual

    alt Ya anulada
        SRV-->>API: Error de estado
        API-->>A: 409 La salida ya se encuentra anulada
    else Motivo vacio
        SRV-->>API: Error de validacion
        API-->>A: 400 Debe indicar el motivo de la anulacion
    else Procedente
        SRV->>DB: BEGIN TRANSACTION
        SRV->>DB: estado = ANULADO con motivo y responsable
        SRV->>STK: revertir_movimiento(salida)
        STK->>DB: Movimiento de reversion y nuevo saldo
        SRV->>AUD: Registrar evento ANULAR
        SRV->>DB: COMMIT
        API-->>A: 200 Salida anulada
    end
```
