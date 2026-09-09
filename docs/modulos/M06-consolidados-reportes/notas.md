# Notas de implementación — M06 Consolidados y reportes

## Backend (Django)

**App:** `apps/reportes/`

### Agregación

Las agregaciones se hacen con el ORM (`annotate`, `aggregate`, `values`), no trayendo los registros a memoria para sumarlos en Python. Con 500 ingresos la diferencia es irrelevante; el punto es que el patrón correcto quede establecido desde el inicio.

La desagregación por titularidad requiere unión con `Vehiculo`:

```python
Ingreso.objects.filter(
    estado=EstadoDocumento.REGISTRADO,
    fecha_pesaje__range=(inicio, fin),
).values('producto__nombre', 'vehiculo__tipo_titularidad').annotate(
    toneladas=Sum('peso_neto_tn'),
    viajes=Count('id_ingreso'),
)
```

### Exportadores

Interfaz común y una implementación por formato:

```python
class ExportadorReporte(ABC):
    @abstractmethod
    def exportar(self, consolidado, encabezado) -> bytes: ...

class ExportadorExcel(ExportadorReporte): ...
class ExportadorPDF(ExportadorReporte): ...
```

Una fábrica resuelve el formato solicitado. `ServicioConsolidado` nunca importa `ExportadorExcel` directamente: recibe la abstracción. Este es el ejemplo concreto de abierto/cerrado y de inversión de dependencias en el proyecto, y conviene tenerlo identificado para la revisión técnica.

- Excel con `openpyxl`. Los números se escriben como números, no como cadenas (CA01): un valor numérico guardado como texto rompe las fórmulas del usuario y es un error frecuente.
- PDF con `ReportLab`. El encabezado con periodo, fecha de generación y usuario es obligatorio (RN-M06-06).

### Declaración semestral

**Bloqueada.** El formato oficial vigente no está disponible todavía. Se puede implementar la agregación semestral —es la misma lógica con otro rango— pero la estructura del archivo depende del formato real. Registrado en `../../00-arquitectura/decisiones_diseno.md`. Fecha límite: antes de la semana 7.

## Frontend (Angular)

**Feature:** `features/reportes/`

- La pantalla principal ofrece un acceso directo a "Consolidado del mes anterior", que es el caso de uso dominante. Cumple RNF-M06-07: dos acciones desde el inicio.
- La descarga se maneja con `HttpClient` en modo `responseType: 'blob'` y creación de un enlace temporal. No abrir el archivo en una pestaña nueva: en móvil el comportamiento es inconsistente.
- El consolidado en pantalla usa la misma estructura de datos que la exportación, para que lo que el usuario ve y lo que descarga no puedan divergir.

## Dependencias

| Depende de | Para |
|---|---|
| M02 | Nombres de producto y titularidad de vehículo |
| M03 | Ingresos del periodo |
| M04 | Salidas del periodo |
| M05 | Saldos de cierre |
| M08 | Registro de eventos de generación y exportación |

Este es el módulo con más dependencias del sistema. Por eso está en la semana 7: requiere que todos los demás estén operativos.
