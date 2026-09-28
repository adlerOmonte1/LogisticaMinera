---
name: frontend-angular
description: Implementa el frontend Angular del sistema web inteligente de ingreso de mineral — componentes standalone con signals, features por módulo con carga diferida, captura de imagen y pantalla de confirmación, interceptor JWT, guards por rol, formularios reactivos y tablas con Angular Material. Úsala al crear o modificar cualquier cosa bajo el repositorio del frontend, al escribir un componente, un servicio de feature, un formulario o una pantalla, y cuando se mencione Angular, SPA, formulario, interceptor, guard o pantalla.
---

# Frontend Angular

Carga antes `contexto-tesis` y `solid-proyecto`. Fuente:
`docs/model-c4/ARQ-02_Arquitectura_Tecnica.md` §4, `docs/00-arquitectura/GUIA_FRONTEND_ANGULAR.md`
y el `notas.md` de cada módulo.

## Stack fijado

Angular 17+ con **componentes standalone y signals** (sin NgModules) · Angular Material, y nada más:
dos librerías de componentes duplican el peso del bundle, que es lo que se carga en un teléfono en
planta. No hay Service Worker ni almacén con cola de reintento en segundo plano: ese componente
pertenecía a un módulo que ya no forma parte del alcance (DR-01).

## Estructura

```
src/app/
  core/               interceptores JWT, guards, manejo de errores, borrador local del registro
  shared/             componentes, pipes y directivas reutilizables
  features/
    auth/              M01     trazabilidad/   M06
    catalogo/           M02     consulta/       M07
    ingresos/            M03 (incluye pantallas de M04 y M05)
                                consolidacion/  M08
                                auditoria/      M09
  models/             interfaces TypeScript espejo de los serializers
```

Un feature por módulo con pantalla propia, con carga diferida (`loadChildren`) y su propio routing.
**M04 y M05 no tienen feature propia**: sus pantallas —campos reconocidos con su confianza,
inconsistencias señaladas— viven dentro de `features/ingresos/`, porque son parte del mismo flujo de
registro.

Nombres de archivo en kebab-case, clases en PascalCase, dominio en español:

```
features/ingresos/ingreso-form.component.ts    class IngresoFormComponent
features/ingresos/ingresos.service.ts          class IngresosService
models/ingreso.model.ts                        interface Ingreso
```

## Reglas no negociables

**1. Ningún componente llama a `HttpClient` directamente.** Cada feature expone un servicio propio
que encapsula sus llamadas. Un `ApiService` global con treinta métodos obliga a cada componente a
depender de todo el sistema (violación de ISP; ver `solid-proyecto`).

**2. Las reglas de negocio no se replican en el cliente como fuente de verdad** (D-08). Angular
puede replicar las reglas V1 a V5 en el formulario para dar respuesta inmediata, pero la validación
autoritativa está en el backend. Una petición que llegue sin pasar por el formulario debe someterse
a las mismas reglas.

**3. Los campos derivados o asignados por el servidor son `readonly`, nunca `disabled`.** Los
campos deshabilitados **no viajan en el payload** de un formulario reactivo. Es un error que rompe
el alta sin dar señal clara. Aplica al tipo de vehículo (derivado de la placa), al código único y a
las dos marcas de tiempo del servidor.

**4. Los mensajes de error del servidor se muestran en el campo correspondiente**, no en un cuadro
genérico, y **con el texto literal** que devuelve la API. Ese texto coincide con el criterio de
aceptación o con el mensaje de una regla V1 a V5, y las pruebas lo verifican por igualdad exacta. No
lo reformules ni lo traduzcas.

**5. Lo que se oculta por rol también se rechaza en el servidor.** El guard de ruta y el `@if` por
rol son experiencia de usuario; el control real está en `permissions.py`. Ver
`backend-auth-permisos`.

**6. Ningún valor propuesto por el reconocimiento se persiste sin confirmación del usuario** (D-13).
El estado de la propuesta vive en el componente hasta que el usuario confirma; el envío al servidor
ocurre una sola vez, con los valores ya revisados.

## El flujo de registro — el crítico

Es la secuencia de la que depende toda la medición de la investigación: captura, propuesta,
confirmación. Debe cumplir, además de las historias:

- Captura con `<input type="file" accept="image/*" capture="environment">`, que abre la cámara
  trasera directamente, sin pantalla intermedia (RNF-M03-07).
- La imagen se reduce en el cliente con `canvas` **antes** de enviarse; una fotografía de teléfono
  actual supera con facilidad los 5 MB y casi todo ese peso es irrelevante para leer un ticket
  (RNF-M03-04).
- Los campos con confianza por debajo del umbral se resaltan sin depender solo del color
  (RNF-M03-08). Un campo sin lectura se muestra vacío y editable, nunca con un valor inventado.
- Las inconsistencias se muestran junto al campo afectado, con el mensaje literal de la regla.
- `inputmode="decimal"` en los campos de peso, para que abra el teclado numérico.
- **Borrador conservado en el navegador con cada cambio** (RNF-M03-05), descartado al confirmar. Si
  el formulario pierde los datos al caerse la conexión, el usuario vuelve al papel. No hay
  reintento automático: al recuperar la conexión, el usuario retoma y confirma manualmente.
- Catálogos de vehículo y tipo de mineral cargados al abrir el formulario, sin depender de una cola
  de sincronización.

## Core

| Pieza | Responsabilidad |
|---|---|
| Interceptor JWT | Adjunta el `access`, renueva con el `refresh`, redirige al login al expirar |
| Guard de sesión | Protege las rutas autenticadas |
| Guard de rol | Restringe rutas por rol; complementa —no sustituye— al permiso del servidor |
| Manejo de errores | Traduce el cuerpo uniforme `{codigo, mensaje, detalles}` al campo correspondiente |
| Borrador de registro | Conserva imagen y campos editados del registro en curso (RNF-M03-05) |

## Tablas y listados

Angular Material. Los listados llevan paginación de 25 registros, orden por fecha y hora del pesaje
descendente por defecto, y **totales del conjunto filtrado** — número de ingresos y suma de peso
neto, que suma solo los ingresos Registrados. Los anulados y los En proceso aparecen en la lista,
señalados como tales —el neto de un ingreso En proceso se muestra «pendiente del destare», nunca
como cero—: ocultarlos haría creer que un volquete nunca se registró.

La búsqueda por placa y fecha (M07) es la ruta más frecuente después del registro; conviene que esté
accesible desde la pantalla inicial, sin navegar por menús (RNF-M07-07).

## Verificación

- [ ] Ningún componente inyecta `HttpClient`.
- [ ] Ningún campo derivado o asignado por el servidor usa `disabled`.
- [ ] Los textos de error visibles coinciden literalmente con los criterios de aceptación o con las
      reglas V1 a V5.
- [ ] Todos los features se cargan de forma diferida.
- [ ] El borrador del registro sobrevive a la pérdida de conexión y se descarta al confirmar.
- [ ] Ningún dato reconocido se envía al servidor antes de que el usuario lo confirme.
