# Diagramas de secuencia — M06 Consolidados y reportes

## S-M06-01 · Generación del consolidado mensual (HU-M06-01)

```mermaid
sequenceDiagram
    actor A as Administrativo
    participant NG as Angular
    participant API as Django REST
    participant SRV as ServicioConsolidado
    participant SEL as SelectorReportes
    participant STK as ServicioStock M05
    participant DB as PostgreSQL
    participant AUD as Auditoria M08

    A->>NG: Selecciona anio y mes
    NG->>API: GET /api/v1/reportes/consolidado/
    API->>SRV: generar_consolidado(anio, mes)
    SRV->>SEL: ingresos_no_anulados_por_producto(periodo)
    SEL->>DB: Agregacion con union a vehiculo por titularidad
    DB-->>SEL: Toneladas y viajes por producto y titularidad
    SEL-->>SRV: Agregados de produccion
    SRV->>SEL: salidas_por_tipo(periodo)
    SEL-->>SRV: Agregados de salidas
    SRV->>SEL: contar_documentos_anulados(periodo)
    SEL-->>SRV: Cantidad de anulados
    SRV->>STK: saldos_al_cierre(fecha_fin)
    STK-->>SRV: Saldo por producto
    SRV->>SRV: Componer consolidado

    alt Periodo sin movimientos
        SRV->>SRV: Componer con valores en cero y nota
    end

    SRV->>AUD: Registrar evento de generacion con periodo
    SRV-->>API: Consolidado
    API-->>NG: 200 con el consolidado
    NG-->>A: Consolidado en pantalla
```

## S-M06-02 · Exportación con estrategia por formato (HU-M06-02, RS-M06-05)

```mermaid
sequenceDiagram
    actor A as Administrativo
    participant API as Django REST
    participant SRV as ServicioConsolidado
    participant FAC as FabricaExportador
    participant EXP as Exportador
    participant AUD as Auditoria M08

    A->>API: GET /api/v1/reportes/consolidado/exportar/?formato=xlsx
    API->>SRV: obtener_consolidado(periodo)
    SRV-->>API: Datos del consolidado
    API->>FAC: obtener_exportador(formato)

    alt Formato xlsx
        FAC-->>API: ExportadorExcel
    else Formato pdf
        FAC-->>API: ExportadorPDF
    else Formato no soportado
        FAC-->>API: Error de formato
        API-->>A: 400 Formato de exportacion no soportado
    end

    API->>EXP: exportar(consolidado, encabezado)
    EXP-->>API: Archivo binario
    API->>AUD: Registrar evento EXPORTAR
    API-->>A: 200 con el archivo adjunto
```

El servicio de consolidado no conoce los formatos concretos: recibe la abstracción desde la fábrica. Agregar un tercer formato no obliga a modificar `ServicioConsolidado` (principio de abierto/cerrado).

## S-M06-03 · Consulta de disponibilidad histórica y el indicador I6

```mermaid
sequenceDiagram
    actor A as Administrativo
    participant API as Django REST
    participant SEL as SelectorReportes
    participant DB as PostgreSQL

    A->>API: GET /api/v1/reportes/disponibilidad/?desde=&hasta=
    API->>SEL: meses_con_consolidado(rango)
    SEL->>DB: Meses del rango con al menos un documento o consolidado generable
    DB-->>SEL: Listado por mes
    SEL-->>API: Disponibilidad por mes
    API-->>A: 200 con el listado
```
