---
name: solid-proyecto
description: Aplica y verifica los principios SOLID en el código del sistema de control de producción y existencias, según la correspondencia requisito-capa fijada en ARQ-02 §5. Úsala al escribir o revisar cualquier modelo, servicio, selector, vista, serializer, permiso, exportador o servicio Angular, cuando se pida refactorizar, cuando se mencione SOLID, responsabilidad única, inversión de dependencias, acoplamiento o "dónde va esta lógica", y antes de dar por cerrado un módulo del backend.
---

# SOLID en este proyecto

Carga antes `contexto-tesis`. La fuente es `docs/00-arquitectura/ARQ-02_Arquitectura_Tecnica.md` §5.

Aquí SOLID no es una preferencia de estilo. La tesis afirma que el sistema cumple **ISO/IEC 25010:2023**
en *mantenibilidad* (modularidad, reusabilidad, modificabilidad, capacidad de ser probado), y esa
afirmación se sustenta enseñando el código. Un servicio que mezcla responsabilidades es una respuesta
peor en sustentación, no solo un código peor.

## La correspondencia que decide dónde va cada cosa

Los cinco tipos de requisito no están separados por formalismo académico: **cada tipo aterriza en una
capa distinta**. Si sabes qué tipo de requisito estás implementando, ya sabes en qué archivo va.

| Tipo de requisito | Capa Django | Capa Angular | Principio |
|---|---|---|---|
| Regla de negocio (RN) | `models.py`, validadores de dominio | — nunca como fuente de verdad | SRP |
| Requisito de sistema (RS) | `services.py` | servicio del feature | SRP, DIP |
| Requisito funcional (RF) | `views.py` + `serializers.py` | componentes y rutas | ISP |
| Requisito no funcional (RNF) | configuración, índices, caché, middleware | service worker, estrategias de caché | OCP |

**La prueba para ubicar cualquier lógica:** si la validación puede enunciarse sin mencionar HTTP,
**no** pertenece a `views.py`. «La tara debe ser menor que el peso bruto» no menciona HTTP: va al
modelo. «Devolver 403 si el rol no es administrador» sí lo menciona: va a `permissions.py`.

---

## S — Responsabilidad única

Una capa, un motivo de cambio.

| Archivo | Única responsabilidad | Lo que NO hace |
|---|---|---|
| `models.py` | Proteger las invariantes de la entidad (RN-*) | Llamar a otros servicios, saber de HTTP |
| `services.py` | Orquestar un caso de uso (RS-*) | Contener reglas de negocio; solo las invoca |
| `selectors.py` | Consultas de lectura | Escribir |
| `serializers.py` | Traducir dominio ↔ JSON | Validar reglas de negocio |
| `views.py` | Entrada/salida HTTP (RF-*) | Todo lo demás |
| `permissions.py` | Autorización por acción | Lógica de negocio |

Ejemplo canónico del proyecto: «la hora de pesaje no puede ser posterior a la hora de registro»
(RN-M03-02) vive en el modelo `Ingreso`. **No** en el formulario Angular, **no** en el `IngresoViewSet`.
Un registro que llega por la cola de sincronización de M07 no pasa por el formulario y debe someterse
a la misma regla — esa es la razón concreta, no una abstracción (D-08).

**Olor a violación:** un `services.py` con un `if` que compara pesos; un `views.py` con más de tres
líneas que no sean traducción de HTTP; un serializer con `validate_*` que implementa una RN en lugar
de delegarla.

## O — Abierto/cerrado

Extender sin modificar lo que ya funciona.

El caso vivo es M06. Los exportadores comparten una abstracción:

```python
class Exportador(Protocol):
    def exportar(self, reporte: Reporte) -> bytes: ...

class ExportadorExcel:  # openpyxl
    def exportar(self, reporte: Reporte) -> bytes: ...

class ExportadorPDF:    # ReportLab
    def exportar(self, reporte: Reporte) -> bytes: ...
```

Añadir el formato de declaración semestral (HU-M06-02) debe ser **una clase nueva**, no un `elif` en
una función existente. Esto importa de forma práctica: el formato oficial de la declaración semestral
todavía no está a la mano (pendiente registrado, límite semana 7), así que M06 se construye sabiendo
que llegará un formato más. Si el diseño no está abierto a extensión, ese pendiente se convierte en
una reescritura en la semana 7, que es cuando menos margen hay.

Mismo criterio para los tipos de movimiento (ENTRADA / SALIDA / AJUSTE) y para las estrategias de
sincronización de M07.

## L — Sustitución de Liskov

Toda implementación de una abstracción debe poder sustituir a otra sin romper a quien la consume.
`ExportadorPDF` va donde se espera un `Exportador`, sin que el llamador pregunte de qué tipo es.

**Violación típica y concreta:** un exportador que lanza `NotImplementedError` para el consolidado
mensual «porque ese solo va en Excel». Si una implementación no honra el contrato completo, el
contrato está mal partido — divídelo (eso es ISP) en lugar de dejar un método que revienta.

Otra: un selector de stock que devuelve `None` cuando el producto no tiene movimientos, mientras
otro devuelve `0`. HU-M05-01 CA04 exige explícitamente **cero, no un error**. Las implementaciones
intercambiables deben coincidir también en los casos límite.

## I — Segregación de interfaces

Nadie depende de métodos que no usa. En este sistema el caso central son los **permisos por acción**,
no un objeto monolítico de «usuario con todos los permisos»:

```python
class PuedeRegistrarIngreso(BasePermission): ...
class PuedeAnularIngreso(BasePermission): ...      # solo Administrador
class PuedeConsultarExistencias(BasePermission): ...
```

El rol **Supervisor** obtiene únicamente registro de ingresos y consulta de existencias. No se le
inyecta la interfaz de gestión de usuarios ni la de reportes. Esto no es elegancia: HU-M01-04 CA02
exige que una solicitud directa al módulo de reportes por parte de un supervisor sea rechazada **en
el servidor** y quede registrada en auditoría. Ocultar un botón no es control de acceso.

En Angular, cada `feature` expone su propio servicio con sus llamadas HTTP. Un `ApiService` global
con treinta métodos obliga a cada componente a depender de todo el sistema.

## D — Inversión de dependencias

Los servicios dependen de abstracciones, no de implementaciones concretas.

El caso obligatorio del proyecto: **`registrar_ingreso()` recibe el generador de correlativo por
inyección, no lo instancia dentro.**

```python
def registrar_ingreso(datos, usuario, generador: GeneradorCorrelativo) -> Ingreso:
    ...
```

La razón es verificable: en pruebas se sustituye por uno determinista sin tocar la lógica del caso
de uso. Y hay una razón de dominio encima — D-02 deja abiertas dos implementaciones válidas
(secuencia de PostgreSQL o tabla de contadores con `select_for_update()`), y cuál se adopte es una
pregunta previsible en sustentación. Si el servicio instancia una concreta, cambiar de estrategia
obliga a tocar el caso de uso y a rehacer sus pruebas.

Aplica igual a los exportadores de M06, al repositorio de lectura de M05 y al reloj: un servicio que
llama a `timezone.now()` internamente **no se puede probar** contra los límites de HU-M03-02
(antigüedad de 72 horas, de 30 días). Inyecta el reloj.

---

## Lo que SOLID no autoriza aquí

Abstraer por si acaso es tan defectuoso como no abstraer. Ocho semanas de cronograma y nueve módulos
no admiten una interfaz por cada clase. Crea la abstracción cuando exista **una segunda
implementación real o una prueba que la exija** — exportadores (la hay), generador de correlativo (la
prueba la exige), reloj (idem). Un `RepositorioProductoInterface` con una sola implementación y
ninguna prueba que la sustituya es ceremonia, y en sustentación se defiende peor que su ausencia.

## Verificación antes de cerrar un módulo

- [ ] Ninguna regla de negocio en `views.py` ni en un componente Angular.
- [ ] Cada RN del módulo es localizable en `models.py` o en un validador de dominio.
- [ ] Los servicios reciben por inyección lo que las pruebas necesitan sustituir (correlativo, reloj,
      exportador).
- [ ] Los permisos están declarados por acción, y hay una prueba que verifica el rechazo por rol
      contra el criterio de aceptación que lo exige.
- [ ] Lectura y escritura separadas: `selectors.py` no escribe, `services.py` no consulta para
      presentar. Esto sostiene I3, porque permite optimizar las consultas de stock sin tocar la
      lógica de escritura.
- [ ] Añadir un formato de reporte o un tipo de movimiento no obligó a editar código existente.
- [ ] Toda la operación de escritura ocurre en una única `transaction.atomic()`: correlativo,
      persistencia, movimiento de stock y evento de auditoría, o ninguno.
