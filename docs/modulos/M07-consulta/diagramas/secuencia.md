# Diagramas de secuencia — M07 Consulta de ingresos y respaldo

## S-M07-01 · Consulta por placa y fecha (HU-M07-01)

```mermaid
sequenceDiagram
    actor A as Administrativo
    participant NG as Angular
    participant API as Django REST
    participant REP as RepositorioConsulta
    participant DB as PostgreSQL

    A->>NG: Indica placa y fecha
    NG->>API: GET /api/v1/consulta/ingresos/

    alt Sin criterios
        API-->>NG: 400 Debe indicar al menos la placa o la fecha
    else Rango de fechas invertido
        API-->>NG: 400 La fecha inicial no puede ser posterior a la fecha final
    else Criterios validos
        API->>REP: buscar(placa, fecha)
        REP->>DB: Consulta sobre indice de vehiculo y fecha
        DB-->>REP: Ingresos ordenados por fecha descendente
        REP-->>API: Resultados con estado y motivo de anulacion

        alt Sin coincidencias
            API-->>NG: 200 lista vacia
            NG-->>A: No se encontraron ingresos con los criterios indicados
        else Con coincidencias
            API-->>NG: 200 con los resultados
            NG-->>A: Lista con los anulados senalados
        end
    end
```

## S-M07-02 · Detalle de un ingreso con su respaldo (HU-M07-01, HU-M07-02)

```mermaid
sequenceDiagram
    actor A as Administrativo
    participant NG as Angular
    participant API as Django REST
    participant SRV as ServicioConsulta
    participant ING as RepositorioIngreso M03
    participant REC as RepositorioReconocimiento M04
    participant VAL as RepositorioValidacion M05
    participant TRZ as RepositorioTrazabilidad M06
    participant IMG as Almacen de imagenes

    A->>NG: Abre un resultado
    NG->>API: GET /api/v1/consulta/ingresos/{id}/
    API->>SRV: componer_detalle(id)
    SRV->>ING: Datos del ingreso y tres marcas de tiempo
    SRV->>REC: Comparacion reconocido y confirmado
    SRV->>VAL: Reglas evaluadas y su resolucion
    SRV->>TRZ: Etapas recorridas por el lote
    SRV-->>API: Detalle con los bloques disponibles
    API-->>NG: 200 con los bloques y sus ausencias indicadas
    NG-->>A: Detalle completo con miniatura del ticket

    A->>NG: Amplia la imagen del ticket
    NG->>API: GET /api/v1/consulta/ingresos/{id}/ticket/
    API->>API: Verificar sesion y permiso sobre el ingreso

    alt Sin sesion valida
        API-->>NG: 401 sin entregar la imagen
    else Almacen sin respuesta
        API->>IMG: Solicitar imagen
        IMG--xAPI: Sin respuesta
        API-->>NG: 200 indicando que el respaldo no esta disponible
    else Imagen disponible
        API->>IMG: Solicitar imagen
        IMG-->>API: Imagen en resolucion original
        API-->>NG: 200 con la imagen
        NG-->>A: Ticket ampliado
    end
```

## S-M07-03 · Listado con filtros y totales (HU-M07-02)

```mermaid
sequenceDiagram
    actor A as Administrativo
    participant NG as Angular
    participant API as Django REST
    participant REP as RepositorioConsulta
    participant DB as PostgreSQL

    A->>NG: Combina filtros de fecha mineral vehiculo y estado
    NG->>API: GET /api/v1/consulta/ingresos/ con filtros
    API->>REP: listar(filtros, pagina)
    REP->>DB: Consulta paginada con los filtros aplicados
    DB-->>REP: Pagina de resultados
    REP->>DB: Consulta agregada de conteo y suma de pesos netos
    Note over REP,DB: La suma excluye los anulados RN-M07-02
    DB-->>REP: Total de ingresos y de toneladas
    REP-->>API: Pagina y totales en un numero fijo de consultas
    API-->>NG: 200 con resultados y totales
    NG-->>A: Listado paginado con el resumen del conjunto
```
