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
| Fecha y hora del pesaje | La fecha se reconoce del ticket —en el registro sin foto la digita el usuario—; la hora la indica el usuario sobre una propuesta del sistema con la hora actual, porque el ticket no la imprime (DR-09, DR-11) | Sí, antes de confirmar |
| Inicio del registro | Asignada por el servidor al recibir la imagen o, en el registro sin foto, cuando el usuario elige esa opción (DR-13) | No |
| Fin del registro | Asignada por el servidor cuando el usuario confirma el ingreso | No |

La propuesta de hora la calcula el servidor con su reloj al abrir la revisión, no el navegador.
Proponer la hora actual no colapsa la primera marca con las otras dos: el usuario la ajusta a la del
pesaje real, y el sistema conserva las tres como valores distintos. Ejemplo de DR-11: pesaje a las
16:00, inicio del registro a las 16:05 y fin a las 16:06.

La primera dice cuándo se pesó el volquete; la segunda, cuándo alguien empezó a registrarlo; la
tercera, cuándo el dato quedó disponible. Son tres hechos distintos del proceso y responden
preguntas distintas.

El fin del registro se asigna al confirmar, **también cuando el ingreso queda En proceso** por estar
pendiente el destare del vehículo (D-17). El destare ocurre después, cuando el volquete ya descargó,
y no mueve ninguna de las tres marcas: si lo hiciera, el tiempo de registro de un primer viaje
incluiría el tiempo de descarga, que no es trabajo de registro.

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

El vehículo se elige del catálogo, y de él se derivan tres datos que el usuario no digita en cada
ingreso: el tipo de vehículo —propio o externo—, la capacidad de carga, que la regla V4 contrasta
contra el peso neto, y la tara, con la que se calcula ese peso neto (D-17).

**Si se revierte.** Con la titularidad escrita a mano, el tipo de vehículo dejaría de ser un valor
clasificable y V4 no tendría contra qué comparar el peso neto.

## D-07. El sistema no borra ingresos: los anula

**Módulos afectados:** M03, M06, M09

Un ingreso registrado no se elimina físicamente. Se marca como anulado, con motivo y responsable, y
permanece en el histórico. Los totales lo excluyen; el detalle lo conserva.

El mismo criterio alcanza al lote de proceso, a sus partes, a sus pasos por etapa y a sus bigbags
(M06): todas sus claves foráneas son `PROTECT`, y un lote Cerrado no admite cambios.

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
  M07 y M08 la exigen; un repositorio de vehículos, no. Tampoco el almacén de imágenes: Django ya
  ofrece esa abstracción (D-18).

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
  exportadores/   CSV del listado
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

`exportadores/` es la aplicación literal del principio abierto/cerrado: en M08, `ExportadorExcel`,
el único formato de la primera versión; en M07, `ExportadorCSVListado` (DR-30). Cualquier formato
futuro —un PDF del consolidado, por ejemplo— es una clase nueva, sin tocar las existentes.

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

## D-12. El motor de reconocimiento queda detrás de la interfaz `ReconocedorTicket` — *motor pendiente; adaptador local provisional*

**Módulos afectados:** M03, M04

El código de negocio no conoce el motor concreto. M03 recibe por inyección un `ReconocedorTicket`
con una operación —dada una imagen, devolver tres campos (placa, fecha y peso bruto) con su confianza, más el identificador y la
versión del motor— y no sabe si detrás hay OCR local, un servicio en la nube o un modelo multimodal
por API.

**Qué está cerrado:** la interfaz, la inyección y el registro del motor y su versión en cada
reconocimiento.
**Qué está pendiente:** cuál motor. Se decide tras un piloto con 20 a 30 tickets reales de dos o
tres alternativas, comparando exactitud de lectura, costo y dependencia de conexión (DR-02).

**Solución provisional (23/10/2026).** El motor se elige cuando el sistema sea funcional, con el
piloto ejecutado sobre el registro completo y, a más tardar, antes del congelamiento de la semana 8
(D-16). Mientras tanto, el primer adaptador de `ReconocedorTicket` se ejecuta **dentro del mismo
backend**, con procesamiento local, sin servicio externo ni credenciales. Las pruebas automatizadas
usan un adaptador determinista. Cambiar al motor elegido es añadir su adaptador y configurarlo: M03
no cambia.

**Si se revierte.** Con el motor invocado directamente desde el servicio de registro, cambiarlo
—algo previsible, porque aún no está elegido— obligaría a reescribir M03 y sus pruebas.

## D-13. El dato reconocido no se persiste sin confirmación del usuario

**Módulos afectados:** M03, M04, M05

El resultado del reconocimiento es una **propuesta**. El sistema la presenta, resalta los campos con
confianza inferior al umbral y señala las inconsistencias, pero no guarda nada como dato del ingreso
hasta que el usuario revisa y confirma. Al persistir, se conservan **por separado** el valor
reconocido y el valor confirmado de cada campo, junto con la confianza, el motor y su versión.

**Registro sin foto (DR-13).** Cuando el ticket se extravió o no puede fotografiarse, no hay
reconocimiento: el usuario digita los datos, el ingreso no tiene `RECONOCIMIENTO_TICKET` y queda
marcado «sin respaldo fotográfico» con su motivo. Las reglas V1 a V5 se aplican igual (D-08). D-13
no se relaja: no hay propuesta que persistir sin confirmar.

**Si se revierte.** Un error de lectura se convertiría en dato oficial sin que nadie lo revisara, y
después sería imposible distinguir qué leyó el motor de qué escribió la persona.

## D-17. El peso neto lo calcula el sistema con la tara del vehículo

**Módulos afectados:** M02, M03, M05, M06, M08

El ticket de balanza imprime un solo peso, el bruto (DR-09). La tara es un atributo del vehículo: se
obtiene en el destare de su primer viaje, la digita el usuario y se mantiene por decisión de la
Gerencia (DR-10). El peso neto lo calcula el servidor al confirmar el ingreso, como peso bruto menos
la tara vigente del vehículo, y no es editable.

El ingreso **conserva la tara que se aplicó** como dato propio, no como referencia al catálogo. Si la
Gerencia decide después actualizar la tara de un vehículo, los ingresos ya registrados mantienen el
neto con el que se registraron; solo los siguientes usan la tara nueva.

Mientras el vehículo no tiene tara —primer viaje, antes del destare—, el ingreso se confirma en
estado **En proceso**: tiene código, peso bruto y marcas de tiempo, pero no peso neto. No cuenta en
la consolidación ni puede asignarse a un lote. Al registrarse la tara, el sistema calcula el neto y
el ingreso pasa a Registrado.

**Si se revierte.** Con un neto digitado en cada ingreso, dos registros del mismo vehículo podrían
aplicar taras distintas sin que nada lo advirtiera. Con la tara como referencia viva al catálogo, un
cambio de tara reescribiría en silencio el histórico de toneladas.

## D-14. Almacenamiento de las imágenes del ticket — *provisional en el backend; medio definitivo pendiente*

**Módulos afectados:** M03, M07

La imagen es el respaldo del ingreso y debe conservarse íntegra mientras el ingreso exista. Solo
falta en el ingreso registrado sin foto, que lleva su marca y su motivo (DR-13). Está
pendiente decidir el medio —volumen del servidor o almacenamiento de objetos—, la compresión
admisible sin perder legibilidad, la política de retención y el respaldo.

**Criterio de cierre:** se fija junto con el servicio de alojamiento que se defina para la
presentación del sistema. Lo que ya no está pendiente es **cómo accede el código** al almacén: por la
API de almacenamiento de Django (D-18), de modo que cerrar D-14 cambia la configuración y no el código.

**Solución provisional (23/10/2026).** Hasta entonces, las imágenes se guardan en el **mismo
backend**: el almacenamiento de archivos de Django sobre el volumen con nombre `media`, montado en el
contenedor del backend, en desarrollo, en preproducción y en la primera puesta en marcha. La
compresión no se aplica todavía; la retención es la del propio ingreso, que nunca se borra (D-07), y
el respaldo es el mínimo de D-20.

## D-18. El almacén de imágenes se usa a través de la API de almacenamiento de Django

**Módulos afectados:** M03, M07 · **Fecha:** 23/10/2026

`ServicioIngreso` guarda la imagen del ticket por el campo `ImageField` del ingreso, que delega en el
almacenamiento de Django (`Storage`) configurado para cada entorno: el sistema de archivos local en
desarrollo y, en producción, el medio que fije D-14 —un volumen del servidor o un servicio de objetos
mediante `django-storages`—. M07 sirve la imagen leyendo del mismo almacenamiento, siempre detrás de
la vista que comprueba la sesión (RN-M07-06).

No se define una interfaz propia `AlmacenImagenes` ni se inyecta en el servicio. Django ya ofrece
esa abstracción, con implementaciones intercambiables por configuración y un almacenamiento en
memoria para las pruebas. Envolverla en otra interfaz con una sola implementación es la ceremonia
que D-09 descarta. `ServicioIngreso` conserva así cuatro dependencias inyectadas: reconocedor,
validador, generador de código y reloj.

**Qué protege.** Que cerrar D-14 sea un cambio de configuración y no de código, y que el caso de uso
del registro no dependa del medio físico donde termina la fotografía.

**Si se revierte.** Una interfaz propia obligaría a mantener dos abstracciones del mismo almacén y a
decidir en cada módulo cuál usar; la imagen podría guardarse por una y servirse por la otra.

## D-19. El listado de ingresos pertenece solo a M07

**Módulos afectados:** M03, M07 · **Fecha:** 23/10/2026

El listado de ingresos con filtros, totales del conjunto y exportación es de M07 (HU-M07-02), el lado
de lectura del sistema (D-10). M03 no expone un listado general: conserva solo lo que su flujo de
escritura necesita, que es el recurso de un ingreso —para corregirlo, revertir su última corrección
o anularlo— y la lista de ingresos pendientes de destare de HU-M03-04.

**Qué protege.** Que haya un solo listado y un solo cálculo del total del conjunto. Con dos listados
sobre la misma entidad, cada uno con sus filtros, el total de la pantalla podría diferir del de la
consulta o del consolidado sin que ninguna prueba de módulo lo advirtiera.

**Si se revierte.** Dos endpoints con el mismo propósito terminan divergiendo en filtros, orden y
criterio de suma, y la interfaz no sabría cuál consumir.

## D-20. Respaldo mínimo ejecutable ahora; servicio y política definitivos para la presentación

**Módulos afectados:** todos · **Fecha:** 23/10/2026

Desde la semana 1 el sistema incluye un procedimiento de respaldo y restauración que se puede
ejecutar a demanda en cualquier entorno: un volcado de la base con `pg_dump` y una copia comprimida
del volumen `media` con las imágenes, tomados en el mismo momento y fechados juntos, y el
procedimiento inverso para restaurarlos. Su verificación es una restauración de prueba en un entorno
limpio, que debe devolver los mismos ingresos con sus imágenes.

El **servicio de alojamiento** que se usará en la presentación del sistema y su **política de
respaldo** —frecuencia, retención, ubicación fuera del servidor y responsable— se definen junto con
ese servicio, porque dependen de lo que ofrezca. Antes de que el sistema entre en operación real
deben estar definidos y con una restauración probada (skill `despliegue-docker`).

**Qué protege.** El histórico que el sistema existe para conservar: ingresos que no se borran (D-07)
y sus fotografías, que son su respaldo. Sin un procedimiento probado, una falla del servidor los
perdería juntos.

**Si se revierte.** Dejar el respaldo para el final convierte la primera falla en una pérdida
irrecuperable, y una copia que nunca se restauró no garantiza que sirva.

## D-21. Códigos de las rutas del lote

**Módulos afectados:** M06 · **Fecha:** 23/10/2026

Las tres rutas de DR-16 se codifican con la secuencia de etapas que recorren después del secado:

| Código | Etapas después del secado | Nombre en pantalla |
|---|---|---|
| `ZARANDEO_ENSACADO` | Zarandeo y ensacado | Zaranda |
| `MOLIENDA_ENSACADO` | Molienda y ensacado | Molido |
| `ZARANDEO_MOLIENDA_ENSACADO` | Zarandeo, molienda y ensacado | Zarandeado y molido |

Se descartan los códigos propuestos antes, `ZARANDEO`, `MOLIENDA` y `AMBAS`: los dos primeros
coinciden con los códigos de etapa de `ETAPA_PROCESO`, de modo que `ZARANDEO` significaría a la vez
una etapa y una ruta, y `AMBAS` no dice cuáles. Con la secuencia completa, el código se lee igual en
la base, en la API y en los registros de auditoría, y no admite dos interpretaciones. Los nombres en
pantalla son los de la maqueta.

**Si se revierte.** Un código que coincide con el de una etapa invita a comparar una ruta con una
etapa en el código —por ejemplo, al calcular cuántas etapas faltan— y a contar mal el recorrido.

## D-22. Ninguna operación de la API usa `DELETE`

**Módulos afectados:** M06 y todos · **Fecha:** 23/10/2026

La regla «nada se elimina» (D-07) se aplica sin excepciones también a los vínculos. Las dos
operaciones de M06 que antes se expresaban como `DELETE` pasan a acciones explícitas:

| Operación | Endpoint | Efecto en la base |
|---|---|---|
| Retirar un ingreso del lote o trasladarlo (DR-29) | `POST /api/v1/lotes/{id}/ingresos/{id_ingreso}/retirar/` | `INGRESO.id_lote` pasa a nulo; el evento de auditoría conserva el lote del que salió |
| Quitar un tipo de mineral de la lista del lote (DR-27) | `POST /api/v1/lotes/{id}/minerales/{id_tipo}/quitar/` | La fila de `LOTE_MINERAL` no se borra: recibe la fecha y el usuario de su retiro (baja lógica) |

`ViewSetBase` no expone `destroy` en ningún módulo, y la revisión rechaza cualquier `DELETE` escrito a
mano.

**Qué protege.** Que la regla no tenga excepciones que haya que recordar, y que la lista de minerales
de un lote pueda reconstruirse tal como estaba en cualquier momento.

**Si se revierte.** Un `DELETE` admitido «solo para vínculos» abre la puerta a otros, y la fila
borrada de `LOTE_MINERAL` deja una autorización de otro mineral sin rastro en la base.

## D-23. Convención de códigos HTTP de la API

**Módulos afectados:** todos · **Fecha:** 23/10/2026

Toda respuesta de error lleva el cuerpo uniforme `{"codigo", "mensaje", "detalles"}` de ARQ-02 §6, y
`mensaje` coincide literalmente con el criterio de aceptación. El código HTTP sigue esta tabla, que
recoge la que ya usan los diagramas de secuencia de los módulos y el manejador de errores del backend:

| Código | Cuándo | Ejemplo |
|---|---|---|
| 200 | Consulta u operación completada | Corrección guardada; consolidado del mes |
| 201 | Alta de un recurso | Ingreso registrado; lote abierto |
| 400 | Datos inválidos o regla de negocio incumplida por lo que se envía | Campos obligatorios; V2, V3 o V5; fracciones que no suman la unidad |
| 401 | Falta de autenticación: credenciales inválidas, cuenta inactiva, sesión expirada o token inválido | «Usuario o contraseña incorrectos» |
| 403 | El rol no autoriza la operación, o la cuenta debe cambiar su contraseña temporal | «Acción no autorizada» |
| 404 | El recurso no existe | Ingreso o lote inexistente |
| 409 | La operación choca con el estado actual del recurso | Ingreso ya anulado; lote cerrado; vehículo con tara; mineral ya zarandeado |
| 423 | Cuenta bloqueada temporalmente por intentos fallidos | «Cuenta bloqueada temporalmente…» |

En el dominio, las excepciones de `common/excepciones.py` se traducen así en el manejador uniforme:
`ErrorDeValidacionDeDominio` a 400, `AccionNoAutorizada` a 403 y `ConflictoDeConcurrencia` —el
conflicto de estado— a 409.

**Qué protege.** Que la interfaz y las pruebas de Postman sepan qué esperar de cada rechazo sin leer
el código, y que un mismo tipo de error responda igual en los nueve módulos.

**Si se revierte.** Cada módulo elegiría su código, el interceptor del frontend tendría que distinguir
casos que deberían ser uno y las pruebas de contrato dejarían de ser comparables.

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
llegaron a `main`; las únicas referencias a ellas están en `apps/salidas`, que se retira en la
preparación del repositorio (`../01-plan/PLAN_DE_TRABAJO.md` §8).

## Pendientes que bloquean decisiones

| Pendiente | Bloquea | Momento |
|---|---|---|
| Piloto de motores de reconocimiento | D-12. M04 se implementa con el adaptador local provisional | Con el sistema funcional, antes del congelamiento de la semana 8 |
| Medio de almacenamiento definitivo, retención y respaldo de imágenes | D-14 y D-20. M03 se implementa con el almacenamiento provisional en el backend | Con el servicio de alojamiento de la presentación |
| Servicio de alojamiento y política de respaldo de la base | D-20 | Con la presentación del sistema, antes de la operación real |
| Valores del catálogo de tipo de mineral, a definir con la empresa | M02, M08 | Antes de implementar M02 |
| ~~Quién registra el destare en planta y cómo se avisa de un vehículo pendiente de destarar (DR-10)~~ — **resuelto por DR-25**: cualquiera de los tres roles, sin plazo; la lista de pendientes de destare (HU-M03-04) es el aviso | — | — |
| ~~Forma real de agrupar el mineral en cancha y de decidir la ruta de cada lote o parte~~ — **resuelto el 22/10/2026** (`../REVISION_TECNICA_V2.md` §7, Q-10): la agrupación se hace en el sistema, con los lotes de M06 y según los roles (DR-23) | — | — |
| Validación con los usuarios del uso de los tres roles y su matriz de permisos (DR-23) | M01 | Antes de implementar M01 |
