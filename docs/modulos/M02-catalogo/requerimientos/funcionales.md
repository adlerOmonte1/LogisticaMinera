# Requerimientos funcionales — M02 Catálogo maestro

**RF asociado:** **RF06** (soporte) — Registrar el tipo de mineral y el tipo de vehículo; M02
provee los catálogos de los que M03 deriva ambos datos.

| Función | Descripción | HU | Endpoint |
|---|---|---|---|
| Listar vehículos | Consulta con filtro por titularidad y vigencia | HU-M02-01 | `GET /api/v1/catalogo/vehiculos/` |
| Crear vehículo | Alta con titularidad y capacidad obligatorias, sin tara; también invocada desde el registro de un ingreso | HU-M02-01 | `POST /api/v1/catalogo/vehiculos/` |
| Editar vehículo | Modificación de los datos distintos de la tara | HU-M02-01 | `PATCH /api/v1/catalogo/vehiculos/{id}/` |
| Registrar tara | Primera tara del vehículo, invocada por el destare de M03 | HU-M02-01, HU-M03-04 | (interno, desde M03) |
| Modificar tara | Cambio de una tara ya registrada, con motivo obligatorio | HU-M02-01 | `PATCH /api/v1/catalogo/vehiculos/{id}/tara/` |
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
transportista. Conserva la tara de cada vehículo, con su fecha y el usuario que la registró, y
controla quién puede cambiarla.

**Lo que no hace.** No decide si un vehículo puede confirmarse en un ingreso —esa decisión es de
M03, aunque consulte este catálogo—, no calcula el peso neto —lo hace M03 con la tara que M02
conserva— y no aplica las reglas V2 ni V4: solo declara la tara y la capacidad que M05 necesita para
evaluarlas.

## Permisos

| Función | Administrador | Administrativo | Supervisor de planta |
|---|:---:|:---:|:---:|
| Consultar catálogos | Sí | Sí | Sí |
| Crear y editar | Sí | Sí | No |
| Dar de alta un vehículo desde el registro de un ingreso | Sí | Sí | Sí |
| Registrar la primera tara, desde el destare | Sí | Sí | Sí |
| Modificar una tara ya registrada | Sí | No | No |
| Desactivar | Sí | Sí | No |

El Supervisor de planta no gestiona el catálogo, pero puede dar de alta un vehículo y registrar su
primera tara porque ambas operaciones ocurren en planta, dentro del registro del ingreso. La
modificación de una tara existente queda reservada al Administrador porque cambia el peso neto de
todos los ingresos siguientes de ese vehículo.

## Dependencias

| Depende de | Para |
|---|---|
| M01 | Autenticación y rol de quien modifica la tara |
| M09 | Registro del alta, la modificación, la tara y su cambio |

| Es requerido por | Para |
|---|---|
| M03 | El vehículo vigente con su titularidad y su tara, el tipo de mineral del ingreso, el alta de un vehículo nuevo y el registro de su primera tara |
| M05 | La tara y la capacidad del vehículo, que contrastan las reglas V2 y V4 |
| M08 | Los tipos de mineral que agrupan el total mensual |
