# Notas de implementación — M03 Registro de ingresos

## Backend (Django)

**App:** `apps/ingresos/`

### Modelo

```python
class Ingreso(models.Model):
    codigo = models.CharField(max_length=20, unique=True, editable=False)
    imagen_ticket = models.ImageField(upload_to="tickets/%Y/%m/", null=True, blank=True)
    sin_respaldo_fotografico = models.BooleanField(default=False, editable=False)
    motivo_sin_respaldo = models.CharField(max_length=60, choices=MOTIVOS_SIN_FOTO, blank=True,
                                           editable=False)
    fecha_hora_pesaje = models.DateTimeField()
    hora_inicio_registro = models.DateTimeField(editable=False)
    hora_fin_registro = models.DateTimeField(editable=False)
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.PROTECT)
    tipo_mineral = models.ForeignKey(TipoMineral, on_delete=models.PROTECT)
    peso_bruto_tn = models.DecimalField(max_digits=8, decimal_places=2)
    tara_tn = models.DecimalField(max_digits=8, decimal_places=2, null=True, editable=False)
    peso_neto_tn = models.DecimalField(max_digits=8, decimal_places=2, null=True, editable=False)
    usuario_registro = models.ForeignKey(Usuario, on_delete=models.PROTECT, editable=False)
    estado = models.CharField(max_length=10, choices=ESTADOS)  # EN_PROCESO, REGISTRADO, ANULADO
    motivo_anulacion = models.TextField(blank=True)
```

Decisiones no obvias:

- **`peso_neto_tn` y `tara_tn` son `editable=False` y los asigna el servicio** (RN-M03-04, D-17).
  El neto se calcula como bruto menos la tara del vehículo en el momento de confirmar, y se
  **almacena**, no se deriva en una propiedad: una propiedad que leyera la tara del catálogo
  reescribiría el neto de todo el histórico cuando la Gerencia actualizara la tara de un vehículo.
- **`tara_tn` y `peso_neto_tn` admiten nulo solo en `EN_PROCESO`.** Una restricción de base lo
  garantiza: si el estado es `REGISTRADO`, ambos son obligatorios.
- **`fecha_hora_pesaje` combina dos orígenes**: la fecha que reconoce M04 y la hora que indica el
  usuario sobre la propuesta del sistema (DR-11). El serializer recibe ambas partes por separado y
  el servicio las compone; así la comparación entre lo reconocido y lo confirmado se hace solo sobre
  la fecha, que es lo que el ticket imprime. La propuesta de hora la calcula el servidor con el
  `Reloj` inyectado al abrir la revisión, no el navegador, para que todos los clientes propongan la
  misma referencia.
- **La imagen admite nulo solo si `sin_respaldo_fotografico` es verdadero** (DR-13). Una restricción
  de base exige exactamente una de las dos cosas: imagen, o marca con motivo. Ambos campos son
  `editable=False`: la marca no se retira por corrección, porque la imagen no es corregible.
  `MOTIVOS_SIN_FOTO` es la lista cerrada de la HU; «Otro» forma parte de ella.
- **Las dos marcas del servidor son `editable=False` y las asigna el servicio**, nunca
  `auto_now_add` (D-01). `auto_now_add` fijaría la hora de inserción, que no es la del inicio real de
  la operación.
- **`on_delete=PROTECT` en las tres claves foráneas.** Nada que tenga ingresos asociados puede
  borrarse, ni siquiera desde el admin.
- **No hay número de ticket** (DR-12): el código del ingreso es su único identificador, y el pesaje
  registrado dos veces lo advierte V1. No se crea la columna ni su índice de unicidad.
- **Restricciones en la base, además del servicio:** que la tara aplicada sea menor que el bruto y
  que los pesos sean positivos. Son salvaguardas: la validación con mensaje para el usuario ocurre en M05.
- **Índices desde la primera migración:** `(vehiculo, fecha_hora_pesaje)`, `(fecha_hora_pesaje,
  tipo_mineral)` y `estado`. Añadirlos después cambiaría el comportamiento a mitad de operación.

### Reconocimiento y validación como dependencias inyectadas

```python
class ServicioIngreso:
    def __init__(self, reconocedor: ReconocedorTicket, validador: ValidadorConsistencia,
                 generador: GeneradorCodigo, reloj: Reloj, auditoria: ServicioAuditoria):
        ...
```

Las cuatro primeras son interfaces. El servicio no importa el motor concreto ni las reglas: los
recibe. Es lo que permite cambiar de motor cuando se cierre D-12 sin tocar este módulo, y probar el
registro con dobles de prueba sin depender de un servicio externo. `ServicioAuditoria` es el servicio
concreto de M09 que todo servicio de escritura recibe para registrar su evento dentro de la misma
transacción (ver las notas de M09).

La imagen no necesita otra dependencia: se guarda por el `ImageField` del ingreso, que delega en el
almacenamiento de Django configurado para el entorno (D-18).

El reloj también se inyecta: las marcas de tiempo son el corazón del registro, y una prueba que no
pueda fijar «ahora» no puede verificarlas.

### Servicio: qué ocurre dentro de la transacción

`registrar_ingreso()` abre `transaction.atomic()` y dentro hace, en este orden: obtener el código
con bloqueo sobre el contador, leer la tara vigente del vehículo, calcular el neto si hay tara,
persistir el ingreso —Registrado o En proceso— con la hora de fin, persistir los valores reconocidos
y confirmados de cada campo, y registrar el evento de auditoría.

`registrar_destare()` recibe el vehículo, no un ingreso: el usuario elige el vehículo entre los que
tienen ingresos En proceso. Abre su propia transacción, pide a M02 que guarde la tara con la fecha y
hora del destare que indicó el usuario, recorre los ingresos En proceso de ese vehículo con
`select_for_update()`, les asigna la tara y el neto, los pasa a Registrado y registra el evento. El bloqueo impide que dos usuarios destaren el
mismo vehículo a la vez con taras distintas.

`registrar_ingreso()` atiende también el registro sin foto: recibe el motivo en lugar de la imagen,
no persiste valores reconocidos —no los hay— y aplica la misma validación. No existe un servicio
aparte para ese caso; separarlo duplicaría las reglas del registro y tarde o temprano divergirían.

`revertir_correccion()` toma el último evento `MODIFICAR` vigente del ingreso en M09, restaura sus
`valores_anteriores` por el mismo camino que `corregir_ingreso()` —con la misma validación— y
registra un evento nuevo que referencia al revertido (RN-M03-28, RN-M03-29). No hay tabla de
versiones: la auditoría ya es el historial.

`corregir_ingreso()` vuelve a leer la tara del vehículo corregido: si no la tiene, deja el ingreso En
proceso (RN-M03-26). Antes de cambiar el tipo de mineral consulta el lote del ingreso a través del
repositorio de M06 (RN-M03-25). `anular_ingreso()` pide al servicio de M06 que retire el ingreso de
su lote cuando este todavía reúne ingresos (RN-M03-27).

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
- **La hora del pesaje se presenta como propuesta**, con un estilo distinto del de los datos
  reconocidos y un control de hora para ajustarla (RNF-M03-14).
- **El registro sin foto es una opción de la pantalla de captura** (RNF-M03-17); abre el mismo
  formulario de revisión, sin visor de imagen y con el motivo como primer campo.
- **El alta del tipo de mineral solo se ofrece al Administrativo y al Administrador**; al Supervisor
  de planta se le muestra el aviso de la HU. La restricción vale igual en el servidor.
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

**Riesgo secundario: que el neto se calcule al vuelo.** Convertir `peso_neto_tn` en una propiedad
que lea la tara del catálogo parece más limpio y pasa todas las pruebas de registro. El defecto
aparece solo cuando la Gerencia actualiza la tara de un vehículo: todo su histórico cambia de
toneladas sin que nadie lo haya corregido. La prueba que lo detecta registra un ingreso, modifica
la tara del vehículo y comprueba que el neto de ese ingreso no cambió.

**Tercer riesgo: el ingreso En proceso olvidado.** Si nadie registra el destare, el ingreso queda
fuera de todos los totales de forma indefinida. La interfaz debe mostrar siempre cuántos ingresos
están pendientes de destare (RNF-M03-15), y el destare debe completar de una vez todos los ingresos
En proceso del mismo vehículo (HU-M03-04 CA07).

## Dependencias

| Depende de | Para |
|---|---|
| M01 | Autenticación y atribución de cada operación a un usuario |
| M02 | Vehículo vigente con titularidad, capacidad y tara; alta rápida de vehículos y registro de la tara en el destare; catálogo de tipos de mineral |
| M04 | Propuesta de la placa, la fecha y el peso bruto del ticket, con su confianza |
| M05 | Evaluación de las reglas V1 a V5 |
| M09 | Registro de los eventos de creación, corrección, anulación y destare |

| Es requerido por | Para |
|---|---|
| M06 | Asignar ingresos Registrados a un lote de proceso |
| M07 | Consultar un ingreso por placa y fecha con su respaldo |
| M08 | Calcular el total acumulado mensual por tipo de mineral |

## Pendientes que afectan a este módulo

| Pendiente | Efecto |
|---|---|
| Medio de almacenamiento y retención de las imágenes (D-14) | Define el backend de almacenamiento de Django, la retención y el respaldo. El código no cambia al cerrarse: la imagen se guarda por la API de almacenamiento de Django (D-18) |
| Motor de reconocimiento (D-12) | No bloquea: el servicio depende de la interfaz. Sí condiciona RNF-M03-02 |
| Valores del catálogo de tipos de mineral (DR-03) | Sin ellos no puede completarse el campo obligatorio de tipo de mineral; el alta desde el registro reduce el bloqueo |
| Tratamiento del ingreso sin foto en la ficha de observación (P-03) | No cambia el sistema; condiciona cómo se usa el ingreso en la medición |
