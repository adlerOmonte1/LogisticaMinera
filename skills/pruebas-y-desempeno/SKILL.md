---
name: pruebas-y-desempeno
description: Escribe las pruebas del sistema de control de producción y existencias — pruebas unitarias y de integración con pytest-django derivadas de los criterios de aceptación, y el protocolo de pruebas de carga con JMeter que produce la evidencia de eficiencia de desempeño ISO/IEC 25010:2023. Úsala al escribir o revisar pruebas, al preparar el plan de pruebas o el acta, y cuando se mencionen tests, cobertura, casos de prueba CP, carga, rendimiento o JMeter.
---

# Pruebas y desempeño

Carga antes `contexto-tesis`. Fuente: los `no_funcionales.md` de cada módulo y `docs/03-pruebas/`
(pendiente de crear).

Las pruebas de este proyecto no solo protegen el código: **producen la evidencia** de la variable
independiente. El acta de pruebas funcionales y el protocolo de carga son entregables de la semana 8.

## Herramientas fijadas

`pytest` + `pytest-django` + `coverage.py` para funcionales. **Apache JMeter** para carga — no Locust:
los `no_funcionales.md` de todos los módulos ya declaran «Prueba de carga JMeter (semana 8)» como
método de verificación, y cambiar la herramienta obliga a reescribir esa columna en siete archivos y
a explicar el cambio en el capítulo de metodología.

## Cada criterio de aceptación es un caso de prueba

Nomenclatura: `CP-HU-M{nn}-{nn}-{nn}`, uno por criterio. La cadena de trazabilidad completa que se
defiende en sustentación es:

```
Indicador de la tesis -> RF -> Módulo -> HU -> Caso de prueba -> Commit
```

Estructura de una prueba, espejo del criterio:

```python
def test_ca04_tara_mayor_que_bruto_es_rechazada(...):
    # Dado que la tara ingresada es mayor o igual que el peso bruto
    # cuando el usuario intenta guardar
    # entonces el sistema rechaza mostrando "La tara debe ser menor que el peso bruto"
```

**El mensaje se verifica por igualdad exacta**, no con `in` ni con una expresión regular laxa. Los
criterios de aceptación fijan el texto literal precisamente para que la prueba pueda compararlo así.
Si una prueba falla porque el texto cambió, la respuesta correcta es revisar cuál de los dos está mal
—historia o código—, nunca relajar la comparación.

## Qué se prueba en cada capa

| Capa | Qué se prueba | Con qué |
|---|---|---|
| `models.py` | Cada RN del módulo, incluidos los límites | Pruebas unitarias, sin base cuando se pueda |
| `services.py` | El caso de uso completo, con sus dependencias sustituidas | Generador de correlativo y reloj deterministas |
| `selectors.py` | Saldos, kardex y cortes de fecha | Datos de prueba con fechas explícitas |
| `views.py` | Códigos HTTP, cuerpo de error uniforme, permisos por rol | Cliente de API |
| Angular | Cálculo del neto, validaciones, borrador en IndexedDB | Pruebas de componente |

La inyección de dependencias que exige `solid-proyecto` existe para esto: un servicio que llama a
`timezone.now()` internamente **no se puede probar** contra los límites de HU-M03-02 (72 horas,
30 días). Inyecta el reloj y el generador de correlativo.

## Pruebas obligatorias por su consecuencia sobre la tesis

Estas no son opcionales aunque el tiempo apriete; cada una protege un indicador:

| Prueba | Protege |
|---|---|
| `hora_pesaje` y `hora_registro` se persisten como valores distintos | I1 |
| Un ingreso offline conserva la hora de captura local, no la de sincronización | I1 |
| Dos clientes sincronizando a la vez no producen correlativos duplicados | Unidad de análisis |
| Reenviar un lote no duplica ingresos | Producción declarada |
| El saldo final del kardex coincide con la consulta de existencias | I3, I4 |
| El stock a fecha de corte usa la fecha del movimiento, no la de registro | I4 |
| Un ingreso anulado se excluye de totales pero aparece en el detalle | I6, auditabilidad |
| Cada operación restringida rechaza al rol no autorizado desde el servidor | I2, no repudio |
| El peso neto del servidor es siempre bruto − tara | RNF-M03-07 |

## Cobertura

`coverage.py` sobre `models.py` y `services.py` en primer lugar: son las capas donde viven las reglas.
Una cobertura alta en `serializers.py` y baja en `models.py` es una cobertura engañosa. El dato que
alimenta el indicador de funcionalidad es el **porcentaje de requerimientos funcionales cumplidos**,
que se calcula sobre los RF verificados por prueba, no sobre las líneas ejecutadas.

## Protocolo de carga (semana 8)

Se ejecuta en **preproducción**, no en producción: producción es donde se recolecta el postest y una
prueba de carga alteraría las condiciones de medición.

| RNF típico | Umbral | Condición de medición |
|---|---|---|
| Alta de ingreso | < 2 s | 20 usuarios concurrentes |
| Listado filtrado de un mes | < 3 s | 1000 ingresos en base |

**Todo umbral se mide con su carga declarada.** Un tiempo de respuesta sin volumen de datos ni
concurrencia declarados no es evidencia de nada. Los datos sintéticos deben reproducir la
distribución real: ingresos concentrados en las horas de llegada de volquetes, no repartidos de forma
uniforme.

Registra: herramienta y versión, hardware, volumen de datos, número de usuarios virtuales, duración,
y percentiles p50/p95/p99 — no solo la media, que oculta las colas.

## Verificaciones que no son automatizables

Algunos RNF se verifican por observación y hay que planificarlas, no improvisarlas:

- Formulario completable en **menos de 90 segundos** por un usuario capacitado: observación
  cronometrada en campo.
- Operable en pantalla de **5 pulgadas** sin desplazamiento horizontal: inspección en dispositivo real.
- Los datos **no se pierden** al caerse la conexión: activar modo avión a media captura.

## Verificación

- [ ] Cada criterio de aceptación tiene su `CP-*` correspondiente.
- [ ] Los mensajes se comparan por igualdad exacta.
- [ ] Las nueve pruebas de la tabla de indicadores existen y pasan.
- [ ] Las pruebas de carga corren en preproducción y quedan registradas con su condición de medición.
- [ ] Las verificaciones manuales están planificadas con fecha, no pendientes de improvisación.
