# Diagramas de secuencia — M03 Registro de ingresos

## S-M03-01 · Registro de un ingreso con reconocimiento y validación (HU-M03-01)

```mermaid
sequenceDiagram
    actor S as Supervisor de planta
    participant NG as Angular
    participant API as Django REST
    participant SRV as ServicioIngreso
    participant REC as ReconocedorTicket M04
    participant VAL as ValidadorConsistencia M05
    participant COR as GeneradorCodigo
    participant IMG as Almacen de imagenes
    participant DB as PostgreSQL
    participant AUD as Auditoria M09

    S->>NG: Captura la foto del ticket
    NG->>NG: Reduce la imagen RNF-M03-04
    NG->>API: POST /api/v1/ingresos/borradores/
    API->>SRV: iniciar_registro(imagen, usuario)

    alt Formato o tamano no admitido
        SRV-->>API: Error de validacion RNF-M03-01
        API-->>NG: 400 La imagen debe estar en formato JPG o PNG
    else Imagen admitida
        SRV->>IMG: Guardar imagen
        SRV->>DB: Registrar hora de inicio del registro
        SRV->>REC: reconocer(imagen)
        REC-->>SRV: Seis campos con su confianza
        SRV->>VAL: validar(datos propuestos)
        VAL-->>SRV: Lista de inconsistencias
        SRV-->>API: Propuesta sin persistir RN-M03-02
        API-->>NG: 200 con campos confianza e inconsistencias
        NG-->>S: Resalta baja confianza e inconsistencias
    end

    S->>NG: Corrige datos y elige tipo de mineral
    NG->>API: POST /api/v1/ingresos/
    API->>SRV: registrar_ingreso(datos confirmados, usuario)
    SRV->>DB: Verificar vehiculo vigente RN-M03-08
    SRV->>VAL: validar(datos confirmados)

    alt Regla bloqueante o advertencia sin justificar
        VAL-->>SRV: Rechazo con mensaje literal
        SRV-->>API: Error de dominio RN-M03-05
        API-->>NG: 400 con el campo afectado
        NG-->>S: Mensaje junto al campo
    else Datos coherentes
        SRV->>DB: BEGIN TRANSACTION
        SRV->>COR: obtener_siguiente_codigo()
        COR-->>SRV: Codigo asignado RN-M03-09
        SRV->>DB: Persistir ingreso y hora de fin del registro
        SRV->>DB: Persistir valor reconocido y confirmado por campo
        SRV->>AUD: Registrar evento CREAR
        SRV->>DB: COMMIT
        SRV-->>API: Ingreso persistido
        API-->>NG: 201 con el codigo
        NG-->>S: Ingreso registrado con el codigo
    end
```

## S-M03-02 · Corrección de un ingreso registrado (HU-M03-02)

```mermaid
sequenceDiagram
    actor A as Administrativo
    participant NG as Angular
    participant API as Django REST
    participant SRV as ServicioIngreso
    participant VAL as ValidadorConsistencia M05
    participant DB as PostgreSQL
    participant AUD as Auditoria M09

    A->>NG: Modifica campos e indica el motivo
    NG->>API: PATCH /api/v1/ingresos/{id}/
    API->>SRV: corregir_ingreso(id, cambios, motivo, usuario)

    alt Rol no autorizado
        SRV-->>API: Acceso denegado
        API-->>NG: 403 Accion no autorizada
    else Ingreso anulado
        SRV-->>API: Estado invalido RN-M03-13
        API-->>NG: 400 No se puede corregir un ingreso anulado
    else Motivo ausente
        SRV-->>API: Error de validacion RN-M03-11
        API-->>NG: 400 Debe indicar el motivo de la correccion
    else Correccion admisible
        SRV->>SRV: Descartar campos no corregibles RS-M03-12
        SRV->>VAL: validar(datos corregidos)

        alt Regla bloqueante incumplida
            VAL-->>SRV: Rechazo con mensaje literal
            API-->>NG: 400 con el campo afectado
        else Datos coherentes
            SRV->>DB: BEGIN TRANSACTION
            SRV->>DB: Actualizar campos corregibles
            SRV->>AUD: Registrar evento MODIFICAR con valores anteriores
            SRV->>DB: COMMIT
            API-->>NG: 200 Ingreso actualizado
            NG-->>A: Confirmacion del cambio
        end
    end
```

## S-M03-03 · Anulación de un ingreso (HU-M03-03)

```mermaid
sequenceDiagram
    actor D as Administrador
    participant NG as Angular
    participant API as Django REST
    participant SRV as ServicioIngreso
    participant DB as PostgreSQL
    participant AUD as Auditoria M09

    D->>NG: Solicita anular e indica el motivo
    NG->>API: PATCH /api/v1/ingresos/{id}/anular/
    API->>SRV: anular_ingreso(id, motivo, usuario)

    alt Rol distinto de Administrador
        SRV-->>API: Acceso denegado
        API-->>NG: 403 Accion no autorizada
    else Ingreso ya anulado
        SRV-->>API: Estado invalido RN-M03-13
        API-->>NG: 409 El ingreso ya fue anulado
    else Motivo ausente
        SRV-->>API: Error de validacion
        API-->>NG: 400 Debe indicar el motivo de la anulacion
    else Anulacion admisible
        SRV->>DB: BEGIN TRANSACTION
        SRV->>DB: Marcar estado ANULADO con motivo y responsable
        SRV->>AUD: Registrar evento ANULAR
        SRV->>DB: COMMIT
        API-->>NG: 200 Ingreso anulado
        NG-->>D: Confirmacion de la anulacion
    end
```

La imagen del ticket no se elimina al anular: el ingreso permanece consultable con su respaldo
(RNF-M03-10).
