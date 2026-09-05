# Diagramas de actividades — M05 Existencias

## A-M05-01 · Determinación del saldo de un producto (RN-M05-01, RS-M05-03)

```mermaid
flowchart TD
    Start([Solicitud de saldo de un producto]) --> Q1[Buscar ultimo movimiento no anulado del producto]
    Q1 --> D1{Existe algun movimiento?}
    D1 -->|No| R0[Saldo = cero]
    R0 --> Fin([Devolver saldo])
    D1 -->|Si| R1[Leer saldo resultante denormalizado]
    R1 --> Fin
```

## A-M05-02 · Registro de un ajuste de inventario (RN-M05-06 a RN-M05-08)

```mermaid
flowchart TD
    Start([Administrador realiza medicion fisica]) --> V1{Rol es Administrador?}
    V1 -->|No| E1[Rechazar: Accion no autorizada]
    E1 --> Fin([Fin])
    V1 -->|Si| V2{Motivo indicado?}
    V2 -->|No| E2[Rechazar: Debe indicar el motivo del ajuste]
    E2 --> Fin
    V2 -->|Si| C1[Leer saldo del sistema]
    C1 --> C2[Calcular diferencia entre medicion y saldo]
    C2 --> V3{Diferencia igual a cero?}
    V3 -->|Si| M1[Informar: No hay diferencia que ajustar]
    M1 --> Fin
    V3 -->|No| P1[Insertar movimiento tipo AJUSTE por la diferencia]
    P1 --> P2[Registrar en auditoria saldo previo, medido, diferencia y motivo]
    P2 --> M2[Confirmar: Ajuste registrado]
    M2 --> Fin
```

## A-M05-03 · Verificación de consistencia del saldo denormalizado (RNF-M05-03)

```mermaid
flowchart TD
    Start([Rutina de verificacion]) --> P1[Para cada producto]
    P1 --> C1[Calcular saldo recorriendo todos los movimientos no anulados]
    C1 --> C2[Leer saldo denormalizado del ultimo movimiento]
    C2 --> V1{Coinciden?}
    V1 -->|Si| S1[Producto consistente]
    V1 -->|No| A1[Registrar inconsistencia con ambos valores]
    A1 --> A2[Alertar al administrador]
    S1 --> D1{Quedan productos?}
    A2 --> D1
    D1 -->|Si| P1
    D1 -->|No| Fin([Fin de la verificacion])
```

Esta rutina no es una funcionalidad para el usuario: es un control interno que debe ejecutarse al menos al inicio y al cierre de la ventana de observación del postest. Su resultado es evidencia de la validez de los datos recolectados y conviene documentarlo como anexo de la tesis.
