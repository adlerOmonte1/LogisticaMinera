# Requerimientos funcionales — M03 Registro de ingresos

**RF globales asociados:**
- **RF-01** — Registrar el ingreso de volquete a planta con los datos del ticket de balanza
- **RF-02** — Calcular automáticamente el peso neto del ingreso
- **RF-09** — Consultar, editar y anular los ingresos registrados

| Función | Descripción | HU | RF | Endpoint |
|---|---|---|---|---|
| Registrar ingreso | Alta con validaciones completas | HU-M03-01 | RF-01 | `POST /api/v1/ingresos/` |
| Calcular peso neto | Cálculo servidor y cliente | HU-M03-02 | RF-02 | (interno) |
| Asignar correlativo | Transaccional | HU-M03-03 | RF-01 | (interno) |
| Listar ingresos | Con filtros y paginación | HU-M03-04 | RF-09 | `GET /api/v1/ingresos/` |
| Consultar detalle | Vista completa | HU-M03-05 | RF-09 | `GET /api/v1/ingresos/{id}/` |
| Editar ingreso | Campos editables únicamente | HU-M03-06 | RF-09 | `PATCH /api/v1/ingresos/{id}/` |
| Anular ingreso | Con motivo obligatorio | HU-M03-07 | RF-09 | `POST /api/v1/ingresos/{id}/anular/` |

## Parámetros de filtrado (RF-09)

```
GET /api/v1/ingresos/?fecha_desde=2027-03-01
                    &fecha_hasta=2027-03-31
                    &producto=1
                    &vehiculo=5
                    &titularidad=PROPIO
                    &estado=REGISTRADO
                    &page=1
```

El filtro `titularidad` no es un atributo del ingreso sino del vehículo asociado. Se expone en este endpoint porque es la consulta directa que alimenta el cálculo del indicador I2.

## Campos editables y no editables (HU-M03-06, CA02)

| Campo | Editable | Razón |
|---|:---:|---|
| fecha_pesaje, hora_pesaje | Sí | Corrección de transcripción del ticket |
| numero_ticket | Sí | Corrección de transcripción |
| vehiculo, producto | Sí | Corrección de selección |
| peso_bruto, tara | Sí | Corrección de transcripción; recalcula stock |
| peso_neto | No | Es calculado |
| **correlativo** | **No** | Decisión D-02: lo asigna el servidor y lo identifica de forma permanente |
| **hora_registro** | **No** | Decisión D-01: es la base del indicador I1; editable, el indicador sería falsificable |
| estado | Solo vía anulación | Decisión D-07 |

## Permisos

| Función | Administrador | Administrativo | Supervisor |
|---|:---:|:---:|:---:|
| Registrar ingreso | Sí | Sí | Sí |
| Listar y consultar | Sí | Sí | Sí |
| Editar | Sí | Sí | No |
| Anular | Sí | Sí | No |
