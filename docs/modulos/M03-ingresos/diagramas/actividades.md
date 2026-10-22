# Diagramas de actividades — M03 Registro de ingresos

## A-M03-01 · Registro de un ingreso a partir del ticket (RN-M03-01 a RN-M03-09, RN-M03-16, RN-M03-17, RN-M03-21, RN-M03-22, RN-M03-24)

```mermaid
flowchart TD
    I([Supervisor junto a la balanza]) --> D0{Hay ticket para fotografiar?}
    D0 -->|Si| C1[Capturar foto del ticket]
    C1 --> V1{Formato y tamano admitidos?}
    V1 -->|No| E1[Rechazar: La imagen debe estar en formato JPG o PNG y no superar los 10 MB]
    E1 --> C1
    V1 -->|Si| A1[Guardar imagen y asignar hora de inicio]
    A1 --> R1[Reconocer placa fecha y peso bruto]
    R1 --> D1{Imagen legible?}
    D1 -->|No| L1[Ingresar placa fecha y peso bruto manualmente]
    D1 -->|Si| C2[Mostrar campos con su confianza]
    D0 -->|No| S1[Elegir registro sin foto y asignar hora de inicio]
    S1 --> S2[Elegir el motivo de la lista]
    S2 --> S3[Ingresar placa fecha y peso bruto]
    L1 --> H1[Proponer la hora actual como hora del pesaje]
    C2 --> H1
    S3 --> H1
    H1 --> L2[Revisar corregir datos y ajustar la hora]
    L2 --> D2{Placa en el catalogo?}
    D2 -->|No| L4[Dar de alta el vehiculo en la misma pantalla]
    D2 -->|De baja| E3[Rechazar: El vehiculo esta dado de baja]
    E3 --> L2
    D2 -->|Si| L5{Tipo de mineral en el catalogo?}
    L4 --> L5
    L5 -->|No| D5{Rol Administrativo o Administrador?}
    D5 -->|Si| L6[Dar de alta el tipo de mineral en la misma pantalla]
    D5 -->|No| E4[Indicar que lo registre un administrativo]
    E4 --> F2([Registro detenido sin perder lo capturado])
    L6 --> L7[Elegir tipo de mineral]
    L5 -->|Si| L7
    L7 --> V2[Validar reglas V1 a V5]
    V2 --> D3{Inconsistencia sin resolver?}
    D3 -->|Si| E2[Senalar campo con el mensaje de la regla]
    E2 --> L2
    D3 -->|No| T1[Iniciar transaccion]
    T1 --> A2[Asignar codigo y hora de fin]
    A2 --> D4{El vehiculo tiene tara?}
    D4 -->|Si| A3[Calcular peso neto con la tara del vehiculo]
    A3 --> P1[Persistir ingreso Registrado con la tara aplicada]
    D4 -->|No| P2[Persistir ingreso En proceso sin peso neto]
    P1 --> P3[Guardar valores reconocidos y confirmados y auditar]
    P2 --> P3
    P3 --> T2[Confirmar transaccion]
    T2 --> F([Ingreso con su codigo])
```

Un vehículo dado de alta en la misma pantalla nunca tiene tara todavía, de modo que su ingreso
siempre termina En proceso: la tara llega con el destare (A-M03-04). El registro sin foto omite el
reconocimiento, pero no la validación: sus datos pasan por las mismas reglas (RN-M03-22) y el
ingreso queda marcado sin respaldo fotográfico, con su motivo. La hora del pesaje se propone en
los tres caminos y el usuario la ajusta antes de confirmar.

## A-M03-02 · Decisión entre corregir y anular (RN-M03-11 a RN-M03-14, RN-M03-25 a RN-M03-27)

```mermaid
flowchart TD
    I([Se detecta un problema en un ingreso]) --> D1{El ingreso debio existir?}
    D1 -->|No| D2{Rol es Administrador?}
    D2 -->|No| E1[Rechazar: Accion no autorizada]
    D2 -->|Si| L1[Indicar motivo de anulacion]
    L1 --> P1[Marcar como anulado y auditar]
    P1 --> D7{El lote todavia reune ingresos?}
    D7 -->|Si| P4[Retirar el ingreso del lote]
    D7 -->|No o sin lote| F1([Queda fuera de los totales y visible en el detalle])
    P4 --> F1

    D1 -->|Si| D3{El dato equivocado es corregible?}
    D3 -->|No| M1[Informar que el codigo la imagen y las horas del servidor no se modifican]
    M1 --> F2([Sin cambios])
    D3 -->|Si| D4{Rol es Administrativo o Administrador?}
    D4 -->|No| E1
    D4 -->|Si| D5{Ingreso anulado?}
    D5 -->|Si| E2[Rechazar: No se puede corregir un ingreso anulado]
    D5 -->|No| L2[Indicar motivo de la correccion]
    L2 --> D8{Cambia el tipo de mineral de un ingreso en lote?}
    D8 -->|Si y no esta en la lista del lote| E4[Rechazar: el mineral no esta en el lote]
    E4 --> L2
    D8 -->|No| V1[Validar reglas V1 a V5 sobre los datos corregidos]
    V1 --> D6{Regla bloqueante incumplida?}
    D6 -->|Si| E3[Senalar campo con el mensaje de la regla]
    E3 --> L2
    D6 -->|No| D9{El vehiculo corregido tiene tara?}
    D9 -->|Si| P2[Recalcular peso neto actualizar y auditar]
    D9 -->|No| P3[Dejar el ingreso En proceso sin neto y auditar]
    P2 --> F3([Ingreso corregido con historial del cambio])
    P3 --> F3
    F3 --> D10{Se revierte la ultima correccion?}
    D10 -->|Si con motivo| V1
    D10 -->|No| F4([Lote consolidado y trazabilidad reflejan el valor vigente])
```

## A-M03-03 · Conservación del borrador ante pérdida de conexión (RNF-M03-05)

```mermaid
flowchart TD
    I([Registro en curso]) --> A1[Guardar borrador en el dispositivo]
    A1 --> D1{Hay conexion al confirmar?}
    D1 -->|Si| P1[Enviar al servidor y confirmar]
    P1 --> A2[Descartar el borrador]
    A2 --> F1([Ingreso registrado])
    D1 -->|No| M1[Avisar que el ingreso no se ha confirmado]
    M1 --> A3[Conservar imagen y campos editados]
    A3 --> D2{Se recupera la conexion?}
    D2 -->|No| A3
    D2 -->|Si| L1[Reanudar el registro sin volver a fotografiar]
    L1 --> P1
```

El borrador vive solo en el dispositivo y no es un ingreso: no tiene código ni figura en ninguna
consulta hasta confirmarse contra el servidor.

## A-M03-04 · Registro del destare de un vehículo en su primer viaje (RN-M03-19, RN-M03-20, RN-M03-23)

```mermaid
flowchart TD
    I([Volquete descargado se pesa vacio]) --> C1[Abrir ingresos pendientes de destare]
    C1 --> D0{Hay ingresos En proceso?}
    D0 -->|No| M0[Informar: No hay vehiculos pendientes de destare]
    M0 --> F0([Sin destare])
    D0 -->|Si| L1[Elegir el vehiculo]
    L1 --> V1{El vehiculo ya tiene tara?}
    V1 -->|Si| E1[Rechazar: El vehiculo ya tiene tara registrada]
    V1 -->|No| L2[Digitar la tara y ajustar la fecha y hora propuestas]
    L2 --> V2{Tara indicada?}
    V2 -->|No| E2[Rechazar: Debe indicar la tara del vehiculo]
    E2 --> L2
    V2 -->|Si| V5{Fecha posterior al registro?}
    V5 -->|Si| E5[Rechazar: La fecha del destare no puede ser posterior a la fecha actual]
    E5 --> L2
    V5 -->|No| V3{Tara menor que el peso bruto de cada ingreso?}
    V3 -->|No| E3[Rechazar: La tara no puede ser mayor o igual que el peso bruto]
    E3 --> L2
    V3 -->|Si| A1[Calcular el peso neto de cada ingreso En proceso]
    A1 --> V4{Algun neto fuera del rango de carga?}
    V4 -->|Si| L3[Escribir la justificacion de cada ingreso fuera de rango]
    L3 --> T1
    V4 -->|No| T1[Iniciar transaccion]
    T1 --> P1[Guardar tara fecha del destare y usuario en el vehiculo]
    P1 --> P2[Aplicar la tara y el neto a todos sus ingresos En proceso]
    P2 --> P3[Pasar esos ingresos a Registrado y auditar]
    P3 --> T2[Confirmar transaccion]
    T2 --> F([Destare registrado con la lista de ingresos completados])
```

La tara se digita, no se reconoce de la imagen: de ella depende el peso neto de todos los viajes
futuros del vehículo (RN-M03-19).
