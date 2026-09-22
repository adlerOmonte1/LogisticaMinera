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
    C4 --> F([Usuario elige un resultado])
```

## A-M07-02 · Presentación del detalle y su respaldo (RN-M07-03, RN-M07-04, RN-M07-08)

```mermaid
flowchart TD
    I([Usuario abre un ingreso]) --> C1[Reunir datos del ingreso y sus tres marcas de tiempo]
    C1 --> C2[Solicitar reconocimiento validaciones y trazabilidad]
    C2 --> D1{Existe cada bloque?}
    D1 -->|No| M1[Indicar su ausencia sin ocultar el bloque]
    D1 -->|Si| M2[Presentar el contenido del bloque]
    M1 --> C3[Componer el detalle]
    M2 --> C3
    C3 --> C4[Mostrar miniatura del ticket]
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

## A-M07-03 · Tratamiento de un ingreso anulado en las consultas (RN-M07-01, RN-M07-02)

```mermaid
flowchart TD
    I([Ingreso encontrado por la consulta]) --> D1{Esta anulado?}
    D1 -->|No| A1[Incluir en la lista]
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
