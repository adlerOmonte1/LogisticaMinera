# Diagramas de actividades — M04 Reconocimiento automático del ticket

## A-M04-01 · Reconocimiento y presentación de la propuesta (RN-M04-01 a RN-M04-07)

```mermaid
flowchart TD
    I([Imagen del ticket recibida]) --> R1[Invocar el motor a traves de la interfaz]
    R1 --> D1{Responde dentro del tiempo?}
    D1 -->|No| E1[Cancelar la espera y avisar que no esta disponible]
    E1 --> L1[Presentar los seis campos vacios y editables]
    D1 -->|Si| D2{Obtuvo alguna lectura?}
    D2 -->|No| E2[Informar que no fue posible leer el ticket]
    E2 --> L1
    D2 -->|Si| R2[Tomar valor y confianza de cada campo]
    R2 --> D3{Campo con lectura?}
    D3 -->|No| A1[Dejar el campo vacio sin proponer valor]
    D3 -->|Si| D4{Confianza bajo el umbral?}
    D4 -->|Si| A2[Marcar el campo como dudoso]
    D4 -->|No| A3[Marcar el campo como confiable]
    A1 --> C1[Componer la propuesta]
    A2 --> C1
    A3 --> C1
    C1 --> L2[Presentar campos precargados con los dudosos resaltados]
    L1 --> F([Registro continua sin reconocimiento])
    L2 --> F2([Usuario revisa corrige y confirma])
```

Ninguna rama de este diagrama escribe en la base: todo lo que produce el reconocimiento es una
propuesta en memoria hasta que el usuario confirma el ingreso.

## A-M04-02 · Conservación de la lectura al confirmar (RN-M04-02, RN-M04-09, RN-M04-10)

```mermaid
flowchart TD
    I([Usuario confirma el ingreso]) --> D1{Hubo reconocimiento?}
    D1 -->|No| A1[Registrar el ingreso como manual con su motivo]
    A1 --> F1([Sin reconocimiento asociado])
    D1 -->|Si| T1[Entrar en la transaccion del ingreso]
    T1 --> P1[Persistir cabecera con motor version y umbral]
    P1 --> C1[Recorrer los seis campos]
    C1 --> P2[Guardar valor reconocido y valor confirmado]
    P2 --> D2{Los dos valores difieren?}
    D2 -->|Si| A2[Marcar el campo como corregido]
    D2 -->|No| A3[Marcar el campo como aceptado]
    A2 --> P3[Registrar evento de correccion]
    A3 --> C2{Quedan campos?}
    P3 --> C2
    C2 -->|Si| C1
    C2 -->|No| T2[Confirmar la transaccion]
    T2 --> F2([Lectura y confirmacion conservadas por separado])
```

## A-M04-03 · Decisión de revisar un campo (RN-M04-03, RN-M04-06)

```mermaid
flowchart TD
    I([Campo presentado al usuario]) --> D1{Tiene valor propuesto?}
    D1 -->|No| M1[Campo vacio: el usuario debe escribirlo]
    D1 -->|Si| D2{Confianza bajo el umbral?}
    D2 -->|Si| M2[Campo resaltado: el usuario debe verificarlo]
    D2 -->|No| M3[Campo normal: el usuario puede aceptarlo]
    M1 --> F([El usuario decide y confirma])
    M2 --> F
    M3 --> F
```

Las tres situaciones son distintas y se presentan distintas. Un campo sin lectura no lleva confianza
cero: no lleva confianza, porque no hubo lectura que calificar.
