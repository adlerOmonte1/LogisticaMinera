# Convenciones de códigos y nomenclatura

**Documento:** transversal
**Aplica a:** documentación, código fuente, historias de usuario y documentación de arquitectura

---

## 1. Códigos de documentación

```
Módulo                       M01 … M09
Requerimiento funcional      RF01 … RF10              (globales, definidos en ARQ-01)
Requerimiento no funcional   RNF-Mxx-nn               (por módulo)
Regla de negocio             RN-Mxx-nn                (por módulo)
Regla de validación del      V1 … V5                  (globales, aplicadas por M05)
  ticket
Requerimiento de usuario     RU-Mxx-nn                (por módulo)
Requerimiento de sistema     RS-Mxx-nn                (por módulo)
Historia de usuario          HU-Mxx-nn                (por módulo)
Criterio de aceptación       CAnn                     (dentro de una historia)
Caso de prueba (por RF)      CPnn                     (lista de control, uno por RF)
Caso de prueba (por criterio) CP-HU-Mxx-nn-nn
Decisión de diseño           D-nn
```

Los RF son globales porque muchos cruzan más de un módulo y porque son los que aparecen en la lista
de control validada por expertos. Los RNF, RN, RU y RS se numeran por módulo porque su alcance es
local. Formato de RF: `RF01`, **sin guion**.

Los indicadores de la tesis (I1 a I6, ERA, TDI, SUS, TCA, RFC, CPS) no forman parte de esta
nomenclatura de código: no se citan en `docs/modulos/`, solo en
`docs/02-trazabilidad/matriz_HU_RF_indicador.md` (ver el principio rector en `skills/contexto-tesis`).

## 2. Por qué los cinco tipos de requisito están separados

No es formalismo académico: cada tipo aterriza en una capa distinta del código (ver
`ARQ-02_Arquitectura_Tecnica.md` §5). Mezclarlos en un solo archivo de "requisitos" produce clases
con más de una responsabilidad.

| Tipo | Pregunta que responde | Ejemplo del proyecto |
|---|---|---|
| RU | ¿Qué pide el usuario, en sus palabras? | "Quiero sacarle una foto al ticket apenas el volquete baje de la balanza, ahí mismo en la planta" |
| RS | ¿Qué debe hacer el sistema, técnicamente? | El sistema asigna `hora_inicio_registro` al recibir la imagen y `hora_fin_registro` al persistir el ingreso |
| RF | ¿Qué función expone? | RF01: registrar el ingreso de mineral con la imagen del ticket de balanza |
| RNF | ¿Con qué calidad? | El reconocimiento de un ticket devuelve resultado en menos de 5 segundos |
| RN | ¿Qué es siempre cierto en el dominio? | RN-M03-06: `hora_inicio_registro` y `hora_fin_registro` las asigna el servidor y ningún rol las modifica |

## 3. Nomenclatura en el código

**Backend (Django, snake_case):**
```
apps/ingresos/models/ingreso.py              class Ingreso
apps/ingresos/repositories/ingreso.py        class RepositorioIngreso
apps/ingresos/services/registrar_ingreso.py  def registrar_ingreso(...)
apps/ingresos/views/ingreso.py               class IngresoViewSet
apps/reconocimiento/motores/paddle_ocr.py    class ReconocedorPaddleOCR
```

**Frontend (Angular, kebab-case en archivos, PascalCase en clases):**
```
features/ingresos/ingreso-form.component.ts       class IngresoFormComponent
features/ingresos/ingresos.service.ts             class IngresosService
models/ingreso.model.ts                           interface Ingreso
```

El idioma del código es el español para las entidades del dominio (`Ingreso`, `LoteProceso`,
`TipoMineral`), porque son términos del negocio con significado preciso en la empresa y traducirlos
introduce ambigüedad. Las palabras del framework permanecen en inglés.

## 4. Convención de ramas y commits

```
main                      Código desplegable
develop                   Integración
feature/M03-ingresos      Una rama por módulo
```

Formato de commit: `M04: reconoce los seis campos del ticket con su confianza (HU-M04-01)`.
Referenciar siempre la historia de usuario permite reconstruir la trazabilidad desde el historial de
git, evidencia útil en la revisión técnica.

## 5. Trazabilidad bidireccional

Toda historia se nombra con el módulo al que pertenece. En consecuencia, desde cualquier punto se
puede navegar en ambos sentidos:

```
Indicador de la tesis  ->  RF  ->  Módulo  ->  HU  ->  Caso de prueba  ->  Commit
```

Esa cadena vive en `docs/02-trazabilidad/matriz_HU_RF_indicador.md`, que es el único documento donde
el lado izquierdo (el indicador) se conecta con el resto. El código y los documentos de módulo
conocen la cadena desde `RF` hacia la derecha; la relación con el indicador se consulta, no se
declara en cada archivo.
