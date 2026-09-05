# Diagramas de secuencia — M03 Registro de ingresos

## S-M03-01 · Registro de un ingreso en línea (HU-M03-01)

```mermaid
sequenceDiagram
    actor S as Supervisor
    participant NG as Angular
    participant API as Django REST
    participant SRV as ServicioIngreso
    participant DOM as Modelo Ingreso
    participant COR as GeneradorCorrelativo
    participant STK as ServicioStock M05
    participant DB as PostgreSQL
    participant AUD as Auditoria M08

    S->>NG: Completa datos del ticket de balanza
    NG->>NG: Calcula peso neto para mostrar
    NG->>API: POST /api/v1/ingresos/
    API->>SRV: registrar_ingreso(datos, usuario)
    SRV->>DOM: Validar RN-M03-02, 03, 05, 07

    alt Validacion falla
        DOM-->>SRV: Error de dominio
        SRV-->>API: Error de validacion
        API-->>NG: 400 con detalle del campo
        NG-->>S: Mensaje en el campo correspondiente
    else Validacion correcta
        SRV->>DB: BEGIN TRANSACTION
        SRV->>COR: obtener_siguiente_correlativo()
        COR->>DB: Bloqueo y siguiente valor
        DB-->>COR: Correlativo
        COR-->>SRV: Correlativo asignado
        SRV->>DOM: Calcular peso neto en servidor
        SRV->>DB: Persistir ingreso con hora_registro del servidor
        SRV->>STK: generar_movimiento_entrada(ingreso)
        STK->>DB: Insertar movimiento y saldo resultante
        SRV->>AUD: Registrar evento CREAR
        SRV->>DB: COMMIT
        SRV-->>API: Ingreso creado
        API-->>NG: 201 con correlativo
        NG-->>S: Ingreso registrado con el numero {correlativo}
    end
```

## S-M03-02 · Detección de ticket duplicado (HU-M03-01, CA04)

```mermaid
sequenceDiagram
    actor S as Supervisor
    participant NG as Angular
    participant API as Django REST
    participant SRV as ServicioIngreso
    participant DB as PostgreSQL

    S->>NG: Ingresa numero de ticket ya registrado
    NG->>API: POST /api/v1/ingresos/
    API->>SRV: registrar_ingreso(datos, usuario)
    SRV->>DB: Buscar ticket entre ingresos no anulados
    DB-->>SRV: Ingreso existente con ese ticket
    SRV-->>API: Error de duplicidad con correlativo existente
    API-->>NG: 409 El ticket numero N ya fue registrado en el ingreso C
    NG-->>S: Mensaje con el correlativo del ingreso previo
```

El mensaje incluye el correlativo del ingreso previo deliberadamente: permite al supervisor verificar de inmediato si se trata de un registro duplicado real o de un error de transcripción del número de ticket.

## S-M03-03 · Anulación de un ingreso (HU-M03-07)

```mermaid
sequenceDiagram
    actor A as Administrativo
    participant NG as Angular
    participant API as Django REST
    participant SRV as ServicioIngreso
    participant STK as ServicioStock M05
    participant DB as PostgreSQL
    participant AUD as Auditoria M08

    A->>NG: Solicita anular e indica motivo
    NG->>API: POST /api/v1/ingresos/{id}/anular/
    API->>SRV: anular_ingreso(id, motivo, usuario)
    SRV->>DB: Consultar estado actual

    alt Ingreso ya anulado
        SRV-->>API: Error de estado
        API-->>NG: 409 El ingreso ya se encuentra anulado
    else Motivo vacio
        SRV-->>API: Error de validacion
        API-->>NG: 400 Debe indicar el motivo de la anulacion
    else Anulacion procedente
        SRV->>DB: BEGIN TRANSACTION
        SRV->>DB: estado = ANULADO, motivo, responsable
        SRV->>STK: revertir_movimiento(ingreso)
        STK->>DB: Movimiento de reversion y nuevo saldo
        SRV->>AUD: Registrar evento ANULAR con motivo
        SRV->>DB: COMMIT
        SRV-->>API: Anulado
        API-->>NG: 200 Ingreso anulado
    end
    NG-->>A: Mensaje correspondiente
```

## S-M03-04 · Edición con recálculo de stock (HU-M03-06, CA03)

```mermaid
sequenceDiagram
    actor A as Administrativo
    participant API as Django REST
    participant SRV as ServicioIngreso
    participant STK as ServicioStock M05
    participant DB as PostgreSQL
    participant AUD as Auditoria M08

    A->>API: PATCH /api/v1/ingresos/{id}/
    API->>SRV: editar_ingreso(id, cambios, usuario)
    SRV->>SRV: Verificar que no se editen correlativo ni hora_registro

    alt Intento de editar campo protegido
        SRV-->>API: Error de campo no editable
        API-->>A: 400 El campo indicado no es editable
    else Cambios permitidos
        SRV->>DB: Leer valores anteriores
        SRV->>DB: BEGIN TRANSACTION
        SRV->>DB: Aplicar cambios
        alt Cambio en peso o producto
            SRV->>STK: recalcular_movimiento(ingreso)
            STK->>DB: Actualizar movimiento y saldos posteriores
        end
        SRV->>AUD: Registrar MODIFICAR con valores anterior y nuevo
        SRV->>DB: COMMIT
        API-->>A: 200 Ingreso actualizado
    end
```
