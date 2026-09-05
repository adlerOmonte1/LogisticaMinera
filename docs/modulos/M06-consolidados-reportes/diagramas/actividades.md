# Diagramas de actividades — M06 Consolidados y reportes

## A-M06-01 · Composición del consolidado mensual (RN-M06-01 a RN-M06-04)

```mermaid
flowchart TD
    Start([Usuario solicita consolidado de un periodo]) --> V1{Rol autorizado?}
    V1 -->|No| E1[Rechazar: Accion no autorizada]
    E1 --> Fin([Fin])
    V1 -->|Si| Q1[Consultar ingresos del periodo en estado REGISTRADO]
    Q1 --> Q2[Agrupar por producto: toneladas y viajes]
    Q2 --> Q3[Desagregar cada grupo por titularidad del vehiculo]
    Q3 --> Q4[Consultar salidas del periodo por tipo de movimiento]
    Q4 --> Q5[Consultar ajustes del periodo]
    Q5 --> Q6[Consultar saldo de cierre desde M05]
    Q6 --> Q7[Contar documentos anulados del periodo]
    Q7 --> V2{Hubo movimientos en el periodo?}
    V2 -->|No| Z1[Componer consolidado en cero con nota explicativa]
    V2 -->|Si| C1[Componer consolidado con los agregados]
    Z1 --> A1[Registrar evento de generacion en auditoria]
    C1 --> A1
    A1 --> M1[Presentar consolidado]
    M1 --> Fin
```

La rama Z1 es la que sostiene el indicador I6: un mes sin producción debe producir reporte, no un error.

## A-M06-02 · Exportación de un reporte (RN-M06-06)

```mermaid
flowchart TD
    Start([Usuario solicita exportar]) --> V1{Rol autorizado?}
    V1 -->|No| E1[Rechazar: Accion no autorizada]
    E1 --> Fin([Fin])
    V1 -->|Si| V2{Formato soportado?}
    V2 -->|No| E2[Rechazar: Formato de exportacion no soportado]
    E2 --> Fin
    V2 -->|Si| O1[Obtener consolidado del periodo]
    O1 --> O2[Seleccionar exportador correspondiente al formato]
    O2 --> O3[Componer encabezado con periodo, fecha y usuario]
    O3 --> O4[Generar archivo]
    O4 --> A1[Registrar evento EXPORTAR en auditoria]
    A1 --> D1[Entregar archivo al usuario]
    D1 --> Fin
```

## A-M06-03 · Cálculo del indicador I6

```mermaid
flowchart TD
    Start([Cierre de la ventana de observacion]) --> L1[Listar los meses del periodo de estudio]
    L1 --> P1[Para cada mes]
    P1 --> V1{Existe consolidado disponible?}
    V1 -->|Si| C1[Contar como mes con reporte]
    V1 -->|No| C2[Contar como mes sin reporte]
    C1 --> D1{Quedan meses?}
    C2 --> D1
    D1 -->|Si| P1
    D1 -->|No| R1[I6 = meses con reporte sobre total de meses]
    R1 --> Fin([Registrar indicador I6])
```

En el pretest, este cálculo se realiza sobre el archivo documental de la empresa. En el postest, se lee directamente del endpoint de disponibilidad. La diferencia entre ambos valores es el efecto que la tesis mide para la dimensión D3.
