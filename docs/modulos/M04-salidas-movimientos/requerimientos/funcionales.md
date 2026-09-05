# Requerimientos funcionales — M04 Salidas y movimientos

**RF global asociado:** RF-05 — Registrar las salidas de producto y los movimientos internos

| Función | Descripción | HU | Endpoint |
|---|---|---|---|
| Registrar salida | Alta con tipo de movimiento | HU-M04-01, HU-M04-02 | `POST /api/v1/salidas/` |
| Listar salidas | Con filtros y paginación | HU-M04-03 | `GET /api/v1/salidas/` |
| Consultar detalle | Vista completa | HU-M04-03 | `GET /api/v1/salidas/{id}/` |
| Anular salida | Con motivo obligatorio | HU-M04-03 | `POST /api/v1/salidas/{id}/anular/` |
| Verificar disponibilidad | Consulta previa de saldo | HU-M04-01, CA02 | `GET /api/v1/existencias/?producto={id}` |

## Tipos de movimiento

| Tipo | Exige cliente | Exige motivo | Efecto en stock |
|---|:---:|:---:|---|
| VENTA | Sí | No | Resta |
| TRASLADO_INTERNO | No | No | Resta |
| MERMA | No | Sí | Resta |

Los tres restan del stock. La distinción existe para que el indicador I4 pueda interpretarse: una desviación explicada por mermas registradas es distinta de una desviación sin explicación.

## Permisos

| Función | Administrador | Administrativo | Supervisor |
|---|:---:|:---:|:---:|
| Registrar salida | Sí | Sí | No |
| Listar y consultar | Sí | Sí | Sí (solo lectura) |
| Anular | Sí | Sí | No |

El Supervisor no registra salidas: su rol opera en la recepción de material, no en el despacho. Esta restricción refleja la organización real del trabajo en la empresa.
