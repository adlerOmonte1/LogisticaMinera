# Requerimientos funcionales — M02 Catálogo maestro

**RF global asociado:** RF-03 — Gestión de catálogos maestros (productos, vehículos, transportistas y clientes)

| Función | Descripción | HU | Endpoint |
|---|---|---|---|
| Listar productos | Consulta con filtro por vigencia | HU-M02-01 | `GET /api/v1/catalogo/productos/` |
| Crear producto | Alta | HU-M02-01 | `POST /api/v1/catalogo/productos/` |
| Editar producto | Modificación | HU-M02-01 | `PATCH /api/v1/catalogo/productos/{id}/` |
| Desactivar producto | Baja lógica | HU-M02-01 | `PATCH /api/v1/catalogo/productos/{id}/desactivar/` |
| Listar vehículos | Consulta con filtro por titularidad | HU-M02-02 | `GET /api/v1/catalogo/vehiculos/` |
| Crear vehículo | Alta con titularidad obligatoria | HU-M02-02 | `POST /api/v1/catalogo/vehiculos/` |
| Editar vehículo | Modificación | HU-M02-02 | `PATCH /api/v1/catalogo/vehiculos/{id}/` |
| Desactivar vehículo | Baja lógica | HU-M02-02 | `PATCH /api/v1/catalogo/vehiculos/{id}/desactivar/` |
| Gestionar transportistas | CRUD con baja lógica | HU-M02-03 | `/api/v1/catalogo/transportistas/` |
| Gestionar clientes | CRUD con baja lógica | HU-M02-04 | `/api/v1/catalogo/clientes/` |

## Relación con el indicador I2

El endpoint `GET /api/v1/catalogo/vehiculos/?titularidad=PROPIO` permite construir el denominador del indicador de cobertura para volquetes propios. Sin este filtro, la cobertura solo puede calcularse de forma agregada y el hallazgo diferencial del diagnóstico no es demostrable.

## Permisos

| Función | Administrador | Administrativo | Supervisor |
|---|:---:|:---:|:---:|
| Consultar catálogos | Sí | Sí | Sí (solo lectura) |
| Crear y editar | Sí | Sí | No |
| Desactivar | Sí | Sí | No |
