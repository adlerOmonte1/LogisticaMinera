# Acta de cierre de la fase documental

| Campo | Valor |
|---|---|
| Documento | ACTA-01 |
| Proyecto | Sistema web inteligente para el control de inventarios de ingreso de mineral — Construcción y Minería, planta de Pillcomarca, Huánuco |
| Fase que se cierra | Documentación del sistema: reformulación del alcance y especificación de la versión 2.1 |
| Periodo | 21/09/2026 a 23/10/2026 |
| Fecha de cierre | 23/10/2026 |
| Línea base | **2.1** |
| Fase siguiente | Implementación, según [`PLAN_DE_TRABAJO.md`](PLAN_DE_TRABAJO.md) §8 |
| Informe de validación | [`../REVISION_V2_1.md`](../REVISION_V2_1.md) |

---

## 1. Objeto

Dejar constancia de que la documentación del sistema está completa, revisada y validada; fijar la
línea base contra la que se programa; registrar el estado de cada decisión al cierre; y establecer
cómo se gestiona cualquier cambio a partir de esta fecha.

La documentación de la tesis —anexos, instrumentos y ficha de observación— sigue su propio proceso y
no forma parte de esta fase. La relación entre la tesis y el sistema está en un solo lugar, la matriz
de trazabilidad, que sí pertenece a la línea base.

## 2. Línea base 2.1

Ningún documento de esta tabla se modifica sin seguir la sección 5.

| Documento | Versión | Estado |
|---|---|---|
| [`../00-tesis/marco_tesis.md`](../00-tesis/marco_tesis.md) | Actualizado el 23/10/2026 | Fuente de verdad 1 |
| [`../00-tesis/decisiones_reformulacion.md`](../00-tesis/decisiones_reformulacion.md) | DR-01 a DR-31 | Todas aceptadas |
| [`../00-arquitectura/decisiones_diseno.md`](../00-arquitectura/decisiones_diseno.md) | D-01 a D-22 | Ver sección 4 |
| [`../modulos/`](../modulos/) M01 a M09 | 2.1 | Validados |
| [`../HistoriasUsuario.md`](../HistoriasUsuario.md) | 3.1 | Validado |
| [`../02-trazabilidad/matriz_HU_RF_indicador.md`](../02-trazabilidad/matriz_HU_RF_indicador.md) | 2.1 | Validada |
| [`../00-arquitectura/modelo_datos_entidad_relacion.md`](../00-arquitectura/modelo_datos_entidad_relacion.md) | 3.1 | Validado |
| [`../model-c4/`](../model-c4/) ARQ-01, ARQ-02 y ARQ-03 | 3.1 | Validados; ARQ-03 con su PDF |
| [`../03-pruebas/plan_de_pruebas.md`](../03-pruebas/plan_de_pruebas.md) | 2.1 | Vigente |
| [`PLAN_DE_TRABAJO.md`](PLAN_DE_TRABAJO.md) | 2.2 | Vigente |
| Guías de `../00-arquitectura/`: marco de trabajo, frontend y convenciones de código | Alineadas con la 2.1 | Vigentes |
| [`../../Mockup/index.html`](../../Mockup/index.html) | 2.1 | Alineada con la documentación |
| `../../skills/` | Alineadas con la 2.1 | Vigentes |
| `Historias_de_Usuario.pdf`, `Requerimientos_y_Diagramas.pdf`, `REVISION_V2_1.pdf`, `ARQ-03_Modelo_C4.pdf` | Generados el 23/10/2026 | Entregables |

**Contenido de la especificación:** 9 módulos · 10 requerimientos funcionales · 27 historias de
usuario con 277 criterios de aceptación · 71 requerimientos de usuario · 170 requerimientos de
sistema · 74 funciones expuestas · 87 requerimientos no funcionales · 143 reglas de negocio ·
50 casos de uso · 76 diagramas de módulo.

La línea base corresponde al estado de la rama `docs/version-2` al cierre. La etiqueta que la
identifique en el repositorio la crea el responsable del repositorio al fusionarla.

## 3. Verificación de cierre

| Comprobación | Resultado |
|---|---|
| `scripts/verificar_migracion.sh`: conceptos del alcance anterior | Sin hallazgos |
| `scripts/validar_docs.py`: Mermaid, enlaces, referencias cruzadas e historias coherentes entre módulos, índice y matriz | Sin hallazgos |
| Revisión de coherencia completa (skill `revision-coherencia`) | Sin códigos huérfanos; 27 de 27 historias con funciones, diagramas, matriz e índice; toda operación restringida con su criterio de rechazo |
| Render de los diagramas Mermaid del repositorio | 88 de 88 |
| Contraste de la maqueta con la documentación | Toda pantalla y acción de la maqueta tiene especificación; los mensajes coinciden, salvo los que solo produce el servidor |
| Contraste de las skills y guías con la documentación | Alineadas; las contradicciones encontradas se resolvieron (sección 4) |

## 4. Estado de las decisiones al cierre

### 4.1 Cerradas en el cierre de la fase

| Decisión | Contenido | Origen |
|---|---|---|
| DR-29 | Retiro de un ingreso del lote hasta el zarandeo o la molienda | Revalidación de la maqueta |
| DR-30 | Inicio con avisos, exportación del listado, gestión de cuentas y bajas, búsqueda desde la cabecera | Revalidación de la maqueta |
| DR-31 | El Supervisor de planta consulta el reconocimiento y la validación | Revalidación de la maqueta |
| D-18 | El almacén de imágenes se usa por la API de almacenamiento de Django | Cierre del modelo C4 |
| D-19 | El listado de ingresos pertenece solo a M07 | Cierre del modelo C4 |
| D-20 | Respaldo mínimo ejecutable desde la semana 1; servicio y política definitivos con el alojamiento de la presentación | Cierre de la fase |
| D-21 | Códigos de ruta `ZARANDEO_ENSACADO`, `MOLIENDA_ENSACADO` y `ZARANDEO_MOLIENDA_ENSACADO` | Cierre de la fase |
| D-22 | Ninguna operación de la API usa `DELETE` | Cierre de la fase |

Durante el cierre se resolvió además, por la fuente de mayor orden, que un cambio de rol se aplica
en la siguiente acción del usuario (HU-M01-03 CA03) y no en su siguiente sesión, como decía la skill
de permisos.

### 4.2 Con solución provisional

Permiten programar sin esperar; se cierran en el momento indicado y su cierre no cambia el código de
negocio.

| Decisión | Solución provisional | Se cierra |
|---|---|---|
| D-12 Motor de reconocimiento | Adaptador local dentro del mismo backend; adaptador determinista en las pruebas | Con el piloto de la semana 7, sobre el sistema funcional, antes del congelamiento de la semana 8 |
| D-14 Almacenamiento de imágenes | Volumen `media` del backend, por la API de almacenamiento de Django (D-18) | Con el servicio de alojamiento de la presentación |

### 4.3 Pendientes, con su momento

| Pendiente | Responsable | Momento |
|---|---|---|
| Validar los roles y su matriz de permisos con los usuarios (DR-23) | Empresa | Inicio de la semana 1 |
| Valores del catálogo de tipos de mineral (DR-03) y taras de los vehículos que ya operan | Empresa | Semana 2 |
| D-15, procesamiento síncrono del reconocimiento | Responsable técnico | Se confirma con el piloto de D-12 |
| Servicio de alojamiento de la presentación y política de respaldo (D-20) | Autor | Antes de la operación real |
| Rama de integración del código (`develop` o `staging`) | Responsable del repositorio | Antes del primer PR de código |
| Contratos de dependencia entre módulos en el CI y tratamiento de datos personales | Autor | Durante la implementación |

Ninguno impide empezar: cada uno está programado antes de la semana que lo necesita.

## 5. Control de cambios desde esta fecha

1. **Todo cambio a la línea base se registra antes de programarlo.** Como decisión de reformulación
   (DR) si cambia el alcance, una historia o una regla del dominio; como decisión de diseño (D) si
   cambia la forma de construirlo. Ningún cambio entra por conversación informal.
2. **La documentación manda sobre la maqueta y sobre el código.** Si al programar el código necesita
   apartarse de la documentación, primero se cambia la documentación por la vía del punto 1.
3. **Una decisión tomada durante la implementación** que no estaba documentada se registra en el PR
   que la introduce, como exige `PLAN_DE_TRABAJO.md` §4.3, y en `decisiones_diseno.md` antes de
   fusionarlo.
4. **Cada cambio revisa lo que depende de él**: los módulos afectados, la matriz, el índice, el
   modelo de datos, la arquitectura, el plan, las skills y la maqueta, en ese orden.
5. **Cada cambio pasa los validadores** —`verificar_migracion.sh` y `validar_docs.py`—, regenera el
   índice y los PDF afectados, y respeta la convención de commits de documentación.
6. **Durante la ventana de medición** no cambian el motor de reconocimiento, su versión ni las reglas
   V1 a V5 (D-16); toda excepción se documenta con fecha y se reporta.

## 6. Criterios de entrada a la implementación

| Momento | Lo que debe estar listo | Estado al cierre |
|---|---|---|
| Antes de la semana 1 | Preparación del backend heredado (`PLAN_DE_TRABAJO.md` §8): `Producto` por `TipoMineral`, refactor de `apps/ingresos` al modelo 3.1, retiro de `existencias`, esqueletos de `reconocimiento`, `validacion` y `trazabilidad`, renombre de `busqueda` y `reportes`, `LOCAL_APPS` con la numeración vigente y volumen `media` | Pendiente; es la primera tarea de programación |
| Antes de la semana 1 | Documentación fusionada en la rama principal | A cargo del responsable del repositorio |
| Semana 1 | Roles validados con la empresa; repositorio del frontend creado; respaldo ejecutable | Programado |
| Semana 2 | Catálogo de tipos de mineral y taras acordados con la empresa | Programado |
| Semana 3 | Adaptador local del reconocimiento y almacenamiento provisional de imágenes | Decidido (D-12 y D-14 provisionales) |
| Semana 5 | Códigos de ruta | Decidido (D-21) |
| Semana 7 | Piloto de D-12 y elección del motor | Programado |

Cada historia entra en desarrollo solo si cumple la definición de listo de `PLAN_DE_TRABAJO.md`
§4.1. Con esta acta, todas las historias de la línea base la cumplen en lo que depende de la
documentación.

## 7. Conformidad

| Rol | Nombre | Firma | Fecha |
|---|---|---|---|
| Autor y responsable técnico | | | |
| Asesor | | | |
