# Diagramas de secuencia — M07 Captura sin conexión

## S-M07-01 · Registro de un ingreso sin conexión (HU-M07-02)

```mermaid
sequenceDiagram
    actor S as Supervisor
    participant NG as Angular
    participant CON as ServicioConectividad
    participant VAL as ValidadorLocal
    participant IDB as IndexedDB

    S->>NG: Abre formulario de ingreso
    NG->>CON: Consultar estado de conexion
    CON-->>NG: Sin conexion
    NG->>IDB: Leer catalogos locales
    IDB-->>NG: Productos y vehiculos
    NG-->>S: Formulario con indicador de sin conexion

    S->>NG: Completa datos y confirma
    NG->>VAL: Validar formato y reglas replicadas
    alt Validacion falla
        VAL-->>NG: Error
        NG-->>S: Mismo mensaje que en linea
    else Validacion correcta
        NG->>NG: Generar UUID local
        NG->>NG: Capturar hora local del dispositivo
        NG->>IDB: Guardar en cola de pendientes
        IDB-->>NG: Confirmacion
        NG-->>S: Ingreso guardado en el dispositivo. Se enviara al recuperar conexion
    end
```

## S-M07-02 · Sincronización automática al recuperar conexión (HU-M07-03)

```mermaid
sequenceDiagram
    participant CON as ServicioConectividad
    participant SYNC as ServicioSincronizacion
    participant IDB as IndexedDB
    participant API as Django REST
    participant SRV as ServicioSincronizacionServidor
    participant DB as PostgreSQL

    CON->>SYNC: Evento de reconexion
    SYNC->>IDB: Leer pendientes en orden de captura
    IDB-->>SYNC: Lote de ingresos
    SYNC->>API: POST /api/v1/sincronizacion/lote/
    API->>SRV: procesar_lote(ingresos, usuario)

    loop Por cada ingreso del lote
        SRV->>DB: Verificar uuid_local existente
        alt UUID ya sincronizado
            SRV-->>SRV: Devolver correlativo previo (idempotencia)
        else UUID nuevo
            SRV->>SRV: Validar reglas de M03 y RN-M07-02
            alt Validacion falla
                SRV-->>SRV: Marcar RECHAZADO con motivo
            else Validacion correcta
                SRV->>DB: Asignar correlativo
                SRV->>DB: hora_registro = hora_captura_local
                SRV->>DB: hora_sincronizacion = ahora
                SRV->>DB: Persistir y generar movimiento de stock
                SRV-->>SRV: Marcar ACEPTADO con correlativo
            end
        end
    end

    SRV-->>API: Resultados por uuid_local
    API-->>SYNC: 200 con los resultados
    SYNC->>IDB: Retirar aceptados, marcar rechazados con motivo
    SYNC->>SYNC: Notificar resultado al usuario
```

## S-M07-03 · Expiración de token durante la sincronización (HU-M07-04, CA04)

```mermaid
sequenceDiagram
    participant SYNC as ServicioSincronizacion
    participant IDB as IndexedDB
    participant INT as Interceptor JWT
    participant API as Django REST
    actor S as Supervisor

    SYNC->>IDB: Leer pendientes
    IDB-->>SYNC: Lote de ingresos
    SYNC->>INT: POST /api/v1/sincronizacion/lote/
    INT->>API: Solicitud con token expirado
    API-->>INT: 401 Sesion expirada
    INT->>INT: Intentar refresco de token
    alt Refresco exitoso
        INT->>API: Reintentar solicitud
        API-->>SYNC: 200 con resultados
    else Refresco fallido
        INT-->>SYNC: Sesion no recuperable
        SYNC->>IDB: Conservar la cola intacta
        SYNC-->>S: Solicitar reautenticacion, pendientes conservados
        S->>SYNC: Reautentica
        SYNC->>INT: Reintentar sincronizacion
    end
```

La rama de refresco fallido es la que RN-M07-07 protege. La cola **no** se descarta bajo ninguna circunstancia relacionada con la sesión.

## S-M07-04 · Rechazo por ticket duplicado (HU-M07-04, CA03)

```mermaid
sequenceDiagram
    participant SYNC as ServicioSincronizacion
    participant API as Django REST
    participant SRV as ServicioSincronizacionServidor
    participant DB as PostgreSQL
    actor S as Supervisor

    SYNC->>API: Enviar lote con ingreso de ticket ya registrado
    API->>SRV: procesar_lote()
    SRV->>DB: Buscar ticket entre ingresos no anulados
    DB-->>SRV: Ingreso existente
    SRV-->>API: RECHAZADO con codigo TICKET_DUPLICADO y correlativo existente
    API-->>SYNC: Resultado del elemento
    SYNC->>SYNC: Marcar elemento como rechazado, conservarlo en cola
    SYNC-->>S: Mostrar motivo y correlativo del ingreso previo
    S->>SYNC: Revisa: era duplicado real o error de transcripcion
    alt Error de transcripcion
        S->>SYNC: Corrige el numero de ticket
        SYNC->>API: Reintentar envio
    else Duplicado real
        S->>SYNC: Descarta manualmente el elemento
    end
```

El elemento nunca se descarta de forma automática (RN-M07-06). La decisión es siempre del usuario, porque solo él puede distinguir entre un duplicado real y un error de transcripción.
