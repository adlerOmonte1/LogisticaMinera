# Decisiones de reformulación

| Campo | Valor |
|---|---|
| Documento | Decisiones DR-01 a DR-28 |
| Origen | Reformulación del alcance del sistema, septiembre de 2026 |
| Fecha de cierre | 22/09/2026 (DR-01 a DR-08) · 28/09/2026 (DR-09 y DR-10) · 20/10/2026 (DR-11 a DR-18) · 21/10/2026 (DR-19 a DR-23) · 22/10/2026 (DR-24 a DR-28) |
| Estado | Todas aceptadas. DR-09 y DR-10 parten del formato real del ticket; DR-11 a DR-18, de la revisión del mockup del sistema (versión 2); DR-19 a DR-22 resuelven los pendientes P-01, P-02 y P-04; DR-23 alinea el alcance del Administrativo con el catálogo y la trazabilidad; DR-24 a DR-28 resuelven los puntos de quiebre de la revisión técnica |

Estas decisiones resuelven las ambigüedades que la reformulación dejó abiertas. Son previas al
diseño: cada una condiciona un módulo, una entidad o un instrumento. Reabrir cualquiera exige
justificación escrita y revisión de los documentos que dependen de ella.

---

| Código | Decisión | Contenido aceptado | Depende de ella |
|---|---|---|---|
| DR-01 | Captura sin señal de red | Se retira como módulo. Queda un RNF acotado: el borrador del registro (imagen y campos editados) se conserva en el dispositivo ante pérdida de conexión y se reanuda al recuperarla. Sin historias propias | M03, decisiones D-03 y D-04 |
| DR-02 | Motor de reconocimiento | La documentación depende de la interfaz `ReconocedorTicket`, nunca del motor concreto. El motor se elige tras un piloto con 20 a 30 tickets reales de dos o tres alternativas (D-12) | M04, backend |
| DR-03 | Tipo de mineral frente a producto | Un solo catálogo, el de tipo de mineral, usado al registrar el ingreso (C6) y al consolidar (RF09). Sus valores se definen con la empresa | M02, M08, modelo de datos |
| DR-04 | Vínculo del ingreso con las etapas | Mediante un **lote de proceso**: el ingreso se asigna a un lote y el lote registra su paso por cada etapa. Refleja la mezcla de mineral en cancha | M06, modelo de datos |
| DR-05 | Placa reconocida que no está en el catálogo | *Ajustada por DR-10.* Una placa ausente del catálogo corresponde al primer viaje de un vehículo: el usuario lo da de alta en la misma pantalla del registro, sin salir de ella. Preserva D-06 y el campo C7 | M03, M02 |
| DR-06 | RF03, RF09 y tarea T06 | RF03 cubre los cinco tipos de inconsistencia V1 a V5. RF09 es generar **y exportar** el total acumulado mensual por producto. T06 es exportar ese total | Anexo 03 y Anexo 04 del documento de tesis |
| DR-07 | Numeración de módulos | Renumerar M01 a M09 según el marco. M01 y M02 conservan su número y su código | Todo `docs/modulos/`, backend |
| DR-08 | Conjunto de prueba | *Ajustada por DR-09.* ERA: 50 tickets reales × 3 campos (150 lecturas). TDI: 10 inconsistencias sembradas, 2 por regla. Motor y reglas congelados durante la medición (D-16) | Plan de pruebas |
| DR-09 | Formato real del ticket de balanza | *Precisada por DR-11 en la hora del pesaje.* El ticket en uso imprime: «Recibí», «La suma de» (tarifa del pesaje), «Concepto», **Peso**, **Placa**, **día, mes y año**, y firmas. No imprime hora, tara ni peso neto. En consecuencia: el reconocimiento lee tres campos —placa, fecha y peso bruto—; la hora del pesaje la digita el usuario; la tara proviene del catálogo del vehículo; el peso neto lo calcula el sistema como peso bruto menos tara. La tarifa, el receptor, el concepto y las firmas no se registran: la tarifa está fuera de alcance. V1 pasa a detectar un ticket posiblemente duplicado, porque la comparación entre neto impreso y resta deja de existir | RF02, RF03, M03, M04, M05, modelo de datos, Anexos 02, 03 y 04 |
| DR-10 | Primer viaje y destare | La tara de un vehículo se obtiene una sola vez, en el destare de su primer viaje: tras descargar, el vehículo se pesa vacío y el usuario **digita** la tara, sin reconocimiento automático, por seguridad del dato. La tara queda en el catálogo y se mantiene por decisión de la Gerencia; solo el Administrador puede modificarla, con motivo. Mientras el vehículo no tiene tara, su ingreso queda en estado **En proceso**: tiene código, peso bruto y marcas de tiempo, pero no peso neto, y no cuenta en ningún total. Al registrar la tara, el sistema calcula el neto y el ingreso pasa a Registrado | M02, M03, M06, M07, M08, modelo de datos |
| DR-11 | Marcas de tiempo del ingreso | Se mantienen las tres marcas de tiempo y se conserva DR-09. La **fecha y hora del pesaje** es la del pesaje real: la fecha se reconoce del ticket y la hora la indica el usuario; el sistema la propone con la hora actual y es editable. El **inicio y el fin del registro** los asigna el servidor. Ejemplo: pesaje a las 16:00, inicio del registro a las 16:05 y fin a las 16:06 dan 5 minutos de espera y 1 minuto de registro | M03, I1, I2 |
| DR-12 | Identificación del ingreso | No existe un número de ticket aparte: el código único del ingreso (RF05) lo identifica | M03, modelo de datos |
| DR-13 | Registro manual de respaldo | Si el ticket se extravía o no puede fotografiarse, el ingreso se registra sin foto, con motivo obligatorio, y queda marcado «sin respaldo fotográfico». Es una excepción documentada como regla de negocio, no un RF nuevo | M03, M07 |
| DR-14 | Cierre del lote con su destino | Cuando todo el mineral del lote está ensacado, el Administrador cierra definitivamente el lote con el resumen de su proceso y registra su destino: **venta** o **traslado a otro punto** (por ejemplo, por ley baja). No incluye guía, facturación ni precios. Es una historia de M06 (RF07), no un módulo nuevo | M06, M01 |
| DR-15 | Datos descriptivos del lote | Los bigbags, su peso aproximado, la diferencia frente a lo registrado y las horas de molienda (t/h) son **datos descriptivos de gestión**. No son inventario de producto terminado, no miden pérdidas y no forman parte de los indicadores | M06 |
| DR-16 | Ruta del lote e I6 | Las etapas no son obligatorias para todos los lotes: se decide la **ruta** de cada lote o de cada parte (secado común; luego zarandeo, molienda o ambos; y ensacado). **I6 se reformula** como etapas vinculadas ÷ etapas de la ruta decidida × 100 | Marco §4, Anexo 02, M06, matriz de trazabilidad |
| DR-17 | Alcance del Supervisor de planta | El Supervisor de planta registra ingresos, vehículos nuevos, destares y el paso del lote por las etapas, y consulta | Marco §8, M01 |
| DR-18 | División de un lote por proporción | El mineral acumulado no se pesa: se estima a la vista. Para dividir un lote, el usuario indica la **fracción** de cada parte (por ejemplo, 1/3 a molienda y 2/3 a zarandeo; también tres partes o más). El sistema calcula las toneladas aproximadas de cada parte (fracción × total) solo para estimar el peso de los bigbags | M06 |
| DR-19 | Términos del ciclo del lote | Se distinguen dos acciones. El **inicio del recorrido** marca que el lote deja de reunir ingresos y empieza su secado. El **cierre del lote** es solo el cierre definitivo de DR-14, con su destino. Los estados del lote son Abierto, En recorrido y Cerrado. Resuelve P-04 | M06, M03 |
| DR-20 | Reparto de los ingresos tardíos | Un ingreso agregado a un lote dividido se reparte entre las partes por fracciones. El sistema propone las fracciones del lote y el usuario puede editarlas; deben sumar la unidad. Si el ingreso llega después del secado del lote, tiene además su propio secado. Resuelve P-01 | M06 |
| DR-21 | I6 en un lote dividido | Cuando el lote de un ingreso se divide en partes con rutas distintas, el denominador de I6 es la unión de las etapas de las rutas de esas partes. Ejemplo: una parte molida y otra zarandeada dan secado, zarandeo, molienda y ensacado, es decir, cuatro etapas. Resuelve P-02 | Marco §4, Anexo 02, M06, matriz de trazabilidad |
| DR-22 | Retiro de ingresos de un lote | Un ingreso solo puede retirarse de un lote, o trasladarse a otro, mientras el lote está Abierto. Desde el inicio del recorrido, el lote admite ingresos tardíos, pero no los devuelve a cancha | M06 |
| DR-23 | Alcance del Administrativo | El alcance de los roles se rige por el catálogo (M02) y por la trazabilidad (M06), que especifican el modelo. El Administrativo, además de registro, corrección, consultas, consolidación y exportación, **gestiona los catálogos** —salvo modificar una tara ya registrada— y **compone los lotes**: los abre, asigna y retira ingresos, inicia el recorrido y los divide. El Administrador conserva la gestión de usuarios, la modificación de la tara, las anulaciones y el cierre del lote con su destino. El uso de los roles se revisará y validará con los usuarios de la empresa antes de implementar M01 | Marco §8, M01, M02, M03, M06 |
| DR-24 | Salida del lote | Por ahora, la salida del mineral es el **cierre del lote con su destino** (DR-14, HU-M06-05): un solo acto con fecha, destino, resumen y responsable. No hay módulo de salidas ni registro de despachos. Si en planta un lote sale en varios viajes, se revisará como despacho dentro de M06, sin guía, cliente ni factura | M06 |
| DR-25 | Destare | El destare es obligatorio para todo vehículo nuevo y lo registra cualquiera de los tres roles. No tiene plazo: puede registrarse días después del ingreso, que mientras tanto sigue En proceso, válido y visible como pendiente. Precisa DR-10 | M02, M03, M08 |
| DR-26 | Uso del registro sin foto | El registro sin foto (DR-13) no tiene límite de uso: a la empresa le conviene registrar el ingreso y su motivo aunque el ticket no pueda fotografiarse, porque deja respaldo de que existió | M03, M07 |
| DR-27 | Lote con varios tipos de mineral | El lote se abre con un tipo de mineral y admite otros por decisión explícita del usuario: la acción **Agregar otro mineral** incorpora un tipo a la lista del lote. Solo se asignan ingresos cuyo tipo está en esa lista, y el lote presenta sus ingresos y toneladas agrupados por tipo de mineral. Un tipo sin ingresos puede quitarse mientras el lote está Abierto. Reemplaza la regla de un solo tipo por lote | M03, M06, modelo de datos |
| DR-28 | Corrección en cadena y reversión | La corrección de un ingreso se propaga a todo lo que depende de él —totales y estimaciones del lote, consolidado, calendario y trazabilidad—, porque todos se calculan sobre el ingreso al consultarse. La **última** corrección vigente de un ingreso puede revertirse, con motivo: el sistema restaura los valores anteriores, los revalida como en una corrección y deja ambos actos en auditoría; nada se borra (D-07) | M03, M06, M08, M09 |

---

## Consecuencias que estas decisiones dejan abiertas

No son decisiones pendientes, sino trabajo que se deriva de las ya tomadas:

| Origen | Trabajo derivado | Momento |
|---|---|---|
| DR-02 | Ejecutar el piloto de motores y cerrar D-12 | Antes de implementar M04 |
| DR-03 | Definir con la empresa los valores del catálogo de tipo de mineral | Antes de implementar M02 |
| DR-06 | Actualizar el Anexo 03 y el Anexo 04 del documento de tesis | **Antes del juicio de expertos** |
| DR-09 | Actualizar en el documento de tesis: RF02 a tres campos y RF03 con la duplicidad (Anexo 03); la hoja A de ERA a tres campos y la hoja B con la nueva V1 (Anexo 04); y el origen de C2, C4 y C5 en la ficha de observación (Anexo 02) | **Antes del juicio de expertos** |
| DR-10 | ~~Definir quién registra el destare~~ — **resuelto por DR-25**: cualquiera de los tres roles, sin plazo; la lista de pendientes de destare (HU-M03-04) es el aviso | — |
| DR-07 | Retirar las apps del backend del alcance anterior; las carpetas de módulo ya se retiraron | Preparación del repositorio, `../01-plan/PLAN_DE_TRABAJO.md` §8 |
| DR-12 | Retirar el número de ticket de M03 y del modelo de datos | **Hecho** en la versión 2: M03 y modelo de datos 3.0 |
| DR-14, DR-15, DR-18 | Incorporar a M06 el nombre del lote, la ruta, la división por proporción, los ingresos agregados después del cierre, los datos descriptivos y el cierre con destino | **Hecho** en la versión 2 (M06 y modelo de datos 3.0) |
| DR-16, DR-21 | Actualizar la ficha de observación (Anexo 02) con la nueva fórmula de I6 y su cálculo en lotes divididos; el marco ya está actualizado | **Antes del juicio de expertos** |
| DR-16 | Reformular I6 en la matriz de trazabilidad | **Hecho** en la versión 2 |
| DR-17 | Ajustar la matriz de roles de M01 al alcance del Supervisor de planta | **Hecho** en la versión 2 |
| DR-23 | Revisar y validar con los usuarios de la empresa el uso de los tres roles y la matriz de permisos de M01 | Antes de implementar M01 |
| DR-14, DR-18 | Ajustar la maqueta (`Mockup/index.html`): divide el lote en toneladas y no en fracciones | Opcional, antes de validar la interfaz con los usuarios |

## Nota sobre DR-06 y DR-09

Son las dos decisiones que obligan a modificar el documento de tesis, no solo el repositorio. En el caso
de DR-06, el motivo es que el instrumento medía más de lo que el requerimiento prometía: la hoja B siembra cinco tipos de
inconsistencia y RF03 solo declaraba la de pesos, y la tarea T06 no correspondía a ningún RF. Si el
juicio de expertos se realiza sobre la redacción anterior, el denominador de RFC queda fijado sobre
una lista que el sistema contradice.

DR-09 tiene el mismo efecto por otra vía: los instrumentos se diseñaron sobre un ticket supuesto que
imprimía seis datos, y el ticket real imprime tres. Medir la exactitud del reconocimiento sobre seis
campos que el papel no contiene, o sembrar una inconsistencia entre un neto impreso y una resta que
no existe, produciría resultados sin sentido. Los instrumentos deben describir el ticket que la
planta usa.

## Nota sobre DR-16

Con la fórmula anterior, etapas vinculadas ÷ 4 × 100, un lote que por decisión de la planta no pasa
por molienda nunca superaría el 75 %, aunque hubiera recorrido completa la ruta que le corresponde. El
indicador mediría entonces una decisión operativa y no la trazabilidad del ingreso. Al tomar como
denominador las etapas de la ruta decidida, I6 mide lo que debe medir: si cada etapa que el mineral
efectivamente recorre queda vinculada. Por la misma razón que DR-06 y DR-09, el cambio debe estar en
la ficha de observación antes del juicio de expertos.

## Pendientes de confirmar

No son decisiones tomadas. Se registran para resolverlas antes de la fase indicada.

| N.° | Pendiente | Propuesta | Antes de |
|---|---|---|---|
| P-01 | *Resuelto por DR-20* | — | — |
| P-02 | *Resuelto por DR-21* | — | — |
| P-03 | Cómo registra la ficha de observación un ingreso sin respaldo fotográfico (DR-13) en I3 e I4 | Registrarlo como caso aparte, sin tiempo de recuperación del respaldo | Anexo 02 |
| P-04 | *Resuelto por DR-19* | — | — |
