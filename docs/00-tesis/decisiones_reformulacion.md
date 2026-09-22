# Decisiones de reformulación

| Campo | Valor |
|---|---|
| Documento | Decisiones DR-01 a DR-08 |
| Origen | Anexo B de `../PLAN_TRABAJO.md` |
| Fecha de cierre | 22/09/2026 |
| Estado | Todas aceptadas con la recomendación del plan |

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
| DR-05 | Placa reconocida que no está en el catálogo | El ingreso no se confirma. El usuario elige el vehículo del catálogo o el Administrativo lo da de alta en el momento. Preserva D-06 y el campo C7 | M03, M02 |
| DR-06 | RF03, RF09 y tarea T06 | RF03 cubre los cinco tipos de inconsistencia V1 a V5. RF09 es generar **y exportar** el total acumulado mensual por producto. T06 es exportar ese total | Anexo 03 y Anexo 04 del documento de tesis |
| DR-07 | Numeración de módulos | Renumerar M01 a M09 según el marco. M01 y M02 conservan su número y su código | Todo `docs/modulos/`, backend |
| DR-08 | Conjunto de prueba | ERA: 50 tickets reales × 6 campos. TDI: 10 inconsistencias sembradas, 2 por regla. Motor y reglas congelados durante la medición (D-16) | Plan de pruebas |

---

## Consecuencias que estas decisiones dejan abiertas

No son decisiones pendientes, sino trabajo que se deriva de las ya tomadas:

| Origen | Trabajo derivado | Momento |
|---|---|---|
| DR-02 | Ejecutar el piloto de motores y cerrar D-12 | Antes de implementar M04 |
| DR-03 | Definir con la empresa los valores del catálogo de tipo de mineral | Antes de implementar M02 |
| DR-06 | Actualizar el Anexo 03 y el Anexo 04 del documento de tesis | **Antes del juicio de expertos** |
| DR-07 | Retirar las carpetas de módulo y las apps del alcance anterior | Fases 7 y 10 del plan |
| Marco §7 | Confirmar la tolerancia de 0,01 t de la regla V1 con la empresa | Antes de fijar el conjunto de prueba |

## Nota sobre DR-06

Es la única decisión que obliga a modificar el documento de tesis, no el repositorio. Su motivo es
que el instrumento medía más de lo que el requerimiento prometía: la hoja B siembra cinco tipos de
inconsistencia y RF03 solo declaraba la de pesos, y la tarea T06 no correspondía a ningún RF. Si el
juicio de expertos se realiza sobre la redacción anterior, el denominador de RFC queda fijado sobre
una lista que el sistema contradice.
