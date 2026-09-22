# Notas de implementación — M04 Reconocimiento automático del ticket

## Backend (Django)

**App:** `apps/reconocimiento/` — no existe todavía; se crea en la fase de preparación del backend.

### Estructura

```
apps/reconocimiento/
├── models/          RECONOCIMIENTO_TICKET y CAMPO_RECONOCIDO
├── services/        proceso de reconocimiento y persistencia
├── repositories/    lectura para la consulta comparativa
├── motores/         un adaptador por motor: el unico lugar que importa la libreria externa
├── serializers/  views/  permissions.py  filters.py  urls.py  tests/
```

### Modelo

```python
class ReconocimientoTicket(models.Model):
    ingreso = models.OneToOneField(Ingreso, on_delete=models.CASCADE,
                                   related_name="reconocimiento")
    motor = models.CharField(max_length=50, editable=False)
    version_motor = models.CharField(max_length=30, editable=False)
    fecha_proceso = models.DateTimeField(editable=False)
    umbral_confianza = models.DecimalField(max_digits=3, decimal_places=2, editable=False)
    exito = models.BooleanField(default=True)


class CampoReconocido(models.Model):
    reconocimiento = models.ForeignKey(ReconocimientoTicket, on_delete=models.CASCADE,
                                       related_name="campos")
    nombre_campo = models.CharField(max_length=12, choices=CAMPOS)
    valor_reconocido = models.CharField(max_length=50, null=True, blank=True)
    valor_confirmado = models.CharField(max_length=50)
    confianza = models.DecimalField(max_digits=4, decimal_places=3, null=True, blank=True)

    @property
    def fue_corregido(self):
        return self.valor_reconocido != self.valor_confirmado
```

Decisiones no obvias:

- **`valor_reconocido` y `confianza` admiten nulo; `valor_confirmado` no.** Un campo sin lectura no
  tiene valor ni confianza —no tiene confianza cero (RN-M04-06)—, pero sí tiene el valor que el
  usuario escribió. Usar cadena vacía o cero en lugar de nulo borraría esa distinción.
- **`fue_corregido` es una propiedad, no una columna.** Se deriva de comparar los dos valores. Como
  columna, el cliente podría enviarla y contradecir a los datos (RN-M04-10). Si el volumen exigiera
  filtrar por ella, se añade como columna generada por la base, nunca como campo escribible.
- **`OneToOneField` con `CASCADE`.** Un ingreso tiene como máximo un reconocimiento (RN-M04-09), y
  una lectura sin ingreso no describe nada. Es la única relación del sistema que borra en cascada, y
  se justifica porque el reconocimiento no es un registro del negocio sino un detalle del ingreso.
- **Los valores se guardan como texto, no con su tipo final.** Lo que el motor leyó es una cadena:
  convertirla a decimal o a fecha antes de guardarla perdería precisamente el caso interesante, el
  de la lectura mal formada que el usuario tuvo que corregir.

### La interfaz y sus adaptadores

```python
class ReconocedorTicket(Protocol):
    def reconocer(self, imagen: bytes) -> ResultadoReconocimiento: ...
```

`ResultadoReconocimiento` lleva el motor, su versión, si hubo éxito y la lista de campos con su
valor y su confianza. Es el único contrato que M03 conoce.

Cada motor candidato se implementa como un adaptador en `motores/`, y **solo esos archivos importan
la librería o el SDK del proveedor** (RNF-M04-05). El motor activo se resuelve desde la
configuración, de modo que cambiarlo sea un cambio de variable de entorno y no de código.

Esta es una de las pocas abstracciones justificadas de antemano en el proyecto (D-09): la segunda
implementación no es hipotética, porque D-12 sigue abierta y el piloto comparará varias.

### Tiempo de espera y fallo

El adaptador impone el límite de diez segundos (RNF-M04-02) y traduce cualquier fallo del proveedor
a un resultado vacío con su causa. **El servicio de registro no ve excepciones del motor**: ve un
resultado sin lecturas. Es lo que hace que la indisponibilidad del motor sea un caso previsto y no
un error que interrumpa el registro.

## Frontend (Angular)

**Feature:** `features/ingresos/` — el reconocimiento no tiene pantalla propia: vive dentro del
formulario de registro.

- Los tres estados de un campo se distinguen sin depender solo del color (RNF-M04-09): vacío con
  indicación de que debe escribirse, dudoso con marca visible y texto de apoyo, y normal.
- El mensaje de baja confianza es el literal del criterio de aceptación, mostrado junto al campo.
- La comparación de HU-M04-02 es un componente de `ui/`, sin estado: recibe la lista de campos y la
  presenta. Se prueba con entradas y salidas, sin simular peticiones.

## Riesgo de implementación identificado

**El riesgo principal es que el umbral de confianza acabe siendo decorativo.**

Es fácil implementar el resaltado de campos dudosos y que, en la práctica, el motor devuelva
confianzas altas para casi todo, incluidas las lecturas equivocadas. Entonces el usuario deja de
revisar —nada aparece resaltado— y los errores del motor pasan directos a la confirmación.

La prueba obvia, que el campo se resalta cuando la confianza es menor que el umbral, no lo detecta:
verifica el mecanismo, no su utilidad. Lo que sí lo detecta es medir, sobre el conjunto de tickets
de prueba, cuántos campos corregidos por el usuario tenían confianza por encima del umbral. Si esa
proporción es alta, el umbral no está cumpliendo su función y hay que subirlo o cambiar de motor.
Esa medición debe hacerse durante el piloto de D-12, no después.

**Riesgo secundario:** que alguien haga que el adaptador rellene con cero o con cadena vacía los
campos sin lectura, para simplificar el modelo. Ninguna prueba fallaría, y el sistema pasaría a
afirmar que leyó algo que no leyó.

## Dependencias

| Depende de | Para |
|---|---|
| M01 | Autenticación y atribución de la consulta |
| M03 | La imagen del ticket y el momento del reconocimiento |
| M09 | Registro de los eventos de reconocimiento y corrección |

| Es requerido por | Para |
|---|---|
| M03 | Proponer los seis campos del ticket al iniciar el registro |

## Pendientes que afectan a este módulo

| Pendiente | Efecto |
|---|---|
| Motor de reconocimiento (D-12) | Define qué adaptador se implementa primero y si el motor es local o externo. La interfaz y el resto del módulo no dependen de esa decisión |
| Procesamiento síncrono o asíncrono (D-15) | Si el piloto muestra tiempos altos, cambia el flujo y con él S-M04-01 |
| Conjunto de tickets de prueba | Necesario para el piloto y para medir la utilidad del umbral |
