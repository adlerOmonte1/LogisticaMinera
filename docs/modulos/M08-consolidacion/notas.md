# Notas de implementación — M08 Consolidación de la producción

## Backend (Django)

**App:** `apps/consolidacion/` — no existe todavía; se crea en la fase de preparación del backend.

### Estructura

```
apps/consolidacion/
├── repositories/    calculo agregado por periodo y tipo de mineral
├── exportadores/    una clase por formato: excel.py hoy, pdf.py o csv.py cuando se necesiten
├── services/        orquesta calculo exportacion y auditoria
├── serializers/  views/  permissions.py  urls.py  tests/
```

Sin `models/` ni `migrations/` (D-10). M08 no aporta ninguna entidad al modelo de datos.

### El cálculo agregado

```python
class RepositorioConsolidacion:
    def calcular(self, mes: int, anio: int) -> list[TotalPorTipoMineral]:
        return (
            Ingreso.objects
            .filter(fecha_hora_ticket__year=anio, fecha_hora_ticket__month=mes)
            .exclude(estado="ANULADO")
            .values("tipo_mineral__nombre")
            .annotate(toneladas=Sum("peso_neto_tn"), cantidad=Count("id"))
            .order_by("tipo_mineral__nombre")
        )
```

Decisiones no obvias:

- **Una sola consulta agregada, sin recorrer ingresos en Python.** Con `values().annotate()` la base
  hace el agrupamiento; es la forma que sostiene RNF-M08-01 conforme crece el histórico.
- **`.exclude(estado="ANULADO")` antes de `.annotate()`**, no después. Filtrar tras agregar sumaría
  primero y descontaría después, lo que con `Sum` puede dar un resultado distinto si hay valores
  negativos en juego, y aquí no debería haberlos pero la regla se aplica siempre en el mismo orden
  para no depender de esa suposición.
- **No hay tabla de acumulado ni tarea programada que la actualice.** Es la traducción directa de
  RN-M08-02: cualquier mecanismo de caché o precálculo reintroduce el riesgo de desincronización que
  la regla existe para evitar. Si el rendimiento lo exigiera más adelante, la vía es un índice, no
  un acumulado.

### Exportadores intercambiables

```python
class ExportadorConsolidado(Protocol):
    def generar(self, resultado: list[TotalPorTipoMineral], periodo: Periodo) -> bytes: ...


class ExportadorExcel:
    def generar(self, resultado, periodo) -> bytes:
        ...  # openpyxl
```

El servicio recibe el exportador por su tipo de contenido solicitado y no conoce la librería
concreta (RNF-M08-04, RN-M08-06). Añadir PDF es una clase nueva en `exportadores/`, sin tocar
`RepositorioConsolidacion` ni `ExportadorExcel`.

### Registro del evento

La exportación se audita con el periodo consolidado como dato del evento (RS-M08-10). La consulta en
pantalla no se audita: leer no es un cambio sobre el que deba quedar constancia, y auditar cada
consulta multiplicaría el volumen de `EVENTO_AUDITORIA` sin aportar trazabilidad útil.

## Frontend (Angular)

**Feature:** `features/consolidacion/`

- El selector de periodo usa un control de mes y año (RNF-M08-06), no dos campos de fecha completa:
  el usuario nunca necesita un día concreto para este reporte.
- La tabla de resultados y el botón de exportación comparten el mismo periodo seleccionado: no hay
  forma de exportar un mes distinto al que se está viendo en pantalla, lo que refuerza en la interfaz
  la garantía de RN-M08-05.
- El componente de resultados es de `ui/`, sin estado: recibe la lista de totales por tipo de mineral
  y la presenta.

## Riesgo de implementación identificado

**El riesgo principal es que alguien introduzca un acumulado «por rendimiento» sin darse cuenta de
que reintroduce el problema que RN-M08-02 resuelve.**

Es una optimización que parece razonable de forma aislada: guardar el total del mes en una tabla y
actualizarlo con una señal cada vez que se registra un ingreso. El defecto aparece con las
correcciones y las anulaciones (HU-M03-02, HU-M03-03), que también deberían disparar esa
actualización y es fácil olvidar en alguna de las dos rutas. El resultado es un acumulado que queda
desactualizado en silencio: ninguna prueba que solo registre ingresos nuevos lo detecta.

La prueba que sí lo detecta registra un ingreso, calcula el consolidado, **corrige** el peso neto de
ese ingreso, y vuelve a calcular el consolidado del mismo mes esperando el valor corregido
(HU-M08-01 CA05). Es la prueba que un acumulado desincronizado no puede pasar.

**Riesgo secundario:** que el exportador redondee de forma distinta a como se presenta en pantalla,
rompiendo RNF-M08-05 sin que el cálculo subyacente haya cambiado.

## Dependencias

| Depende de | Para |
|---|---|
| M01 | Autenticación y control de acceso |
| M02 | Los tipos de mineral que agrupan el resultado |
| M03 | Los ingresos del periodo, con su peso neto y su estado |
| M09 | Registro del evento de exportación |

| Es requerido por | Para |
|---|---|
| — | Ningún módulo depende de M08: es un punto final de lectura |

## Pendientes que afectan a este módulo

| Pendiente | Efecto |
|---|---|
| Valores del catálogo de tipos de mineral (DR-03) | Define las filas que puede devolver el consolidado |
| Formatos de exportación adicionales, si se requieren | No bloquea: la estructura de `exportadores/` los admite sin rediseño |
