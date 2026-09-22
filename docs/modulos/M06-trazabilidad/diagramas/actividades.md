# Diagramas de actividades — M06 Trazabilidad del proceso

## A-M06-01 · Ciclo de vida de un lote (RN-M06-01 a RN-M06-05, RN-M06-10)

```mermaid
flowchart TD
    I([Mineral acumulandose en cancha]) --> A1[Abrir lote con su tipo de mineral]
    A1 --> L1[Seleccionar ingresos para la carga]
    L1 --> V1{Mismo tipo de mineral?}
    V1 -->|No| E1[Rechazar: El ingreso corresponde a otro tipo de mineral]
    E1 --> L1
    V1 -->|Si| V2{Ingreso anulado?}
    V2 -->|Si| E2[Rechazar: No se puede asignar un ingreso anulado]
    E2 --> L1
    V2 -->|No| V3{Ya esta en un lote cerrado?}
    V3 -->|Si| E3[Rechazar: El lote ya fue cerrado]
    E3 --> L1
    V3 -->|No| P1[Asignar el ingreso y recalcular totales]
    P1 --> D1{Carga completa?}
    D1 -->|No| L1
    D1 -->|Si| V4{Tiene al menos un ingreso?}
    V4 -->|No| E4[Rechazar: El lote no tiene ingresos asignados]
    E4 --> L1
    V4 -->|Si| P2[Cerrar el lote y fijar su composicion]
    P2 --> F([Lote listo para recorrer las etapas])
```

## A-M06-02 · Recorrido del lote por las cuatro etapas (RN-M06-06 a RN-M06-08)

```mermaid
flowchart TD
    I([Lote cerrado]) --> D1{Paso por secado registrado?}
    D1 -->|No| R1[Registrar secado]
    D1 -->|Si| D2{Paso por zarandeo registrado?}
    R1 --> V1[Validar fecha y unicidad]
    D2 -->|No| R2[Registrar zarandeo]
    D2 -->|Si| D3{Paso por molienda registrado?}
    R2 --> V1
    D3 -->|No| R3[Registrar molienda]
    D3 -->|Si| D4{Paso por ensacado registrado?}
    R3 --> V1
    D4 -->|No| R4[Registrar ensacado]
    D4 -->|Si| F1([Proceso completo: cuatro de cuatro etapas])
    R4 --> V1
    V1 --> V2{Fecha posterior al momento actual?}
    V2 -->|Si| E1[Rechazar: La fecha de la etapa no puede ser posterior a la fecha actual]
    E1 --> I
    V2 -->|No| V3{Fecha anterior a la de la etapa previa?}
    V3 -->|Si| E2[Rechazar: La fecha no puede ser anterior a la de la etapa previa]
    E2 --> I
    V3 -->|No| P1[Persistir paso con fecha y responsable]
    P1 --> I
```

La interfaz ofrece únicamente la etapa que corresponde registrar (RNF-M06-07); las decisiones de
este diagrama son las que el servidor comprueba de todas formas.

## A-M06-03 · Respuesta a la pregunta por dónde va un ingreso (RN-M06-11)

```mermaid
flowchart TD
    I([Consulta sobre un ingreso]) --> D1{Tiene lote asignado?}
    D1 -->|No| M1[Mostrar cuatro etapas no recorridas]
    M1 --> M2[Indicar que el ingreso aun no tiene lote]
    M2 --> F1([Cero de cuatro etapas])
    D1 -->|Si| C1[Leer los pasos registrados del lote]
    C1 --> C2[Componer las cuatro etapas con su estado]
    C2 --> D2{Las cuatro registradas?}
    D2 -->|Si| M3[Senalar proceso completo]
    D2 -->|No| M4[Senalar la etapa pendiente mas proxima]
    M3 --> F2([Recorrido con fecha y responsable por etapa])
    M4 --> F2
```

Un ingreso sin lote no es un dato faltante: es el estado normal de un ingreso recién registrado, y
se presenta como cero etapas recorridas.
