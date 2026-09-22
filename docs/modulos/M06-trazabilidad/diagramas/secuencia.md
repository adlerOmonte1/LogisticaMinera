# Diagramas de secuencia — M06 Trazabilidad del proceso

## S-M06-01 · Composición y cierre de un lote (HU-M06-01)

```mermaid
sequenceDiagram
    actor A as Administrativo
    participant NG as Angular
    participant API as Django REST
    participant SRV as ServicioLote
    participant ING as RepositorioIngreso M03
    participant DB as PostgreSQL
    participant AUD as Auditoria M09

    A->>NG: Abre un lote para un tipo de mineral
    NG->>API: POST /api/v1/lotes/
    API->>SRV: abrir_lote(tipo_mineral, fecha, usuario)
    SRV->>DB: Persistir lote abierto con su codigo
    SRV->>AUD: Registrar evento CREAR
    API-->>NG: 201 Lote abierto

    A->>NG: Selecciona ingresos para el lote
    NG->>API: POST /api/v1/lotes/{id}/ingresos/
    API->>SRV: asignar_ingresos(lote, ingresos)
    SRV->>ING: Leer tipo de mineral y estado de cada ingreso
    ING-->>SRV: Datos de los ingresos

    alt Tipo de mineral distinto
        SRV-->>API: Rechazo RN-M06-02
        API-->>NG: 400 El ingreso corresponde a otro tipo de mineral
    else Ingreso anulado
        SRV-->>API: Rechazo RN-M06-03
        API-->>NG: 400 No se puede asignar un ingreso anulado
    else Ingreso en lote cerrado
        SRV-->>API: Rechazo RN-M06-04
        API-->>NG: 409 El lote ya fue cerrado
    else Asignacion admisible
        SRV->>DB: Actualizar el lote de cada ingreso
        SRV->>DB: Recalcular total de ingresos y toneladas
        API-->>NG: 200 con la composicion actualizada
    end

    A->>NG: Cierra el lote
    NG->>API: PATCH /api/v1/lotes/{id}/cerrar/
    API->>SRV: cerrar_lote(lote, usuario)

    alt Lote sin ingresos
        SRV-->>API: Rechazo RN-M06-10
        API-->>NG: 400 El lote no tiene ingresos asignados
    else Lote con ingresos
        SRV->>DB: BEGIN TRANSACTION
        SRV->>DB: Marcar cerrado con fecha de cierre
        SRV->>AUD: Registrar evento MODIFICAR
        SRV->>DB: COMMIT
        API-->>NG: 200 Lote cerrado
    end
```

## S-M06-02 · Registro del paso por una etapa (HU-M06-02)

```mermaid
sequenceDiagram
    actor S as Supervisor de planta
    participant NG as Angular
    participant API as Django REST
    participant SRV as ServicioLote
    participant DB as PostgreSQL
    participant AUD as Auditoria M09

    S->>NG: Selecciona el lote y la etapa a registrar
    NG->>API: POST /api/v1/lotes/{id}/etapas/
    API->>SRV: registrar_etapa(lote, etapa, fecha, usuario)

    alt Lote abierto
        SRV-->>API: Rechazo RN-M06-05
        API-->>NG: 400 El lote debe cerrarse antes de registrar etapas
    else Etapa anterior sin registrar
        SRV-->>API: Rechazo RN-M06-06
        API-->>NG: 400 El lote debe pasar primero por la etapa anterior
    else Etapa ya registrada
        SRV-->>API: Rechazo RN-M06-07
        API-->>NG: 409 La etapa ya fue registrada para el lote
    else Fecha invalida
        SRV-->>API: Rechazo RN-M06-08
        API-->>NG: 400 con el mensaje de la fecha
    else Registro admisible
        SRV->>DB: BEGIN TRANSACTION
        SRV->>DB: Persistir paso con fecha y usuario responsable
        SRV->>AUD: Registrar evento CREAR
        SRV->>DB: COMMIT
        API-->>NG: 201 Etapa registrada
        NG-->>S: Muestra el recorrido actualizado
    end
```

## S-M06-03 · Consulta de la trazabilidad de un ingreso (HU-M06-03)

```mermaid
sequenceDiagram
    actor A as Administrativo
    participant NG as Angular
    participant API as Django REST
    participant REP as RepositorioTrazabilidad
    participant DB as PostgreSQL

    A->>NG: Abre la trazabilidad de un ingreso
    NG->>API: GET /api/v1/ingresos/{id}/trazabilidad/
    API->>REP: obtener_recorrido(ingreso)
    REP->>DB: Leer lote del ingreso y sus pasos por etapa

    alt Ingreso sin lote
        DB-->>REP: Sin lote asignado
        REP-->>API: Cuatro etapas no recorridas RN-M06-11
        API-->>NG: 200 indicando que el ingreso aun no tiene lote
    else Ingreso con lote
        DB-->>REP: Lote y pasos registrados
        REP-->>API: Cuatro etapas con fecha y responsable
        API-->>NG: 200 con el recorrido y las etapas completadas
        NG-->>A: Secuencia de cuatro etapas con su estado
    end
```
