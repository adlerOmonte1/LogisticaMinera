# Diagramas de actividades — M08 Consolidación de la producción

## A-M08-01 · Cálculo del consolidado mensual (RN-M08-01 a RN-M08-04)

```mermaid
flowchart TD
    I([Usuario solicita el total de un mes]) --> V1{Periodo posterior al mes en curso?}
    V1 -->|Si| E1[Rechazar: No se puede consolidar un periodo futuro]
    E1 --> I
    V1 -->|No| C1[Agregar peso neto y conteo por tipo de mineral]
    C1 --> C2[Excluir los ingresos anulados del calculo]
    C2 --> D1{Algun tipo de mineral con ingresos?}
    D1 -->|No| M1[Informar: No hay ingresos registrados para el periodo indicado]
    M1 --> F1([Sin resultado para el periodo])
    D1 -->|Si| C3[Omitir los tipos sin ingresos del resultado]
    C3 --> F2([Total por tipo de mineral con actividad])
```

## A-M08-02 · Consulta frente a exportación del mismo cálculo (RN-M08-05, RN-M08-06)

```mermaid
flowchart TD
    I([Se necesita el total de un periodo]) --> C1[Ejecutar el calculo agregado del periodo]
    C1 --> D1{Se pidio en pantalla o como archivo?}
    D1 -->|Pantalla| P1[Presentar la tabla con los totales]
    D1 -->|Archivo| P2[Entregar el mismo resultado a un exportador]
    P2 --> P3[Componer el archivo con periodo y fecha de generacion]
    P3 --> P4[Registrar el evento de exportacion]
    P1 --> F1([Numero mostrado])
    P4 --> F2([Numero descargado identico al mostrado])
```

Ambos caminos parten del mismo cálculo agregado. Si se implementara un cálculo separado para el
archivo, cualquier diferencia de redondeo o de filtro entre ambos produciría dos cifras distintas
para el mismo mes.
