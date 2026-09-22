# Notas de implementación — M06 Trazabilidad del proceso

## Backend (Django)

**App:** `apps/trazabilidad/` — no existe todavía; se crea en la fase de preparación del backend.

### Estructura

```
apps/trazabilidad/
├── models/          LOTE_PROCESO, ETAPA_PROCESO, PASO_ETAPA
├── migrations/      incluye la carga inicial de las cuatro etapas
├── services/        ciclo de vida del lote y registro de etapas
├── repositories/    composicion del lote y recorrido de un ingreso
├── serializers/  views/  permissions.py  filters.py  urls.py  tests/
```

### Modelo

```python
class LoteProceso(models.Model):
    codigo = models.CharField(max_length=20, unique=True, editable=False)
    tipo_mineral = models.ForeignKey(TipoMineral, on_delete=models.PROTECT)
    fecha_apertura = models.DateField()
    fecha_cierre = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=10, choices=ESTADOS, default=ABIERTO)


class PasoEtapa(models.Model):
    lote = models.ForeignKey(LoteProceso, on_delete=models.PROTECT, related_name="pasos")
    etapa = models.ForeignKey(EtapaProceso, on_delete=models.PROTECT)
    fecha_hora = models.DateTimeField()
    usuario_registro = models.ForeignKey(Usuario, on_delete=models.PROTECT, editable=False)
    observacion = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["lote", "etapa"], name="uq_paso_lote_etapa"),
        ]
```

Decisiones no obvias:

- **El vínculo ingreso–lote vive en `INGRESO.id_lote`, no en una tabla intermedia.** Un ingreso
  pertenece a un lote como máximo (RN-M06-01), y una tabla intermedia permitiría insertar dos filas
  para el mismo ingreso sin que ninguna restricción lo impidiera.
- **`UniqueConstraint` sobre lote y etapa.** Es la garantía en la base de RN-M06-07; el servicio
  también lo comprueba, para devolver el mensaje literal en lugar de un error de integridad.
- **`ETAPA_PROCESO` se carga en una migración de datos**, no por el admin. Es un catálogo cerrado
  (RN-M06-09): si se administrara, alguien añadiría una quinta etapa y los recorridos anteriores
  dejarían de ser comparables.
- **`on_delete=PROTECT` también aquí.** Nada de lo que participa en un recorrido puede borrarse.
- **El orden de las etapas es el campo `orden`, no el identificador.** Comparar por identificador
  funcionaría hoy y se rompería si alguna vez se recarga el catálogo.

### Servicio: la comprobación de orden

Registrar una etapa exige que todas las anteriores estén registradas para ese lote. La forma directa
—contar los pasos y comparar con el orden de la etapa— funciona mientras no haya huecos, y los
huecos son exactamente lo que la regla debe impedir. La comprobación correcta consulta si existe el
paso por la etapa inmediatamente anterior.

### Composición del lote

El detalle del lote necesita el número de ingresos y la suma de sus pesos netos. Se resuelve con una
consulta agregada sobre `INGRESO`, no recorriendo los ingresos en Python (RNF-M06-02). La suma
excluye los ingresos anulados (RN-M06-03): un ingreso retirado del histórico no aporta toneladas,
aunque su vínculo con el lote se conserve.

Que la suma se calcule y no se almacene es deliberado. Un total guardado en el lote quedaría
desactualizado en cuanto un ingreso se anulara, y habría que recordarlo desde M03.

### Consulta de trazabilidad

`GET /api/v1/ingresos/{id}/trazabilidad/` vive en las rutas de ingresos pero lo resuelve este
módulo: el ingreso es el punto de entrada natural de la pregunta, y el recorrido es conocimiento de
M06. La respuesta siempre trae las cuatro etapas, marcadas como recorridas o pendientes; nunca una
lista parcial, porque la pregunta es cuántas de las cuatro se completaron.

## Frontend (Angular)

**Feature:** `features/trazabilidad/`

- El recorrido se presenta como una secuencia visible de cuatro pasos, distinguiendo completados de
  pendientes sin depender solo del color (RNF-M06-08).
- La interfaz ofrece **únicamente la etapa que corresponde registrar** (RNF-M06-07). Las posteriores
  no se muestran como disponibles: la restricción se percibe como guía y no como rechazo.
- El registro del paso se completa en tres toques desde el detalle del lote (RNF-M06-06), porque se
  hace en planta y con el teléfono.
- La composición del lote es un componente de `ui/` sin estado; la selección de ingresos, una página
  con su propio estado en `pages/`.

## Riesgo de implementación identificado

**El riesgo principal es que el lote deje de corresponder a la operación real de la planta.**

Todo este módulo descansa en un supuesto: que el mineral se procesa por cargas y no volquete por
volquete. Si la planta trabaja de otra manera —por ejemplo, con flujo continuo, donde el mineral
entra al secado según llega—, el lote se convierte en un registro administrativo que alguien rellena
después, con fechas aproximadas, y el recorrido deja de describir nada.

No es un riesgo que una prueba detecte: el sistema funcionaría correctamente y los datos serían
inútiles. La comprobación es de campo, y debe hacerse antes de implementar: acompañar una jornada y
verificar si existe algo que el personal reconozca como «una carga», con principio y fin. Si no
existe, el vínculo directo entre ingreso y etapa es más simple y más fiel, y este módulo se
simplifica en consecuencia.

**Riesgo secundario:** que el total de toneladas del lote se almacene en lugar de calcularse, por
rendimiento. Quedaría desactualizado en la primera anulación, y el error sería silencioso porque
nadie recalcula un total que ya está escrito.

## Dependencias

| Depende de | Para |
|---|---|
| M01 | Autenticación y atribución del registro de cada etapa |
| M02 | El tipo de mineral del lote |
| M03 | Los ingresos que componen el lote, con su peso y su estado |
| M09 | Registro de los eventos de apertura, cierre y paso por etapa |

| Es requerido por | Para |
|---|---|
| M07 | Mostrar el recorrido del proceso en el detalle de un ingreso |

## Pendientes que afectan a este módulo

| Pendiente | Efecto |
|---|---|
| Forma real de agrupar el mineral en cancha | Decide si el lote es la abstracción correcta o si procede el vínculo directo. Debe verificarse en planta antes de implementar |
| Valores del catálogo de tipos de mineral (DR-03) | Sin ellos no puede abrirse ningún lote |
| Criterio de cierre de un lote en la operación real | Define si el cierre lo decide el Administrativo o responde a un hecho de planta, como completar una tonelada objetivo |
