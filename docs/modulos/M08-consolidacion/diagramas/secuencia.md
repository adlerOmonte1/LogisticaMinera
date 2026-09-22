# Diagramas de secuencia — M08 Consolidación de la producción

## S-M08-01 · Consulta del consolidado mensual (HU-M08-01)

```mermaid
sequenceDiagram
    actor A as Administrativo
    participant NG as Angular
    participant API as Django REST
    participant REP as RepositorioConsolidacion
    participant DB as PostgreSQL

    A->>NG: Indica mes y anio
    NG->>API: GET /api/v1/consolidacion/mensual/

    alt Periodo futuro
        API-->>NG: 400 No se puede consolidar un periodo futuro
    else Periodo valido
        API->>REP: calcular(mes, anio)
        REP->>DB: Agregar peso neto y conteo por tipo de mineral
        Note over REP,DB: Excluye ingresos anulados RN-M08-01
        DB-->>REP: Filas por tipo de mineral con actividad

        alt Sin ingresos en el periodo
            REP-->>API: Resultado vacio
            API-->>NG: 200 No hay ingresos registrados para el periodo indicado
        else Con ingresos
            REP-->>API: Total y conteo por tipo de mineral
            API-->>NG: 200 con el detalle del periodo
            NG-->>A: Tabla con toneladas por tipo de mineral
        end
    end
```

## S-M08-02 · Exportación del consolidado mensual (HU-M08-02)

```mermaid
sequenceDiagram
    actor A as Administrativo
    participant NG as Angular
    participant API as Django REST
    participant SRV as ServicioConsolidacion
    participant REP as RepositorioConsolidacion
    participant EXP as ExportadorExcel
    participant AUD as Auditoria M09

    A->>NG: Solicita exportar el periodo
    NG->>API: GET /api/v1/consolidacion/mensual/exportar/
    API->>SRV: exportar(mes, anio, usuario, formato)
    SRV->>REP: calcular(mes, anio)
    REP-->>SRV: Total y conteo por tipo de mineral

    alt Sin ingresos en el periodo
        SRV-->>API: Rechazo RS-M08-06
        API-->>NG: 400 No hay ingresos registrados para el periodo indicado
    else Con ingresos
        SRV->>EXP: generar(resultado, periodo)
        EXP-->>SRV: Archivo XLSX con periodo y fecha de generacion
        SRV->>AUD: Registrar evento EXPORTAR
        SRV-->>API: Archivo listo
        API-->>NG: 200 con el archivo para descargar
        NG-->>A: Descarga el consolidado
    end
```

El exportador se invoca después de obtener el mismo resultado que usa la consulta en pantalla
(RN-M08-05): no existe un segundo cálculo para la exportación.
