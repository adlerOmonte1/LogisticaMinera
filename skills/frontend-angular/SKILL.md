---
name: frontend-angular
description: Implementa el frontend Angular del sistema de control de producción y existencias — componentes standalone con signals, features por módulo con carga diferida, interceptor JWT, guards por rol, formularios reactivos y tablas con Angular Material. Úsala al crear o modificar cualquier cosa bajo frontend/src/app, al escribir un componente, un servicio de feature, un formulario o una tabla, y cuando se mencione Angular, SPA, formulario, interceptor, guard o pantalla.
---

# Frontend Angular

Carga antes `contexto-tesis` y `solid-proyecto`. Fuente: `docs/00-arquitectura/ARQ-02_Arquitectura_Tecnica.md` §4
y el `notas.md` de cada módulo.

## Stack fijado

Angular 17+ con **componentes standalone y signals** (sin NgModules) · Angular Material ·
Angular Service Worker + IndexedDB para M07 · `ngx-charts` solo si se aprueba un dashboard, que hoy
**no está en el alcance** (ninguna de las 34 historias lo cubre).

Elige **Angular Material** y no mezcles con PrimeNG: dos librerías de componentes duplican el peso
del bundle, que es precisamente lo que se carga en un teléfono con conectividad intermitente.

## Estructura

```
frontend/src/app/
  core/               interceptores JWT, guards, manejo de errores, servicio de conectividad
  shared/             componentes, pipes y directivas reutilizables
  features/
    autenticacion/ M01   catalogo/ M02   ingresos/ M03   salidas/ M04
    existencias/   M05   reportes/ M06   sincronizacion/ M07
    auditoria/     M08   busqueda/ M09
  models/             interfaces TypeScript espejo de los serializers
```

Un feature por módulo, con carga diferida (`loadChildren`) y su propio routing. Nombres de archivo en
kebab-case, clases en PascalCase, dominio en español:

```
features/ingresos/ingreso-form.component.ts    class IngresoFormComponent
features/ingresos/ingresos.service.ts          class IngresosService
models/ingreso.model.ts                        interface Ingreso
```

## Reglas no negociables

**1. Ningún componente llama a `HttpClient` directamente.** Cada feature expone un servicio propio
que encapsula sus llamadas. Un `ApiService` global con treinta métodos obliga a cada componente a
depender de todo el sistema (violación de ISP; ver `solid-proyecto`).

**2. Las reglas de negocio no se replican en el cliente como fuente de verdad** (D-08). Angular valida
en el formulario para mejorar la experiencia, pero la validación autoritativa está en el backend. Un
registro que llega por la cola de sincronización de M07 no pasa por el formulario y debe someterse a
las mismas reglas del servidor.

**3. Los campos calculados son `readonly`, nunca `disabled`.** Los campos deshabilitados **no viajan
en el payload** de un formulario reactivo. Es un error que rompe el alta sin dar señal clara. Aplica
al peso neto (HU-M03-01 CA03), que se recalcula con `valueChanges` sobre bruto y tara y no se puede
editar a mano.

**4. Los mensajes de error del servidor se muestran en el campo correspondiente**, no en un cuadro
genérico, y **con el texto literal** que devuelve la API. Ese texto coincide con el criterio de
aceptación y las pruebas lo verifican por igualdad exacta. No lo reformules ni lo traduzcas.

**5. Lo que se oculta por rol también se rechaza en el servidor.** El guard de ruta y el `*ngIf` por
rol son experiencia de usuario; el control real está en `permissions.py`. Ver `backend-auth-permisos`.

## Formulario de ingreso — el crítico

Es la pantalla de la que dependen I1 e I2. Debe cumplir, además de la historia:

- Operable por completo en pantalla de **5 pulgadas sin desplazamiento horizontal** (RNF-M03-05).
- Completable en **menos de 90 segundos** por un usuario capacitado (RNF-M03-03). Cada campo que
  añadas se paga en ese cronómetro; un formulario de treinta campos anularía el beneficio del sistema.
- `inputmode="decimal"` en los campos de peso, para que abra el teclado numérico (RNF-M03-04).
- **Borrador persistido en IndexedDB con cada cambio** (RNF-M03-06), limpiado al confirmar. Si el
  formulario pierde los datos al caerse la conexión, el supervisor vuelve al papel y la latencia
  regresa a los valores del pretest.
- Catálogos de producto y vehículo desde caché, para que el formulario abra sin red.

## Core

| Pieza | Responsabilidad |
|---|---|
| Interceptor JWT | Adjunta el `access`, renueva con el `refresh`, redirige al login al expirar |
| Guard de sesión | Protege las rutas autenticadas |
| Guard de rol | Restringe rutas por rol; complementa —no sustituye— al permiso del servidor |
| Manejo de errores | Traduce el cuerpo uniforme `{codigo, mensaje, detalles}` al campo correspondiente |
| Servicio de conectividad | Estado en línea/sin conexión, consumido por M07 |

## Tablas y listados

Angular Material. Los listados llevan paginación de 25 registros (HU-M03-05), orden por fecha y hora
de pesaje descendente por defecto, y **totales del conjunto filtrado** — número de ingresos y suma de
peso neto. El filtro por titularidad debe presentar propios y externos por separado (HU-M03-05 CA04):
es la lectura directa del indicador I2.

La pantalla de existencias es la ruta predeterminada tras el login del rol Administrativo
(RNF-M05-06). Cada paso de navegación que elimines reduce el tiempo que mide I3.

## Verificación

- [ ] Ningún componente inyecta `HttpClient`.
- [ ] Ningún campo calculado usa `disabled`.
- [ ] Los textos de error visibles coinciden literalmente con los criterios de aceptación.
- [ ] Todos los features se cargan de forma diferida.
- [ ] El formulario de ingreso abre y valida sin conexión.
- [ ] Ninguna pantalla depende de un dashboard o gráfico que no tenga historia de usuario.
