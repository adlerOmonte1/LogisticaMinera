# Diagramas de actividades — M06 Trazabilidad del proceso

## A-M06-01 · Ciclo de vida de un lote (RN-M06-01 a RN-M06-04, RN-M06-10, RN-M06-13, RN-M06-14)

```mermaid
flowchart TD
    I([Mineral acumulandose en cancha]) --> A1[Abrir lote con nombre tipo de mineral y fecha]
    A1 --> V0{Nombre repetido o fecha futura?}
    V0 -->|Si| E0[Rechazar con el mensaje correspondiente]
    E0 --> A1
    V0 -->|No| L1[Seleccionar ingresos para la carga]
    L1 --> V1{Mineral del ingreso en la lista del lote?}
    V1 -->|No| D0{Unificar desde Agregar de otro tipo con autorizacion?}
    D0 -->|No| E1[No se asigna: el mineral no esta en el lote]
    E1 --> L1
    D0 -->|Si| M1[Registrar la autorizacion sumar el mineral y marcar Otro mineral]
    M1 --> V2
    V1 -->|Si| V2{Ingreso anulado o En proceso?}
    V2 -->|Si| E2[Rechazar con el mensaje de la regla]
    E2 --> L1
    V2 -->|No| P1[Asignar el ingreso y recalcular totales]
    P1 --> D1{Carga reunida?}
    D1 -->|No| L1
    D1 -->|Si| V3{Tiene al menos un ingreso?}
    V3 -->|No| E3[Rechazar: El lote no tiene ingresos asignados]
    E3 --> L1
    V3 -->|Si| P2[Iniciar el recorrido y pasar a En recorrido]
    P2 --> D4{Ingreso agregado por error?}
    D4 -->|Si| V4{Su mineral paso por zarandeo o molienda?}
    V4 -->|Si| E4[Rechazar: el mineral ya paso por zarandeo o molienda]
    V4 -->|No| P5[Retirar el ingreso y devolverlo a cancha]
    E4 --> D2
    P5 --> D2
    D4 -->|No| D2{Llega un volquete tardio?}
    D2 -->|Si| D3{Secado del lote registrado?}
    D3 -->|No| P3[Agregarlo para secarse con el lote]
    D3 -->|Si| P4[Agregarlo con secado propio]
    P3 --> D2
    P4 --> D2
    D2 -->|No| F([Lote recorriendo su ruta hasta el cierre])
```

Mientras el lote está Abierto, un ingreso puede retirarse o trasladarse a otro lote. Desde el inicio
del recorrido se suman ingresos tardíos, y un ingreso agregado por error todavía puede retirarse
hasta que su mineral pase por zarandeo o molienda, siempre que el lote conserve al menos un ingreso.
El secado ya registrado se conserva (RN-M06-04).

## A-M06-02 · Recorrido del lote por su ruta (RN-M06-05 a RN-M06-08, RN-M06-15, RN-M06-19)

```mermaid
flowchart TD
    I([Lote En recorrido]) --> D1{Secado registrado?}
    D1 -->|No| R1[Registrar el secado comun]
    D1 -->|Si| D2{Ruta decidida?}
    D2 -->|No| R2[Elegir la ruta y registrar su primera etapa]
    D2 -->|Si| D3{Quedan etapas de la ruta?}
    D3 -->|No| F1([Todo el mineral ensacado: listo para el cierre])
    D3 -->|Si| R3[Registrar la siguiente etapa de la ruta]
    R1 --> V1[Validar fechas y unicidad]
    R2 --> V1
    R3 --> V1
    V1 --> V2{Fecha valida?}
    V2 -->|No| E1[Rechazar con el mensaje de la fecha]
    E1 --> I
    V2 -->|Si| D4{Es molienda o ensacado?}
    D4 -->|Molienda| M1[Registrar horas de molino si se indican]
    D4 -->|Ensacado| B1[Asociar bigbags con peso aproximado]
    D4 -->|Otra| P1[Persistir paso con fecha y responsable]
    M1 --> P1
    B1 --> P1
    P1 --> I
```

Si el lote está dividido, este recorrido ocurre por cada parte, con su propia ruta. La interfaz
ofrece únicamente la etapa que corresponde registrar (RNF-M06-07); las decisiones de este diagrama
son las que el servidor comprueba de todas formas.

## A-M06-03 · Respuesta a la pregunta por dónde va un ingreso (RN-M06-11, RN-M06-22)

```mermaid
flowchart TD
    I([Consulta sobre un ingreso]) --> D1{Tiene lote asignado?}
    D1 -->|No| M1[Indicar que el ingreso aun no tiene lote]
    M1 --> F1([Ninguna etapa recorrida])
    D1 -->|Si| C1[Leer los pasos del lote y de sus partes]
    C1 --> D2{Ruta decidida?}
    D2 -->|No| M2[Mostrar el secado e indicar ruta por decidir]
    M2 --> F2([Recorrido sin proporcion])
    D2 -->|Si| D3{Lote dividido?}
    D3 -->|Si| C2[Unir las etapas de las rutas de sus partes]
    D3 -->|No| C3[Tomar las etapas de la ruta del lote]
    C2 --> C4[Contar etapas recorridas sobre etapas de la ruta]
    C3 --> C4
    C4 --> D4{Todas recorridas?}
    D4 -->|Si| M3[Senalar proceso completo]
    D4 -->|No| M4[Senalar la etapa pendiente mas proxima]
    M3 --> F3([Recorrido con fecha y responsable por etapa])
    M4 --> F3
```

Un ingreso sin lote no es un dato faltante: es el estado normal de un ingreso recién registrado.

## A-M06-04 · División de un lote y reparto de un ingreso tardío (RN-M06-16 a RN-M06-18)

```mermaid
flowchart TD
    I([Se decide partir la carga]) --> V1{Ya fue dividido?}
    V1 -->|Si| E1[Rechazar: El lote ya fue dividido]
    V1 -->|No| V2{Alguna parte avanzo por su ruta?}
    V2 -->|Si| E2[Rechazar: No se puede dividir: el lote ya avanzo por su ruta]
    V2 -->|No| L1[Indicar nombre fraccion y ruta de cada parte]
    L1 --> V3{Datos completos y nombres distintos?}
    V3 -->|No| E3[Rechazar con el mensaje correspondiente]
    E3 --> L1
    V3 -->|Si| V4{Las fracciones suman la unidad?}
    V4 -->|No| E4[Rechazar: Las fracciones de las partes deben sumar el total del lote]
    E4 --> L1
    V4 -->|Si| P1[Crear las partes y calcular toneladas aproximadas]
    P1 --> D1{Llega un ingreso tardio?}
    D1 -->|No| F([Partes recorriendo su ruta])
    D1 -->|Si| L2[Proponer las fracciones del lote para repartirlo]
    L2 --> L3[Usuario acepta o ajusta las fracciones]
    L3 --> V5{Suman la unidad?}
    V5 -->|No| E4
    V5 -->|Si| P2[Repartir el ingreso entre las partes]
    P2 --> F
```

Las toneladas de cada parte son una estimación: el mineral acumulado no se pesa (RN-M06-17).

## A-M06-05 · Cierre del lote con su destino (RN-M06-20, RN-M06-21)

```mermaid
flowchart TD
    I([Administrador abre el cierre del lote]) --> C1[Calcular pendientes y resumen del proceso]
    C1 --> D1{Hay pendientes?}
    D1 -->|Si| E1[Rechazar: Todavia no se puede cerrar el lote y listar lo pendiente]
    D1 -->|No| M1[Mostrar resumen con estimaciones senaladas]
    M1 --> L1[Elegir destino venta o traslado]
    L1 --> V1{Destino indicado?}
    V1 -->|No| E2[Rechazar: Debe indicar el destino del lote]
    E2 --> L1
    V1 -->|Si| T1[Iniciar transaccion]
    T1 --> P1[Marcar el lote Cerrado con destino fecha y responsable]
    P1 --> P2[Auditar destino y resumen]
    P2 --> T2[Confirmar transaccion]
    T2 --> F([Lote cerrado: no admite ingresos etapas ni bigbags])
```

El cierre registra el destino, no la venta ni el traslado: no hay guía, factura ni precio (DR-14).
