# Diagramas de secuencia — M02 Catálogo maestro

## S-M02-01 · Registro de vehículo externo (HU-M02-02, CA03)

```mermaid
sequenceDiagram
    actor A as Administrativo
    participant NG as Angular
    participant API as Django REST
    participant SRV as ServicioCatalogo
    participant DOM as Modelo Vehiculo
    participant DB as PostgreSQL
    participant AUD as Auditoria M08

    A->>NG: Completa placa, titularidad EXTERNO, capacidad
    NG->>NG: Validacion de formulario (conveniencia)
    NG->>API: POST /api/v1/catalogo/vehiculos/
    API->>SRV: crear_vehiculo(datos)
    SRV->>DOM: Validar invariantes RN-M02-02 a 05
    alt Titularidad EXTERNO sin transportista
        DOM-->>SRV: Error de dominio
        SRV-->>API: Error de validacion
        API-->>NG: 400 Debe indicar el transportista
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

## S-M02-02 · Desactivación con registros dependientes (HU-M02-01, CA03)

```mermaid
sequenceDiagram
    actor A as Administrativo
    participant NG as Angular
    participant API as Django REST
    participant SRV as ServicioCatalogo
    participant DB as PostgreSQL

    A->>NG: Solicita eliminar producto
    NG->>API: PATCH /api/v1/catalogo/productos/{id}/desactivar/
    API->>SRV: desactivar_producto(id)
    SRV->>DB: Contar movimientos asociados
    DB-->>SRV: Cantidad de movimientos
    alt Tiene movimientos
        SRV->>DB: activo = falso
        SRV-->>API: Desactivado con advertencia
        API-->>NG: 200 El producto se desactivo porque tiene movimientos
    else Sin movimientos
        SRV->>DB: activo = falso
        SRV-->>API: Desactivado
        API-->>NG: 200 Producto desactivado
    end
    NG-->>A: Mensaje correspondiente
```

## S-M02-03 · Precarga de catálogos para operación offline (RNF-M02-03)

```mermaid
sequenceDiagram
    participant NG as Angular
    participant SW as Service Worker
    participant API as Django REST
    participant IDB as IndexedDB

    NG->>API: GET /api/v1/catalogo/productos/
    API-->>NG: Lista de productos vigentes
    NG->>IDB: Guardar catalogo local
    NG->>API: GET /api/v1/catalogo/vehiculos/
    API-->>NG: Lista de vehiculos vigentes
    NG->>IDB: Guardar catalogo local
    Note over SW,IDB: Al perder conexion, el formulario<br/>de ingreso lee de IndexedDB
    NG->>IDB: Leer catalogo (sin conexion)
    IDB-->>NG: Productos y vehiculos
```
