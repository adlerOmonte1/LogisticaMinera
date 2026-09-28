---
name: solid-proyecto
description: Aplica y verifica los principios SOLID en el código del sistema web inteligente de ingreso de mineral, según la correspondencia requisito-capa fijada en ARQ-02 §5. Úsala al escribir o revisar cualquier modelo, servicio, repositorio, vista, serializer, permiso, exportador, adaptador de motor o servicio Angular, cuando se pida refactorizar, cuando se mencione SOLID, responsabilidad única, inversión de dependencias, acoplamiento o "dónde va esta lógica", y antes de dar por cerrado un módulo del backend.
---

# SOLID en este proyecto

Carga antes `contexto-tesis`. La fuente es `docs/model-c4/ARQ-02_Arquitectura_Tecnica.md` §5.

Aquí SOLID no es una preferencia de estilo: un servicio que mezcla responsabilidades es más difícil
de probar, de sustituir y de defender frente a la pregunta «¿por qué está organizado así».

## La correspondencia que decide dónde va cada cosa

Los cinco tipos de requisito no están separados por formalismo académico: **cada tipo aterriza en una
capa distinta**. Si sabes qué tipo de requisito estás implementando, ya sabes en qué archivo va.

| Tipo de requisito | Capa Django | Capa Angular | Principio |
|---|---|---|---|
| Regla de negocio (RN) | `models/`, validadores de dominio | — nunca como fuente de verdad | SRP |
| Requisito de sistema (RS) | `services/` | servicio del feature | SRP, DIP |
| Requisito funcional (RF) | `views/` + `serializers/` | componentes y rutas | ISP |
| Requisito no funcional (RNF) | configuración, índices, timeouts | estrategias de captura y compresión de imagen | OCP |

**La prueba para ubicar cualquier lógica:** si la validación puede enunciarse sin mencionar HTTP,
**no** pertenece a `views/`. «El peso neto no coincide con el peso bruto menos la tara» (V1) no
menciona HTTP: va a una regla de M05. «Devolver 403 si el rol no es Administrador» sí lo menciona:
va a `permissions.py`.

---

## S — Responsabilidad única

Una capa, un motivo de cambio.

| Archivo | Única responsabilidad | Lo que NO hace |
|---|---|---|
| `models/` | Proteger las invariantes de la entidad (RN-*) | Llamar a otros servicios, saber de HTTP |
| `services/` | Orquestar un caso de uso (RS-*) | Contener reglas de negocio; solo las invoca |
| `repositories/` | Consultas de lectura | Escribir |
| `serializers/` | Traducir dominio ↔ JSON | Validar reglas de negocio |
| `views/` | Entrada/salida HTTP (RF-*) | Todo lo demás |
| `permissions.py` | Autorización por acción | Lógica de negocio |

Ejemplo canónico del proyecto: «el peso neto no coincide con el peso bruto menos la tara» (V1) vive
en una regla de M05, invocada desde el servicio de M03. **No** en el formulario Angular, **no** en el
`IngresoViewSet`. Una petición que llegue directo a la API, sin pasar por el formulario, debe
someterse a la misma regla — esa es la razón concreta, no una abstracción (D-08).

**Olor a violación:** un `services/` con un `if` que compara pesos directamente en vez de invocar
`ValidadorConsistencia`; un `views/` con más de tres líneas que no sean traducción de HTTP; un
serializer con `validate_*` que implementa una RN en lugar de delegarla.

## O — Abierto/cerrado

Extender sin modificar lo que ya funciona.

El caso vivo es M05: las reglas V1 a V5 comparten una abstracción.

```python
class Regla(Protocol):
    codigo: str
    def cumple(self, datos: DatosTicket) -> bool: ...

class ReglaV1PesoNeto:
    codigo = "V1"
    def cumple(self, datos): ...

class ReglaV4Capacidad:
    codigo = "V4"
    def cumple(self, datos): ...
```

Añadir una regla nueva —por ejemplo, una placa que no está en el catálogo— debe ser **una clase
nueva registrada en la colección**, no un `elif` en una función existente ni una modificación de V1
a V5. El mismo criterio aplica a los exportadores de M08 (`ExportadorExcel` hoy, otros formatos
después) y a los adaptadores del motor de reconocimiento de M04.

## L — Sustitución de Liskov

Toda implementación de una abstracción debe poder sustituir a otra sin romper a quien la consume.
Cualquier `ExportadorConsolidado` va donde se espera esa interfaz, sin que el llamador pregunte de
qué tipo es. Lo mismo para cualquier implementación de `ReconocedorTicket`: el servicio de registro
de M03 no cambia según qué motor esté detrás.

**Violación típica y concreta:** un adaptador de motor que lanza una excepción distinta a las demás
implementaciones cuando la imagen es ilegible, en vez de devolver el mismo `ResultadoReconocimiento`
con `exito=False` que devuelven las demás. Si una implementación no honra el contrato completo, el
contrato está mal definido — corrígelo, no lo rodees con un `try/except` especial en el llamador.

Otra: una regla de validación que devuelve `None` cuando falta un dato, mientras otra devuelve
`False`. RN-M05-07 exige explícitamente que una regla sin datos suficientes **se omita**, no que
falle de dos maneras distintas según la regla.

## I — Segregación de interfaces

Nadie depende de métodos que no usa. En este sistema el caso central son los **permisos por acción**,
no un objeto monolítico de «usuario con todos los permisos»:

```python
class PuedeRegistrarIngreso(BasePermission): ...
class PuedeAnularIngreso(BasePermission): ...              # solo Administrador
class PuedeConsultarConsolidacion(BasePermission): ...
```

El rol **Supervisor de planta** obtiene únicamente registro y consulta. No se le inyecta la interfaz
de gestión de usuarios ni la de consolidación. Esto no es elegancia: una solicitud directa a un
módulo fuera de su rol debe ser rechazada **en el servidor** y quedar registrada en auditoría.
Ocultar un botón no es control de acceso.

En Angular, cada `feature` expone su propio servicio con sus llamadas HTTP. Un `ApiService` global
con treinta métodos obliga a cada componente a depender de todo el sistema.

## D — Inversión de dependencias

Los servicios dependen de abstracciones, no de implementaciones concretas.

El caso obligatorio del proyecto: **`ServicioIngreso` recibe `ReconocedorTicket`,
`ValidadorConsistencia`, el generador de código y el reloj por inyección, no los instancia dentro.**

```python
class ServicioIngreso:
    def __init__(self, reconocedor: ReconocedorTicket, validador: ValidadorConsistencia,
                 generador_codigo, reloj):
        ...
```

La razón es verificable: en pruebas se sustituyen por dobles deterministas sin invocar a un servicio
externo real. Y hay una razón de dominio encima — D-12 aún no elige el motor concreto, así que
cambiar de proveedor no debe obligar a tocar el servicio de registro ni a rehacer sus pruebas.

Aplica igual a los exportadores de M08, al repositorio de lectura de M07 y al reloj: un servicio que
llama a `timezone.now()` internamente **no se puede probar** controlando el instante exacto de cada
una de las tres marcas de tiempo del ingreso.

---

## Lo que SOLID no autoriza aquí

Abstraer por si acaso es tan defectuoso como no abstraer. Nueve módulos no admiten una interfaz por
cada clase. Crea la abstracción cuando exista **una segunda implementación real o una prueba que la
exija** — el motor de reconocimiento (D-12 exige comparar candidatos), las reglas de validación (OCP
lo pide explícitamente), el generador de código (la prueba de concurrencia lo exige), el reloj
(ídem). Un `RepositorioVehiculoInterface` con una sola implementación y ninguna prueba que la
sustituya es ceremonia, y se defiende peor que su ausencia.

## Verificación antes de cerrar un módulo

- [ ] Ninguna regla de negocio en `views/` ni en un componente Angular.
- [ ] Cada RN del módulo es localizable en `models/` o en una regla de dominio.
- [ ] Los servicios reciben por inyección lo que las pruebas necesitan sustituir (reconocedor,
      validador, generador de código, reloj, exportador).
- [ ] Los permisos están declarados por acción, y hay una prueba que verifica el rechazo por rol
      contra el criterio de aceptación que lo exige.
- [ ] Lectura y escritura separadas: `repositories/` no escribe, `services/` no consulta para
      presentar. Esto permite optimizar las consultas de M07 y M08 sin tocar la lógica de escritura.
- [ ] Añadir una regla de validación, un formato de exportación o un adaptador de motor no obligó a
      editar código existente.
- [ ] Toda operación de escritura ocurre en una única `transaction.atomic()`: código, persistencia
      de valores reconocidos y confirmados, y evento de auditoría, o ninguno.
