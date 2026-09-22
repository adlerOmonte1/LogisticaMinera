# Notas de implementación — M03 Registro de ingresos

## Backend (Django)

**App:** `apps/ingresos/`

> La app existe con el diseño anterior —peso neto calculado, marca de tiempo única y campos de
> captura local— y se refactoriza, no se recrea. El cambio se aplica en la fase de limpieza del
> backend del plan de migración.

### Modelo

```python
class Ingreso(models.Model):
    codigo = models.CharField(max_length=20, unique=True, editable=False)
    imagen_ticket = models.ImageField(upload_to="tickets/%Y/%m/")
    fecha_hora_ticket = models.DateTimeField()
    hora_inicio_registro = models.DateTimeField(editable=False)
    hora_fin_registro = models.DateTimeField(editable=False)
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.PROTECT)
    tipo_mineral = models.ForeignKey(TipoMineral, on_delete=models.PROTECT)
    peso_bruto_tn = models.DecimalField(max_digits=8, decimal_places=2)
    tara_tn = models.DecimalField(max_digits=8, decimal_places=2)
    peso_neto_tn = models.DecimalField(max_digits=8, decimal_places=2)
    numero_ticket = models.CharField(max_length=20, blank=True)
    justificacion_peso = models.TextField(blank=True)
    usuario_registro = models.ForeignKey(Usuario, on_delete=models.PROTECT, editable=False)
    estado = models.CharField(max_length=10, choices=ESTADOS, default=REGISTRADO)
    motivo_anulacion = models.TextField(blank=True)
```

Decisiones no obvias:

- **`peso_neto_tn` no es `editable=False` ni una propiedad calculada.** Es un dato del ticket
  (RN-M03-04). Quien lo convierta en propiedad rompe la regla V1 sin que ninguna prueba de M03 falle:
  la comprobación vive en M05.
- **Las dos marcas del servidor son `editable=False` y las asigna el servicio**, nunca
  `auto_now_add` (D-01). `auto_now_add` fijaría la hora de inserción, que no es la del inicio real de
  la operación.
- **`on_delete=PROTECT` en las tres claves foráneas.** Nada que tenga ingresos asociados puede
  borrarse, ni siquiera desde el admin.
- **Restricciones en la base, además del servicio:** unicidad de `numero_ticket` condicionada a
  `estado='REGISTRADO'`, y comprobaciones de que la tara sea menor que el bruto y de que los pesos
  sean positivos. Son salvaguardas: la validación con mensaje para el usuario ocurre en M05.
- **Índices desde la primera migración:** `(vehiculo, fecha_hora_ticket)`, `(fecha_hora_ticket,
  tipo_mineral)` y `estado`. Añadirlos después cambiaría el comportamiento a mitad de operación.

### Reconocimiento y validación como dependencias inyectadas

```python
class ServicioIngreso:
    def __init__(self, reconocedor: ReconocedorTicket, validador: ValidadorConsistencia,
                 generador: GeneradorCodigo, reloj: Reloj):
        ...
```

Las cuatro son interfaces. El servicio no importa el motor concreto ni las reglas: los recibe. Es lo
que permite cambiar de motor cuando se cierre D-12 sin tocar este módulo, y probar el registro con
dobles de prueba sin depender de un servicio externo.

El reloj también se inyecta: las marcas de tiempo son el corazón del registro, y una prueba que no
pueda fijar «ahora» no puede verificarlas.

### Servicio: qué ocurre dentro de la transacción

`registrar_ingreso()` abre `transaction.atomic()` y dentro hace, en este orden: obtener el código
con bloqueo sobre el contador, persistir el ingreso con la hora de fin, persistir los valores
reconocidos y confirmados de cada campo, y registrar el evento de auditoría.

Fuera de la transacción quedan el reconocimiento y la primera validación, porque ocurren antes de
que el usuario confirme y no escriben nada del ingreso.

**Lo que no puede quedar fuera:** el evento de auditoría. Si se registrara después del `commit`, un
fallo intermedio dejaría un ingreso sin rastro de quién lo creó (RN-M03-15).

### Escritura de la imagen

La imagen se guarda antes de abrir la transacción del registro, porque el sistema de archivos no
participa del `rollback`. Una imagen huérfana —guardada para un registro que nunca se confirmó— es
aceptable y se limpia con una tarea periódica; un ingreso sin imagen, no.

## Frontend (Angular)

**Feature:** `features/ingresos/`

- **Captura con `<input type="file" accept="image/*" capture="environment">`.** Abre la cámara
  trasera directamente en el teléfono, sin pantalla intermedia (RNF-M03-07).
- **Reducción en el cliente antes de enviar** mediante `canvas`, conservando legible el texto del
  ticket (RNF-M03-04).
- **Formulario reactivo con los campos precargados** desde la propuesta, cada uno con su indicador
  de confianza. Los campos por debajo del umbral se resaltan (RNF-M03-08).
- **Los campos derivados y asignados por el servidor se muestran `readonly`, nunca `disabled`:** un
  control deshabilitado no viaja en el payload y el valor se perdería.
- **Borrador en almacenamiento local del navegador**, guardado con cada cambio y descartado al
  confirmar (RNF-M03-05). El borrador guarda la imagen ya reducida y los campos editados.
- **Los mensajes de error se muestran literalmente como los devuelve el servidor**, junto al campo
  afectado. La interfaz no los reformula ni los resume.

## Riesgo de implementación identificado

**El riesgo principal es que las tres marcas de tiempo terminen midiendo lo que no deben.**

`hora_inicio_registro` debe asignarse cuando llega la imagen, no cuando se confirma el ingreso. Es
un error fácil de cometer, porque la forma natural de escribir el servicio es asignar todo junto al
final, y entonces el inicio y el fin quedan separados por milisegundos: el registro parecería
instantáneo siempre.

La prueba obvia —verificar que los tres campos existen y son distintos— no lo detecta. La prueba que
sí lo detecta usa el reloj inyectado para simular que entre la carga de la imagen y la confirmación
transcurren varios minutos, y comprueba que el inicio corresponde al primer momento y el fin al
segundo.

**Riesgo secundario:** que alguien convierta `peso_neto_tn` en un campo calculado durante una
refactorización, por parecer redundante. Ninguna prueba de M03 fallaría. La defensa es la prueba de
M05 que registra un ingreso cuyo neto no coincide con la resta y espera que la regla V1 lo señale;
si el neto se calcula, esa prueba deja de poder construirse.

## Dependencias

| Depende de | Para |
|---|---|
| M01 | Autenticación y atribución de cada operación a un usuario |
| M02 | Vehículo vigente con titularidad y capacidad; catálogo de tipos de mineral |
| M04 | Propuesta de los seis campos del ticket, con su confianza |
| M05 | Evaluación de las reglas V1 a V5 |
| M09 | Registro de los eventos de creación, corrección y anulación |

| Es requerido por | Para |
|---|---|
| M06 | Asignar ingresos a un lote de proceso |
| M07 | Consultar un ingreso por placa y fecha con su respaldo |
| M08 | Calcular el total acumulado mensual por tipo de mineral |

## Pendientes que afectan a este módulo

| Pendiente | Efecto |
|---|---|
| Medio de almacenamiento y retención de las imágenes (D-14) | Define `upload_to`, el respaldo y el acceso restringido de RNF-M03-11 |
| Motor de reconocimiento (D-12) | No bloquea: el servicio depende de la interfaz. Sí condiciona RNF-M03-02 |
| Valores del catálogo de tipos de mineral (DR-03) | Sin ellos no puede completarse el campo obligatorio de tipo de mineral |
