# Diagramas de actividades — M07 Consulta de ingresos y respaldo

## A-M07-01 · Búsqueda de un ingreso por placa y fecha (RN-M07-01, RN-M07-05)

```mermaid
flowchart TD
    I([Alguien pregunta por un volquete]) --> L1[Indicar placa total o parcial y fecha]
    L1 --> V1{Hay al menos un criterio?}
    V1 -->|No| E1[Rechazar: Debe indicar al menos la placa o la fecha]
    E1 --> L1
    V1 -->|Si| V2{Rango de fechas coherente?}
    V2 -->|No| E2[Rechazar: La fecha inicial no puede ser posterior a la fecha final]
    E2 --> L1
    V2 -->|Si| C1[Normalizar la placa sin guiones ni mayusculas]
    C1 --> C2[Consultar por vehiculo y fecha]
    C2 --> D1{Hay coincidencias?}
    D1 -->|No| M1[Informar: No se encontraron ingresos con los criterios indicados]
    M1 --> L1
    D1 -->|Si| C3[Presentar resultados por fecha descendente]
    C3 --> C4[Senalar los ingresos anulados con su motivo]
    C4 --> C5[Usuario elige un resultado]
    C5 --> D2{El ingreso tiene lote?}
    D2 -->|Si| C6[Mostrar el lote su estado y el recorrido de su ruta]
    D2 -->|No| C7[Indicar que el mineral espera en cancha]
    C6 --> F([Ingreso con su respaldo y su trazabilidad])
    C7 --> F
```

## A-M07-02 · Presentación del detalle y su respaldo (RN-M07-03, RN-M07-04, RN-M07-08)

```mermaid
flowchart TD
    I([Usuario abre un ingreso]) --> C1[Reunir datos del ingreso y sus tres marcas de tiempo]
    C1 --> C2[Solicitar reconocimiento validaciones y trazabilidad]
    C2 --> C8[Solicitar el historial a M09]
    C8 --> D1{Existe cada bloque?}
    D1 -->|No| M1[Indicar su ausencia sin ocultar el bloque]
    D1 -->|Si| M2[Presentar el contenido del bloque]
    M1 --> C3[Componer el detalle]
    M2 --> C3
    C3 --> D0{Registrado sin foto?}
    D0 -->|Si| M0[Mostrar que no tiene respaldo fotografico y su motivo]
    M0 --> F0([Datos visibles con el motivo de la ausencia])
    D0 -->|No| C4[Mostrar miniatura del ticket]
    C4 --> D2{Usuario amplia la imagen?}
    D2 -->|No| F1([Detalle consultado])
    D2 -->|Si| V1{Sesion valida y permiso sobre el ingreso?}
    V1 -->|No| E1[Denegar el acceso a la imagen]
    V1 -->|Si| D3{Almacen responde?}
    D3 -->|No| M3[Informar que el respaldo no esta disponible]
    D3 -->|Si| M4[Entregar la imagen en resolucion original]
    M3 --> F2([Datos visibles sin respaldo])
    M4 --> F3([Ticket contrastable con lo registrado])
```

## A-M07-03 · Tratamiento de un ingreso anulado o en proceso en las consultas (RN-M07-01, RN-M07-02, RN-M07-10)

```mermaid
flowchart TD
    I([Ingreso encontrado por la consulta]) --> D1{Esta anulado?}
    D1 -->|No| D2{Esta en proceso?}
    D2 -->|Si| P1[Incluir en la lista senalado como en proceso]
    P1 --> P2[Mostrar el peso neto como pendiente del destare]
    P2 --> P3[Excluir el ingreso del total del conjunto]
    P3 --> F
    D2 -->|No| A1[Incluir en la lista]
    A1 --> A2[Sumar su peso neto al total del conjunto]
    D1 -->|Si| A3[Incluir en la lista senalado como anulado]
    A3 --> A4[Mostrar el motivo de la anulacion]
    A4 --> A5[Excluir su peso neto del total del conjunto]
    A2 --> F([Resultado coherente con la consolidacion])
    A5 --> F
```

Aparecer y sumar son decisiones distintas. El ingreso anulado aparece porque el hecho ocurrió, y no
suma porque fue retirado del cómputo; si sumara, el total contradiría al de la consolidación para el
mismo periodo.

## A-M07-04 · Calendario de llegadas de un mes (RN-M07-11, RN-M07-12)

```mermaid
flowchart TD
    I([Usuario abre el calendario]) --> C1[Tomar el mes en curso]
    C1 --> C2[Agrupar ingresos por dia de la fecha del pesaje]
    C2 --> C3[Contar ingresos no anulados por dia]
    C3 --> C4[Sumar toneladas netas de los Registrados por dia]
    C4 --> C5[Marcar dias con ingresos En proceso o anulados]
    C5 --> C6[Calcular el resumen del mes]
    C6 --> M1[Mostrar el mes con el color segun las toneladas]
    M1 --> D1{Usuario elige un dia?}
    D1 -->|Otro mes| C7[Cambiar de mes]
    C7 --> C2
    D1 -->|Si| D2{El dia tiene ingresos?}
    D2 -->|No| M2[Informar: No llegaron volquetes este dia]
    D2 -->|Si| M3[Listar los ingresos del dia]
    M3 --> F([Usuario abre el detalle de un ingreso])
```

Los ingresos En proceso cuentan como llegadas pero no suman toneladas, y los anulados no cuentan
ni suman: el total del mes coincide con el consolidado (RN-M07-12).

