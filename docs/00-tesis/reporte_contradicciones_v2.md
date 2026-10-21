# Reporte de contradicciones — versión 2 frente a la arquitectura

| Campo | Valor |
|---|---|
| Documento | Reporte de contradicciones de la Fase 3 de `plan_version2.md` |
| Fecha | 21/10/2026 |
| Fuentes contrastadas | `marco_tesis.md`, `decisiones_reformulacion.md` (DR-01 a DR-22) y los nueve módulos de `docs/modulos/` en su versión 2 |
| Documentos revisados | `00-arquitectura/`, `model-c4/` y las skills que los repiten |
| Estado | Para decisión del autor. **Ningún archivo de arquitectura se modificó** |

El plan de la versión 2 excluye `00-arquitectura/`, `model-c4/` y `backend/`, y en esta fase solo
pide reportar. Por el orden de las fuentes de verdad de `CLAUDE.md`, las decisiones DR prevalecen
sobre las decisiones de diseño D-nn: en cada fila, el texto de arquitectura es el que queda
desactualizado.

---

## 1. Contradicciones con las decisiones de diseño (D-nn)

| N.° | Decisión | Texto vigente | Decisión que lo contradice | Propuesta |
|---|---|---|---|---|
| C-01 | D-01, tabla de marcas | «la hora la digita el usuario, porque el ticket no la imprime (DR-09)» | DR-11: el sistema propone la hora actual y el usuario la ajusta | Cambiar el origen a «la hora la indica el usuario sobre una propuesta del sistema con la hora actual (DR-11)» |
| C-02 | D-01, tabla de marcas | «Inicio del registro: asignada por el servidor al recibir la imagen» | DR-13: en el registro sin foto no hay imagen; M03 fija el inicio cuando el usuario elige registrar sin foto (HU-M03-01, Detalles) | Añadir el caso sin foto a la fila del inicio del registro |
| C-03 | D-07 y el modelo de datos | La imagen del ticket es obligatoria y no se sustituye (`modelo_datos_entidad_relacion.md`, invariantes y campo `imagen_ticket`) | DR-13: registro sin foto con motivo y marca «sin respaldo fotográfico» | Hacer `imagen_ticket` nula solo con motivo de registro sin foto; añadir `sin_respaldo_fotografico` y `motivo_sin_foto`; reescribir la invariante |
| C-04 | D-13 | Supone que todo ingreso pasa por el reconocimiento | DR-13: el ingreso sin foto no tiene reconocimiento ni `CAMPO_RECONOCIDO` | Añadir que D-13 no aplica al ingreso sin foto, cuyos datos digita el usuario y validan V1 a V5 |

## 2. Contradicciones con el modelo de datos

`00-arquitectura/modelo_datos_entidad_relacion.md` es el documento más desactualizado. Los módulos
de la versión 2 ya describen en sus `notas.md` entidades que el modelo no tiene.

| N.° | Elemento | Texto vigente | Decisión que lo contradice | Propuesta |
|---|---|---|---|---|
| C-05 | `INGRESO.numero_ticket` | Opcional, único entre los no anulados | DR-12: no existe número de ticket | Retirar el campo y su índice parcial |
| C-06 | `INGRESO.fecha_hora_pesaje` | «hora digitada por el usuario» | DR-11 | Igual que C-01 |
| C-07 | `LOTE_PROCESO.estado` | ABIERTO / CERRADO | DR-19: Abierto, En recorrido y Cerrado | Añadir EN_RECORRIDO y la fecha del inicio del recorrido |
| C-08 | `LOTE_PROCESO` | Sin nombre, ruta, partes, fracciones, bigbags, destino ni horas de molienda | DR-14, DR-15, DR-16, DR-18, DR-20 | Incorporar las entidades que ya usa M06: `PARTE_LOTE`, `REPARTO_INGRESO` y `BIGBAG`, y los campos de nombre, ruta, destino y resumen del cierre |
| C-09 | `ETAPA_PROCESO.orden` | «1 a 4, orden del proceso» | DR-16: la ruta no recorre siempre las cuatro etapas | Mantener el orden como posición dentro de una ruta y documentar las tres rutas admitidas |
| C-10 | `TIPO_MINERAL` | `codigo varchar(20)` único; `nombre` sin unicidad | M02 versión 2: RN-M02-15 y RN-M02-16 | Añadir la unicidad sin distinguir mayúsculas y el formato de dos a seis caracteres |
| C-11 | `TRANSPORTISTA.ruc` | `varchar(11)` sin restricción de unicidad | M02 versión 2: RN-M02-18 | Añadir la restricción de unicidad |

## 3. Contradicciones con las guías y el modelo C4

| N.° | Archivo | Texto vigente | Decisión que lo contradice | Propuesta |
|---|---|---|---|---|
| C-12 | `00-arquitectura/GUIA_FRONTEND_ANGULAR.md` | «La hora del pesaje se digita en un campo sin valor precargado» | DR-11 | Reescribir: el campo trae la hora actual y debe ajustarse a la del pesaje real |
| C-13 | `00-arquitectura/GUIA_MARCO_DE_TRABAJO.md` | El modelo `Ingreso` de ejemplo incluye `numero_ticket` y comenta «hora digitada» | DR-11, DR-12 | Actualizar el ejemplo, o fusionar la guía en las skills `backend-django` y `solid-proyecto` (mapa de limpieza §3) |
| C-14 | `model-c4/ARQ-01_Modulos_del_Sistema.md` | M06 «registra su paso por secado, zarandeo, molienda y ensacado» | DR-14, DR-16, DR-18 | Usar la responsabilidad del marco: ruta por lote o parte, división por fracciones y cierre con destino |
| C-15 | `model-c4/ARQ-02_Arquitectura_Tecnica.md` §5 | «El rol Supervisor de planta obtiene únicamente las interfaces de registro y consulta» | DR-17 | Ampliar con el alta de vehículo, el destare y el paso por etapa, como ya dice la skill `solid-proyecto` |
| C-16 | `model-c4/ARQ-03_Modelo_C4.md` | Las cuatro etapas como recorrido fijo (mapa de limpieza §3) | DR-16 | Revisar con la ruta decidida |

## 4. Skills que repiten la arquitectura

| N.° | Skill | Texto vigente | Decisión | Propuesta |
|---|---|---|---|---|
| C-17 | `base-datos-postgresql` | Índice de unicidad parcial de `numero_ticket` y su casilla de verificación | DR-12 | Retirar ambas menciones al actualizar el modelo de datos |
| C-18 | `reconocimiento-validacion` | No menciona el registro sin foto | DR-13 | Añadir que el ingreso sin foto no invoca `ReconocedorTicket`, pero sí `ValidadorConsistencia` |

## 5. Observaciones entre fuentes de verdad

No son contradicciones con la arquitectura, sino diferencias de redacción entre documentos de orden
más alto que conviene confirmar:

| N.° | Diferencia | Situación |
|---|---|---|
| O-01 | El marco (§8) asigna los catálogos al Administrador y no los menciona en el alcance del Administrativo; M02 y el mockup permiten al Administrativo crear, editar y desactivar entradas de catálogo | Se conservó lo de M02 y el mockup, que ya regía en la versión 1. Si la intención es que solo el Administrador gestione catálogos, cambian M02, M03 (alta de tipo de mineral desde el registro) y M01 |
| O-02 | El marco (§8) no menciona que el Administrativo compone y divide lotes; M06 y el mockup sí se lo permiten | Igual que O-01 |
| O-03 | P-03 sigue abierto: cómo trata la ficha de observación un ingreso sin respaldo fotográfico en I3 e I4 | La matriz de trazabilidad lo marca `[PENDIENTE: P-03]` |
| O-04 | `docs/Historias_de_Usuario_v1.1.docx` no se puede regenerar | Sigue a la espera de la decisión del mapa de limpieza §1 |

## 6. Orden propuesto para resolverlas

1. Decidir si se levanta la exclusión de `00-arquitectura/` y `model-c4/` (mapa de limpieza §6, punto 1).
2. Si se levanta: C-03 a C-11 en el modelo de datos, en un solo commit, porque los módulos M03 y M06
   ya dependen de esos cambios. Después C-01, C-02 y C-04 en `decisiones_diseno.md`.
3. C-12 a C-16, y finalmente C-17 y C-18 en las skills.
4. Confirmar O-01 y O-02 antes de implementar M02 y M06.

## Consecuencia de no resolverlas

Quien implemente M03 o M06 siguiendo `modelo_datos_entidad_relacion.md` construirá un ingreso con
número de ticket y sin la posibilidad de registrarse sin foto, y un lote de dos estados sin ruta ni
partes. El código contradiría las historias de usuario aprobadas, y las pruebas de aceptación CP07,
CP11 y CP12 fallarían por diseño, no por defecto de implementación.
