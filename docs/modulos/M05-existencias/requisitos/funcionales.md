# Requerimientos funcionales — M05 Existencias

**RF global asociado:** RF-04 — Determinar las existencias por producto a partir de los movimientos registrados

| Función | Descripción | HU | Endpoint |
|---|---|---|---|
| Consultar existencias | Saldo de todos los productos | HU-M05-01 | `GET /api/v1/existencias/` |
| Consultar existencia de un producto | Saldo puntual | HU-M05-01 | `GET /api/v1/existencias/?producto={id}` |
| Consultar kardex | Movimientos cronológicos con saldo | HU-M05-02 | `GET /api/v1/existencias/kardex/?producto={id}&desde=&hasta=` |
| Registrar ajuste | Diferencia física vs. sistema | HU-M05-03 | `POST /api/v1/existencias/ajustes/` |
| Listar ajustes | Histórico de ajustes | HU-M05-03 | `GET /api/v1/existencias/ajustes/` |

## Estructura de la respuesta de existencias

```json
{
  "producto": {"id": 1, "codigo": "SAR", "nombre": "Saranda"},
  "saldo_tn": 145.50,
  "unidad_medida": "tn",
  "ultimo_movimiento": "2027-03-15T14:22:00-05:00"
}
```

No existe ningún endpoint `PUT` o `PATCH` sobre existencias. Esta ausencia es intencional y verificable: es la forma en que RN-M05-02 se materializa en el contrato de la API.

## Permisos

| Función | Administrador | Administrativo | Supervisor |
|---|:---:|:---:|:---:|
| Consultar existencias | Sí | Sí | Sí |
| Consultar kardex | Sí | Sí | No |
| Registrar ajuste | Sí | No | No |
| Listar ajustes | Sí | Sí | No |

El ajuste queda restringido al Administrador porque su registro es la evidencia del indicador I4. Si cualquier usuario pudiera ajustar, las desviaciones podrían normalizarse sin dejar rastro atribuible.
