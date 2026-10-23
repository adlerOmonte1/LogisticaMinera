# Notas de implementación — M06 Trazabilidad del proceso

## Backend (Django)

**App:** `apps/trazabilidad/`

### Estructura

```
apps/trazabilidad/
├── models/          LOTE_PROCESO, PARTE_LOTE, REPARTO_INGRESO, ETAPA_PROCESO, PASO_ETAPA, BIGBAG
├── migrations/      incluye la carga inicial de las cuatro etapas
├── services/        ciclo de vida del lote, division, registro de etapas, bigbags y cierre
├── repositories/    composicion del lote, recorrido de un ingreso y resumen de cierre
├── serializers/  views/  permissions.py  filters.py  urls.py  tests/
```

### Modelo

```python
class LoteProceso(models.Model):
    codigo = models.CharField(max_length=20, unique=True, editable=False)
    nombre = models.CharField(max_length=80, unique=True)
    tipo_mineral = models.ForeignKey(TipoMineral, on_delete=models.PROTECT)  # el de apertura
    minerales = models.ManyToManyField(TipoMineral, through="LoteMineral", related_name="+")
    fecha_apertura = models.DateField()
    fecha_inicio_recorrido = models.DateTimeField(null=True, editable=False)
    ruta = models.CharField(max_length=30, choices=Ruta.choices, blank=True)  # sin dividir
    estado = models.CharField(max_length=12, choices=ESTADOS)  # ABIERTO, EN_RECORRIDO, CERRADO
    destino = models.CharField(max_length=10, choices=DESTINOS, blank=True)  # VENTA, TRASLADO
    observacion_cierre = models.TextField(blank=True)
    fecha_cierre = models.DateTimeField(null=True, editable=False)
    usuario_cierre = models.ForeignKey(Usuario, null=True, on_delete=models.PROTECT,
                                       editable=False, related_name="+")


class LoteMineral(models.Model):          # lista de tipos admitidos (DR-27)
    lote = models.ForeignKey(LoteProceso, on_delete=models.PROTECT, related_name="lista_minerales")
    tipo_mineral = models.ForeignKey(TipoMineral, on_delete=models.PROTECT)
    autorizacion = models.TextField(blank=True)  # obligatoria si entra al unificar otro mineral
    fecha_hora = models.DateTimeField(editable=False)
    usuario_registro = models.ForeignKey(Usuario, on_delete=models.PROTECT, editable=False)
    fecha_retiro = models.DateTimeField(null=True, editable=False)  # baja logica al quitarlo (D-22)
    usuario_retiro = models.ForeignKey(Usuario, null=True, on_delete=models.PROTECT,
                                       editable=False, related_name="+")

    class Meta:
        constraints = [models.UniqueConstraint(fields=["lote", "tipo_mineral"],
                                               condition=models.Q(fecha_retiro__isnull=True),
                                               name="lote_mineral_vigente_unico")]


class ParteLote(models.Model):
    lote = models.ForeignKey(LoteProceso, on_delete=models.PROTECT, related_name="partes")
    nombre = models.CharField(max_length=80)
    numerador = models.PositiveSmallIntegerField()
    denominador = models.PositiveSmallIntegerField()
    ruta = models.CharField(max_length=30, choices=Ruta.choices)


class RepartoIngreso(models.Model):       # porcion de un ingreso tardio en un lote dividido
    ingreso = models.ForeignKey(Ingreso, on_delete=models.PROTECT, related_name="repartos")
    parte = models.ForeignKey(ParteLote, on_delete=models.PROTECT)
    numerador = models.PositiveSmallIntegerField()
    denominador = models.PositiveSmallIntegerField()


class PasoEtapa(models.Model):
    lote = models.ForeignKey(LoteProceso, on_delete=models.PROTECT, related_name="pasos")
    parte = models.ForeignKey(ParteLote, null=True, on_delete=models.PROTECT)
    ingreso_tardio = models.ForeignKey(Ingreso, null=True, on_delete=models.PROTECT)  # secado propio
    etapa = models.ForeignKey(EtapaProceso, on_delete=models.PROTECT)
    fecha_hora = models.DateTimeField()
    usuario_registro = models.ForeignKey(Usuario, on_delete=models.PROTECT, editable=False)
    observacion = models.TextField(blank=True)
    horas_molienda = models.DecimalField(max_digits=6, decimal_places=2, null=True)


class Bigbag(models.Model):
    lote = models.ForeignKey(LoteProceso, on_delete=models.PROTECT, related_name="bigbags")
    parte = models.ForeignKey(ParteLote, null=True, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    peso_aproximado_tn = models.DecimalField(max_digits=6, decimal_places=2)
    recalculado = models.BooleanField(default=False)
    fecha_hora = models.DateTimeField(editable=False)
    usuario_registro = models.ForeignKey(Usuario, on_delete=models.PROTECT, editable=False)
```

`Ruta` es un `TextChoices` con tres valores —`ZARANDEO_ENSACADO`, `MOLIENDA_ENSACADO` y
`ZARANDEO_MOLIENDA_ENSACADO`, con los nombres en pantalla «Zaranda», «Molido» y «Zarandeado y
molido» (D-21)—, y una constante del módulo asocia a cada ruta sus etapas en orden. El secado no
forma parte de ninguna ruta porque es común a todo el lote.

Decisiones no obvias:

- **El vínculo ingreso–lote sigue en `INGRESO.id_lote`**, no en una tabla intermedia. Un ingreso
  pertenece a un lote como máximo (RN-M06-01). El ingreso tardío se distingue porque su asignación
  ocurre después de `fecha_inicio_recorrido`; no hace falta un campo propio.
- **Las fracciones se guardan como numerador y denominador**, no como decimal (RNF-M06-11). Con
  decimales, tres tercios suman 0,999999 y una división correcta se rechazaría. El servicio usa
  `fractions.Fraction` para sumar y exige que el resultado sea exactamente 1. Los porcentajes que
  escriba el usuario se convierten a fracción en el serializer.
- **Las toneladas aproximadas de cada parte no se almacenan.** Se calculan al consultar como
  fracción por las toneladas netas del lote (RN-M06-17). Guardarlas haría que una corrección o una
  anulación en M03 dejara la estimación desactualizada sin que nadie lo notara.
- **Unicidad del paso con restricciones condicionales.** Un paso pertenece al lote —el secado
  común—, a una parte o al secado propio de un ingreso tardío. Tres `UniqueConstraint` con condición
  garantizan una sola fila por combinación (RN-M06-07); el servicio lo comprueba antes, para
  devolver el mensaje literal.
- **El peso aproximado del bigbag se calcula en el servicio**: toneladas pendientes de ensacar del
  lote o la parte entre la cantidad de bigbags. Si el usuario lo recalcula, se guarda su valor y
  `recalculado` queda en verdadero, para que el resumen distinga lo estimado por el sistema de lo
  observado.
- **`ETAPA_PROCESO` se carga en una migración de datos**, no por el admin. Es un catálogo cerrado
  (RN-M06-09): si se administrara, alguien añadiría una quinta etapa y los recorridos anteriores
  dejarían de ser comparables.
- **`on_delete=PROTECT` en todas las claves foráneas.** Nada de lo que participa en un recorrido
  puede borrarse.

### Servicio: la comprobación de orden

Registrar una etapa exige que la anterior de la ruta esté registrada para ese lote o esa parte. La
forma directa —contar los pasos y comparar con la posición de la etapa— funciona mientras no haya
huecos, y los huecos son exactamente lo que la regla debe impedir. La comprobación correcta busca la
etapa inmediatamente anterior en la ruta y consulta si existe su paso. Para la primera etapa después
del secado, la anterior es el secado común del lote.

`registrar_etapa()` guarda la ruta en el mismo paso en que se registra la primera etapa posterior al
secado (RN-M06-15): la ruta no existe como dato separado antes de que se use.

### División y reparto

`dividir_lote()` comprueba, en este orden: que el lote no esté dividido, que ninguna parte haya
avanzado, que haya de dos a seis partes con nombre distinto y que las fracciones sumen 1. Si el lote
ya tenía ruta sin dividir, no puede dividirse: ya avanzó por ella.

El secado de un ingreso tardío en un lote dividido crea a la vez el `PasoEtapa` del secado propio y
sus `RepartoIngreso`. El serializer recibe las fracciones propuestas por la interfaz, que parte de
las del lote (DR-20), y el servicio repite la comprobación de suma.

### Retiro de ingresos

`retirar_ingreso()` comprueba que ninguna parte del lote tenga registrado zarandeo o molienda —o, si
el ingreso tiene secado propio, que ninguna de sus partes haya empezado su ruta— y que un lote
`EN_RECORRIDO` conserve al menos un ingreso (RN-M06-04). Pone en nulo el `id_lote` del ingreso y no
borra ningún paso: el secado del lote, y el secado propio del ingreso tardío con su reparto, quedan
como hecho registrado y el retiro en auditoría (D-07). Las estimaciones de las partes no requieren
ajuste, porque se calculan sobre los ingresos que pertenecen al lote al consultarse (RN-M06-24). El
traslado a otro lote es el mismo retiro seguido de una asignación, dentro de una transacción.

### Composición, trazabilidad y resumen

El detalle del lote necesita el número de ingresos y la suma de sus pesos netos. Se resuelve con una
consulta agregada sobre `INGRESO`, no recorriendo los ingresos en Python (RNF-M06-02). La suma
excluye los ingresos anulados (RN-M06-03): un ingreso anulado no aporta toneladas, aunque su vínculo
con el lote se conserve si ya inició el recorrido.

La asignación filtra por `estado="REGISTRADO"` y no por «distinto de anulado» (RN-M06-13). Con el
segundo criterio, un ingreso En proceso —sin peso neto— entraría al lote y su suma trataría el nulo
como ausencia.

`GET /api/v1/ingresos/{id}/trazabilidad/` vive en las rutas de ingresos, pero lo resuelve este
módulo. La respuesta trae las etapas de la ruta del lote o de cada parte, la unión de esas etapas como
denominador (RN-M06-22) y, si el ingreso fue tardío, su secado propio. Sin ruta decidida, la respuesta
no trae proporción.

`GET /api/v1/lotes/{id}/resumen/` calcula los pendientes y el resumen de cierre en una consulta
agregada: toneladas, bigbags, ensacado aproximado, diferencia, horas de molienda y toneladas por hora
por parte, y duraciones. El mismo cálculo de pendientes lo usa `cerrar_lote()`, para que la pantalla
y el servidor no puedan discrepar sobre si el lote está listo.

### Integración con M03

M03 invoca `retirar_ingreso()` de este servicio cuando anula un ingreso de un lote Abierto
(RS-M06-27), y lee el tipo de mineral del lote cuando corrige un ingreso. M06 no escribe sobre el
ingreso más allá de su `id_lote`.

## Frontend (Angular)

**Feature:** `features/trazabilidad/`

- El recorrido se presenta como una secuencia visible de las etapas de la ruta, por parte cuando el
  lote está dividido, distinguiendo completadas de pendientes sin depender solo del color
  (RNF-M06-08).
- La interfaz ofrece **únicamente la etapa que corresponde registrar**, y la elección de la ruta
  justo después del secado (RNF-M06-07).
- La división muestra, mientras el usuario escribe, la suma de las fracciones y lo que falta o sobra
  para la unidad (RNF-M06-10). Acepta fracciones como 1/3 o porcentajes.
- Las toneladas aproximadas, el peso de los bigbags y la diferencia del resumen llevan una marca de
  estimación visible (RNF-M06-09).
- El registro del paso se completa en tres toques desde el detalle del lote (RNF-M06-06), porque se
  hace en planta y con el teléfono.
- El cierre con destino solo se ofrece al Administrador, y solo cuando el resumen no tiene
  pendientes; la restricción vale igual en el servidor.

## Riesgo de implementación identificado

**El riesgo principal es que las estimaciones se filtren a los totales.** Las toneladas aproximadas
por parte y el peso de los bigbags son útiles en planta, y la tentación es mostrarlos junto a las
toneladas registradas o sumarlos en algún reporte. Si eso ocurre, una estimación hecha a la vista
pasa a parecer un dato de balanza. La prueba que lo detecta divide un lote, asocia bigbags con un
peso recalculado distinto del estimado y comprueba que el total del lote y el consolidado de M08 no
cambian.

**Riesgo secundario: que la trazabilidad se calcule sobre las cuatro etapas.** Es el cálculo de la
versión anterior y el más fácil de escribir. Con él, toda carga que no pasa por molienda aparecería
incompleta. La prueba registra un lote con ruta de zarandeo y ensacado, completa sus tres etapas
—secado, zarandeo y ensacado— y espera proceso completo.

**Tercer riesgo: que el lote deje de corresponder a la operación real.** Todo el módulo descansa en
que el mineral se procesa por cargas. La versión 2 incorpora la forma en que la planta describió su
operación —rutas, división a la vista, volquetes tardíos—, pero conviene acompañar una jornada antes
de implementar y verificar que el personal reconoce las cargas, sus partes y su cierre.

## Dependencias

| Depende de | Para |
|---|---|
| M01 | Autenticación y atribución de cada operación |
| M02 | Los tipos de mineral del lote |
| M03 | Los ingresos que componen el lote, con su peso y su estado |
| M09 | Registro de los eventos del lote |

| Es requerido por | Para |
|---|---|
| M03 | La lista de tipos de mineral del lote al corregir un ingreso, y el retiro del ingreso anulado de un lote Abierto |
| M07 | Mostrar el recorrido del proceso en el detalle de un ingreso |

## Pendientes que afectan a este módulo

| Pendiente | Efecto |
|---|---|
| Valores del catálogo de tipos de mineral (DR-03) | Sin ellos no puede abrirse ningún lote |
