# Decisiones de reformulación

| Campo | Valor |
|---|---|
| Documento | Decisiones DR-01 a DR-10 |
| Origen | Reformulación del alcance del sistema, septiembre de 2026 |
| Fecha de cierre | 22/09/2026 (DR-01 a DR-08) · 28/09/2026 (DR-09 y DR-10) |
| Estado | Todas aceptadas; DR-09 y DR-10 a partir del formato real del ticket, informado por el autor |

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
| DR-09 | Formato real del ticket de balanza | El ticket en uso imprime: «Recibí», «La suma de» (tarifa del pesaje), «Concepto», **Peso**, **Placa**, **día, mes y año**, y firmas. No imprime hora, tara ni peso neto. En consecuencia: el reconocimiento lee tres campos —placa, fecha y peso bruto—; la hora del pesaje la digita el usuario; la tara proviene del catálogo del vehículo; el peso neto lo calcula el sistema como peso bruto menos tara. La tarifa, el receptor, el concepto y las firmas no se registran: la tarifa está fuera de alcance. V1 pasa a detectar un ticket posiblemente duplicado, porque la comparación entre neto impreso y resta deja de existir | RF02, RF03, M03, M04, M05, modelo de datos, Anexos 02, 03 y 04 |
| DR-10 | Primer viaje y destare | La tara de un vehículo se obtiene una sola vez, en el destare de su primer viaje: tras descargar, el vehículo se pesa vacío y el usuario **digita** la tara, sin reconocimiento automático, por seguridad del dato. La tara queda en el catálogo y se mantiene por decisión de la Gerencia; solo el Administrador puede modificarla, con motivo. Mientras el vehículo no tiene tara, su ingreso queda en estado **En proceso**: tiene código, peso bruto y marcas de tiempo, pero no peso neto, y no cuenta en ningún total. Al registrar la tara, el sistema calcula el neto y el ingreso pasa a Registrado | M02, M03, M06, M07, M08, modelo de datos |

---

## Consecuencias que estas decisiones dejan abiertas

No son decisiones pendientes, sino trabajo que se deriva de las ya tomadas:

| Origen | Trabajo derivado | Momento |
|---|---|---|
| DR-02 | Ejecutar el piloto de motores y cerrar D-12 | Antes de implementar M04 |
| DR-03 | Definir con la empresa los valores del catálogo de tipo de mineral | Antes de implementar M02 |
| DR-06 | Actualizar el Anexo 03 y el Anexo 04 del documento de tesis | **Antes del juicio de expertos** |
| DR-09 | Actualizar en el documento de tesis: RF02 a tres campos y RF03 con la duplicidad (Anexo 03); la hoja A de ERA a tres campos y la hoja B con la nueva V1 (Anexo 04); y el origen de C2, C4 y C5 en la ficha de observación (Anexo 02) | **Antes del juicio de expertos** |
| DR-10 | Definir con la Gerencia quién registra el destare en planta y cómo se comunica al supervisor que un vehículo está pendiente de destarar | Antes de implementar M03 |
| DR-07 | Retirar las carpetas de módulo y las apps del alcance anterior | Fases 7 y 10 del plan |

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
