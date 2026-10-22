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
        SRV->>SRV: Proponer la hora actual como hora del pesaje
        SRV->>VAL: validar(datos propuestos)
        VAL-->>SRV: Lista de inconsistencias
        SRV-->>API: Propuesta sin persistir RN-M03-02
        API-->>NG: 200 con campos confianza hora propuesta e inconsistencias
        NG-->>S: Resalta baja confianza e inconsistencias
    end

    S->>NG: Corrige datos ajusta la hora del pesaje y elige tipo de mineral
    opt Placa sin registrar en el catalogo
        NG-->>S: Formulario de alta del vehiculo en la misma pantalla
        S->>NG: Completa titularidad y capacidad
        NG->>API: POST /api/v1/catalogo/vehiculos/
        API-->>NG: 201 vehiculo creado sin tara
    end
    opt Tipo de mineral nuevo y rol Administrativo o Administrador
        NG->>API: POST /api/v1/catalogo/tipos-mineral/
        API-->>NG: 201 tipo de mineral creado y elegido
    end
    NG->>API: POST /api/v1/ingresos/
    API->>SRV: registrar_ingreso(datos confirmados, usuario)
    SRV->>DB: Leer vehiculo vigente con su tara RN-M03-08
    SRV->>VAL: validar(datos confirmados)

    alt Vehiculo dado de baja
        SRV-->>API: Rechazo RN-M03-08
        API-->>NG: 400 El vehiculo esta dado de baja
    else Regla bloqueante o advertencia sin justificar
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
    participant LOT as RepositorioLote M06
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
    else Sin cambios
        API-->>NG: 400 No hay cambios que guardar
    else Correccion admisible
        SRV->>SRV: Descartar campos no corregibles RS-M03-12
        opt Cambia el tipo de mineral y el ingreso esta en un lote
            SRV->>LOT: Leer la lista de minerales del lote
            LOT-->>SRV: Minerales del lote
        end
        SRV->>VAL: validar(datos corregidos)

        alt Mineral fuera de la lista del lote
            SRV-->>API: Rechazo RN-M03-25
            API-->>NG: 400 El mineral no esta en el lote
        else Regla bloqueante incumplida
            VAL-->>SRV: Rechazo con mensaje literal
            API-->>NG: 400 con el campo afectado
        else Datos coherentes
            SRV->>DB: BEGIN TRANSACTION
            alt Vehiculo con tara
                SRV->>DB: Actualizar campos y recalcular tara aplicada y neto
            else Vehiculo sin tara
                SRV->>DB: Actualizar campos y dejar el ingreso En proceso RN-M03-26
            end
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
    participant LOT as ServicioLote M06
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
        opt El lote del ingreso todavia reune ingresos
            SRV->>LOT: retirar_ingreso(lote, ingreso) RN-M03-27
        end
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

    S->>NG: Elige el vehiculo digita la tara y ajusta la fecha propuesta
    NG->>API: POST /api/v1/ingresos/destares/
    API->>SRV: registrar_destare(vehiculo, tara, fecha_hora, usuario)

    alt Vehiculo ya tiene tara
        SRV-->>API: Rechazo RN-M03-19
        API-->>NG: 409 El vehiculo ya tiene tara registrada
    else Fecha posterior al registro
        SRV-->>API: Rechazo RN-M03-23
        API-->>NG: 400 La fecha del destare no puede ser posterior a la fecha actual
    else Tara mayor o igual que el peso bruto de algun ingreso
        SRV->>VAL: validar(bruto y tara de cada ingreso)
        VAL-->>SRV: V2 incumplida
        API-->>NG: 400 La tara no puede ser mayor o igual que el peso bruto
    else Tara admisible
        SRV->>DB: BEGIN TRANSACTION
        SRV->>CAT: registrar_tara(vehiculo, tara, fecha_hora, usuario)
        CAT->>DB: Guardar tara fecha del destare y usuario
        SRV->>DB: Bloquear y leer los ingresos En proceso del vehiculo
        SRV->>DB: Aplicar tara y neto y pasarlos a Registrado
        SRV->>AUD: Registrar evento MODIFICAR con la tara y los ingresos afectados
        SRV->>DB: COMMIT
        API-->>NG: 200 Destare registrado con los ingresos completados
        NG-->>S: Lista de ingresos con su peso neto
    end
```

La tara se guarda en el vehículo a través del servicio de M02, que es el dueño de esa entidad; M03
no escribe directamente en la tabla de vehículos.

## S-M03-05 · Registro de un ingreso sin foto (HU-M03-01)

```mermaid
sequenceDiagram
    actor S as Supervisor de planta
    participant NG as Angular
    participant API as Django REST
    participant SRV as ServicioIngreso
    participant VAL as ValidadorConsistencia M05
    participant COR as GeneradorCodigo
    participant DB as PostgreSQL
    participant AUD as Auditoria M09

    S->>NG: Elige registrar sin foto
    NG->>API: POST /api/v1/ingresos/borradores/ sin imagen
    API->>SRV: iniciar_registro_sin_foto(usuario)
    SRV->>DB: Registrar hora de inicio del registro
    SRV-->>API: Borrador sin propuesta con la hora actual propuesta
    API-->>NG: 200 formulario manual
    S->>NG: Elige el motivo e ingresa placa fecha hora peso y mineral
    NG->>API: POST /api/v1/ingresos/ con el motivo
    API->>SRV: registrar_ingreso(datos, motivo, usuario)
    SRV->>VAL: validar(datos ingresados) RN-M03-22

    alt Motivo ausente o campo obligatorio vacio
        SRV-->>API: Error de validacion
        API-->>NG: 400 Debe completar los campos obligatorios
    else Regla bloqueante o advertencia sin justificar
        VAL-->>SRV: Rechazo con mensaje literal
        API-->>NG: 400 con el campo afectado
    else Datos coherentes
        SRV->>DB: BEGIN TRANSACTION
        SRV->>COR: obtener_siguiente_codigo()
        COR-->>SRV: Codigo asignado
        SRV->>DB: Persistir ingreso sin imagen marcado sin respaldo fotografico con su motivo
        SRV->>AUD: Registrar evento CREAR como registro manual sin foto
        SRV->>DB: COMMIT
        API-->>NG: 201 con el codigo y el estado
        NG-->>S: Ingreso registrado sin respaldo fotografico
    end
```

El registro sin foto no invoca a `ReconocedorTicket`: no hay imagen que leer y, por tanto, no se
guardan valores reconocidos. El cálculo del peso neto y el estado En proceso siguen las mismas reglas
que en S-M03-01.
