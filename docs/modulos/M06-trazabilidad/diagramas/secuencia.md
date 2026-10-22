# Diagramas de secuencia — M06 Trazabilidad del proceso

## S-M06-01 · Composición de un lote e inicio del recorrido (HU-M06-01)

```mermaid
sequenceDiagram
    actor A as Administrativo
    participant NG as Angular
    participant API as Django REST
    participant SRV as ServicioLote
    participant ING as RepositorioIngreso M03
    participant DB as PostgreSQL
    participant AUD as Auditoria M09

    A->>NG: Abre un lote con nombre tipo de mineral y fecha
    NG->>API: POST /api/v1/lotes/
    API->>SRV: abrir_lote(nombre, tipo_mineral, fecha, usuario)

    alt Nombre repetido
        SRV-->>API: Rechazo RN-M06-14
        API-->>NG: 400 Ya existe un lote con ese nombre
    else Fecha posterior a hoy
        API-->>NG: 400 La fecha de apertura no puede ser posterior a hoy
    else Datos validos
        SRV->>DB: Persistir lote Abierto con su codigo
        SRV->>AUD: Registrar evento CREAR
        API-->>NG: 201 Lote abierto
    end

    A->>NG: Selecciona ingresos para el lote
    NG->>API: POST /api/v1/lotes/{id}/ingresos/
    API->>SRV: asignar_ingresos(lote, ingresos)
    SRV->>ING: Leer tipo de mineral y estado de cada ingreso
    ING-->>SRV: Datos de los ingresos

    alt Tipo de mineral distinto
        SRV-->>API: Rechazo RN-M06-02
        API-->>NG: 400 El ingreso corresponde a otro tipo de mineral
    else Ingreso anulado o En proceso
        SRV-->>API: Rechazo RN-M06-03 o RN-M06-13
        API-->>NG: 400 con el mensaje de la regla
    else Lote Cerrado
        SRV-->>API: Rechazo RN-M06-21
        API-->>NG: 409 El lote ya fue cerrado
    else Asignacion admisible
        alt Lote En recorrido
            SRV->>DB: Vincular como ingresos tardios con o sin secado propio
        else Lote Abierto
            SRV->>DB: Vincular los ingresos al lote
        end
        SRV->>AUD: Registrar evento MODIFICAR
        API-->>NG: 200 con la composicion y el total de toneladas
    end

    A->>NG: Inicia el recorrido
    NG->>API: PATCH /api/v1/lotes/{id}/iniciar-recorrido/
    API->>SRV: iniciar_recorrido(lote, usuario)

    alt Lote sin ingresos
        SRV-->>API: Rechazo RN-M06-10
        API-->>NG: 400 El lote no tiene ingresos asignados
    else Lote con ingresos
        SRV->>DB: BEGIN TRANSACTION
        SRV->>DB: Pasar a En recorrido con fecha de inicio
        SRV->>AUD: Registrar evento MODIFICAR
        SRV->>DB: COMMIT
        API-->>NG: 200 Recorrido del lote iniciado
    end
```

## S-M06-02 · Registro del paso por una etapa de la ruta (HU-M06-02)

```mermaid
sequenceDiagram
    actor S as Supervisor de planta
    participant NG as Angular
    participant API as Django REST
    participant SRV as ServicioLote
    participant DB as PostgreSQL
    participant AUD as Auditoria M09

    S->>NG: Elige el lote o la parte y registra la etapa que corresponde
    NG->>API: POST /api/v1/lotes/{id}/etapas/
    API->>SRV: registrar_etapa(lote, parte, ruta, fecha, horas, bigbags, usuario)

    alt Lote Abierto o Cerrado
        SRV-->>API: Rechazo RN-M06-05 o RN-M06-21
        API-->>NG: 400 con el mensaje del estado del lote
    else Secado registrado y ruta sin elegir
        SRV-->>API: Rechazo RN-M06-15
        API-->>NG: 400 Elija que etapa sigue despues del secado
    else Etapa fuera de orden o ya registrada
        SRV-->>API: Rechazo RN-M06-06 o RN-M06-07
        API-->>NG: 400 con el mensaje de la regla
    else Fecha invalida
        SRV-->>API: Rechazo RN-M06-08
        API-->>NG: 400 con el mensaje de la fecha
    else Horas de molienda no positivas
        API-->>NG: 400 Las horas de molienda deben ser mayores que cero
    else Registro admisible
        SRV->>DB: BEGIN TRANSACTION
        opt Primer paso despues del secado
            SRV->>DB: Guardar la ruta elegida del lote o de la parte
        end
        SRV->>DB: Persistir paso con fecha y usuario responsable
        opt Molienda con horas
            SRV->>DB: Guardar horas de molienda
        end
        opt Ensacado con bigbags
            SRV->>DB: Asociar bigbags con su peso aproximado
        end
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
    REP->>DB: Leer lote partes reparto y pasos por etapa

    alt Ingreso sin lote
        DB-->>REP: Sin lote asignado
        REP-->>API: Ninguna etapa recorrida RN-M06-11
        API-->>NG: 200 indicando que el ingreso aun no tiene lote
    else Ruta sin decidir
        DB-->>REP: Lote con secado y sin ruta
        REP-->>API: Etapas recorridas y ruta por decidir
        API-->>NG: 200 sin proporcion
    else Ruta decidida
        DB-->>REP: Lote o partes con su ruta y sus pasos
        REP->>REP: Unir etapas de las rutas de las partes RN-M06-22
        REP-->>API: Etapas recorridas sobre etapas de la ruta
        API-->>NG: 200 con el recorrido por parte y la proporcion
        NG-->>A: Secuencia de etapas de la ruta con su estado
    end
```

## S-M06-04 · División de un lote por fracciones (HU-M06-04)

```mermaid
sequenceDiagram
    actor A as Administrativo
    participant NG as Angular
    participant API as Django REST
    participant SRV as ServicioLote
    participant DB as PostgreSQL
    participant AUD as Auditoria M09

    A->>NG: Indica nombre fraccion y ruta de cada parte
    NG->>NG: Mostrar la suma de fracciones RNF-M06-10
    NG->>API: POST /api/v1/lotes/{id}/division/
    API->>SRV: dividir_lote(lote, partes, usuario)

    alt Rol no autorizado
        API-->>NG: 403 Accion no autorizada
    else Lote ya dividido o con una parte avanzada
        SRV-->>API: Rechazo RN-M06-16
        API-->>NG: 400 con el mensaje de la regla
    else Datos incompletos nombres repetidos o mas de seis partes
        SRV-->>API: Error de validacion
        API-->>NG: 400 con el mensaje correspondiente
    else Fracciones que no suman la unidad
        SRV-->>API: Rechazo RN-M06-16
        API-->>NG: 400 Las fracciones de las partes deben sumar el total del lote
    else Division admisible
        SRV->>DB: BEGIN TRANSACTION
        SRV->>DB: Crear las partes con su fraccion y su ruta
        SRV->>AUD: Registrar evento MODIFICAR con las partes
        SRV->>DB: COMMIT
        API-->>NG: 201 Lote dividido con toneladas aproximadas por parte
    end
```

El reparto de un ingreso tardío en un lote dividido sigue la misma comprobación de fracciones: el
sistema propone las del lote y el usuario puede ajustarlas antes de confirmar (DR-20).

## S-M06-05 · Cierre del lote con su destino (HU-M06-05)

```mermaid
sequenceDiagram
    actor D as Administrador
    participant NG as Angular
    participant API as Django REST
    participant SRV as ServicioLote
    participant REP as RepositorioTrazabilidad
    participant DB as PostgreSQL
    participant AUD as Auditoria M09

    D->>NG: Abre el cierre del lote
    NG->>API: GET /api/v1/lotes/{id}/resumen/
    API->>REP: resumen_y_pendientes(lote)
    REP->>DB: Consulta agregada de toneladas bigbags horas y fechas
    REP-->>API: Resumen y pendientes
    API-->>NG: 200 con el resumen y las estimaciones senaladas

    D->>NG: Elige el destino y confirma
    NG->>API: PATCH /api/v1/lotes/{id}/cerrar/
    API->>SRV: cerrar_lote(lote, destino, observacion, usuario)

    alt Rol distinto de Administrador
        API-->>NG: 403 Accion no autorizada
    else Lote ya cerrado
        SRV-->>API: Rechazo RN-M06-21
        API-->>NG: 409 El lote ya fue cerrado
    else Etapas pendientes
        SRV-->>API: Rechazo RN-M06-20
        API-->>NG: 400 Todavia no se puede cerrar el lote con la lista de pendientes
    else Destino ausente
        API-->>NG: 400 Debe indicar el destino del lote
    else Cierre admisible
        SRV->>DB: BEGIN TRANSACTION
        SRV->>DB: Marcar Cerrado con destino fecha y responsable
        SRV->>AUD: Registrar evento MODIFICAR con destino y resumen
        SRV->>DB: COMMIT
        API-->>NG: 200 Lote cerrado con su destino
    end
```

El cierre no registra la venta ni el traslado en sí: solo su destino (DR-14).
