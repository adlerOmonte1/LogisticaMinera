# Diagramas de secuencia — M09 Auditoría

## S-M09-01 · Registro de un evento dentro de otra operación (HU-M09-01)

```mermaid
sequenceDiagram
    participant SRV as ServicioIngreso M03
    participant AUD as ServicioAuditoria M09
    participant DB as PostgreSQL

    Note over SRV,DB: Dentro de la transaccion de registro del ingreso
    SRV->>DB: Persistir el ingreso
    SRV->>AUD: registrar(usuario, CREAR, INGRESO, id, valores nuevos)
    AUD->>DB: Persistir evento con fecha y hora

    alt El registro del evento falla
        DB--xAUD: Error de escritura
        AUD-->>SRV: Excepcion propagada RNF-M09-03
        SRV->>DB: ROLLBACK de toda la transaccion
    else Evento registrado
        AUD-->>SRV: Confirmacion
        SRV->>DB: COMMIT
    end
```

El servicio de auditoría no abre su propia transacción: participa de la del módulo que lo invoca. Si
el evento no puede escribirse, toda la operación se revierte (RN-M09-01, RNF-M09-03).

## S-M09-02 · Registro de un acceso rechazado (HU-M09-01)

```mermaid
sequenceDiagram
    actor S as Supervisor de planta
    participant NG as Angular
    participant API as Django REST
    participant AUD as ServicioAuditoria M09
    participant DB as PostgreSQL

    S->>NG: Intenta anular un ingreso
    NG->>API: PATCH /api/v1/ingresos/{id}/anular/
    API->>API: Verificar permiso del rol

    alt Rol no autorizado
        API->>AUD: registrar(usuario, ACCESO_RECHAZADO, INGRESO, id)
        AUD->>DB: Persistir evento
        API-->>NG: 403 Accion no autorizada
    else Rol autorizado
        Note over API: Continua con la operacion normal
    end
```

El intento rechazado se registra con el mismo rigor que uno completado: RN-M09-04 exige que el
control de acceso pueda demostrarse, no solo asumirse.

## S-M09-03 · Consulta del historial de una entidad (HU-M09-02)

```mermaid
sequenceDiagram
    actor D as Administrador
    participant NG as Angular
    participant API as Django REST
    participant REP as RepositorioAuditoria
    participant DB as PostgreSQL

    D->>NG: Indica entidad e identificador
    NG->>API: GET /api/v1/auditoria/{entidad}/{id}/
    API->>REP: historial(entidad, id)
    REP->>DB: Leer eventos por indice de entidad e identificador
    DB-->>REP: Eventos ordenados cronologicamente

    alt Sin eventos
        REP-->>API: Lista vacia
        API-->>NG: 200 Sin eventos registrados para este registro
    else Con eventos
        REP-->>API: Eventos con autor accion y valores del cambio
        API-->>NG: 200 con el historial completo
        NG-->>D: Linea de tiempo del registro
    end
```
