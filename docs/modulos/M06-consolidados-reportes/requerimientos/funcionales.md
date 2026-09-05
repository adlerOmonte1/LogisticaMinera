# Requerimientos funcionales — M06 Consolidados y reportes

**RF globales asociados:**
- **RF-06** — Generar el consolidado mensual de producción
- **RF-07** — Exportar los reportes en formatos de uso externo

| Función | Descripción | HU | RF | Endpoint |
|---|---|---|---|---|
| Generar consolidado mensual | Agregación por producto y titularidad | HU-M06-01 | RF-06 | `GET /api/v1/reportes/consolidado/?anio=&mes=` |
| Exportar a Excel | Archivo XLSX | HU-M06-02 | RF-07 | `GET /api/v1/reportes/consolidado/exportar/?formato=xlsx` |
| Exportar a PDF | Archivo PDF | HU-M06-02 | RF-07 | `GET /api/v1/reportes/consolidado/exportar/?formato=pdf` |
| Generar declaración semestral | Estructura del formato oficial | HU-M06-03 | RF-06 | `GET /api/v1/reportes/declaracion-semestral/?anio=&semestre=` |
| Consultar disponibilidad histórica | Meses con consolidado generado | HU-M06-01 | RF-06 | `GET /api/v1/reportes/disponibilidad/` |

## Contenido del consolidado mensual

| Sección | Contenido |
|---|---|
| Producción por producto | Toneladas ingresadas, cantidad de viajes |
| Desagregación por titularidad | Toneladas y viajes de vehículos PROPIO vs. EXTERNO |
| Salidas del periodo | Toneladas por tipo de movimiento (venta, traslado, merma) |
| Ajustes del periodo | Cantidad y magnitud de los ajustes registrados |
| Saldo de cierre | Existencia por producto al último día del periodo |
| Documentos anulados | Cantidad de ingresos y salidas anulados, excluidos del cálculo |

## El endpoint de disponibilidad y el indicador I6

`GET /api/v1/reportes/disponibilidad/` devuelve, para cada mes del periodo consultado, si existe consolidado disponible. Este endpoint es la fuente directa del indicador I6: el porcentaje de meses con reporte disponible se lee de aquí, sin cálculo manual.

## Permisos

| Función | Administrador | Administrativo | Supervisor |
|---|:---:|:---:|:---:|
| Generar consolidado | Sí | Sí | No |
| Exportar | Sí | Sí | No |
| Generar declaración semestral | Sí | No | No |
| Consultar disponibilidad | Sí | Sí | No |
