# Diagramas de secuencia — M04 Reconocimiento automático del ticket

## S-M04-01 · Reconocimiento de los datos del ticket (HU-M04-01)

```mermaid
sequenceDiagram
    participant SRV as ServicioIngreso M03
    participant REC as ReconocedorTicket M04
    participant MOT as Motor concreto
    participant NG as Angular
    actor S as Supervisor de planta

    SRV->>REC: reconocer(imagen)
    REC->>MOT: Procesar imagen

    alt Motor sin respuesta o fuera de tiempo
        MOT--xREC: Tiempo de espera agotado RNF-M04-02
        REC-->>SRV: Resultado vacio con causa
        SRV-->>NG: Seis campos vacios y editables
        NG-->>S: El reconocimiento no esta disponible
    else Imagen ilegible
        MOT-->>REC: Sin lectura utilizable
        REC-->>SRV: exito falso
        SRV-->>NG: Seis campos vacios y editables
        NG-->>S: No fue posible leer el ticket
    else Lectura obtenida
        MOT-->>REC: Valores por campo con confianza
        REC->>REC: Comparar cada confianza con el umbral
        REC-->>SRV: Seis campos con confianza y marca de duda
        SRV-->>NG: Propuesta sin persistir RN-M04-01
        NG-->>S: Campos precargados con los dudosos resaltados
    end
```

## S-M04-02 · Persistencia del reconocimiento al confirmar el ingreso (HU-M04-01)

```mermaid
sequenceDiagram
    actor S as Supervisor de planta
    participant NG as Angular
    participant SRV as ServicioIngreso M03
    participant RCS as ServicioReconocimiento M04
    participant DB as PostgreSQL
    participant AUD as Auditoria M09

    S->>NG: Corrige los campos dudosos y confirma
    NG->>SRV: Datos confirmados y referencia del reconocimiento
    SRV->>DB: BEGIN TRANSACTION
    SRV->>DB: Persistir ingreso
    SRV->>RCS: guardar(reconocimiento, valores confirmados)
    RCS->>DB: Persistir cabecera con motor y version
    RCS->>DB: Persistir seis campos con valor reconocido y confirmado
    RCS->>AUD: Registrar evento RECONOCER
    RCS->>AUD: Registrar evento CORREGIR_DATO por cada campo corregido
    SRV->>DB: COMMIT
    SRV-->>NG: 201 con el codigo del ingreso
```

El reconocimiento se persiste dentro de la misma transacción del ingreso: si el ingreso no llega a
registrarse, tampoco queda constancia de la lectura, porque una lectura sin ingreso no describe
nada.

## S-M04-03 · Consulta del dato reconocido frente al confirmado (HU-M04-02)

```mermaid
sequenceDiagram
    actor A as Administrativo
    participant NG as Angular
    participant API as Django REST
    participant REP as RepositorioReconocimiento
    participant DB as PostgreSQL

    A->>NG: Abre el detalle del ingreso
    NG->>API: GET /api/v1/reconocimientos/{id}/

    alt Rol no autorizado
        API-->>NG: 403 Accion no autorizada
    else Sin reconocimiento asociado
        API->>REP: obtener_por_ingreso(id)
        REP-->>API: Sin resultado
        API-->>NG: 200 indicando registro manual y su motivo
    else Reconocimiento existente
        API->>REP: obtener_por_ingreso(id)
        REP->>DB: Leer cabecera y seis campos
        DB-->>REP: Valores reconocido y confirmado
        REP-->>API: Comparacion por campo
        API-->>NG: 200 con motor version y confianza
        NG-->>A: Tabla comparativa con los corregidos senalados
    end
```
