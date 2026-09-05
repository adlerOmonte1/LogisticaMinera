# Requerimientos funcionales — M07 Captura sin conexión

**RF global asociado:** RF-10 — Permitir el registro de ingresos sin conexión, con sincronización posterior

| Función | Descripción | HU | Ubicación |
|---|---|---|---|
| Instalación como PWA | Manifiesto y service worker | HU-M07-01 | Cliente |
| Cacheo de interfaz y catálogos | Precarga y revalidación | HU-M07-01 | Cliente |
| Registro local de ingreso | Persistencia en IndexedDB | HU-M07-02 | Cliente |
| Detección de conectividad | Escucha de eventos de red | HU-M07-03 | Cliente |
| Sincronización en lote | Envío de la cola | HU-M07-03 | `POST /api/v1/sincronizacion/lote/` |
| Gestión de cola y reintentos | Estados y contadores | HU-M07-04 | Cliente |
| Consulta de pendientes | Lista local | HU-M07-05 | Cliente |
| Filtro de ingresos offline | Consulta en servidor | HU-M07-05 | `GET /api/v1/ingresos/?capturado_offline=true` |

## Contrato del endpoint de sincronización

**Solicitud**
```json
{
  "ingresos": [
    {
      "uuid_local": "550e8400-e29b-41d4-a716-446655440000",
      "hora_captura_local": "2027-03-15T18:42:00-05:00",
      "fecha_pesaje": "2027-03-15",
      "hora_pesaje": "18:35:00",
      "numero_ticket": "004521",
      "id_vehiculo": 7,
      "id_producto": 1,
      "peso_bruto_tn": 32.40,
      "tara_tn": 12.10
    }
  ]
}
```

**Respuesta**
```json
{
  "resultados": [
    {
      "uuid_local": "550e8400-e29b-41d4-a716-446655440000",
      "estado": "ACEPTADO",
      "correlativo": "ING-2027-000342"
    },
    {
      "uuid_local": "660e8400-e29b-41d4-a716-446655440001",
      "estado": "RECHAZADO",
      "codigo": "TICKET_DUPLICADO",
      "mensaje": "El ticket número 004520 ya fue registrado en el ingreso ING-2027-000339"
    }
  ]
}
```

Cada elemento se procesa de forma independiente: el rechazo de uno no impide el procesamiento de los demás. El cliente actualiza su cola según el estado devuelto para cada `uuid_local`.

## Funciones que requieren conexión

| Función | Disponible sin conexión |
|---|:---:|
| Registrar ingreso | Sí |
| Consultar pendientes locales | Sí |
| Consultar catálogos | Sí (versión local) |
| Consultar existencias | No |
| Buscar ingresos | No |
| Generar reportes | No |
| Registrar salidas | No |

El alcance offline se limita deliberadamente al registro de ingresos. Ampliarlo a salidas o existencias exigiría resolver conflictos de saldo entre dispositivos, complejidad que no aporta a ningún indicador de la tesis.
