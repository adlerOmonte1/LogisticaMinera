# Diagramas de secuencia — M02 Catálogo maestro

## S-M02-01 · Registro de un vehículo externo (HU-M02-01, CA04)

```mermaid
sequenceDiagram
    actor A as Administrativo
    participant NG as Angular
    participant API as Django REST
    participant SRV as ServicioCatalogo
    participant DOM as Modelo Vehiculo
    participant DB as PostgreSQL
    participant AUD as Auditoria M09

    A->>NG: Completa placa, titularidad EXTERNO y capacidad
    NG->>NG: Validacion de formulario de conveniencia
    NG->>API: POST /api/v1/catalogo/vehiculos/
    API->>SRV: crear_vehiculo(datos)
    SRV->>DOM: Validar invariantes RN-M02-01 a 05

    alt Titularidad EXTERNO sin transportista
        DOM-->>SRV: Error de dominio
        SRV-->>API: Error de validacion
        API-->>NG: 400 Debe indicar el transportista para un vehiculo externo
        NG-->>A: Mensaje de error en el campo
    else Datos validos
        DOM->>DB: Persistir vehiculo activo
        DB-->>DOM: Confirmacion
        SRV->>AUD: Registrar evento CREAR
        SRV-->>API: Vehiculo creado
        API-->>NG: 201 con el recurso
        NG-->>A: Confirmacion y actualizacion de la lista
    end
```

## S-M02-02 · Desactivación con registros dependientes (HU-M02-02, CA03)

```mermaid
sequenceDiagram
    actor A as Administrativo
    participant NG as Angular
    participant API as Django REST
    participant SRV as ServicioCatalogo
    participant DB as PostgreSQL
    participant AUD as Auditoria M09

    A->>NG: Solicita desactivar un tipo de mineral
    NG->>API: PATCH /api/v1/catalogo/tipos-mineral/{id}/desactivar/
    API->>SRV: desactivar_tipo_mineral(id)
    SRV->>DB: Contar ingresos asociados
    DB-->>SRV: Cantidad de ingresos

    alt Tiene ingresos asociados
        SRV->>DB: activo = falso
        SRV->>AUD: Registrar evento MODIFICAR
        SRV-->>API: Desactivado con advertencia
        API-->>NG: 200 El tipo de mineral se desactivo porque tiene ingresos registrados
    else Sin ingresos asociados
        SRV->>DB: activo = falso
        SRV->>AUD: Registrar evento MODIFICAR
        SRV-->>API: Desactivado
        API-->>NG: 200 Tipo de mineral desactivado
    end

    NG-->>A: Mensaje correspondiente
```

## S-M02-03 · Consulta del catálogo desde el registro de ingresos (HU-M02-01, HU-M02-02)

```mermaid
sequenceDiagram
    actor S as Supervisor de planta
    participant NG as Angular
    participant API as Django REST
    participant REP as RepositorioCatalogo

    S->>NG: Abre el formulario de registro de un ingreso
    NG->>API: GET /api/v1/catalogo/vehiculos/?vigente=true
    API->>REP: listar_vigentes()
    REP-->>API: Vehiculos activos
    API-->>NG: 200 con la lista

    NG->>API: GET /api/v1/catalogo/tipos-mineral/?vigente=true
    API->>REP: listar_vigentes()
    REP-->>API: Tipos de mineral activos
    API-->>NG: 200 con la lista

    NG-->>S: Selectores de placa y tipo de mineral poblados
```
