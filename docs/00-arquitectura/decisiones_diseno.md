# Decisiones de diseño fijadas

**Estado:** cerradas salvo las marcadas como pendientes. Reabrir cualquiera exige justificación
escrita, porque todas condicionan la integridad del dominio o la comparabilidad de los registros
durante el periodo de medición.

Cada decisión declara: enunciado, módulos afectados, razón, qué protege y qué ocurre si se revierte.

---

## D-01. El ingreso guarda tres marcas de tiempo independientes

**Módulos afectados:** M03, M07

El ingreso registra tres momentos distintos, y ninguno se deriva de otro:

| Marca | Origen | Editable |
|---|---|---|
| Fecha y hora del ticket | Leída del ticket por el motor, corregible por el usuario | Sí, antes de confirmar |
| Inicio del registro | Asignada por el servidor al recibir la imagen | No |
| Fin del registro | Asignada por el servidor al persistir el ingreso | No |

La primera dice cuándo se pesó el volquete; la segunda, cuándo alguien empezó a registrarlo; la
tercera, cuándo el dato quedó disponible. Son tres hechos distintos del proceso y responden
preguntas distintas.

**Implementación.** Las dos marcas del servidor son `editable=False` y las asigna **el servicio**,
no el ORM: `auto_now_add` fijaría la hora de inserción y no la del inicio real de la operación.
Ningún rol las modifica, y la API rechaza cualquier intento de enviarlas.

**Si se revierte.** Con una sola marca de tiempo no se distingue un ingreso registrado al momento de
otro transcrito tres días después, y el histórico deja de poder explicar cómo se trabajó.

## D-02. El código único lo asigna el servidor, dentro de una transacción con bloqueo

**Módulos afectados:** M03

El código identifica al ingreso como unidad de registro. Lo asigna el servidor al confirmar,
mediante bloqueo sobre la tabla de contadores o secuencia de PostgreSQL. Nunca
`MAX(codigo) + 1` fuera de transacción, y nunca el dispositivo.

**Si se revierte.** Dos registros simultáneos recibirían el mismo código y dejarían de ser
identificables de forma única.

## D-06. La titularidad del vehículo es un atributo del catálogo, no texto libre

**Módulos afectados:** M02, M03, M05

El vehículo se elige del catálogo, y de él se derivan dos datos que el usuario no digita: el tipo de
vehículo del ingreso —propio o externo— y la capacidad de carga, que la regla V4 contrasta contra el
peso neto.

**Si se revierte.** Con la titularidad escrita a mano, el tipo de vehículo dejaría de ser un valor
clasificable y V4 no tendría contra qué comparar el peso neto.

## D-07. El sistema no borra ingresos: los anula

**Módulos afectados:** M03, M09

Un ingreso registrado no se elimina físicamente. Se marca como anulado, con motivo y responsable, y
permanece en el histórico. Los totales lo excluyen; el detalle lo conserva.

**Si se revierte.** No se podría demostrar que el histórico no fue depurado retroactivamente, y
cualquier total sería indefendible.

## D-08. Las reglas de negocio viven en el servidor; el cliente solo muestra el resultado

**Módulos afectados:** todos, con particular fuerza en M05

Angular puede validar en el formulario para mejorar la experiencia, pero la validación autoritativa
está en el backend. Esto vale sin excepción para las reglas V1 a V5: se aplican sobre los datos
propuestos por el reconocimiento y otra vez sobre los confirmados por el usuario.

**Si se revierte.** Una petición que no pase por el formulario entraría sin validar, y el histórico
contendría datos que el sistema declara imposibles.

## D-09. `repositories/` es el lado de lectura, no una abstracción sobre el ORM

**Módulos afectados:** todos

Cada app separa la lectura (`repositories/`) de la escritura (`services/`). La razón es de
rendimiento: las consultas de M07 y M08 habrá que optimizarlas —`select_related`, índices,
agregados— y esa optimización no debe obligar a tocar la lógica de escritura ni a rehacer sus
pruebas.

Lo que **no** es: el patrón Repository clásico, pensado para aislar un ORM que se quiere poder
sustituir. Django ORM ya es la capa de acceso a datos, y envolverlo en una interfaz con una sola
implementación es ceremonia que en la revisión técnica se defiende peor que su ausencia. En
consecuencia:

- Una clase concreta por entidad (`RepositorioIngreso`), sin `Protocol` ni clase base abstracta.
- No escribe: ni `save()`, ni `create()`, ni `update()`, ni `delete()`.
- Devuelve entidades o `QuerySet`, nunca diccionarios listos para la respuesta HTTP: eso es trabajo
  del serializer.
- La abstracción se crea solo cuando exista una segunda implementación real o una prueba que exija
  sustituirla. El reconocedor (D-12), el generador de código (D-02), el reloj y los exportadores de
  M08 la exigen; un repositorio de vehículos, no.

Pregunta previsible en la revisión técnica: «¿por qué repositorios sobre un ORM que ya abstrae la
base?». La respuesta es la de arriba: aquí no abstraen la base, separan lectura de escritura.

## D-10. M07 y M08 son apps de lectura: no tienen `models/` ni `migrations/`

**Módulos afectados:** M07, M08

Ni Consulta ni Consolidación poseen entidad propia. M07 lee `INGRESO` por placa y fecha; M08 agrega
sobre `INGRESO` por mes y tipo de mineral. Ninguno aparece como entidad en el modelo
entidad-relación, y ese documento es la fuente única.

Su estructura es:

```
apps/consulta/         M07              apps/consolidacion/    M08
  repositories/   lectura sobre M03       repositories/   lectura sobre M03
  services/                               exportadores/   una clase por formato
  serializers/                            services/
  views/                                  serializers/
  permissions.py  filters.py              views/
  urls.py  tests/                         permissions.py  filters.py  urls.py  tests/
```

Sin `models/` y sin `migrations/`. Crear paquetes vacíos «por simetría» es peor que no crearlos: un
`models/` vacío invita a que alguien agregue ahí una entidad que debía discutirse primero en el
modelo entidad-relación.

**La regla que esto fija, y que vale para los nueve módulos:** una app solo tiene `models/` si
aporta una entidad al modelo entidad-relación. Si un módulo necesita persistir algo nuevo, la
entidad se añade primero al modelo y después al código, nunca al revés.

`exportadores/` en M08 es la aplicación literal del principio abierto/cerrado: `ExportadorExcel` y
`ExportadorPDF` como clases separadas, y cualquier formato futuro como clase nueva, sin tocar lo
existente.

## D-11. El frontend vive en un repositorio separado, con capas dentro de cada feature

**Módulos afectados:** todos los del cliente

Dos decisiones en una, porque se tomaron juntas.

**Repositorio aparte.** El frontend se despliega como archivos estáticos y el backend como servicio
con base de datos: dos ciclos de vida distintos. Con un solo repositorio, un cambio de estilos
obliga a reconstruir y volver a desplegar la API, y todo despliegue en producción durante la ventana
de observación es un cambio no controlado en las condiciones de trabajo. El costo es que el contrato
de la API deja de estar garantizado por el compilador; se compensa con el esquema OpenAPI en
`/api/v1/docs/` como contrato, la misma convención de commits en ambos historiales y una etiqueta
`M{nn}-cerrado` puesta el mismo día en los dos repositorios.

**Capas dentro del feature.** Cada `features/<modulo>/` se divide en `data-access/` (única puerta a
`HttpClient`), `pages/` (componentes ruteados, con estado) y `ui/` (presentacionales, sin estado).
Es la misma separación por motivo de cambio que se aplica en el servidor. La consecuencia
verificable es que un componente de `ui/` se prueba con entradas y salidas, sin
`HttpTestingController`.

Se descartó un monorepo Nx: aporta límites de dependencia y build incremental, que rinden con varios
equipos y varias aplicaciones. Aquí hay una aplicación y un equipo reducido.

## D-12. El motor de reconocimiento queda detrás de la interfaz `ReconocedorTicket` — *pendiente de elegir el motor*

**Módulos afectados:** M03, M04

El código de negocio no conoce el motor concreto. M03 recibe por inyección un `ReconocedorTicket`
con una operación —dada una imagen, devolver seis campos con su confianza, más el identificador y la
versión del motor— y no sabe si detrás hay OCR local, un servicio en la nube o un modelo multimodal
por API.

**Qué está cerrado:** la interfaz, la inyección y el registro del motor y su versión en cada
reconocimiento.
**Qué está pendiente:** cuál motor. Se decide tras un piloto con 20 a 30 tickets reales de dos o
tres alternativas, comparando exactitud de lectura, costo y dependencia de conexión (DR-02).

**Si se revierte.** Con el motor invocado directamente desde el servicio de registro, cambiarlo
—algo previsible, porque aún no está elegido— obligaría a reescribir M03 y sus pruebas.

## D-13. El dato reconocido no se persiste sin confirmación del usuario

**Módulos afectados:** M03, M04, M05

El resultado del reconocimiento es una **propuesta**. El sistema la presenta, resalta los campos con
confianza inferior al umbral y señala las inconsistencias, pero no guarda nada como dato del ingreso
hasta que el usuario revisa y confirma. Al persistir, se conservan **por separado** el valor
reconocido y el valor confirmado de cada campo, junto con la confianza, el motor y su versión.

**Si se revierte.** Un error de lectura se convertiría en dato oficial sin que nadie lo revisara, y
después sería imposible distinguir qué leyó el motor de qué escribió la persona.

## D-14. Almacenamiento de las imágenes del ticket — *pendiente*

**Módulos afectados:** M03, M07

La imagen es el respaldo del ingreso y debe conservarse íntegra mientras el ingreso exista. Está
pendiente decidir el medio —volumen del servidor o almacenamiento de objetos—, la compresión
admisible sin perder legibilidad, la política de retención y el respaldo.

**Criterio de cierre:** se fija junto con el despliegue, antes de implementar M03.

## D-15. Procesamiento del reconocimiento: síncrono por defecto — *pendiente de confirmar*

**Módulos afectados:** M04

El reconocimiento se ejecuta de forma síncrona dentro de la petición, sin broker de tareas. El
usuario está de pie junto al volquete esperando el resultado: una cola asíncrona añadiría
complejidad de infraestructura y una espera que igualmente habría que mostrar.

**Criterio de cierre:** si el piloto de D-12 muestra tiempos de más de unos pocos segundos por
ticket, se revisa esta decisión y con ella la tabla de contenedores de ARQ-03.

## D-16. El motor, su versión y las reglas no cambian durante la ventana de medición

**Módulos afectados:** M04, M05

Entre el inicio y el fin del periodo de medición no se actualiza el motor de reconocimiento, su
versión ni los parámetros de las reglas V1 a V5. Si una corrección resulta inevitable, se documenta
con fecha y se reporta.

**Si se revierte.** Dos ingresos del mismo periodo habrían sido procesados por sistemas distintos, y
dejarían de ser comparables entre sí.

---

## Decisiones retiradas

Se conservan sus códigos para que el historial siga siendo legible. **Ningún código retirado vuelve
a usarse con otro significado**, salvo los dos casos señalados, que se reasignaron antes de que
llegaran a `main`.

| Código | Decisión original | Motivo del retiro |
|---|---|---|
| D-03 | La hora de registro de un ingreso capturado sin señal es la de captura local | Se retira con el módulo de captura local (DR-01). Con ella desaparece la contradicción que mantenía con D-01 |
| D-04 | La captura sin conexión se decide en la semana 1 | Se retira con el mismo módulo. Queda un RNF de conservación del borrador | <!-- migracion:ok -->
| D-05 | El módulo de búsqueda existe porque un indicador lo exige | Se reformula: M07 existe por RF08 y por su responsabilidad de recuperar un ingreso con su respaldo |
| D-12 *(anterior)* | El kardex es de solo-anexado | Se retira con el inventario de producto terminado, fuera de alcance. El código **D-12 se reasignó** al motor de reconocimiento | <!-- migracion:ok -->
| D-13 *(anterior)* | Cada serie de correlativos tiene su propia tabla de contadores | Existía porque había dos series, ingresos y salidas. Con una sola serie la decisión pierde objeto. El código **D-13 se reasignó** a la confirmación del dato reconocido |

Las decisiones D-12 y D-13 anteriores solo existieron en la rama `feature/M03-ingresos` y nunca
llegaron a `main`; las únicas referencias a ellas están en `apps/salidas`, que se retira en la fase
10 del plan de migración.

## Pendientes que bloquean decisiones

| Pendiente | Bloquea | Momento |
|---|---|---|
| Piloto de motores de reconocimiento | D-12, implementación de M04 | Antes de implementar M04 |
| Medio de almacenamiento y política de retención de imágenes | D-14, implementación de M03 | Junto con el despliegue |
| Valores del catálogo de tipo de mineral, a definir con la empresa | M02, M08 | Antes de implementar M02 |
| Confirmación de la tolerancia de 0,01 t de la regla V1 | M05, conjunto de prueba | Antes de fijar el conjunto de prueba |
| Forma real de agrupar el mineral en cancha | M06, alcance de DR-04 | Antes de implementar M06 |
