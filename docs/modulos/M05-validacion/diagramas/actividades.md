# Diagramas de actividades — M05 Validación automática de consistencia

## A-M05-01 · Evaluación de las cinco reglas (RN-M05-01 a RN-M05-07)

```mermaid
flowchart TD
    I([Datos del ticket recibidos]) --> C1[Obtener la capacidad del vehiculo del catalogo]
    C1 --> V1{V1 neto igual a bruto menos tara?}
    V1 -->|No| E1[Anotar: El peso neto no coincide con el peso bruto menos la tara]
    V1 -->|Si| V2{V2 tara menor que bruto?}
    E1 --> V2
    V2 -->|No| E2[Anotar: La tara no puede ser mayor o igual que el peso bruto]
    V2 -->|Si| V3{V3 placa con formato valido?}
    E2 --> V3
    V3 -->|No| E3[Anotar: La placa no tiene un formato valido]
    V3 -->|Si| V4{V4 neto dentro del rango de carga?}
    E3 --> V4
    V4 -->|No| E4[Anotar advertencia: El peso neto esta fuera del rango de carga]
    V4 -->|Si| V5{V5 fecha del ticket no posterior al registro?}
    E4 --> V5
    V5 -->|No| E5[Anotar: La fecha del ticket no puede ser posterior a la fecha de registro]
    V5 -->|Si| C2[Componer la lista de inconsistencias]
    E5 --> C2
    C2 --> F([Devolver todas las inconsistencias encontradas])
```

El flujo atraviesa las cinco reglas sin interrumpirse: cada incumplimiento se anota y la evaluación
continúa, de modo que el usuario reciba la lista completa en un solo intento.

## A-M05-02 · Resolución de las inconsistencias antes de confirmar (RN-M05-02, RN-M05-03)

```mermaid
flowchart TD
    I([Lista de inconsistencias presentada]) --> D1{Hay alguna bloqueante?}
    D1 -->|Si| M1[Impedir la confirmacion y senalar los campos]
    M1 --> L1[Usuario corrige el dato]
    L1 --> V1[Revalidar las cinco reglas]
    V1 --> I
    D1 -->|No| D2{Hay advertencia de peso fuera de rango?}
    D2 -->|No| A1[Habilitar la confirmacion]
    D2 -->|Si| D3{Hay justificacion escrita?}
    D3 -->|No| M2[Rechazar: Debe indicar la justificacion del peso fuera de rango]
    M2 --> L2[Usuario escribe la explicacion o corrige el peso]
    L2 --> V1
    D3 -->|Si| A1
    A1 --> F([Ingreso listo para confirmarse])
```

## A-M05-03 · Momento en que se aplica cada evaluación (RN-M05-05)

```mermaid
flowchart TD
    I([Imagen del ticket procesada]) --> V1[Validar los datos propuestos por el reconocimiento]
    V1 --> M1[Mostrar inconsistencias junto a los campos]
    M1 --> L1[Usuario revisa corrige y elige el tipo de mineral]
    L1 --> A1[Usuario confirma]
    A1 --> V2[Validar los datos confirmados en el servidor]
    V2 --> D1{Coherentes?}
    D1 -->|No| M2[Rechazar con el mensaje de la regla]
    M2 --> L1
    D1 -->|Si| P1[Persistir el ingreso y el resultado de ambas evaluaciones]
    P1 --> F([Queda registro de lo evaluado antes y despues de corregir])
```

La segunda evaluación no es redundante: entre una y otra el usuario editó los datos, y esa edición
puede haber introducido una incoherencia que la primera no podía conocer.
