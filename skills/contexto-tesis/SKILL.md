---
name: contexto-tesis
description: Carga el contexto del sistema web inteligente para el control de inventarios de ingreso de mineral antes de redactar, ampliar o revisar cualquier documento de docs/ (historias de usuario, requerimientos, diagramas, notas de implementación). Aporta la responsabilidad de cada módulo M01 a M09, los requerimientos funcionales RF01 a RF10, los roles, las decisiones de diseño vigentes, las reglas de nomenclatura y, como referencia única dentro de skills/, el marco de la tesis (variables, indicadores, tareas y reglas de validación). Úsala como primer paso de toda tarea de documentación y siempre que aparezcan siglas como HU-M, RN-M, RNF-M, RU-M, RS-M, RF01 o D-nn.
---

# Contexto de la tesis

Cárgalo antes de escribir una sola línea en `docs/`. Sin él, se producen documentos correctos
como software y **desalineados con el sistema que la tesis mide**.

## Qué se está documentando

Un **sistema web inteligente** (Django REST + Angular) para el control de inventarios de ingreso
de mineral en la planta de procesamiento de Pillcomarca de la empresa Construcción y Minería
(Huánuco). Solo entra en el alcance el ingreso de mineral óxido a planta; la mina de Chaulán y el
sulfuro quedan fuera.

El ticket de balanza **se fotografía, se reconoce y se valida antes de persistir**: el usuario
captura la imagen, el sistema propone los datos leídos, señala inconsistencias, el usuario corrige
y confirma, y solo entonces el servidor asigna el código único y conserva la imagen como respaldo.

El diagnóstico encontró que:

- El ticket de balanza se anota en papel y se transcribe después en la oficina, con horas o días
  de espera entre el pesaje y el registro.
- El respaldo en papel es difícil de recuperar cuando se necesita verificar un ingreso concreto.
- El total mensual por producto se reconstruye a mano y no siempre se obtiene.

## Principio rector de la documentación

**La documentación describe un sistema, no una tesis.** Cada módulo existe por una
responsabilidad del dominio (registro, reconocimiento, validación, trazabilidad, consulta,
consolidación, catálogo, acceso, auditoría), no por el indicador que sostiene. La relación
tesis ↔ sistema se registra en **un solo lugar**: `docs/02-trazabilidad/matriz_HU_RF_indicador.md`
(HU → RF → indicador → tarea → caso de prueba). Esta skill es el resumen de ese marco para el
agente. Ningún archivo de `docs/modulos/` cita indicadores ni contiene secciones «Relación con el
indicador» o «qué se rompe en la tesis»; lo que antes se justificaba «porque protege una medición»
se expresa como regla de negocio o RNF con su consecuencia en términos del dominio y su método de
verificación.

## Marco de la tesis (referencia)

**Título:** Efecto de un sistema web inteligente en el control de inventarios de ingreso de
mineral en la empresa Construcción y Minería, Huánuco, 2027. Diseño preexperimental con pretest y
postest; unidad de análisis: el ingreso de mineral registrado mediante ticket de balanza.

**Variable independiente — sistema web inteligente.** Se evalúa una sola vez, después de la
implementación.

| Dimensión | Indicador | Sigla | Instrumento |
|---|---|---|---|
| D1 Funcionalidad del sistema | % de requerimientos funcionales cumplidos | RFC | Lista de control de funcionalidad (10 RF) |
| D1 Funcionalidad del sistema | % de casos de prueba superados | CPS | Lista de control de funcionalidad (CP01 a CP10) |
| D2 Capacidad inteligente | Exactitud del reconocimiento automático del ticket | ERA | Ficha de capacidad inteligente, hoja A |
| D2 Capacidad inteligente | Tasa de detección de inconsistencias | TDI | Ficha de capacidad inteligente, hoja B |
| D3 Usabilidad del sistema | Puntaje System Usability Scale (≥ 68 aceptable) | SUS | Cuestionario SUS |
| D3 Usabilidad del sistema | % de tareas completadas sin asistencia | TCA | Ficha de capacidad inteligente, hoja C |

**Variable dependiente — control de inventarios de ingreso de mineral.** Se mide por observación
directa de cada ingreso (ficha de observación), no desde consultas al sistema; el sistema debe
conservar marcas de tiempo confiables porque sirven para triangular el postest.

| Dimensión | Indicador | Fórmula por ingreso | Unidad |
|---|---|---|---|
| D1 Oportunidad del registro | I1 Tiempo de espera del registro | Inicio del registro − fecha y hora del ticket | h |
| D1 Oportunidad del registro | I2 Tiempo de registro del ingreso | Fin del registro − inicio del registro | min |
| D2 Integridad del registro | I3 Completitud del registro | Campos consignados / 7 × 100 | % |
| D2 Integridad del registro | I4 Tiempo de recuperación del respaldo | Consulta → presentación del ticket y sus datos | min |
| D3 Consolidación de la producción | I5 Tiempo de consolidación | Solicitud → entrega del total acumulado del mes por producto que incluye el ingreso | min |
| D3 Consolidación de la producción | I6 Grado de trazabilidad | Etapas vinculadas / 4 × 100 | % |

**Campos de completitud:** C1 placa · C2 fecha y hora · C3 peso bruto · C4 tara · C5 peso neto ·
C6 tipo de mineral · C7 tipo de vehículo (propio o externo).
**Etapas del proceso:** secado, zarandeo, molienda, ensacado.

**Tareas de usabilidad (hoja C):** T01 registrar un ingreso a partir de la imagen del ticket ·
T02 corregir un dato reconocido de forma incorrecta · T03 consultar un ingreso por placa y fecha ·
T04 vincular un ingreso con una etapa del proceso · T05 obtener el total acumulado mensual por
producto · T06 exportar el total acumulado mensual por producto.

**Reglas de validación (hoja B):**

| Regla | Inconsistencia | Tipo |
|---|---|---|
| V1 | Peso neto distinto de peso bruto menos tara (tolerancia 0,01 t) | Bloqueante |
| V2 | Tara mayor o igual que el peso bruto | Bloqueante |
| V3 | Placa con formato inválido | Bloqueante |
| V4 | Peso neto fuera del rango de carga del vehículo (capacidad del catálogo) | Exige justificación |
| V5 | Fecha del ticket posterior a la fecha de registro | Bloqueante |

**Conjunto de prueba de la capacidad inteligente:** ERA sobre 50 tickets reales × 6 campos; TDI
sobre 10 inconsistencias sembradas, 2 por regla. Motor y reglas congelados durante la medición.

> **Regla:** los códigos I1 a I6, RFC, CPS, ERA, TDI, SUS, TCA, T01 a T06 y C1 a C7 solo se citan
> en esta skill y en la matriz de trazabilidad; **nunca en `docs/modulos/`**. Las reglas V1 a V5
> sí se citan en los módulos, porque son reglas del sistema.

## Exigencias transversales

El diseño preexperimental exige que durante la ventana de observación ningún registro desaparezca
ni el sistema cambie de condiciones. De ahí cuatro exigencias que atraviesan todo el repositorio:

1. **Nada se elimina.** Baja lógica y anulación con motivo; jamás `DELETE` físico.
2. **Todo queda atribuido.** Usuario y marca de tiempo en cada operación.
3. **El ingreso guarda tres marcas de tiempo independientes.** `fecha_hora_ticket` se lee del
   ticket y es editable antes de confirmar; `hora_inicio_registro` y `hora_fin_registro` las asigna
   el servidor y ningún rol las edita. Colapsarlas «para simplificar» destruye la medición.
4. **Ningún dato reconocido se persiste sin confirmación del usuario** (D-13). El resultado del
   reconocimiento es una propuesta; el sistema conserva por separado el valor reconocido y el
   valor confirmado de cada campo.

## Roles

| Rol | Código | Alcance |
|---|---|---|
| Administrador | `ADMINISTRADOR` | Acceso total, incluida gestión de usuarios, catálogos y anulaciones |
| Administrativo | `ADMINISTRATIVO` | Registro, corrección, consultas, consolidación y exportación |
| Supervisor de planta | `SUPERVISOR` | Registro y consulta |

## Requerimientos funcionales

Los RF son la lista de control validada por expertos (Anexo 03 de la tesis). Son **globales** y
constituyen el denominador del avance: 10 RF, no un número de módulos. RNF, RN, RU y RS se
numeran **por módulo** porque su alcance es local.

| RF | Descripción | Módulo principal |
|---|---|---|
| RF01 | Registrar el ingreso de mineral con la imagen del ticket de balanza | M03 |
| RF02 | Reconocer automáticamente placa, fecha, hora, peso bruto, tara y peso neto del ticket | M04 |
| RF03 | Validar automáticamente la consistencia de los datos del ticket: pesos, formato de placa, capacidad del vehículo y fecha (V1 a V5) | M05 |
| RF04 | Permitir el registro y la corrección manual de los datos reconocidos | M03 |
| RF05 | Asignar un código único a cada ingreso de mineral | M03 |
| RF06 | Registrar el tipo de mineral y el tipo de vehículo (propio o externo) | M03 (catálogo en M02) |
| RF07 | Vincular cada ingreso con las etapas de secado, zarandeo, molienda y ensacado | M06 |
| RF08 | Consultar un ingreso por placa y fecha con su ticket de respaldo | M07 |
| RF09 | Generar y exportar el total acumulado mensual por producto | M08 |
| RF10 | Gestionar usuarios y roles de acceso | M01 |

La auditoría (M09) es transversal: no tiene RF propio y **no suma ni resta** en el avance.

## Mapa de módulos

| Módulo | Nombre | Responsabilidad | RF principal | Estado del código |
|---|---|---|---|---|
| M01 | Autenticación y roles | Identificar al usuario y limitar cada operación según su rol | RF10 | Implementado con pruebas (`apps/accounts`) |
| M02 | Catálogo maestro | Mantener tipos de mineral, vehículos con titularidad y capacidad, y transportistas | RF06 (soporte) | Implementado con pruebas (`apps/catalogo`); pendiente retirar clientes y definir tipo de mineral |
| M03 | Registro de ingresos | Registrar el ingreso a partir de la imagen del ticket, con corrección, confirmación y código único | RF01, RF04, RF05, RF06 | Implementado con el diseño anterior (`apps/ingresos`); pendiente de refactor |
| M04 | Reconocimiento automático del ticket | Leer los seis campos del ticket con su nivel de confianza, detrás de la interfaz `ReconocedorTicket` | RF02 | Sin código |
| M05 | Validación automática de consistencia | Aplicar V1 a V5 en el servidor y registrar el resultado, detrás de la interfaz `ValidadorConsistencia` | RF03 | Sin código |
| M06 | Trazabilidad del proceso | Asignar ingresos a lotes de proceso y registrar su paso por cada etapa | RF07 | Sin código |
| M07 | Consulta de ingresos y respaldo | Localizar un ingreso por placa y fecha y presentar su ticket | RF08 | Sin código (`apps/busqueda` es un esqueleto) |
| M08 | Consolidación de la producción | Calcular y exportar el total acumulado mensual por producto | RF09 | Sin código (`apps/reportes` es un esqueleto) |
| M09 | Auditoría | Registrar quién hizo qué y cuándo sobre cada entidad, incluidos reconocimiento y corrección | — (transversal) | Sin código (`apps/auditoria` es un esqueleto) |

Añadir un módulo consiste en crear su carpeta, agregar una fila a esta tabla y sus filas a la
matriz de trazabilidad. No se renumera nada ni se toca otro módulo.

> **Nota sobre la renumeración.** Los módulos se renumeraron el 21/09/2026. Las cuatro carpetas
> de `docs/modulos/` con la numeración antigua M04 a M07 (salidas y movimientos, inventario por
> producto, consolidados y reportes, captura local) y las apps del backend que no figuran en el
> mapa (`apps/salidas` entre ellas) corresponden al sistema anterior y se retiran en las fases 7
> y 10 del plan de migración. Los commits `M04:` de la rama `feature/M03-ingresos` anteriores a
> esa fecha se refieren a Salidas, no a Reconocimiento. No documentes nada sobre esas carpetas ni
> cites sus historias.

El cronograma vive solo en `docs/01-plan/`; ningún documento de módulo asigna semanas.

## Stack

PostgreSQL 16 · Django 5.x + Django REST Framework · SimpleJWT · Angular 17+ (standalone,
signals) · Pillow para las imágenes del ticket · motor de reconocimiento detrás de la interfaz
`ReconocedorTicket` (el motor concreto lo fija D-12) · openpyxl / ReportLab para la exportación ·
pytest-django. Detalle en `docs/model-c4/ARQ-02_Arquitectura_Tecnica.md`.

## Decisiones de diseño

Reabrir cualquiera de las cerradas exige justificación escrita: todas condicionan la integridad
del dominio o la comparabilidad de la medición. Están en `docs/00-arquitectura/decisiones_diseno.md`.

**Cerradas**

| ID | Decisión |
|---|---|
| D-01 | El ingreso guarda tres marcas de tiempo independientes: fecha y hora del ticket, inicio del registro y fin del registro |
| D-02 | El código único lo asigna el servidor, dentro de una transacción con bloqueo |
| D-06 | La titularidad del vehículo es un atributo del catálogo, no texto libre; de ella se deriva el tipo de vehículo del ingreso |
| D-07 | El sistema no borra ingresos: los anula |
| D-08 | Las reglas de negocio, incluidas V1 a V5, viven en el servidor; el cliente solo muestra el resultado |
| D-09 | `repositories/` es el lado de lectura de cada app |
| D-10 | M07 Consulta y M08 Consolidación son apps de lectura, sin modelos propios |
| D-11 | El frontend vive en un repositorio separado |
| D-13 | El dato reconocido no se guarda sin confirmación del usuario |
| D-16 | Motor, versión y reglas no cambian entre el inicio y el fin de la medición |

**Pendientes de cierre**

| ID | Decisión | Criterio de cierre |
|---|---|---|
| D-12 | Motor de reconocimiento (OCR local, servicio en la nube o modelo multimodal por API) | Piloto con 20 a 30 tickets reales de dos o tres motores; se compara exactitud, costo y dependencia de conexión. La documentación usa `ReconocedorTicket` y no depende del motor |
| D-14 | Almacenamiento de imágenes (volumen del servidor u objetos, compresión, retención, respaldo) | Se fija con el despliegue |
| D-15 | Procesamiento síncrono o asíncrono del reconocimiento | Síncrono, salvo que el piloto de D-12 muestre tiempos de más de unos segundos por ticket |

**Retiradas**

- D-03 (hora de registro de una captura local) y D-04 (captura local decidida en la semana 1): se
  retiran con el módulo de captura local; solo queda un RNF de conservación del borrador ante
  pérdida de conexión.
- D-05 (la búsqueda existe por un indicador): se reformula como M07, que existe por RF08.

## Decisiones de reformulación asumidas

Del Anexo B del plan de migración, tomadas con su recomendación mientras el autor no indique lo
contrario: DR-01 borrador ante pérdida de conexión como RNF, sin historias propias · DR-02 motor
detrás de `ReconocedorTicket` · DR-03 un solo catálogo de tipo de mineral, usado al registrar y al
consolidar · DR-04 vínculo ingreso–etapa mediante lote de proceso · DR-05 una placa que no está en
el catálogo impide confirmar el ingreso hasta elegir o dar de alta el vehículo · DR-06 RF03 cubre
V1 a V5 y RF09 incluye la exportación · DR-07 módulos renumerados M01 a M09 · DR-08 conjunto de
prueba de 50 tickets y 10 inconsistencias.

## Fuera de alcance — declarado

Salidas y ventas · inventario de producto terminado (saldos, movimientos internos y pérdidas
por humedad) · reportes normativos periódicos · facturación, precios y fletes · contabilidad y
planillas · actividad en la mina · mineral sulfuro · integración con la balanza · predicción de
demanda o pronósticos · aplicación móvil nativa · operación sin señal de red (solo se conserva el
borrador) · multiempresa · balance metalúrgico y leyes.

Se declara explícitamente para proteger el cronograma y para poder responderlo en sustentación.
**Antes de añadir cualquier funcionalidad, comprueba que no esté en esta lista.**

## Nomenclatura

| Elemento | Formato | Ejemplo |
|---|---|---|
| Historia de usuario | `HU-M{módulo}-{nn}` | HU-M03-01 |
| Criterio de aceptación | `CA{nn}` dentro de la HU | CA01 |
| Requerimiento funcional global | `RF{nn}` (sin guion) | RF03 |
| Requerimiento de usuario | `RU-M{módulo}-{nn}` | RU-M03-01 |
| Requerimiento de sistema | `RS-M{módulo}-{nn}` | RS-M03-01 |
| Requerimiento no funcional | `RNF-M{módulo}-{nn}` | RNF-M03-06 |
| Regla de negocio | `RN-M{módulo}-{nn}` | RN-M03-05 |
| Regla de validación del ticket | `V{n}` | V4 |
| Diagrama de secuencia | `S-M{módulo}-{nn}` | S-M03-01 |
| Diagrama de actividades | `A-M{módulo}-{nn}` | A-M03-02 |
| Caso de prueba por RF (lista de control) | `CP{nn}` | CP03 |
| Caso de prueba por criterio | `CP-{historia}-{nn}` | CP-HU-M03-01-01 |
| Decisión de diseño | `D-{nn}` | D-13 |
| Tarea de usabilidad (solo en la matriz) | `T{nn}` | T02 |
| Campo de completitud (solo en la matriz) | `C{n}` | C5 |

**Prioridades:** Crítica · Alta · Media · Baja.
**Unidad de medida:** toneladas, con tipo decimal, jamás punto flotante. **Titularidad:** `PROPIO` /
`EXTERNO`. **Tipo de mineral:** un solo catálogo (DR-03); sus valores se definen con la empresa.

## Estructura de un módulo

```
docs/modulos/M{nn}-{slug}/
├── HU.md
├── notas.md                    (todo módulo con código)
├── requerimientos/
│   ├── usuario.md
│   ├── sistema.md
│   ├── funcionales.md
│   ├── no_funcionales.md
│   └── reglas_negocio.md
└── diagramas/
    ├── caso_uso.md
    ├── secuencia.md
    └── actividades.md
```

Todos los módulos usan la carpeta `requerimientos/`. No la renombres: rompería los enlaces
relativos de los documentos ya versionados.

## Registro maestro

`docs/HistoriasUsuario.md` es un **índice** generado desde los `HU.md` de cada módulo: tabla por
módulo con identificador, título, rol, prioridad y enlace. No lleva criterios de aceptación; el
detalle vive solo en el módulo. Si el índice y un `HU.md` difieren en la lista de historias,
repórtalo; no lo corrijas en silencio en ambos lados.

## Tono

Español académico formal, sin anglicismos evitables, sin marketing y sin adjetivos entusiastas.
Cada archivo cierra con la sección que **el sistema necesita**: dependencias entre módulos,
tabla de permisos, consecuencia de violar una regla, riesgo de implementación. La relación con la
tesis no se escribe en los módulos: se registra en la matriz de trazabilidad.
