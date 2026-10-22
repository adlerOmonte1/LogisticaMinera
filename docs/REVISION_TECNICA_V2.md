# Revisión técnica de la versión 2 — arquitectura, estructura y puntos abiertos

| Campo | Valor |
|---|---|
| Fecha | 21/10/2026 |
| Alcance | Todo `docs/`, `skills/`, `scripts/`, `Mockup/` y el estado de `backend/` |
| Propósito | Preparar la revisión del asesor técnico: qué arquitectura sigue el sistema, si la estructura de carpetas es correcta y qué queda sin resolver |
| Índice de archivos | [`INDICE.md`](INDICE.md), generado por `scripts/indexar_docs.py` |

---

## 1. Estado de la validación

| Comprobación | Resultado | Cómo se verifica |
|---|---|---|
| Conceptos del alcance anterior en `docs/` y `skills/` | Sin hallazgos | `scripts/verificar_migracion.sh` |
| Reglas de Mermaid, enlaces, referencias cruzadas (HU, RU, RS, RNF, RN, S, A, D, DR) | Sin hallazgos | `scripts/validar_docs.py` (PR #14) |
| Historias iguales en cada `HU.md`, el índice y la matriz | 26 historias coherentes | `scripts/validar_docs.py` |
| Backend: lint, migraciones y pruebas sobre PostgreSQL 16 | 184 pruebas aprobadas | CI de GitHub Actions (PR #14) |
| PDF de historias (57 páginas) y de requerimientos y diagramas (168 páginas) | Generados con la versión 2 | `scripts/generar_pdf_hu.py`, `scripts/generar_pdf_requerimientos.py` |
| PDF de este documento | Generado por script | `scripts/md_a_pdf.py` |

La validación automática garantiza **coherencia interna**, no que el sistema descrito sea el
correcto. Eso es lo que revisa la sección 5.

---

## 2. Arquitectura del sistema: qué es y con qué nombre se defiende

### 2.1 Clasificación

El sistema **no** tiene una arquitectura de criterio propio. Combina estilos y patrones con nombre,
cada uno en un nivel distinto:

| Nivel | Estilo o patrón | Referencia | Dónde se aplica |
|---|---|---|---|
| Sistema | **Monolito modular** (*modular monolith*) | Richardson, *Microservices Patterns* (2018), cap. 2; Newman, *Monolith to Microservices* (2019) | Un solo despliegue Django; un módulo por responsabilidad del dominio (M01 a M09), cada uno una app |
| Límites de cada módulo | **Contexto delimitado** (*bounded context*), en versión ligera | Evans, *Domain-Driven Design* (2003) | Cada app es dueña de sus entidades; las demás la usan por su servicio, no por sus tablas |
| Dentro de cada módulo | **Arquitectura en capas** con **Service Layer** y **Repository** | Fowler, *Patterns of Enterprise Application Architecture* (2002) | `views → services → models`, y `repositories/` para la lectura (D-09) |
| Motor de reconocimiento y reglas | **Puertos y adaptadores** (*hexagonal*) y **Strategy** | Cockburn (2005); Gamma et al. (1994) | `ReconocedorTicket` (M04, D-12) y `ValidadorConsistencia` con una clase por regla (M05) |
| Consulta y consolidación | **Separación de lectura y escritura** (CQRS ligero, sin bases separadas) | Young (2010); Fowler, *CQRS* (2011) | M07 y M08 son apps de solo lectura, sin modelos (D-10) |
| Código compartido | **Núcleo compartido** (*shared kernel*) | Evans (2003) | `common/`: excepciones de dominio, catálogo de acciones de auditoría, utilidades de red |
| Cliente | **SPA** con *feature modules* | Guía oficial de Angular | Repositorio separado (D-11), una *feature* por módulo |
| Documentación | **Modelo C4** y **registros de decisión** (ADR) | Brown, *The C4 Model*; Nygard (2011) | ARQ-03; `decisiones_diseno.md` (D-nn) y `decisiones_reformulacion.md` (DR-nn) funcionan como ADR |

**Nombre para la defensa:** *monolito modular en capas, con puertos y adaptadores para el
reconocimiento y la validación, documentado con el modelo C4 y registros de decisión.*

### 2.2 Por qué este estilo y no otro

| Alternativa | Por qué se descarta |
|---|---|
| Microservicios | Un equipo de una persona, un solo despliegue en planta y transacciones que cruzan módulos (registrar ingreso + reconocimiento + validación + auditoría en un solo acto, D-02). Distribuirlos exigiría transacciones distribuidas sin beneficio medible |
| Capas globales (`models/`, `services/` en la raíz) | Baja cohesión: un cambio en el lote tocaría carpetas compartidas con el catálogo. El código no reflejaría las responsabilidades del dominio |
| Hexagonal completa en todos los módulos | Ceremonia sin segunda implementación: un catálogo CRUD no gana nada con puertos. Se aplica solo donde hay sustitución real (motor y reglas) |
| Monolito sin módulos | Imposible de trazar contra RF y HU, y de escalar a otra planta o a más usuarios |

### 2.3 Correspondencia con SOLID

| Principio | Cómo se cumple | Dónde se verifica |
|---|---|---|
| S — Responsabilidad única | Una app por responsabilidad; dentro, una capa por razón de cambio | ARQ-02 §5, `skills/solid-proyecto` |
| O — Abierto/cerrado | Reglas V1 a V5 como clases registradas; exportadores de M08 como clases nuevas | M05 y M08 `notas.md` |
| L — Sustitución de Liskov | Cualquier motor que implemente `ReconocedorTicket` sustituye a otro | ARQ-03 §5 |
| I — Segregación de interfaces | Permisos por acción, no por rol monolítico (RN-M01-09) | M01 `notas.md` |
| D — Inversión de dependencias | `ServicioIngreso` recibe reconocedor, validador, generador de código y reloj | ARQ-03 nivel 4 |

### 2.4 Qué la hace escalable a nivel organizacional

1. **Contratos entre módulos.** Un módulo solo usa a otro por su servicio o su repositorio, nunca por
   sus modelos internos. **Hoy es una convención, no una regla verificada.** Propuesta: añadir
   `import-linter` al CI con un contrato por módulo.
2. **Extracción posible.** Si otra planta o la mina se incorporan, un módulo con contrato claro puede
   separarse sin reescribir los demás. Es la ventaja del monolito modular sobre el monolito simple.
3. **Configuración por entorno** (`config/settings/`), **una base PostgreSQL** y **despliegue con
   Docker** (`skills/despliegue-docker`): mismo artefacto en preproducción y producción.
4. **Trazabilidad verificable**: RF → HU → regla → prueba, comprobada en el CI.

---

## 3. Estructura de carpetas: evaluación

### 3.1 ¿Cada módulo necesita su propia carpeta y su propia app?

Sí en la documentación: cada módulo tiene historias, requerimientos y diagramas propios. En el
backend, la regla es: **un módulo es una app si tiene una responsabilidad y un contrato propios,
aunque no tenga tablas.** Tener modelos no es el criterio.

| Módulo | Entidades propias | ¿App propia? | Justificación |
|---|---|---|---|
| M01 Autenticación | `USUARIO`, `ROL` | Sí | Dueño de la identidad y de la matriz de permisos que usan todos |
| M02 Catálogo | `VEHICULO`, `TIPO_MINERAL`, `TRANSPORTISTA` | Sí | Dueño de los datos de referencia |
| M03 Registro | `INGRESO` | Sí | Núcleo; orquesta M04 y M05 |
| M04 Reconocimiento | `RECONOCIMIENTO_TICKET`, `CAMPO_RECONOCIDO` | Sí | Tiene datos propios y un adaptador sustituible |
| M05 Validación | `RESULTADO_VALIDACION` | Sí | Tiene datos propios y reglas extensibles |
| M06 Trazabilidad | `LOTE_PROCESO`, `PARTE_LOTE`, `REPARTO_INGRESO`, `PASO_ETAPA`, `BIGBAG` | Sí | El módulo con más lógica después de M03 |
| M07 Consulta | Ninguna | **Sí, como módulo de lectura** | Tiene endpoints, permisos, filtros y el calendario. Sin app, esa lógica caería en M03 y lo engordaría |
| M08 Consolidación | Ninguna | **Sí, como módulo de lectura** | Tiene el cálculo agregado y los exportadores; su razón de cambio (formatos de reporte) no es la de M03 |
| M09 Auditoría | `EVENTO_AUDITORIA` | Sí | Transversal: el registrador vive en `common/eventos.py` y la consulta en la app |

**Conclusión:** la estructura M01 a M09 es correcta. M07 y M08 sin modelos no son un error: son la
parte de lectura del CQRS ligero (D-10). Lo que conviene es **explicitarlo** en ARQ-02 con el nombre
del patrón, para que el asesor no lo lea como una carpeta vacía.

### 3.2 Backend: estado actual frente al objetivo

| Hoy | Objetivo | Acción |
|---|---|---|
| `apps/salidas`, `apps/existencias`, `apps/sincronizacion` | No existen | Retirar (PLAN §8). Pendiente de tu autorización |
| `apps/busqueda`, `apps/reportes` | `apps/consulta`, `apps/consolidacion` | Renombrar para que el código coincida con el módulo |
| `apps/accounts` | Se mantiene | Es la convención de Django; el resto en español |
| `Producto`, `numero_ticket`, `hora_registro`, `hora_sincronizacion` y el descuento de stock en `apps/ingresos` | Modelo 3.0 | Refactor de M03 | <!-- migracion:ok -->
| Faltan `apps/reconocimiento`, `apps/validacion`, `apps/trazabilidad` | Existen con la estructura de capas | Crear esqueletos |

### 3.3 Documentación: observaciones menores

| Observación | Propuesta |
|---|---|
| `00-tesis/` y `00-arquitectura/` comparten el prefijo; `model-c4/` no tiene número | Opcional: `00-tesis`, `01-arquitectura` (con `model-c4` dentro), `02-plan`, `03-trazabilidad`, `04-pruebas`. Cambia muchos enlaces; `validar_docs.py` los comprobaría |
| `GUIA_MARCO_DE_TRABAJO.md` (911 líneas) repite gran parte de las skills `backend-django` y `solid-proyecto` | Fusionarla en las skills o reducirla a un índice: dos fuentes para lo mismo terminan divergiendo |
| `CLAUDE.md` dice «DR-01 a DR-10» y lista solo `verificar_migracion.sh` en `scripts/` | Actualizar a DR-23 y a los scripts actuales |
| El PDF de requerimientos dice «Versión 1.0» en el encabezado | El texto está fijo en el generador; parametrizarlo |

---

## 4. Salidas: cómo cerrar el lote sin entrar en ventas

Hoy el cierre ya existe: **HU-M06-05** cierra el lote con su destino, **venta** o **traslado**, sin
guía, factura ni precio (DR-14). Lo que falta decidir es si basta un registro o hace falta un módulo.

| Opción | Qué incluye | Cuándo conviene | Riesgo para el alcance |
|---|---|---|---|
| **A. Cierre en M06 (actual)** | Un acto: fecha, destino, resumen del proceso, responsable | El lote sale de una sola vez | Ninguno |
| **B. Despacho del lote dentro de M06** | A + uno o varios despachos: fecha, bigbags, peso aproximado, transporte, observación | El lote sale en varios viajes | Bajo: son datos descriptivos, como los bigbags (DR-15) |
| C. Módulo M10 de salidas | Entidad propia, guía de remisión, cliente, comprobante | Se necesita el documento de salida | **Alto**: reabre facturación, guías y clientes, retirados en la reformulación |

**Recomendación:** A, y B solo si en planta un lote sale en varios viajes. C queda fuera: es justo lo
que la reformulación retiró. La decisión debe registrarse como una **nueva decisión de reformulación**, la siguiente a DR-23.

**Incongruencia con la maqueta:** la maqueta usa «cerrar» para lo que la documentación llama «inicio
del recorrido», y «dar de alta» para el cierre con destino; además solo ofrece venta y divide en
toneladas. La documentación es la que manda; la maqueta debe ajustarse antes de mostrarla a usuarios.

---

## 5. Puntos de quiebre, incongruencias y dudas abiertas

Severidad: **B** bloquea implementar o medir · **A** alta · **M** media · **b** baja.

### 5.1 Del sistema

| ID | Sev. | Punto | Qué pasa si no se resuelve | Quién decide |
|---|---|---|---|---|
| Q-01 | B | El backend sigue en el diseño anterior: `numero_ticket`, `Producto`, `hora_registro`, `hora_sincronizacion`, descuento de stock y las apps retiradas | Implementar M03 sobre él contradice las historias aprobadas | Tú: autorizar la preparación (PLAN §8) | <!-- migracion:ok -->
| Q-02 | A | Pruebas del backend citan 10 criterios de historias retiradas en la reformulación (la cuarta de M02 y de la quinta a la séptima de M03), y las 51 de `salidas` usan la numeración antigua | Una trazabilidad que aparenta cobertura que no hay | Se resuelve con Q-01 |
| Q-03 | B | Valores del catálogo de tipos de mineral (DR-03) | No se puede abrir un lote ni consolidar | Empresa |
| Q-04 | B | Motor de reconocimiento sin piloto (D-12) | M04 no puede implementarse ni medirse | Tú, con 20 a 30 tickets reales |
| Q-05 | A | Medio, retención y respaldo de las imágenes (D-14) | El respaldo del ingreso no tiene dónde vivir | Tú, con el despliegue |
| Q-06 | A | **No existe ningún requisito de respaldo de la base de datos** | Una falla del servidor borra el histórico, que es justo lo que D-07 protege | Proponer un RNF transversal |
| Q-07 | A | Quién registra el destare en planta y cómo se avisa de un vehículo pendiente (DR-10) | Ingresos En proceso que nadie completa | Gerencia |
| Q-08 | A | **Ingresos En proceso sin plazo**: si el vehículo no vuelve, el ingreso queda así para siempre | El total del mes nunca es definitivo | Proponer un aviso o un plazo |
| Q-09 | A | **Registro sin foto sin límite de uso** (DR-13) | Si se vuelve la norma, el reconocimiento deja de usarse sin que nadie lo note | Proponer un reporte de su frecuencia |
| Q-10 | A | Forma real de agrupar el mineral en cancha y de decidir la ruta (DR-04, DR-16) | M06 podría modelar algo que la planta no hace | Jefatura de operaciones |
| Q-11 | M | El lote admite un solo tipo de mineral | Si en cancha se mezclan tipos, la regla no se puede cumplir | Jefatura de operaciones |
| Q-12 | M | Validar los tres roles y su matriz con los usuarios (DR-23) | Rehacer M01 | Usuarios |
| Q-13 | M | Un ingreso corregido después de exportar el total del mes cambia ese total (RN-M08-02) | Un archivo ya entregado a gerencia deja de coincidir con el sistema | Decidir si hace falta un cierre mensual |
| Q-14 | M | Salidas: opción A o B (sección 4) | Rediseño tardío de M06 | Tú, como nueva decisión de reformulación |
| Q-15 | M | La maqueta no coincide con la documentación en el ciclo del lote, el destino y la división | Usuarios validan una interfaz distinta de la documentada | Ajustar la maqueta |
| Q-16 | b | Códigos de ruta `ZARANDEO`, `MOLIENDA`, `AMBAS` propuestos, no decididos | Ninguno grave | Tú |

### 5.2 De la medición (tesis)

| ID | Sev. | Punto | Riesgo | Acción |
|---|---|---|---|---|
| Q-17 | B | Anexos 02, 03 y 04 del documento de tesis desactualizados (DR-06, DR-09, DR-16, DR-21) | El juicio de expertos validaría instrumentos que el sistema contradice | Actualizarlos antes del juicio |
| Q-18 | A | P-03: cómo trata la ficha de observación un ingreso sin foto en I3 e I4 | Casos sin criterio de medición | Decidir y registrar |
| Q-19 | A | **La hora del pesaje propuesta puede sesgar I1**: si el usuario acepta la hora actual sin ajustarla, el tiempo de espera medido es casi cero | Un resultado favorable que no refleja la realidad | La ficha registra la hora real del pesaje por observación directa y la contrasta con la del sistema |
| Q-20 | A | El denominador de I6 depende de la ruta, que decide la planta | Si la ruta se decide después de ver qué etapas se registraron, I6 se infla | Registrar la ruta antes de las etapas siguientes al secado (ya lo exige M06) y verificarlo en la ficha |
| Q-21 | M | Congelamiento de motor y reglas durante la medición (D-16) sin control automático | Un cambio no registrado invalida la comparación | Etapa 7 del CI |

### 5.3 Del proceso y del repositorio

| ID | Sev. | Punto | Acción |
|---|---|---|---|
| Q-22 | M | Rama de integración: el plan dice `develop`, en GitHub existe `staging`; `main` ya incluye una versión intermedia de la documentación (PR #12) | Elegir una y documentarla |
| Q-23 | M | El repositorio del frontend no existe todavía | Crearlo antes de la semana 1 |
| Q-24 | M | Servidor de preproducción y producción sin definir | Bloquea las etapas 5 y 6 del CI |
| Q-25 | b | Las reglas de dependencia entre módulos no se verifican | `import-linter` en el CI |
| Q-26 | b | Datos personales (usuarios, transportistas, placas) sin política de tratamiento | Preguntar al asesor si la tesis la exige |

---

## 6. Orden sugerido

1. **Antes del juicio de expertos:** Q-17, Q-18, Q-19.
2. **Con la empresa:** Q-03, Q-07, Q-10, Q-11, Q-12, Q-14.
3. **Decisiones técnicas tuyas:** Q-01 (autorizar), Q-04, Q-05, Q-06, Q-22.
4. **Propuestas que puedo redactar si las apruebas:** RNF de respaldo (Q-06), plazo o aviso de En
   proceso (Q-08), reporte de registros sin foto (Q-09), la decisión de salidas (Q-14), contratos con
   `import-linter` (Q-25).

---

## 7. Resoluciones del 22/10/2026

| Punto | Resolución | Dónde queda |
|---|---|---|
| Q-01, Q-02 | Retiradas `apps/salidas`, `apps/sincronizacion` y `Cliente` (migración `0002_retira_cliente`). El resto del backend se modifica al cerrar la documentación | PLAN §8 |
| Q-07, Q-08 | Cualquiera de los tres roles registra el destare; es obligatorio y sin plazo: puede hacerse días después, y el ingreso sigue En proceso mientras tanto | DR-25, HU-M03-04 |
| Q-09 | Sin límite para el registro sin foto: a la empresa le conviene el respaldo de que el ingreso existió | DR-26 |
| Q-10 | La agrupación del mineral se hace en el sistema, con los lotes y según los roles (DR-23) | M06 |
| Q-11 | El lote admite varios tipos de mineral, agregados con «Agregar otro mineral» y presentados por grupo | DR-27, HU-M06-01 |
| Q-13 | La corrección se propaga en cadena y la última corrección puede revertirse | DR-28, HU-M03-02 |
| Q-14 | La salida es, por ahora, el cierre del lote con destino (opción A) | DR-24 |
| Q-15 | Maqueta actualizada al proceso documentado de ingresos, lotes y salida | `Mockup/index.html` |

Siguen abiertos: Q-03 a Q-06, Q-12, Q-16 a Q-26.
