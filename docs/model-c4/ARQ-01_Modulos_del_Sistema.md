# ARQ-01 — Definición de módulos del sistema

**Documento:** ARQ-01
**Versión:** 1.1
**Estado:** Aprobado — base del indicador I1

---

## 1. Propósito

Fijar la lista cerrada de módulos que constituyen el sistema web. Esta lista es el **denominador** del indicador de avance de la implementación "porcentaje de módulos implementados sobre módulos planificados". Toda ampliación posterior baja ese porcentaje; toda reducción debe documentarse antes de firmar la ficha técnica.

## 2. Criterio de derivación

Ningún módulo se incorpora por analogía con otros sistemas de inventario. Cada uno se deriva de una de dos fuentes:

- **Un indicador de resultado** que no puede mejorar sin ese módulo.
- **Una restricción documentada** en el diagnóstico inicial (conectividad intermitente en planta, ausencia de registro de volquetes propios, pérdida del reporte mensual).

## 3. Lista de módulos

| Código | Módulo | RF que agrupa | Indicador que habilita | Semana |
|---|---|---|---|---|
| M01 | Autenticación y control de acceso | RF-08 | — (habilitante) | 1 |
| M02 | Catálogo maestro | RF-03 | I2 | 2 |
| M03 | Registro de ingresos | RF-01, RF-02, RF-09 | I1, I2, I5 | 2–3 |
| M04 | Salidas y movimientos | RF-05 | I4 | 5 |
| M05 | Existencias | RF-04 | I3, I4 | 5 |
| M06 | Consolidados y reportes | RF-06, RF-07 | I6 | 7 |
| M07 | Captura sin conexión (PWA) | RF-10 | I1, I2 | 4 |
| M08 | Auditoría | RF-12 | — (trazabilidad) | 3 y 6 |
| M09 | Búsqueda | RF-11 | I5 | 6 |

**Total planificado: 9 módulos.**

## 4. Justificación módulo por módulo

**M01 — Autenticación.** No deriva de un indicador; es habilitante. Sin control de acceso por rol, el registro de eventos de M08 no puede atribuirse a un responsable y la cobertura de registro (I2) no es auditable.

**M02 — Catálogo maestro.** El indicador I2 mide cobertura de registro *por tipo de vehículo* (propio vs. externo). Esa distinción exige un catálogo de vehículos con su titularidad declarada. Sin catálogo, el tipo de vehículo se captura como texto libre y el indicador se vuelve inclasificable.

**M03 — Registro de ingresos.** Es el núcleo. La unidad de registro de todo el sistema es el ingreso de volquete a planta. I1 (latencia entre pesaje y disponibilidad del dato) e I2 (cobertura) se miden directamente sobre los registros que produce este módulo.

**M04 — Salidas y movimientos.** El indicador I4 (desviación entre stock declarado y estimado) requiere que las salidas se registren con el mismo rigor que los ingresos. Sin salidas, el stock calculado es acumulativo y la desviación carece de sentido.

**M05 — Existencias.** I3 mide el tiempo de determinación del stock por producto. Hoy ese cálculo es manual sobre papel. El módulo lo convierte en una consulta.

**M06 — Consolidados y reportes.** I6 mide el porcentaje de meses con reporte de producción consolidado disponible. El reporte mensual existió en la empresa y se perdió; este módulo lo restituye de forma automática. Incluye el formato de declaración semestral requerido por la normativa vigente.

**M07 — Captura sin conexión.** Deriva de una restricción documentada: la conectividad en planta es intermitente. Si el registro exige conexión, la latencia (I1) no baja en las horas sin señal y la cobertura (I2) se degrada justamente en los turnos con más ingresos. Es el diferenciador del sistema frente a una aplicación web convencional.

**M08 — Auditoría.** No mejora ningún indicador de resultado, pero sostiene la confiabilidad de los datos recolectados: permite demostrar ante la gerencia que los registros del histórico no fueron alterados retroactivamente.

**M09 — Búsqueda.** Deriva del indicador I5 (tiempo de recuperación del dato de un ingreso concreto). Ninguno de los diez requerimientos originales contemplaba búsqueda por criterios. Sin ella, I5 no mejora y la dimensión D3 queda sin efecto medible. Se incorporó como RF-11.

## 5. Fuera de alcance

Se declara explícitamente para proteger el cronograma de desarrollo y para poder responder en la revisión técnica:

- Facturación, cobranza y precios de venta
- Cálculo y pago de fletes a transportistas
- Contabilidad y planillas
- Cualquier registro de la actividad en la concesión minera
- Geolocalización o seguimiento de vehículos
- Predicción de demanda, aprendizaje automático o analítica avanzada
- Aplicación móvil nativa (el alcance es una aplicación web progresiva)
- Operación multiempresa
- Balance metalúrgico y determinación de leyes

## 6. Distribución en ocho semanas

| Semana | Foco | Entregable verificable |
|---|---|---|
| 1 | Arquitectura, modelo de datos, esqueleto PWA, M01 | Login funcional con roles; decisión de arquitectura documentada |
| 2 | M02 y arranque de M03 | Catálogo operativo; formulario de ingreso con validaciones |
| 3 | M03 completo y M08 | Alta, edición, listado e histórico de ingresos, con registro de eventos |
| 4 | M07 sobre M03 | Registro de un ingreso sin conexión y sincronización verificada |
| 5 | M04 y M05 | Stock por producto coincidente con el cálculo manual |
| 6 | M09 y kardex | Búsqueda de un ingreso por padrón en menos de un minuto |
| 7 | M06 | Consolidado mensual y formato de declaración semestral exportables |
| 8 | Pruebas funcionales, pruebas de carga, corrección y despliegue | Acta de pruebas funcionales y protocolo de carga completados |

M07 se aborda en la semana 4 y no al final, por la razón indicada en `decisiones_diseno.md` §4. La semana 8 es de estabilización y **no** de desarrollo: es donde se consolidan las mediciones de los indicadores operativos.

## 7. Riesgos del alcance

| Riesgo | Impacto | Mitigación |
|---|---|---|
| M07 resulta más costoso de lo previsto | Baja el porcentaje de módulos implementados y se pierde el diferenciador | Decisión firme en semana 1. Si se descarta, retirarlo de la lista planificada **antes** de firmar la ficha técnica |
| El criterio de merma no está definido | M04 no puede construirse correctamente y el indicador I4 queda sin interpretación | Definirlo antes de la semana 5 |
| El formato de declaración semestral no está a la mano | M06 se construye a ciegas | Conseguir el formato oficial antes de la semana 7 |
| Nueve módulos en ocho semanas | Sobrecarga | M08 puede reducirse a registro de eventos sin interfaz de consulta si el tiempo aprieta |
| Volumen de datos insuficiente en el periodo de medición | Los indicadores pierden representatividad | Acordar con la jefatura de operaciones la extensión del periodo antes de cerrarlo |

## 8. Referencias cruzadas

- Convención de códigos: `convenciones_codigo.md`
- Decisiones que condicionan la implementación: `decisiones_diseno.md`
- Organización del código Django/Angular: `ARQ-02_Arquitectura_Tecnica.md`
- Trazabilidad completa: `../02-trazabilidad/matriz_HU_RF_indicador.md`
