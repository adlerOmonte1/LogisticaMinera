# Convenciones de códigos y nomenclatura

**Documento:** transversal
**Aplica a:** documentación, código fuente, historias de usuario y documentación de arquitectura

---

## 1. Códigos de documentación

```
Módulo                     M01 … M09
Requerimiento funcional    RF-01 … RF-12          (globales, definidos en ARQ-01)
Requerimiento no funcional RNF-Mxx-nn             (por módulo)
Regla de negocio           RN-Mxx-nn              (por módulo)
Requerimiento de usuario   RU-Mxx-nn              (por módulo)
Requerimiento de sistema   RS-Mxx-nn              (por módulo)
Historia de usuario        HU-Mxx-nn              (por módulo)
Criterio de aceptación     CAnn                   (dentro de una historia)
Caso de prueba             CP-RF-xx-nn
Indicador operativo        I1 … I6                (resultados operativos)
```

Los RF son globales porque muchos cruzan más de un módulo y porque son los que aparecen en la documentación de requisitos. Los RNF, RN, RU y RS se numeran por módulo porque su alcance es local.

## 2. Por qué los cinco tipos de requisito están separados

No es formalismo académico: cada tipo aterriza en una capa distinta del código (ver `ARQ-02_Arquitectura_Tecnica.md` §5). Mezclarlos en un solo archivo de "requisitos" produce clases con más de una responsabilidad.

| Tipo | Pregunta que responde | Ejemplo del proyecto |
|---|---|---|
| RU | ¿Qué pide el usuario, en sus palabras? | "Quiero registrar el volquete apenas baje de la balanza, sin esperar a llegar a la oficina" |
| RS | ¿Qué debe hacer el sistema, técnicamente? | El sistema persiste el ingreso con marca temporal del servidor y asigna correlativo |
| RF | ¿Qué función expone? | RF-01: registrar el ingreso de volquete |
| RNF | ¿Con qué calidad? | El alta de un ingreso responde en menos de 2 s con 20 usuarios concurrentes |
| RN | ¿Qué es siempre cierto en el dominio? | RN-M03-02: la hora de pesaje nunca puede ser posterior a la hora de registro |

## 3. Nomenclatura en el código

**Backend (Django, snake_case):**
```
apps/ingresos/models/ingreso.py            class Ingreso, class TicketBalanza
apps/ingresos/repositories/ingreso.py      class RepositorioIngreso
apps/ingresos/services/registrar_ingreso.py  def registrar_ingreso(...)
apps/ingresos/views/ingreso.py             class IngresoViewSet
```

**Frontend (Angular, kebab-case en archivos, PascalCase en clases):**
```
features/ingresos/ingreso-form.component.ts       class IngresoFormComponent
features/ingresos/ingresos.service.ts             class IngresosService
models/ingreso.model.ts                           interface Ingreso
```

El idioma del código es el español para las entidades del dominio (`Ingreso`, `Volquete`, `Producto`), porque son términos del negocio con significado preciso en la empresa y traducirlos introduce ambigüedad. Las palabras del framework permanecen en inglés.

## 4. Convención de ramas y commits

```
main                      Código desplegable
develop                   Integración
feature/M03-ingresos      Una rama por módulo
```

Formato de commit: `M03: registra hora de pesaje separada de hora de registro (HU-M03-01)`. Referenciar siempre la historia de usuario permite reconstruir la trazabilidad desde el historial de git, evidencia útil en la revisión técnica.

## 5. Trazabilidad bidireccional

Toda historia se nombra con el módulo al que pertenece. En consecuencia, desde cualquier punto se puede navegar en ambos sentidos:

```
Indicador operativo  ->  RF  ->  Módulo  ->  HU  ->  Caso de prueba  ->  Commit
```

Esta cadena es lo que permite responder en la revisión técnica a la pregunta "¿cómo demuestra que el sistema mejoró el indicador?" sin improvisar.
