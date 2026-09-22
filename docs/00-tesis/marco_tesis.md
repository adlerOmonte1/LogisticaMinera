# Marco de tesis — fuente de verdad

> Este archivo manda sobre cualquier otro documento del repositorio. Si hay contradicción,
> gana este archivo y la contradicción se reporta.

| Campo | Valor |
|---|---|
| Documento | Marco de tesis |
| Origen | Anexos 01 a 05 de la tesis, validados por juicio de expertos |
| Fecha | 21/09/2026 |
| Estado | Vigente |

---

## 1. Identificación

- **Título:** Efecto de un sistema web inteligente en el control de inventarios de ingreso de
  mineral en la empresa Construcción y Minería, Huánuco, 2027.
- **Empresa:** Construcción y Minería (sin abreviatura societaria, a pedido de la empresa).
- **Ámbito:** planta de procesamiento de Pillcomarca. La mina de Chaulán queda fuera.
- **Autores:** dos. Redacción en plural: «los investigadores».

## 2. Diseño de la investigación

- Tipo aplicada, enfoque cuantitativo, diseño preexperimental G O1 X O2.
- **Unidad de análisis:** el ingreso de mineral registrado mediante ticket de balanza.
- **Muestra:** 90 a 100 ingresos por medición, censal. Pretest prospectivo por observación.
- **Prueba estadística:** Shapiro-Wilk; t de Student para muestras independientes o U de
  Mann-Whitney; α = 0,05.

La variable dependiente se mide por **observación directa de cada ingreso** mediante la ficha de
observación, no con consultas al sistema. El sistema debe conservar marcas de tiempo confiables
porque sirven para triangular el postest, pero no es la fuente del indicador.

## 3. Variable independiente: sistema web inteligente

Se evalúa una sola vez, después de la implementación.

| Dimensión | Indicador | Sigla | Instrumento |
|---|---|---|---|
| D1 Funcionalidad del sistema | % de requerimientos funcionales cumplidos | RFC | Lista de control de funcionalidad |
| D1 Funcionalidad del sistema | % de casos de prueba superados | CPS | Lista de control de funcionalidad |
| D2 Capacidad inteligente | Exactitud del reconocimiento automático del ticket | ERA | Ficha de capacidad inteligente, hoja A |
| D2 Capacidad inteligente | Tasa de detección de inconsistencias | TDI | Ficha de capacidad inteligente, hoja B |
| D3 Usabilidad del sistema | Puntaje SUS (≥ 68 aceptable) | SUS | Cuestionario SUS |
| D3 Usabilidad del sistema | % de tareas completadas sin asistencia | TCA | Ficha de capacidad inteligente, hoja C |

El denominador de RFC son los **10 RF** de la sección 5, no un número de módulos. Las cinco
características de ISO/IEC 25010 y el protocolo de carga dejaron de ser instrumento de esta
variable; la norma se conserva únicamente como taxonomía para clasificar los RNF.

## 4. Variable dependiente: control de inventarios de ingreso de mineral

| Dimensión | Indicador | Fórmula por ingreso | Unidad |
|---|---|---|---|
| D1 Oportunidad del registro | I1 Tiempo de espera del registro | Inicio del registro − fecha y hora del ticket | h |
| D1 Oportunidad del registro | I2 Tiempo de registro del ingreso | Fin del registro − inicio del registro | min |
| D2 Integridad del registro | I3 Completitud del registro | Campos consignados / 7 × 100 | % |
| D2 Integridad del registro | I4 Tiempo de recuperación del respaldo | Consulta → presentación del ticket y sus datos | min |
| D3 Consolidación de la producción | I5 Tiempo de consolidación | Solicitud → entrega del total acumulado del mes por producto que incluye el ingreso | min |
| D3 Consolidación de la producción | I6 Grado de trazabilidad | Etapas vinculadas / 4 × 100 | % |

**Campos de completitud (I3):** C1 placa · C2 fecha y hora · C3 peso bruto · C4 tara · C5 peso neto ·
C6 tipo de mineral · C7 tipo de vehículo (propio o externo).

**Etapas del proceso (I6):** secado, zarandeo, molienda, ensacado.

> Los indicadores I1 a I6 del sistema anterior llevaban la misma numeración con otro significado.
> Ninguna referencia a aquellos debe sobrevivir en el repositorio.

## 5. Requerimientos funcionales (lista de control, Anexo 03)

| RF | Descripción |
|---|---|
| RF01 | Registrar el ingreso de mineral con la imagen del ticket de balanza |
| RF02 | Reconocer automáticamente los datos del ticket: placa, fecha, hora, peso bruto, tara y peso neto |
| RF03 | Validar automáticamente la consistencia de los datos del ticket: pesos, formato de placa, capacidad del vehículo y fecha |
| RF04 | Permitir el registro y la corrección manual de los datos reconocidos |
| RF05 | Asignar un código único a cada ingreso de mineral |
| RF06 | Registrar el tipo de mineral y el tipo de vehículo (propio o externo) |
| RF07 | Vincular cada ingreso con las etapas de secado, zarandeo, molienda y ensacado |
| RF08 | Consultar un ingreso por placa y fecha con su ticket de respaldo |
| RF09 | Generar y exportar el total acumulado mensual por producto |
| RF10 | Gestionar usuarios y roles de acceso |

La redacción ampliada de RF03 y la inclusión de la exportación en RF09 corresponden a DR-06 y deben
estar reflejadas en el Anexo 03 del documento de tesis **antes** del juicio de expertos. Después de
esa validación, la lista queda fija: cualquier cambio altera el denominador de RFC.

Formato del código: `RF01`, sin guion.

## 6. Tareas de usabilidad (hoja C)

| Tarea | Descripción |
|---|---|
| T01 | Registrar un ingreso a partir de la imagen del ticket |
| T02 | Corregir un dato reconocido de forma incorrecta |
| T03 | Consultar un ingreso por placa y fecha |
| T04 | Vincular un ingreso con una etapa del proceso |
| T05 | Obtener el total acumulado mensual por producto |
| T06 | Exportar el total acumulado mensual por producto |

## 7. Reglas de validación (hoja B)

| Regla | Inconsistencia | Tipo |
|---|---|---|
| V1 | Peso neto distinto de peso bruto menos tara (tolerancia 0,01 t) | Bloqueante |
| V2 | Tara mayor o igual que el peso bruto | Bloqueante |
| V3 | Placa con formato inválido | Bloqueante |
| V4 | Peso neto fuera del rango de carga del vehículo, según la capacidad del catálogo | Exige justificación |
| V5 | Fecha del ticket posterior a la fecha de registro | Bloqueante |

La tolerancia de 0,01 t es el valor adoptado; confirmarlo con la empresa antes de fijar el conjunto
de prueba. El patrón de placa peruana se documenta en el módulo de validación.

**Conjunto de prueba (DR-08):** ERA sobre 50 tickets reales × 6 campos. TDI sobre 10
inconsistencias sembradas, 2 por regla. Motor y reglas congelados durante toda la medición.

## 8. Roles

| Rol | Alcance |
|---|---|
| Administrador | Acceso total, incluidos usuarios, catálogos y anulaciones |
| Administrativo | Registro, corrección, consultas, consolidación y exportación |
| Supervisor de planta | Registro y consulta |

## 9. Módulos

Cada módulo existe por una **responsabilidad del dominio**. La relación con los indicadores se
registra en `../02-trazabilidad/matriz_HU_RF_indicador.md`, no en los documentos de módulo.

| Módulo | Nombre | Responsabilidad | RF |
|---|---|---|---|
| M01 | Autenticación y roles | Identificar al usuario y limitar cada operación según su rol | RF10 |
| M02 | Catálogo maestro | Mantener tipos de mineral, vehículos con titularidad y capacidad, y transportistas | RF06 (soporte) |
| M03 | Registro de ingresos | Registrar el ingreso desde la imagen del ticket, con corrección, confirmación y código único | RF01, RF04, RF05, RF06 |
| M04 | Reconocimiento automático del ticket | Leer los seis campos del ticket con su nivel de confianza | RF02 |
| M05 | Validación automática de consistencia | Aplicar V1 a V5 en el servidor y registrar el resultado | RF03 |
| M06 | Trazabilidad del proceso | Asignar ingresos a lotes y registrar su paso por cada etapa | RF07 |
| M07 | Consulta de ingresos y respaldo | Localizar un ingreso por placa y fecha y presentar su ticket | RF08 |
| M08 | Consolidación de la producción | Calcular y exportar el total acumulado mensual por producto | RF09 |
| M09 | Auditoría | Registrar quién hizo qué y cuándo, incluidos reconocimiento y corrección | — (transversal) |

## 10. Fuera de alcance

Salidas y ventas · inventario de producto terminado, sus movimientos internos y las pérdidas por
humedad · reportes normativos periódicos · facturación, precios y fletes · contabilidad y planillas ·
actividad en la mina · mineral sulfuro · integración con la balanza · predicción de demanda o
pronósticos · aplicación móvil nativa · operación sin señal de red, salvo la conservación del
borrador · operación multiempresa · balance metalúrgico y determinación de leyes.

## 11. Condición de campo

El pretest se mide sobre el proceso manual actual, con unos 30 ingresos al mes; reunir de 90 a 100
toma cerca de tres meses y medio, de modo que puede correr en paralelo con el desarrollo. **El
sistema no se usa en planta hasta que el pretest termine.**
