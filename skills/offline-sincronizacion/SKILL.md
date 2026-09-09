---
name: offline-sincronizacion
description: Implementa la captura sin conexión y la sincronización del módulo M07 — PWA instalable, service worker, cola en IndexedDB, identificador local UUID, asignación del correlativo en el servidor y semántica de la hora de registro offline. Úsala al trabajar en features/sincronizacion, apps/sincronizacion, el service worker o el endpoint de lote, y cuando se mencione offline, sin conexión, PWA, cola, sincronización o IndexedDB.
---

# Captura sin conexión (M07)

Carga antes `contexto-tesis`, `backend-django` y `frontend-angular`.
Fuentes: `docs/modulos/M07-sin-conexion/` y `decisiones_diseno.md` D-02, D-03, D-04.

Es el módulo de mayor riesgo del proyecto y el diferenciador del sistema frente a una aplicación web
convencional. También es donde un error de implementación **destruye el indicador I1 sin dar ninguna
señal visible**.

## D-04: no se añade al final

La PWA, el almacenamiento local y la cola de sincronización son decisiones de arquitectura, no una
funcionalidad agregable. Si M03 se construye asumiendo conexión permanente, incorporar M07 obliga a
reescribirlo. Por eso el esqueleto PWA es entregable de la **semana 1** y M07 está en la **semana 4**,
no en la 8.

Si vas a escribir el formulario de ingreso de M03, escríbelo ya sobre el almacenamiento local.

## D-03: la regla que más fácil se rompe

**La `hora_registro` de un ingreso capturado sin conexión es la hora de captura local, NO la de
sincronización.**

```
cliente  ->  {..., uuid_local, hora_captura_local}
servidor ->  hora_registro       = hora_captura_local   (validada)
             hora_sincronizacion = timezone.now()       (solo auditoría)
             correlativo         = asignado ahora
```

Si se tomara la hora de sincronización, I1 mediría el tiempo transcurrido **hasta que hubo señal de
red**, no hasta que se capturó el dato. El indicador quedaría invalidado justo en el módulo diseñado
para mejorarlo, y el resultado del postest sería peor cuanto peor fuera la cobertura móvil de la
planta — exactamente lo contrario de lo que el sistema demuestra.

El servidor **no acepta** una `hora_captura_local` posterior a su propia hora. Un reloj de dispositivo
adelantado produciría latencias negativas.

## D-02: el correlativo lo asigna el servidor

El dispositivo genera un **UUID local** al capturar. El correlativo definitivo se asigna al
sincronizar. Si el dispositivo asignara el correlativo, dos supervisores trabajando sin conexión a la
vez generarían el mismo número y la unidad de análisis de la tesis dejaría de ser identificable de
forma única.

`uuid_local` es único en la base y sirve de **clave de idempotencia**: si un lote se reenvía por un
reintento, el servidor reconoce el UUID ya sincronizado y no crea un duplicado. Sin esto, un reintento
tras un timeout duplica ingresos e infla la producción declarada.

## Cliente

| Pieza | Detalle |
|---|---|
| Manifiesto | Nombre, icono y color; instalable desde el navegador, sin tienda de aplicaciones |
| Service worker | Cachea los recursos del formulario de ingreso y los catálogos de producto y vehículo |
| IndexedDB | Cola de pendientes y borrador del formulario en curso (RNF-M03-06) |
| Bandeja de pendientes | Muestra cuántos ingresos esperan envío, con marca visible |
| Servicio de conectividad | Detecta el cambio de estado y dispara el envío |

Las validaciones de campos obligatorios y de peso **se aplican localmente con los mismos textos** que
en línea (HU-M07-02 CA02). El usuario no debe percibir dos sistemas distintos.

Mensaje al guardar sin conexión, literal: `"Ingreso guardado. Se enviará al recuperar la conexión"`.

## Servidor

```
POST /api/v1/sincronizacion/lote/
```

Recibe un lote y responde **por elemento**, no con un único éxito o fallo global:

- Envío en **orden cronológico de captura**.
- Un elemento que falla **permanece en la cola con el motivo** y **no bloquea a los demás**.
- Reintento automático hasta **tres veces** por elemento; después queda para envío manual.
- Cada elemento recibe su correlativo y se retira de la cola local al confirmarse.

El lote pasa por **las mismas reglas de negocio** que el alta en línea (D-08): un registro que llega
por la cola no pasó por el formulario. Reutiliza `registrar_ingreso()`; no escribas un camino
paralelo de validación más laxa, porque sería el camino por el que entrarían los datos del postest.

## El riesgo principal

**Correlativo bajo sincronización simultánea.** Dos clientes enviando lotes al mismo tiempo es el
punto más probable de fallo de todo el sistema. Debe probarse explícitamente con dos clientes
concurrentes; no basta con probar el alta en línea ni el envío de un lote aislado. El caso de prueba
va en `docs/03-pruebas/`.

## Verificación

- [ ] `hora_registro` de un ingreso offline es la hora de captura local, y existe una prueba que lo
      comprueba comparando contra `hora_sincronizacion`.
- [ ] El servidor rechaza una `hora_captura_local` futura.
- [ ] Reenviar el mismo lote dos veces no duplica ingresos (idempotencia por `uuid_local`).
- [ ] Un elemento con error no impide el envío de los demás.
- [ ] El formulario abre, valida y guarda con el dispositivo en modo avión.
- [ ] La cola envía en orden cronológico de captura.
- [ ] Dos clientes sincronizando a la vez no producen correlativos duplicados ni saltos.
- [ ] El token JWT sigue vigente al recuperar la conexión tras la ventana offline prevista.
