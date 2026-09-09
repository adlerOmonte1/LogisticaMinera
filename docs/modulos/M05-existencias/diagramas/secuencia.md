# Diagramas de secuencia — M05 Existencias

## S-M05-01 · Consulta de existencias (HU-M05-01)

```mermaid
sequenceDiagram
    actor A as Administrativo
    participant NG as Angular
    participant API as Django REST
    participant SEL as SelectorExistencias
    participant DB as PostgreSQL

    A->>NG: Abre pantalla de existencias
    NG->>API: GET /api/v1/existencias/
    API->>SEL: obtener_saldos_vigentes()
    SEL->>DB: Ultimo movimiento por producto con saldo denormalizado
    DB-->>SEL: Saldos por producto
    SEL-->>API: Lista de existencias
    API-->>NG: 200 con saldos
    NG-->>A: Tabla de productos con saldo y ultimo movimiento
```

La consulta lee el saldo denormalizado del último movimiento de cada producto (RS-M05-03). No recorre el histórico: si lo hiciera, el tiempo de respuesta crecería con el volumen y el indicador I3 se degradaría durante el periodo de medición.

## S-M05-02 · Generación de movimiento desde un ingreso (RN-M05-03)

```mermaid
sequenceDiagram
    participant SRV as ServicioIngreso M03
    participant STK as ServicioStock
    participant DB as PostgreSQL

    SRV->>STK: generar_movimiento_entrada(ingreso)
    STK->>DB: Leer saldo actual del producto con bloqueo
    DB-->>STK: Saldo vigente
    STK->>STK: Nuevo saldo = saldo vigente mas peso neto
    STK->>DB: Insertar movimiento tipo ENTRADA con saldo resultante
    DB-->>STK: Confirmacion
    STK-->>SRV: Movimiento creado
```

La lectura del saldo se hace con bloqueo dentro de la transacción que abrió M03. Sin bloqueo, dos ingresos simultáneos del mismo producto calcularían el saldo resultante sobre la misma base y uno de los dos quedaría con un saldo denormalizado incorrecto.

## S-M05-03 · Registro de ajuste de inventario (HU-M05-03)

```mermaid
sequenceDiagram
    actor AD as Administrador
    participant NG as Angular
    participant API as Django REST
    participant SRV as ServicioAjuste
    participant DB as PostgreSQL
    participant AUD as Auditoria M08

    AD->>NG: Indica producto, cantidad medida y motivo
    NG->>API: POST /api/v1/existencias/ajustes/
    API->>SRV: registrar_ajuste(producto, medido, motivo, usuario)
    SRV->>DB: Leer saldo del sistema
    DB-->>SRV: Saldo actual
    SRV->>SRV: diferencia = medido menos saldo del sistema

    alt Diferencia igual a cero
        SRV-->>API: Sin diferencia
        API-->>NG: 200 No hay diferencia que ajustar
    else Motivo vacio
        SRV-->>API: Error de validacion
        API-->>NG: 400 Debe indicar el motivo del ajuste
    else Diferencia distinta de cero
        SRV->>DB: BEGIN TRANSACTION
        SRV->>DB: Insertar movimiento tipo AJUSTE por la diferencia
        SRV->>AUD: Registrar saldo previo, medido, diferencia, motivo
        SRV->>DB: COMMIT
        API-->>NG: 201 Ajuste registrado
    end
    NG-->>AD: Mensaje correspondiente
```
