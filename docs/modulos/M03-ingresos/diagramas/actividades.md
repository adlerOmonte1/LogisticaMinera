# Diagramas de actividades — M03 Registro de ingresos

## A-M03-01 · Registro de un ingreso a partir del ticket (RN-M03-01 a RN-M03-10)

```mermaid
flowchart TD
    I([Supervisor junto a la balanza]) --> C1[Capturar foto del ticket]
    C1 --> V1{Formato y tamano admitidos?}
    V1 -->|No| E1[Rechazar: La imagen debe estar en formato JPG o PNG y no superar los 10 MB]
    E1 --> C1
    V1 -->|Si| A1[Guardar imagen y asignar hora de inicio]
    A1 --> R1[Reconocer los seis campos del ticket]
    R1 --> D1{Imagen legible?}
    D1 -->|No| L1[Ingresar los datos manualmente]
    D1 -->|Si| C2[Mostrar campos con su confianza]
    L1 --> L2[Revisar y corregir datos]
    C2 --> L2
    L2 --> L3[Elegir tipo de mineral]
    L3 --> V2[Validar reglas V1 a V5]
    V2 --> D2{Inconsistencia sin resolver?}
    D2 -->|Si| E2[Senalar campo con el mensaje de la regla]
    E2 --> L2
    D2 -->|No| V3{Placa en el catalogo y vigente?}
    V3 -->|No| E3[Rechazar: La placa no esta registrada en el catalogo de vehiculos]
    E3 --> L2
    V3 -->|Si| V4{Numero de ticket ya registrado?}
    V4 -->|Si| E4[Rechazar: El ticket ya fue registrado en otro ingreso]
    E4 --> L2
    V4 -->|No| T1[Iniciar transaccion]
    T1 --> A2[Asignar codigo y hora de fin]
    A2 --> P1[Persistir ingreso con valores reconocidos y confirmados]
    P1 --> P2[Registrar evento de auditoria]
    P2 --> T2[Confirmar transaccion]
    T2 --> F([Ingreso registrado con su codigo])
```

## A-M03-02 · Decisión entre corregir y anular (RN-M03-11 a RN-M03-14)

```mermaid
flowchart TD
    I([Se detecta un problema en un ingreso]) --> D1{El ingreso debio existir?}
    D1 -->|No| D2{Rol es Administrador?}
    D2 -->|No| E1[Rechazar: Accion no autorizada]
    D2 -->|Si| L1[Indicar motivo de anulacion]
    L1 --> P1[Marcar como anulado y auditar]
    P1 --> F1([Queda fuera de los totales y visible en el detalle])

    D1 -->|Si| D3{El dato equivocado es corregible?}
    D3 -->|No| M1[Informar que el codigo la imagen y las horas del servidor no se modifican]
    M1 --> F2([Sin cambios])
    D3 -->|Si| D4{Rol es Administrativo o Administrador?}
    D4 -->|No| E1
    D4 -->|Si| D5{Ingreso anulado?}
    D5 -->|Si| E2[Rechazar: No se puede corregir un ingreso anulado]
    D5 -->|No| L2[Indicar motivo de la correccion]
    L2 --> V1[Validar reglas V1 a V5 sobre los datos corregidos]
    V1 --> D6{Regla bloqueante incumplida?}
    D6 -->|Si| E3[Senalar campo con el mensaje de la regla]
    E3 --> L2
    D6 -->|No| P2[Actualizar y auditar valores anteriores]
    P2 --> F3([Ingreso corregido con historial del cambio])
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
