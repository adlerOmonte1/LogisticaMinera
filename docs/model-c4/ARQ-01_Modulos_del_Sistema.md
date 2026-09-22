# ARQ-01 — Definición de módulos del sistema

**Documento:** ARQ-01
**Versión:** 2.0
**Estado:** Aprobado
**Alcance:** la lista cerrada de módulos del sistema web inteligente, con la justificación de cada uno
**Deriva de:** `../00-tesis/marco_tesis.md` y `../00-tesis/decisiones_reformulacion.md`

---

## 1. Propósito

Fijar la lista cerrada de módulos que constituyen el sistema web inteligente para el control de
inventarios de ingreso de mineral, y dejar por escrito por qué existe cada uno.

Un módulo es una **responsabilidad acotada del dominio**: un conjunto de decisiones que cambian
juntas y por el mismo motivo. No es una pantalla, ni una tabla, ni un indicador.

El avance de la implementación se mide sobre los **10 requerimientos funcionales** de la lista de
control del marco, no sobre el número de módulos. Un módulo puede cubrir varios RF y un RF puede
apoyarse en más de un módulo; el denominador fijo son los RF. Esta es la única mención al
seguimiento de la tesis en este documento: el detalle está en
`../02-trazabilidad/matriz_HU_RF_indicador.md`.

## 2. Criterio de derivación

Ningún módulo se incorpora por analogía con otros sistemas de inventario. Cada uno existe porque
cumple las tres condiciones siguientes:

1. **Responsabilidad propia.** Cubre una parte del dominio que ningún otro módulo cubre. Si dos
   módulos cambian siempre a la vez y por la misma razón, son uno solo.
2. **Contrato explícito.** Lo que ofrece a los demás se expresa como una interfaz o un conjunto de
   endpoints, no como acceso directo a sus tablas.
3. **Requerimiento que lo exige.** Corresponde a al menos un RF de la lista de control, o es
   transversal y da soporte a todos (auditoría).

Un módulo que no cumple las tres es una capa, una utilidad compartida o una pantalla, y pertenece
dentro de otro.

## 3. Lista de módulos

| Código | Módulo | Responsabilidad | RF que cubre |
|---|---|---|---|
| M01 | Autenticación y roles | Identificar al usuario y limitar cada operación según su rol | RF10 |
| M02 | Catálogo maestro | Mantener tipos de mineral, vehículos con titularidad y capacidad, y transportistas | RF06 (soporte) |
| M03 | Registro de ingresos | Registrar el ingreso a partir de la imagen del ticket, con corrección, confirmación y código único | RF01, RF04, RF05, RF06 |
| M04 | Reconocimiento automático del ticket | Leer los seis campos del ticket con su nivel de confianza | RF02 |
| M05 | Validación automática de consistencia | Aplicar las reglas V1 a V5 y registrar su resultado | RF03 |
| M06 | Trazabilidad del proceso | Asignar ingresos a lotes y registrar su paso por cada etapa | RF07 |
| M07 | Consulta de ingresos y respaldo | Localizar un ingreso por placa y fecha y presentar su ticket | RF08 |
| M08 | Consolidación de la producción | Calcular y exportar el total acumulado mensual por producto | RF09 |
| M09 | Auditoría | Registrar quién hizo qué y cuándo sobre cada entidad | — (transversal) |

**Total: 9 módulos y 10 RF.** Cada RF tiene un módulo principal responsable; ningún RF queda sin
dueño y ninguno está repartido entre dos módulos sin que uno decida.

## 4. Justificación módulo por módulo

**M01 — Autenticación y roles.** Es habilitante. Sin control de acceso por rol, ninguna operación
puede atribuirse a un responsable y el registro de eventos de M09 no tiene a quién imputar los
cambios. Cubre RF10.

**M02 — Catálogo maestro.** El ingreso referencia datos que no se digitan: el vehículo, su
titularidad y su capacidad, y el tipo de mineral. Que esos datos sean un catálogo y no texto libre
es lo que permite derivar el tipo de vehículo de la placa (D-06) y contrastar el peso neto con la
capacidad declarada (regla V4). Un catálogo escrito a mano en cada ingreso haría ambas cosas
imposibles.

**M03 — Registro de ingresos.** Es el núcleo. La unidad de registro del sistema es el ingreso de
mineral a planta, y aquí se materializa: recibe la imagen, orquesta el reconocimiento y la
validación, recoge la confirmación del usuario y persiste el ingreso con su código único y sus tres
marcas de tiempo. M03 no lee la imagen ni aplica las reglas: las delega y decide con su resultado.

**M04 — Reconocimiento automático del ticket.** Existe como módulo propio, y no como una función
dentro de M03, por dos razones. La primera es de sustitución: el motor concreto está pendiente de
elegir (D-12) y debe poder cambiarse sin tocar el registro, por lo que queda detrás de la interfaz
`ReconocedorTicket`. La segunda es de responsabilidad: extraer texto de una imagen y decidir si un
ingreso es válido son problemas distintos, con datos, errores y pruebas distintos. Cubre RF02.

**M05 — Validación automática de consistencia.** Las reglas V1 a V5 son conocimiento del dominio que
se consulta desde dos momentos distintos —sobre los datos propuestos por el reconocimiento y sobre
los confirmados por el usuario— y que debe poder ampliarse sin tocar el registro. Se ejecuta siempre
en el servidor (D-08). Cubre RF03.

**M06 — Trazabilidad del proceso.** El mineral de varios volquetes se mezcla en cancha, de modo que
el vínculo directo entre un ingreso y una etapa no es realista: el ingreso se asigna a un lote de
proceso y es el lote el que registra su paso por secado, zarandeo, molienda y ensacado (DR-04). Esa
indirección es la responsabilidad del módulo. Cubre RF07.

**M07 — Consulta de ingresos y respaldo.** Recuperar un ingreso concreto por placa y fecha, con la
imagen de su ticket, es una lectura con sus propios índices y su propio contrato. No tiene entidad
propia: lee sobre M03 (D-10). Cubre RF08.

**M08 — Consolidación de la producción.** Agrega los ingresos no anulados del mes por tipo de
mineral y entrega el total, con su exportación (DR-06). Tampoco tiene entidad propia. Cubre RF09.

**M09 — Auditoría.** Transversal y sin RF propio. Registra creación, corrección y anulación, y
también el reconocimiento y las correcciones sobre los datos propuestos. No mejora ninguna función
del negocio: sostiene que el histórico pueda demostrarse íntegro, que es condición de todo lo demás.

## 5. Fuera de alcance

Se declara explícitamente para proteger el cronograma y para poder responderlo en la revisión
técnica:

- Salidas de producto y ventas
- Inventario de producto terminado, sus movimientos internos y las pérdidas por humedad
- Reportes normativos periódicos
- Facturación, cobranza, precios y fletes a transportistas
- Contabilidad y planillas
- Cualquier registro de la actividad en la mina
- Mineral sulfuro
- Integración directa con la balanza
- Predicción de demanda o pronósticos
- Aplicación móvil nativa
- Operación sin señal de red, salvo la conservación del borrador (DR-01)
- Operación multiempresa
- Balance metalúrgico y determinación de leyes

## 6. Orden de construcción

Las semanas concretas están en `../01-plan/PLAN_DE_TRABAJO.md`. Aquí solo consta el orden que
imponen las dependencias:

| Orden | Módulos | Por qué en esa posición |
|---|---|---|
| 1 | M01, M02 | Todo lo demás necesita usuario atribuido y catálogos |
| 2 | M03 | Núcleo; debe existir antes que lo que lo consume |
| 3 | M04, M05 | Se inyectan en M03; requieren su servicio de registro |
| 4 | M09 | Transversal; se incorpora junto con las operaciones que audita |
| 5 | M06, M07, M08 | Leen o amplían lo que M03 ya produce |

M04 y M05 no pueden quedar para el final: M03 se construye asumiendo que existen, con sus interfaces
inyectadas desde el principio. Si se añadieran después, habría que reescribir el servicio de
registro.

## 7. Riesgos del alcance

| Riesgo | Impacto | Mitigación |
|---|---|---|
| Precisión insuficiente del motor de reconocimiento | El usuario corrige tantos campos que el registro tarda más que la transcripción manual | Piloto con 20 a 30 tickets reales antes de fijar D-12; la interfaz `ReconocedorTicket` permite cambiar de motor sin tocar M03 |
| Calidad de las fotografías en planta | Tickets ilegibles por luz, sombra, papel térmico desvaído o encuadre | Camino manual siempre disponible (HU-M04-01 CA03 y CA04); guía de captura al usuario; validación de tamaño y formato |
| Mezcla de mineral en cancha | El vínculo ingreso–etapa no refleja la operación real y la trazabilidad queda inservible | Lote de proceso como indirección (DR-04); confirmar con la empresa cómo se agrupa realmente el mineral antes de implementar M06 |
| Placa reconocida que no está en el catálogo | El registro se bloquea en planta, donde no hay quien dé de alta el vehículo | DR-05: el Administrativo puede darlo de alta en el momento; medir cuántas veces ocurre durante el piloto |
| El catálogo de tipo de mineral no está definido | M02 y M08 se construyen sobre un supuesto | Definir sus valores con la empresa antes de implementar M02 (DR-03) |
| Motor o reglas modificados durante la medición | Los ingresos del periodo dejan de ser comparables entre sí | D-16: motor, versión y reglas congelados; la versión se registra en cada reconocimiento |
| Nueve módulos en el cronograma previsto | Sobrecarga | M09 puede reducirse a registro de eventos sin interfaz de consulta si el tiempo aprieta |

## 8. Referencias cruzadas

- Marco de la tesis y lista de RF: `../00-tesis/marco_tesis.md`
- Decisiones de reformulación: `../00-tesis/decisiones_reformulacion.md`
- Decisiones que condicionan la implementación: `../00-arquitectura/decisiones_diseno.md`
- Convención de códigos: `../00-arquitectura/convenciones_codigo.md`
- Organización del código Django/Angular: `ARQ-02_Arquitectura_Tecnica.md`
- Contenedores y componentes: `ARQ-03_Modelo_C4.md`
- Trazabilidad completa: `../02-trazabilidad/matriz_HU_RF_indicador.md`

## 9. Nota sobre la numeración anterior

Los módulos se renumeraron el 21/09/2026 (DR-07). Las carpetas de `docs/modulos/` con la numeración
antigua M04 a M07 y las apps del backend que no figuran en la sección 3 pertenecen al alcance
anterior y se retiran en las fases 7 y 10 del plan de migración. Los commits `M04:` anteriores a esa
fecha se refieren al módulo de salidas, hoy fuera de alcance.
