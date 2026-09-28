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
        REC-->>SRV: Placa fecha y peso bruto con su confianza
        SRV->>VAL: validar(datos propuestos)
        VAL-->>SRV: Lista de inconsistencias
        SRV-->>API: Propuesta sin persistir RN-M03-02
        API-->>NG: 200 con campos confianza e inconsistencias
        NG-->>S: Resalta baja confianza e inconsistencias
    end

    S->>NG: Corrige datos digita la hora del pesaje y elige tipo de mineral
    opt Placa sin registrar en el catalogo
        NG-->>S: Formulario de alta del vehiculo en la misma pantalla
        S->>NG: Completa titularidad y capacidad
        NG->>API: POST /api/v1/catalogo/vehiculos/
        API-->>NG: 201 vehiculo creado sin tara
    end
    NG->>API: POST /api/v1/ingresos/
    API->>SRV: registrar_ingreso(datos confirmados, usuario)
    SRV->>DB: Leer vehiculo vigente con su tara RN-M03-08
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
        alt Vehiculo con tara
            SRV->>SRV: Calcular peso neto como bruto menos tara RN-M03-04
            SRV->>DB: Persistir ingreso Registrado con tara aplicada y hora de fin
        else Vehiculo sin tara
            SRV->>DB: Persistir ingreso En proceso sin neto y hora de fin RN-M03-17
        end
        SRV->>DB: Persistir valor reconocido y confirmado por campo
        SRV->>AUD: Registrar evento CREAR
        SRV->>DB: COMMIT
        SRV-->>API: Ingreso persistido
        API-->>NG: 201 con el codigo y el estado
        NG-->>S: Ingreso registrado o pendiente de destare
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

## S-M03-04 · Registro del destare de un vehículo en su primer viaje (HU-M03-04)

```mermaid
sequenceDiagram
    actor S as Supervisor de planta
    participant NG as Angular
    participant API as Django REST
    participant SRV as ServicioIngreso
    participant CAT as ServicioCatalogo M02
    participant VAL as ValidadorConsistencia M05
    participant DB as PostgreSQL
    participant AUD as Auditoria M09

    S->>NG: Elige el ingreso En proceso y digita la tara
    NG->>API: POST /api/v1/ingresos/{id}/destare/
    API->>SRV: registrar_destare(ingreso, tara, usuario)

    alt Vehiculo ya tiene tara
        SRV-->>API: Rechazo RN-M03-19
        API-->>NG: 409 El vehiculo ya tiene tara registrada
    else Tara mayor o igual que el peso bruto
        SRV->>VAL: validar(bruto y tara)
        VAL-->>SRV: V2 incumplida
        API-->>NG: 400 La tara no puede ser mayor o igual que el peso bruto
    else Tara admisible
        SRV->>DB: BEGIN TRANSACTION
        SRV->>CAT: registrar_tara(vehiculo, tara, usuario)
        CAT->>DB: Guardar tara fecha de destare y usuario
        SRV->>DB: Calcular neto de los ingresos En proceso del vehiculo
        SRV->>DB: Pasar esos ingresos a Registrado
        SRV->>AUD: Registrar evento MODIFICAR con la tara y los ingresos afectados
        SRV->>DB: COMMIT
        API-->>NG: 200 Destare registrado con el peso neto
        NG-->>S: Peso neto del ingreso
    end
```

La tara se guarda en el vehículo a través del servicio de M02, que es el dueño de esa entidad; M03
no escribe directamente en la tabla de vehículos.
