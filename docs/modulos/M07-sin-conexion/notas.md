# Notas de implementación — M07 Captura sin conexión

## Este módulo condiciona la arquitectura desde la semana 1

Es la advertencia principal. La aplicación web progresiva, el almacenamiento local y la cola de sincronización no son una capa que se añade sobre M03: son decisiones estructurales. Si M03 se construye asumiendo conexión permanente —formularios que consultan el servidor al abrirse, validaciones que dependen de una llamada, selectores que cargan por red—, incorporar M07 obliga a reescribirlo.

Por eso el esqueleto PWA figura como entregable de la semana 1 y M07 se desarrolla en la semana 4, no al final.

## Frontend (Angular)

**Feature:** `features/sincronizacion/` más configuración transversal en `core/`

### Service worker

`@angular/pwa` con `ngsw-config.json`. Estrategia:

| Recurso | Estrategia |
|---|---|
| Interfaz (JS, CSS, HTML) | `prefetch` — debe estar disponible sin red |
| Catálogos (`/api/v1/catalogo/*`) | `freshness` con `maxAge` de 7 días |
| Resto de la API | Sin cacheo — requieren conexión |

### IndexedDB

Se recomienda una biblioteca ligera (`idb`) en lugar de la API nativa, que es verbosa y propensa a errores. Dos almacenes:

```
catalogos     { tipo, datos, fecha_actualizacion }
cola_ingresos { uuid_local, datos, hora_captura, estado, intentos, motivo_rechazo }
```

`estado` toma los valores PENDIENTE, ENVIANDO, RECHAZADO. Los aceptados se retiran del almacén.

### Detección de conectividad

`navigator.onLine` es insuficiente: informa que hay interfaz de red, no que el servidor sea alcanzable. En planta es habitual tener señal aparente sin conectividad real.

Combinar el evento `online` con una verificación efectiva contra un endpoint ligero antes de iniciar la sincronización. Esta distinción es una fuente frecuente de fallos silenciosos en aplicaciones offline.

### Reloj del dispositivo

La hora de captura proviene del dispositivo y puede estar desajustada. RN-M07-02 rechaza horas futuras en el servidor, pero un reloj **atrasado** produciría latencias infladas sin ser detectado.

Mitigación: al iniciar sesión, el cliente compara su hora con la del servidor y almacena el desfase; si supera unos minutos, muestra una advertencia al usuario. Documentar esta limitación en el capítulo de limitaciones de la tesis: es una amenaza a la validez de la medición de I1 que se mitiga pero no se elimina.

## Backend (Django)

**App:** `apps/sincronizacion/`

- El endpoint de lote **reutiliza** el servicio de M03 (`registrar_ingreso`), no reimplementa la lógica. Duplicarla garantizaría que ambas versiones divergieran (RN-M07-08).
- `uuid_local` con restricción de unicidad en base de datos. La idempotencia se implementa así: si el UUID existe, devolver el correlativo previo en lugar de crear un registro nuevo (RN-M07-04).
- Cada elemento del lote se procesa en su propia transacción. Si uno falla, los demás no deben revertirse: el lote no es atómico, sus elementos sí.
- Limitar el tamaño del lote (por ejemplo, 50 elementos) y paginar desde el cliente. Un lote sin límite podría agotar el tiempo de espera en red móvil.

## Pruebas específicas que este módulo exige

Estas pruebas no son opcionales; son la evidencia de que el módulo funciona en las condiciones para las que fue diseñado:

1. Capturar sin conexión, cerrar la aplicación, reiniciar el dispositivo, verificar que el pendiente sigue.
2. Capturar sin conexión, esperar varias horas, sincronizar, y **verificar en el detalle que `hora_registro` es la hora de captura**, no la de sincronización (RNF-M07-05).
3. Sincronizar dos dispositivos simultáneamente y verificar que los correlativos no se duplican.
4. Enviar un lote, cortar la red antes de recibir la respuesta, reintentar, y verificar que no se duplicó el ingreso.
5. Expirar el token durante la operación offline y verificar que la cola sobrevive.
6. Probar en el teléfono real del supervisor, no en emulador (RNF-M07-08).

Los casos de prueba formales están en `../../03-pruebas/`.

## Dependencias

| Depende de | Para |
|---|---|
| M01 | Token de sesión; su expiración no debe descartar la cola |
| M02 | Catálogos precargados en IndexedDB |
| M03 | Servicio de registro reutilizado en el servidor |

| Es requerido por | Para |
|---|---|
| Indicadores I1 e I2 | Su mejora en condiciones reales de conectividad |
