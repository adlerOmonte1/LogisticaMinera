# Diagrama de casos de uso — M07 Consulta de ingresos y respaldo

```mermaid
flowchart LR
    SUP(("Supervisor de planta"))
    ADV(("Administrativo"))
    ADM(("Administrador"))

    UC1["Buscar ingreso por placa y fecha"]
    UC2["Ver el ticket de respaldo"]
    UC3["Listar ingresos con filtros"]
    UC4["Consultar el detalle de un ingreso"]
    UC5["Ver el calendario de llegadas"]
    UC6["Ver el historial de un ingreso"]
    UC7["Ver el resumen del dia y los avisos"]
    UC8["Buscar desde la cabecera"]
    UC9["Exportar el listado de ingresos"]

    SUP --> UC1
    SUP --> UC2
    SUP --> UC3
    SUP --> UC4
    SUP --> UC5
    SUP --> UC6
    SUP --> UC7
    SUP --> UC8
    ADV --> UC1
    ADV --> UC2
    ADV --> UC3
    ADV --> UC4
    ADV --> UC5
    ADV --> UC6
    ADV --> UC7
    ADV --> UC8
    ADV --> UC9
    ADM --> UC1
    ADM --> UC2
    ADM --> UC3
    ADM --> UC4
    ADM --> UC5
    ADM --> UC6
    ADM --> UC7
    ADM --> UC8
    ADM --> UC9
```

## Casos de uso

| Caso | HU | Actores | Nota |
|---|---|---|---|
| Buscar ingreso por placa y fecha | HU-M07-01 | Los tres roles | Admite placa parcial. Exige al menos uno de los dos criterios. Muestra también el lote y el recorrido del ingreso |
| Ver el ticket de respaldo | HU-M07-01 | Los tres roles | La imagen se amplía para poder contrastarla con lo registrado; sin foto, se muestra el motivo |
| Listar ingresos con filtros | HU-M07-02 | Los tres roles | Filtros combinables y búsqueda por placa o código, con el total de ingresos y de toneladas del conjunto |
| Consultar el detalle de un ingreso | HU-M07-01, HU-M07-02 | Los tres roles | Reúne datos, imagen, validaciones, reconocimiento, trazabilidad e historial |
| Ver el calendario de llegadas | HU-M07-03 | Los tres roles | Llegadas y toneladas por día del mes, con acceso a los ingresos de cada día |
| Ver el historial de un ingreso | HU-M09-02 | Los tres roles | Pestaña del detalle; lo provee M09 |
| Ver el resumen del día y los avisos | HU-M07-04 | Los tres roles | Pantalla de inicio. Los avisos se calculan al consultarse y se filtran por rol |
| Buscar desde la cabecera | HU-M07-02 | Los tres roles | Un código abre el ingreso; si no hay coincidencia, el texto se busca como placa |
| Exportar el listado de ingresos | HU-M07-02 | Administrativo, Administrador | CSV del conjunto filtrado completo; queda en auditoría |

Los ingresos anulados aparecen en todos los casos de uso, señalados como tales: ocultarlos haría
creer que el volquete nunca se registró.

Los actores se definen en el diagrama de casos de uso de M01 y no se redefinen aquí.
