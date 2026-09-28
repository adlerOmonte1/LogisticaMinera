---
name: reconocimiento-validacion
description: Implementa el reconocimiento automático del ticket (M04) y la validación automática de consistencia (M05) del sistema web inteligente de ingreso de mineral — la interfaz ReconocedorTicket y sus adaptadores, el umbral de confianza, las cinco reglas V1 a V5 como clases registradas, y cómo se registran los datos que alimentan ERA y TDI. Úsala al trabajar en apps/reconocimiento, apps/validacion, al escribir un adaptador de motor o una regla de validación, y cuando se mencione OCR, motor de reconocimiento, confianza, inconsistencia o las reglas V1 a V5.
---

# Reconocimiento y validación

Carga antes `contexto-tesis`, `solid-proyecto` y `backend-django`. Fuentes:
`docs/modulos/M04-reconocimiento/`, `docs/modulos/M05-validacion/` y
`docs/00-arquitectura/decisiones_diseno.md` D-12, D-13, D-16.

Estos dos módulos son el componente que distingue a este sistema de un formulario de captura. Se
documentan juntos porque comparten un mismo momento del flujo —la propuesta que antecede a la
confirmación— aunque sean apps y responsabilidades separadas.

## M04 — La interfaz, no el motor

`ReconocedorTicket` es el único punto de acoplamiento entre el servicio de registro y el motor
concreto. El motor lo elige D-12, tras un piloto con 20 a 30 tickets reales; **el código no se
escribe pensando en un motor específico**.

```python
class ReconocedorTicket(Protocol):
    def reconocer(self, imagen: bytes) -> ResultadoReconocimiento: ...

class ResultadoReconocimiento:
    exito: bool
    motor: str
    version_motor: str
    campos: list[CampoLeido]   # placa, fecha, peso_bruto: lo unico que imprime el ticket (DR-09)

class CampoLeido:
    nombre: str
    valor: str | None      # None si no hubo lectura (RN-M04-03)
    confianza: float | None  # None si no hubo lectura; nunca 0.0 en su lugar (RN-M04-06)
```

**Solo `apps/reconocimiento/motores/` importa el SDK o la librería del proveedor.** Un adaptador por
motor candidato:

```python
# apps/reconocimiento/motores/paddle_ocr.py
class ReconocedorPaddleOCR:
    def reconocer(self, imagen: bytes) -> ResultadoReconocimiento:
        ...  # unica clase que importa paddleocr

# apps/reconocimiento/motores/azure_document_intelligence.py
class ReconocedorAzureDocumentIntelligence:
    def reconocer(self, imagen: bytes) -> ResultadoReconocimiento:
        ...  # unica clase que importa el SDK de Azure
```

El motor activo se resuelve desde la configuración (`RECONOCEDOR_ACTIVO` en `.env`), nunca por un
`if` en el código de negocio.

### Umbral de confianza

Configurable, 0,80 por defecto (`ReconocimientoTicket.umbral_confianza`, guardado en cada
reconocimiento). El umbral vigente al procesar se persiste junto con el resultado: si se cambia
después, los reconocimientos anteriores conservan el umbral con el que realmente se evaluaron.

Un campo con confianza por debajo del umbral se marca como dudoso; un campo sin lectura no tiene
confianza y se presenta vacío. Son estados distintos: **no conviertas la ausencia de lectura en una
confianza de cero**, porque confundiría «no leí nada» con «leí algo con calidad nula».

### Fallo y tiempo de espera

El adaptador impone el límite de tiempo (RNF-M04-02, 10 segundos) y traduce cualquier excepción del
proveedor a un `ResultadoReconocimiento` con `exito=False`. **El servicio de registro nunca ve una
excepción del motor**: ve un resultado sin lecturas y continúa con el registro manual (RN-M04-07).
Un motor caído no debe poder detener el registro de un ingreso.

### Persistencia: valor reconocido y valor confirmado, siempre separados

```python
class CampoReconocido(models.Model):
    reconocimiento = models.ForeignKey(ReconocimientoTicket, on_delete=models.CASCADE)
    nombre_campo = models.CharField(max_length=12, choices=CAMPOS)
    valor_reconocido = models.CharField(max_length=50, null=True, blank=True)
    valor_confirmado = models.CharField(max_length=50)
    confianza = models.DecimalField(max_digits=4, decimal_places=3, null=True, blank=True)

    @property
    def fue_corregido(self):
        return self.valor_reconocido != self.valor_confirmado
```

`fue_corregido` es una propiedad derivada, nunca una columna que el cliente pueda escribir
(RN-M04-10): si el cliente pudiera declararla, podría afirmar que no hubo corrección cuando sí la
hubo, y ERA perdería su única fuente de verificación.

## M05 — Una clase por regla, nunca un `if` por regla en el servicio

```python
class Regla(Protocol):
    codigo: str            # "V1" a "V5"
    bloqueante: bool        # False en V1 y V4, que exigen justificacion
    campo: str
    mensaje: str            # literal, con marcadores como {placa}
    def datos_completos(self, datos: DatosTicket) -> bool: ...
    def cumple(self, datos: DatosTicket) -> bool: ...
```

| Regla | Condición | Bloqueante |
|---|---|---|
| V1 | no existe un ingreso no anulado con la misma placa, fecha y peso bruto | No — exige justificación |
| V2 | tara del vehículo < bruto | Sí |
| V3 | placa cumple el patrón de placa peruana | Sí |
| V4 | neto calculado dentro de la capacidad del vehículo | No — exige justificación |

La tara y la capacidad llegan en los datos, leídas del catálogo por el servicio de registro; V2 y V4
se omiten si el vehículo aún no tiene tara y se evalúan al registrar el destare. V1 es la única regla
que consulta otros ingresos, a través de un repositorio de lectura inyectado
(`buscar_por_placa_fecha_peso`), para seguir probándose sin base de datos.
| V5 | fecha del ticket ≤ fecha de registro | Sí |

`ValidadorConsistencia` recorre la colección registrada de reglas y **no nombra ninguna regla
concreta** (RN-M05-01 a RN-M05-04): el servicio de registro no sabe cuántas reglas hay ni cuáles son,
solo invoca `validar(datos)` y recibe la lista de inconsistencias. Añadir una regla nueva es una
clase más en la colección, sin tocar V1 a V5 ni el validador.

**Las cinco se evalúan siempre**, aunque la primera ya haya fallado (RN-M05-04): el usuario debe ver
de una vez todo lo que tiene que corregir, no un error a la vez. Una regla cuyos datos necesarios
faltan **se omite**, no se reporta como incumplida (RN-M05-07): un campo vacío lo reclama el
registro, no el validador.

Se aplican **sobre los datos que propone el reconocimiento, de nuevo sobre los que el usuario
confirma y, en el primer viaje, al registrar el destare** (RN-M05-05). La segunda pasada existe porque el usuario pudo introducir
una incoherencia nueva al corregir.

### Persistencia del resultado

```python
class ResultadoValidacion(models.Model):
    ingreso = models.ForeignKey(Ingreso, on_delete=models.PROTECT)
    regla = models.CharField(max_length=2, choices=REGLAS)
    momento = models.CharField(max_length=12, choices=MOMENTOS)  # PROPUESTA / CONFIRMACION / DESTARE
    cumple = models.BooleanField()
    detalle = models.TextField(blank=True)
    resolucion = models.CharField(max_length=12, choices=RESOLUCIONES, blank=True)
    justificacion = models.TextField(blank=True)  # obligatoria si V1 o V4 se resolvieron asi
```

`detalle` conserva los valores concretos que motivaron el incumplimiento, no solo el hecho de que
ocurrió: saber que V2 falló sirve de poco sin saber qué peso bruto se leyó y qué tara tenía el vehículo.

## Cómo se registran los datos para ERA y TDI

Ninguno de los dos indicadores se calcula dentro del sistema: se miden aparte, sobre el conjunto de
prueba de `docs/03-pruebas/plan_de_pruebas.md` §4. Lo que este código debe garantizar es que **los
datos necesarios para calcularlos existan y sean correctos**:

- **Para ERA:** cada `CampoReconocido` conserva `valor_reconocido`, `confianza`, y el
  `ReconocimientoTicket` conserva `motor` y `version_motor`. Sin esto, no hay con qué comparar la
  lectura del motor contra el valor real del ticket.
- **Para TDI:** cada `ResultadoValidacion` conserva `regla`, `momento` y `cumple`. El conjunto de
  prueba siembra inconsistencias conocidas y verifica que el sistema las señale con el código de
  regla correcto.

**Condición de congelamiento (D-16):** durante la medición de ERA y TDI, ni el motor ni las reglas
V1 a V5 cambian de versión o de parámetro. Escribe una prueba que verifique que todos los
reconocimientos de un periodo comparten el mismo `motor` y `version_motor`.

## Verificación

- [ ] Ningún archivo fuera de `apps/reconocimiento/motores/` importa una librería de un proveedor de
      reconocimiento.
- [ ] Un campo sin lectura tiene `valor_reconocido` y `confianza` nulos, nunca cero ni vacío.
- [ ] `fue_corregido` es una propiedad derivada, no una columna escribible.
- [ ] El fallo del motor no impide registrar el ingreso.
- [ ] Cada regla de M05 es una clase independiente, registrada en una colección que el validador
      recorre sin nombrarlas.
- [ ] Las cinco reglas se evalúan siempre, y una con datos incompletos se omite en vez de fallar.
- [ ] Existe una prueba que siembra cada una de las diez inconsistencias del conjunto de prueba y
      verifica que se detecta con el código correcto.
