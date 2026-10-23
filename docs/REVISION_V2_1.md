# Revisión y validación de la versión 2.1 de la documentación

| Campo | Valor |
|---|---|
| Fecha | 23/10/2026 |
| Alcance | Todo `docs/`, `skills/contexto-tesis`, `skills/requisitos-modulo`, `skills/solid-proyecto`, `scripts/generar_pdf_requerimientos.py` y `Mockup/index.html`; el cierre del modelo C4 se registra en la sección 8 |
| Propósito | Cerrar la versión 2.1 de la documentación del sistema: contrastarla con la maqueta validada por el autor, resolver las divergencias y dejarla lista como base de la documentación requerida por la tesis y de la implementación |
| Resultado | **Documentación revisada y validada.** Sin hallazgos en las comprobaciones automáticas ni divergencias abiertas entre la documentación y la maqueta |
| Antecedente | [`REVISION_TECNICA_V2.md`](REVISION_TECNICA_V2.md), revisión técnica del 21/10/2026 y sus resoluciones del 22/10/2026 |
| Índice de archivos | [`INDICE.md`](INDICE.md), generado por `scripts/indexar_docs.py` |

---

## 1. Estado de la validación

| Comprobación | Resultado | Cómo se verifica |
|---|---|---|
| Conceptos del alcance anterior en `docs/` y `skills/` | Sin hallazgos | `scripts/verificar_migracion.sh` |
| Mermaid, enlaces y referencias cruzadas (HU, RU, RS, RNF, RN, S, A, D, DR) | Sin hallazgos | `scripts/validar_docs.py` |
| Códigos RU, RS, RNF y RN citados y no definidos | Ninguno | Comprobación 1 de la skill `revision-coherencia` |
| Formato de RF | Solo `RF01` a `RF10`, sin guion | Comprobación 1 de la skill `revision-coherencia` |
| Cobertura de cada historia en `funcionales.md`, diagramas, matriz e índice | 27 de 27 | Comprobación 2 de la skill `revision-coherencia` |
| Numeración de historias y cabeceras de `HU.md` | Sin saltos ni duplicados; cada cabecera coincide con sus historias | Comprobación 3 de la skill `revision-coherencia` |
| Tildes, eñes y signos de apertura dentro de Mermaid | Ninguno | Comprobación 4 de la skill `revision-coherencia` |
| Diagramas Mermaid que renderizan | 88 de 88, incluidos los diez de ARQ-03 | Render de cada bloque con Mermaid 11 en Chrome sin interfaz |
| Operaciones restringidas por rol con criterio de rechazo | Todas | Revisión de las 27 historias |
| RNF con característica ISO/IEC 25010:2023 y método de verificación | 87 de 87, con la nomenclatura de la edición 2023 | Revisión de los nueve `no_funcionales.md` |
| Mensajes literales de los criterios frente a la maqueta | Coinciden, salvo los que solo produce el servidor: bloqueo de cuenta, expiración de sesión, ticket ilegible o motor no disponible, y los rechazos que la interfaz ya evita al no ofrecer la acción (confirmar sin imagen, asignar un anulado, registrar una etapa fuera de orden o repetida) | Contraste automático de los 277 criterios con `Mockup/index.html` |
| Pantallas y acciones de la maqueta con especificación | Todas | Inventario de rutas y acciones de la maqueta contra M01 a M09 |
| PDF de historias (63 páginas) y de requerimientos y diagramas (178 páginas) | Regenerados con la versión 2.1; todos los diagramas Mermaid renderizados | `scripts/generar_pdf_hu.py`, `scripts/generar_pdf_requerimientos.py` |

La validación garantiza **coherencia interna** y **correspondencia con la maqueta**. Que el sistema
descrito sea el que la planta necesita lo confirman los puntos de la sección 6 que dependen de la
empresa.

## 2. Contenido de la versión 2.1

| Elemento | Cantidad |
|---|---|
| Módulos | 9 (M01 a M09) |
| Requerimientos funcionales globales | 10 (RF01 a RF10), sin cambios |
| Historias de usuario | 27 (una más que la versión 2: HU-M07-04) |
| Criterios de aceptación | 277 |
| Requerimientos de usuario | 71 |
| Requerimientos de sistema | 170 |
| Funciones expuestas | 74 |
| Requerimientos no funcionales | 87 |
| Reglas de negocio | 143 |
| Casos de uso | 50 |
| Diagramas | 76 |
| Decisiones de reformulación | 31 (DR-01 a DR-31) |
| Decisiones de diseño | 16 (D-01, D-02 y D-06 a D-19), de las cuales D-12, D-14 y D-15 siguen pendientes de cierre; D-03 a D-05 están retiradas |

## 3. Decisiones incorporadas en esta versión

| Código | Decisión | Módulos |
|---|---|---|
| DR-29 | Un ingreso asignado por error puede retirarse del lote, o trasladarse, hasta que su mineral pase por zarandeo o molienda, también con el lote En recorrido; el lote En recorrido conserva al menos un ingreso. Amplía DR-22 | M06, modelo de datos |
| DR-30 | La maqueta 2.1 aporta cuatro elementos que pasan a la especificación: la pantalla de inicio con el resumen del día y los avisos de pendientes según el rol; la exportación a CSV del listado de ingresos; la gestión de cuentas y bajas (restablecimiento de contraseña con cambio obligatorio, prohibición de desactivar la propia cuenta, reactivación de usuarios y de registros de catálogo); y la búsqueda desde la cabecera | M01, M02, M07, M09 |
| DR-31 | Los tres roles consultan el reconocimiento y la validación de un ingreso; el Supervisor de planta sigue sin corregir ni anular | M01, M04, M05 |

Ninguna de las tres crea un RF: el denominador de la lista de control sigue siendo diez.

## 4. Correcciones hechas en la revisión

### 4.1 Divergencias resueltas con decisión del autor

| Divergencia | Resolución |
|---|---|
| La maqueta ofrecía la pantalla de inicio, los avisos, la exportación del listado, el restablecimiento de contraseñas, la reactivación y la búsqueda de la cabecera, sin especificación; M07 marcaba la exportación como pendiente de decidir | DR-30: HU-M07-04 nueva; HU-M07-02, HU-M01-01, HU-M01-02 y HU-M02-01 a HU-M02-03 ampliadas, con sus requerimientos, reglas, diagramas y notas |
| M04 y M05 negaban al Supervisor de planta la consulta del reconocimiento y la validación, que la maqueta le mostraba | DR-31: permisos, casos de uso y criterios de M04 y M05, matriz de M01 |
| La documentación solo permitía retirar ingresos de un lote Abierto | DR-29: M06 completo y modelo de datos; la maqueta ya aplica la regla |

### 4.2 Divergencias resueltas por la fuente de mayor orden

| Hallazgo | Corrección |
|---|---|
| Criterios de M01 y M02 que describían «eliminar» un usuario o un registro de catálogo, cuando nada se elimina (D-07) | Reformulados como baja lógica, con su mensaje; RN-M01-03 y RN-M02-08 dejan de condicionar la regla a tener registros dependientes |
| HU-M01-03 CA01 describía un menú del Supervisor sin el inicio, el listado ni el calendario, que M07 le concede | Menú completo por rol en HU-M01-03 y en la guía del frontend |
| HU-M02-01 a HU-M02-03 no verificaban el rechazo por rol | CA14, CA10 y CA06 nuevos |
| HU-M01-03 no figuraba en la tabla de funciones de M01 | Función «Controlar el acceso por rol» |
| 29 RNF usaban la taxonomía de ISO/IEC 25010:2011 bajo el rótulo de la edición 2023 —«Usabilidad», «madurez»— y uno citaba una subcaracterística inexistente, «Fiabilidad — exactitud» | Renombrados a la edición 2023 —«Capacidad de interacción», «ausencia de fallos»— y RNF-M08-05 reclasificado como «Adecuación funcional — corrección». La skill `requisitos-modulo` documenta la nomenclatura |
| Mensajes de HU-M06-02 (identificaba el lote por su código, cuando la planta lo nombra), HU-M06-04 (fracciones) y HU-M09-03 (consulta sin resultados) distintos de la maqueta y menos precisos | Alineados en las historias y en sus diagramas |
| M03 hablaba del «tipo de mineral del lote», anterior a DR-27, y situaba la reversión de una corrección en el historial | «Lista de tipos de mineral del lote»; la reversión se ofrece desde el detalle y el listado |
| Pendientes ya resueltos que seguían abiertos: el ajuste de la maqueta (M06), el retiro de `Cliente` (M02), quién registra el destare y cómo se agrupa el mineral (modelo de datos) | Retirados o actualizados |
| Versiones desactualizadas: ARQ-01 a ARQ-03 y el modelo de datos en la 3.0 «hasta DR-23», la matriz en la 2.0 «hasta DR-22» | Todas en la versión 2.1 del sistema, hasta DR-31 |
| El PDF de requerimientos se emitía como «Versión 1.0», con una rama de origen que ya no existe | El generador toma la versión 2.1, el historial de versiones y la rama actual |

### 4.3 Ajustes de la maqueta a la documentación

| Ajuste | Referencia |
|---|---|
| Retiro de un ingreso del lote hasta el zarandeo o la molienda, también En recorrido; traslado con la misma regla | DR-29, HU-M06-01 |
| La contraseña temporal obliga a cambiarla antes de continuar | HU-M01-01 CA09, HU-M01-02 CA08 |
| Mensajes de la corrección y del inicio del recorrido | HU-M03-02 CA01, HU-M06-01 CA10 |
| Mensajes de la baja de vehículos, tipos de mineral y transportistas con registros asociados | HU-M02-01 CA06, HU-M02-02 CA03, HU-M02-03 CA03 |
| Aviso de ingresos En proceso en la consolidación | HU-M08-01 CA07 |
| La pestaña de reconocimiento decía que el sistema asigna la fecha y la hora del pesaje; la fecha se lee del ticket y la hora la indica el usuario | DR-09, DR-11 |

## 5. Documentos entregables

| Documento | Uso |
|---|---|
| [`HistoriasUsuario.md`](HistoriasUsuario.md) y `Historias_de_Usuario.pdf` | Especificación de las 27 historias con sus criterios |
| `Requerimientos_y_Diagramas.pdf` | Requerimientos, reglas, casos de uso y diagramas de los nueve módulos, versión 2.1 |
| [`02-trazabilidad/matriz_HU_RF_indicador.md`](02-trazabilidad/matriz_HU_RF_indicador.md) | Única relación entre el sistema y los indicadores de la tesis |
| [`03-pruebas/plan_de_pruebas.md`](03-pruebas/plan_de_pruebas.md) | Lista de control CP01 a CP10, conjunto de la capacidad inteligente y tareas de usabilidad |
| [`00-arquitectura/modelo_datos_entidad_relacion.md`](00-arquitectura/modelo_datos_entidad_relacion.md) | Modelo de datos 3.1 |
| [`model-c4/`](model-c4/) y `model-c4/ARQ-03_Modelo_C4.pdf` | ARQ-01 a ARQ-03, versión 3.1; ARQ-03 validado con sus cuatro niveles y la vista de despliegue, y su PDF con los diagramas renderizados |
| Este informe y su PDF | Constancia de la revisión |

## 6. Puntos abiertos

Ninguno bloquea la documentación del sistema; varios bloquean la implementación o la medición. Se
conserva la numeración de la revisión anterior. Estado actualizado al cierre de la fase documental
(`01-plan/ACTA_CIERRE_FASE_DOCUMENTAL.md`).

| ID | Sev. | Punto | Estado | Quién decide | Antes de |
|---|---|---|---|---|---|
| Q-17 | B | Anexos 02, 03 y 04 del documento de tesis desactualizados (DR-06, DR-09, DR-16, DR-21) | Fuera de esta fase: lo atiende el proceso de la tesis | Autor | **El juicio de expertos** |
| Q-18 | A | P-03: tratamiento del ingreso sin foto en la ficha de observación | Fuera de esta fase; sigue marcado `[PENDIENTE]` en la matriz | Autor | Anexo 02 |
| Q-19 | A | La hora del pesaje propuesta puede sesgar la medición del tiempo de espera | Fuera de esta fase; la ficha debe registrar la hora real por observación directa | Autor | Anexo 02 |
| Q-03 | B | Valores del catálogo de tipos de mineral (DR-03) | Programado en la semana 2 del plan | Empresa | Implementar M02 |
| Q-12 | M | Validar los tres roles y su matriz de permisos con los usuarios (DR-23), ahora con DR-30 y DR-31 | Programado al inicio de la semana 1 | Usuarios | Implementar M01 |
| Q-04 | B | Piloto del motor de reconocimiento (D-12) | Provisional: adaptador local en el backend; piloto en la semana 7, con el sistema funcional | Autor | El congelamiento de la semana 8 |
| Q-05 | A | Almacenamiento, retención y respaldo de las imágenes (D-14) | Provisional: volumen `media` del backend (D-14, D-18) | Autor | El servicio de alojamiento de la presentación |
| Q-06 | A | No existe un requisito de respaldo de la base de datos | Resuelto por D-20: respaldo mínimo ejecutable desde la semana 1; política definitiva con el alojamiento | Autor | La operación real |
| Q-02 | A | Ocho pruebas del backend citan criterios de historias de M03 retiradas en la reformulación, con la numeración anterior a la versión 2 | Abierto; se resuelve con el refactor de `apps/ingresos` | Autor | Implementar M03 |
| Q-16 | b | Códigos de ruta propuestos y no decididos | Resuelto por D-21 | Autor | — |
| Q-20, Q-21 | A, M | Denominador de la trazabilidad y congelamiento de motor y reglas durante la medición | Abiertos; el sistema ya exige la ruta antes de las etapas siguientes al secado | Autor | La medición |
| Q-22 a Q-26 | M, b | Rama de integración, repositorio del frontend, servidores, contratos entre módulos y tratamiento de datos personales | La rama la fija el responsable del repositorio; el repositorio del frontend se crea en la semana 1; los servidores, con el alojamiento de la presentación; Q-25 y Q-26 siguen abiertos | Autor | La semana 1 de implementación |

## 7. Siguiente fase

La documentación del sistema queda cerrada en la versión 2.1. Cualquier cambio posterior entra
como una decisión de reformulación nueva, la siguiente a DR-31, con su revisión de dependencias.

Orden recomendado para la documentación requerida por la tesis:

1. **Anexos del documento de tesis** (Q-17, Q-18, Q-19): ficha de observación con la fórmula de la
   trazabilidad por ruta y el tratamiento del ingreso sin foto; lista de control con RF02 a tres
   campos y RF03 con la duplicidad; ficha de la capacidad inteligente con la hoja A a tres campos y
   la hoja B con la nueva V1. La correspondencia con el sistema está en la matriz de trazabilidad.
2. **Validación con la empresa** (Q-03, Q-12): valores del catálogo de tipos de mineral y matriz de
   roles, con la maqueta 2.1 como soporte.
3. **Decisiones técnicas previas a la implementación** (Q-04, Q-05, Q-06, Q-22).

## 8. Cierre del modelo C4 (23/10/2026)

### 8.1 Hallazgos

La revisión de `model-c4/ARQ-03_Modelo_C4.md` encontró que el documento tenía los cuatro niveles,
pero no estaba cerrado:

| ID | Tipo | Hallazgo |
|---|---|---|
| C4-01 | Incompleto | El nivel 3 no dibujaba M06, el módulo con más reglas después de M03, ni M07, el lado de lectura |
| C4-02 | Incompleto | No había vista de despliegue; ARQ-02 describía los entornos solo en texto |
| C4-03 | Desactualizado | El modelo `Ingreso` citaba «RN-M03-01 a RN-M03-27»; M03 llega a RN-M03-29 |
| C4-04 | Desactualizado | `ServicioIngreso` no tenía `revertir_correccion` (DR-28) en los niveles 3 y 4 |
| C4-05 | Incoherente | El nivel 3 inyectaba `AlmacenImagenes`; el nivel 4, las notas de M03 y D-09 solo admitían cuatro interfaces |
| C4-06 | Incoherente | `SelectorIngresos` atribuía a M03 un listado con totales, que HU-M07-02 asigna a M07; M03 y M07 exponían dos listados de la misma entidad |
| C4-07 | Incoherente | Las notas de M09 inyectan `ServicioAuditoria` en todo servicio de escritura, pero el constructor de `ServicioIngreso` en M03, ARQ-02 y el nivel 4 no lo incluían |
| C4-08 | Error | El diagrama de componentes de M04 usaba sintaxis de diagrama de clases dentro de un `flowchart` y no se renderizaba |
| C4-09 | Desactualizado | La tabla de contenedores que no existen solo mencionaba la exportación del consolidado, y no explicaba por qué no hay servicio de notificaciones |
| C4-10 | Desactualizado | La trazabilidad del modelo no cubría DR-27 a DR-31 |
| C4-11 | Incoherente | D-10 citaba un `ExportadorPDF` que M08 no tiene: su primera versión solo exporta XLSX |
| C4-12 | Incoherente | Las notas de M07 registraban la exportación desde la vista, y no desde el servicio como hace M08 |
| C4-13 | Menor | M03 llamaba `RepositorioLote` al repositorio de M06 que el resto de la documentación llama `RepositorioTrazabilidad` |

### 8.2 Consultas al autor y decisiones registradas

C4-05 y C4-06 exigían una decisión de diseño. Se consultaron al autor el 23/10/2026:

| Consulta | Opciones | Respuesta | Registro |
|---|---|---|---|
| ¿Cómo accede `ServicioIngreso` al almacén de imágenes? | API de almacenamiento de Django · interfaz propia inyectada | API de almacenamiento de Django | **D-18** |
| ¿Qué módulo es dueño del listado de ingresos? | Solo M07 · mantener ambos | Solo M07 | **D-19** |

Las demás se resolvieron con la fuente de mayor orden, sin decisión nueva: C4-07 con las notas de M09,
que ya fijaban la inyección; C4-11 con HU-M08-02, que fija XLSX como único formato inicial; C4-12 con
el patrón de M08 y la regla de que las vistas solo traducen HTTP (ARQ-02 §5).

### 8.3 Correcciones

| Hallazgo | Corrección | Archivos |
|---|---|---|
| C4-01 | Secciones 4.5 (M06) y 4.6 (M07), con su diagrama y la justificación de cada componente | ARQ-03 |
| C4-02 | Sección 6, vista de despliegue: Compose por entorno, volúmenes con nombre, motor según D-12, respaldo como pendiente Q-06 | ARQ-03 |
| C4-03, C4-04 | Nivel 3 de M03 rehecho; `revertir_correccion` en el nivel 4 | ARQ-03 |
| C4-05 | D-18: la imagen se guarda por el `ImageField`, que delega en el almacenamiento de Django; sin interfaz propia | `decisiones_diseno.md`, ARQ-02, ARQ-03, notas de M03, `GUIA_MARCO_DE_TRABAJO.md` |
| C4-06 | D-19: M03 retira su listado general y conserva el recurso del ingreso y los pendientes de destare | `decisiones_diseno.md`, funcionales y caso de uso de M03, reglas de M07, ARQ-02, ARQ-03 |
| C4-07 | `ServicioAuditoria` en el constructor de `ServicioIngreso` y en los niveles 3 y 4 | Notas de M03, ARQ-02, ARQ-03 |
| C4-08 | Relación de implementación expresada con flechas de `flowchart` | ARQ-03 |
| C4-09, C4-10 | Tabla de contenedores y trazabilidad ampliadas | ARQ-03 |
| C4-11 | D-10 y D-09 nombran los exportadores reales de M07 y M08 | `decisiones_diseno.md`, ARQ-02, skill `solid-proyecto` |
| C4-12 | `ServicioConsulta.exportar_listado()` orquesta la exportación y registra el evento | Notas, secuencia y sistema de M07 |
| C4-13 | Nombre unificado | Secuencia de M03 |

ARQ-03 pasa a la versión 3.1 con estado **Validado** y una tabla de control de versiones.

### 8.4 Validación

| Comprobación | Resultado |
|---|---|
| `scripts/verificar_migracion.sh` | Sin hallazgos |
| `scripts/validar_docs.py` | Sin hallazgos |
| Render de los 88 diagramas Mermaid del repositorio | 88 de 88 |
| PDF de requerimientos y diagramas | Regenerado con el cambio de M03 |
| PDF de ARQ-03 | Generado con sus diez diagramas renderizados; `scripts/md_a_pdf.py` ahora renderiza los bloques Mermaid |

