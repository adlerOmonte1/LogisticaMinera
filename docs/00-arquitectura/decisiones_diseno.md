# Decisiones de diseño fijadas

**Estado:** cerradas. Reabrir cualquiera exige justificación escrita, porque todas condicionan un indicador de la tesis o la integridad del dominio.

---

## D-01. La hora de pesaje y la hora de registro son dos campos independientes

**Módulos afectados:** M03, M07
**Indicador en juego:** I1 (latencia entre pesaje y disponibilidad del dato)

La hora de pesaje la ingresa el usuario copiándola del ticket de balanza. La hora de registro la asigna el servidor automáticamente al persistir. La diferencia entre ambas **es** el indicador I1.

Si se colapsan en un solo campo, el indicador desaparece y la dimensión D1 de la variable dependiente queda sin medición. En el código, `hora_registro` es `editable=False` y la asigna **el servicio**, no el ORM. `auto_now_add` sería incorrecto: fija la hora de inserción en la base, y para un ingreso capturado sin conexión el valor correcto es la hora de captura local que envía el cliente (ver D-03). Ningún rol puede modificarla.

## D-02. El correlativo lo asigna el servidor, nunca el dispositivo

**Módulos afectados:** M03, M07

Un ingreso capturado sin conexión recibe un identificador local temporal (UUID generado en el cliente) y obtiene su correlativo definitivo al sincronizar. Si el dispositivo asignara el correlativo, dos supervisores trabajando sin conexión de forma simultánea generarían el mismo número, y la unidad de análisis de la tesis dejaría de ser identificable de forma única.

Implementación: transacción con bloqueo sobre la tabla de correlativos, o secuencia de PostgreSQL. Nunca `MAX(correlativo) + 1` fuera de transacción.

## D-03. La hora de registro de un ingreso offline es la hora de captura local, no la de sincronización

**Módulo afectado:** M07
**Indicadores en juego:** I1, I2

Si se tomara la hora de sincronización, la latencia mediría el tiempo transcurrido hasta que hubo señal de red, no el tiempo hasta que se capturó el dato. Eso invalidaría el indicador justamente en el módulo diseñado para mejorarlo.

Implementación: el cliente envía `hora_captura_local` junto con el registro; el servidor la persiste como `hora_registro` y guarda además `hora_sincronizacion` como campo auxiliar de auditoría. El sistema no acepta una `hora_captura_local` posterior a la hora del servidor.

## D-04. La captura sin conexión se decide en la semana 1, no se añade al final

**Módulo afectado:** M07

La aplicación web progresiva, el almacenamiento local y la cola de sincronización son decisiones de arquitectura, no una funcionalidad agregable. Si M03 se construye asumiendo conexión permanente, incorporar M07 obliga a reescribirlo.

Por eso M07 figura en la semana 4 del cronograma y no en la 8, y por eso el esqueleto PWA aparece como entregable de la semana 1.

## D-05. M09-Búsqueda existe porque el indicador I5 lo exige

**Módulo afectado:** M09

I5 mide el tiempo de recuperación del dato de un ingreso concreto (por padrón, fecha, placa o producto). Ninguno de los diez requerimientos originales cubría búsqueda por criterios. Sin ella, I5 no mejora en el postest y la dimensión D3 queda sin efecto medible. Se incorporó como RF-11.

## D-06. El tipo de vehículo (propio / externo) es un atributo del catálogo, no texto libre

**Módulos afectados:** M02, M03
**Indicador en juego:** I2 (cobertura de registro por tipo de vehículo)

El hallazgo central del diagnóstico es que los volquetes propios se registran peor que los externos, porque a los externos se les paga por viaje y eso obliga a fotografiar el ticket. Demostrarlo con datos requiere que la titularidad del vehículo sea un campo clasificado y obligatorio en el catálogo, no una anotación libre.

## D-07. El sistema no borra ingresos: los anula

**Módulos afectados:** M03, M08

Un ingreso registrado no se elimina físicamente. Se marca como anulado, con motivo y responsable, y permanece en el histórico. La razón es metodológica: si durante la ventana de observación un registro pudiera desaparecer, no se podría demostrar ante el jurado que la cobertura del postest no fue depurada retroactivamente.

## D-08. Las reglas de negocio no se replican en el cliente como fuente de verdad

**Módulos afectados:** todos

Angular puede validar en el formulario para mejorar la experiencia, pero la validación autoritativa está en el backend. Un registro que llega por la cola de sincronización de M07 no pasa por el formulario y debe someterse a las mismas reglas.

## D-09. `repositories/` es el lado de lectura, no una abstracción sobre el ORM

**Módulos afectados:** todos
**Indicadores en juego:** I3, I5

Cada app separa la lectura (`repositories/`) de la escritura (`services/`). La razón es de rendimiento
con consecuencia metodológica: I3 mide el tiempo de determinación del stock e I5 el de recuperación de
un ingreso. Ambas son consultas que habrá que optimizar —`select_related`, índices, agregados— y esa
optimización no debe obligar a tocar la lógica de escritura ni a rehacer sus pruebas.

Lo que **no** es: el patrón Repository clásico, pensado para aislar un ORM que se quiere poder
sustituir. Django ORM ya es la capa de acceso a datos, y envolverlo en una interfaz con una sola
implementación es ceremonia que en sustentación se defiende peor que su ausencia. En consecuencia:

- Una clase concreta por entidad (`RepositorioIngreso`), sin `Protocol` ni clase base abstracta.
- No escribe: ni `save()`, ni `create()`, ni `update()`, ni `delete()`.
- Devuelve entidades o `QuerySet`, nunca diccionarios listos para la respuesta HTTP: eso es trabajo
  del serializer.
- La abstracción se crea solo cuando exista una segunda implementación real o una prueba que exija
  sustituirla — el generador de correlativo (D-02), el reloj y los exportadores de M06 la exigen; un
  repositorio de productos, no.

Pregunta previsible en sustentación: «¿por qué repositorios sobre un ORM que ya abstrae la base?».
La respuesta es la de arriba: aquí no abstraen la base, separan lectura de escritura.

## D-10. M06 y M09 son apps de lectura: no tienen `models/` ni `migrations/`

**Módulos afectados:** M06, M09
**Indicadores en juego:** I5, I6

Ni Consolidados-Reportes ni Búsqueda poseen entidad propia. M06 agrega sobre `INGRESO`, `SALIDA` y
`MOVIMIENTO_STOCK`; M09 consulta `INGRESO` por padrón, fecha, placa o producto. Ninguno de los dos
aparece como entidad en el modelo entidad-relación, y ese documento es la fuente única.

En consecuencia, su estructura es:

```
apps/reportes/          M06            apps/busqueda/        M09
  repositories/   lectura sobre M03/M04/M05    repositories/  lectura sobre M03
  exportadores/   una clase por formato (OCP)  services/
  services/                                    serializers/
  serializers/                                 views/
  views/                                       permissions.py  filters.py  urls.py  tests/
  permissions.py  filters.py  urls.py  tests/
```

Sin `models/` y sin `migrations/`. Crear paquetes vacíos «por simetría» es peor que no crearlos: un
`models/` vacío invita a que alguien agregue ahí una entidad que debía discutirse primero en el
modelo ER, y un `migrations/` vacío hace creer que el módulo tiene esquema propio cuando no lo tiene.

**La regla que esto fija, y que vale para los nueve módulos:** una app solo tiene `models/` si aporta
una entidad al modelo entidad-relación. Si un módulo necesita persistir algo nuevo, la entidad se
añade primero al ERD y después al código, nunca al revés. Aplica a M07: si la cola de sincronización
llegara a necesitar un registro de lote, ese registro se discute en el ERD antes de existir en
`apps/sincronizacion/models/`.

`exportadores/` en M06 es la aplicación literal del principio abierto/cerrado: `ExportadorExcel` y
`ExportadorPDF` hoy, y el formato de declaración semestral —pendiente hasta la semana 7— como clase
nueva, sin tocar lo existente. Es el único caso del backend donde la abstracción está justificada de
antemano, porque la segunda implementación ya existe.

## D-11. El frontend vive en un repositorio separado, con capas dentro de cada feature

**Módulos afectados:** todos los del cliente
**Indicador en juego:** ninguno de forma directa; protege la ventana de observación

Dos decisiones en una, porque se tomaron juntas.

**Repositorio aparte.** El frontend se despliega como archivos estáticos y el backend como servicio
con base de datos: dos ciclos de vida distintos. Con un solo repositorio, un cambio de estilos obliga
a reconstruir y volver a desplegar la API, y todo despliegue en producción durante la ventana de
observación es una amenaza a la validez interna (`ARQ-02` §7). El costo es que el contrato de la API
deja de estar garantizado por el compilador; se compensa con el esquema OpenAPI en `/api/v1/docs/`
como contrato, la misma convención de commits en ambos historiales y una etiqueta `M{nn}-cerrado`
puesta el mismo día en los dos repositorios.

**Capas dentro del feature.** Cada `features/<modulo>/` se divide en `data-access/` (única puerta a
`HttpClient`), `pages/` (componentes ruteados, con estado) y `ui/` (presentacionales, sin estado). Es
la misma separación por motivo de cambio que ya se aplica en el servidor. La consecuencia verificable
es que un componente de `ui/` se prueba con entradas y salidas, sin `HttpTestingController`: eso es
lo que sostiene la característica *capacidad de ser probado* de ISO/IEC 25010 que afirma la tesis.

Se descartó un monorepo Nx: aporta límites de dependencia y build incremental, que rinden con varios
equipos y varias aplicaciones. Aquí hay una aplicación, un desarrollador y ocho semanas.

M07 no tiene carpeta en `features/`: la captura sin conexión es transversal y vive en `core/` como
interceptor más cola. Si fuera una pantalla, M03 tendría que saber si hay red — la dependencia que
D-04 prohíbe.

## Pendientes que bloquean decisiones

| Pendiente | Bloquea | Fecha límite |
|---|---|---|
| Criterio de estimación de merma por humedad | M04, indicador I4 | Antes de la semana 5 |
| Formato oficial de declaración semestral | M06 | Antes de la semana 7 |
| Confirmación de tamaño de muestra para D3 con la asesora | Análisis inferencial | Antes de cerrar el capítulo III |
