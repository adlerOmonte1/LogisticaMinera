# Requerimientos funcionales — M02 Catálogo maestro

**RF asociado:** **RF06** (soporte) — Registrar el tipo de mineral y el tipo de vehículo; M02
provee los catálogos de los que M03 deriva ambos datos.

| Función | Descripción | HU | Endpoint |
|---|---|---|---|
| Listar vehículos | Consulta con filtro por titularidad y vigencia | HU-M02-01 | `GET /api/v1/catalogo/vehiculos/` |
| Crear vehículo | Alta con titularidad y capacidad obligatorias | HU-M02-01 | `POST /api/v1/catalogo/vehiculos/` |
| Editar vehículo | Modificación | HU-M02-01 | `PATCH /api/v1/catalogo/vehiculos/{id}/` |
| Desactivar vehículo | Baja lógica | HU-M02-01 | `PATCH /api/v1/catalogo/vehiculos/{id}/desactivar/` |
| Listar tipos de mineral | Consulta con filtro por vigencia | HU-M02-02 | `GET /api/v1/catalogo/tipos-mineral/` |
| Crear tipo de mineral | Alta | HU-M02-02 | `POST /api/v1/catalogo/tipos-mineral/` |
| Editar tipo de mineral | Modificación | HU-M02-02 | `PATCH /api/v1/catalogo/tipos-mineral/{id}/` |
| Desactivar tipo de mineral | Baja lógica | HU-M02-02 | `PATCH /api/v1/catalogo/tipos-mineral/{id}/desactivar/` |
| Gestionar transportistas | CRUD con baja lógica | HU-M02-03 | `/api/v1/catalogo/transportistas/` |

## Responsabilidad y límites

M02 es el dueño de `VEHICULO`, `TIPO_MINERAL` y `TRANSPORTISTA`. Mantiene estos catálogos vigentes
y expone su consulta a los módulos que los referencian.

**Lo que hace.** Da de alta, edita y desactiva vehículos, tipos de mineral y transportistas, y
valida sus invariantes: formato de placa, longitud de RUC, coherencia entre titularidad y
transportista.

**Lo que no hace.** No decide si un vehículo puede confirmarse en un ingreso —esa decisión es de
M03, aunque consulte este catálogo— y no aplica la regla V4: solo declara la capacidad que M05
necesita para evaluarla.

## Permisos

| Función | Administrador | Administrativo | Supervisor de planta |
|---|:---:|:---:|:---:|
| Consultar catálogos | Sí | Sí | Sí (solo lectura) |
| Crear y editar | Sí | Sí | No |
| Desactivar | Sí | Sí | No |

## Dependencias

| Es requerido por | Para |
|---|---|
| M03 | El vehículo vigente, su titularidad y el tipo de mineral del ingreso |
| M05 | La capacidad del vehículo, que contrasta la regla V4 |
| M08 | Los tipos de mineral que agrupan el total mensual |
