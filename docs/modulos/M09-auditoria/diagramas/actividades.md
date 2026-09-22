# Diagramas de actividades — M09 Auditoría

## A-M09-01 · Registro de un evento como parte de otra operación (RN-M09-01, RN-M09-06)

```mermaid
flowchart TD
    I([Una operacion de escritura esta por completarse]) --> C1[Tomar el usuario autenticado que ejecuta la operacion]
    C1 --> C2[Componer el evento con accion entidad e identificador]
    C2 --> D1{La operacion es una modificacion?}
    D1 -->|Si| A1[Incluir valores anteriores y nuevos]
    D1 -->|No| A2[Incluir solo los valores que correspondan]
    A1 --> P1[Persistir el evento en la misma transaccion]
    A2 --> P1
    P1 --> D2{Se pudo persistir?}
    D2 -->|No| E1[Revertir toda la transaccion]
    D2 -->|Si| F1([Operacion y evento confirmados juntos])
    E1 --> F2([Ni la operacion ni el evento quedan registrados])
```

## A-M09-02 · Reconstrucción del historial de una entidad (RU-M09-04)

```mermaid
flowchart TD
    I([Administrador indica entidad e identificador]) --> C1[Consultar eventos por ese indice]
    C1 --> D1{Existen eventos?}
    D1 -->|No| M1[Informar: Sin eventos registrados para este registro]
    D1 -->|Si| C2[Ordenar cronologicamente del primero al mas reciente]
    C2 --> C3[Para cada evento anadir su autor y su accion]
    C3 --> D2{El evento es una modificacion?}
    D2 -->|Si| A1[Mostrar valor anterior y valor nuevo del campo]
    D2 -->|No| A2[Mostrar el detalle disponible para esa accion]
    A1 --> C4{Quedan eventos?}
    A2 --> C4
    C4 -->|Si| C3
    C4 -->|No| F1([Linea de tiempo completa del registro])
    M1 --> F2([Sin historial que mostrar])
```

## A-M09-03 · Distinción entre operación completada y acceso rechazado (RN-M09-04)

```mermaid
flowchart TD
    I([Usuario intenta una operacion]) --> D1{Tiene permiso para el rol?}
    D1 -->|No| E1[Registrar evento ACCESO_RECHAZADO]
    E1 --> M1[Rechazar: Accion no autorizada]
    M1 --> F1([Intento queda en el historial sin efecto sobre los datos])
    D1 -->|Si| P1[Ejecutar la operacion]
    P1 --> E2[Registrar el evento correspondiente a la accion]
    E2 --> F2([Operacion y su evento quedan en el historial])
```

Ambas ramas terminan con un evento registrado. La diferencia no está en si se audita, sino en qué se
audita: una es un cambio sobre los datos, la otra es la constancia de que el cambio no se permitió.
