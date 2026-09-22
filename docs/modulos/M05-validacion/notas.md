# Notas de implementación — M05 Validación automática de consistencia

## Backend (Django)

**App:** `apps/validacion/` — no existe todavía; se crea en la fase de preparación del backend.

### Estructura

```
apps/validacion/
├── models/          RESULTADO_VALIDACION
├── reglas/          una clase por regla: v1_pesos.py, v2_tara.py, v3_placa.py, v4_capacidad.py, v5_fecha.py
├── services/        composicion de las reglas y persistencia del resultado
├── repositories/    lectura de los resultados de un ingreso
├── serializers/  views/  permissions.py  urls.py  tests/
```

### La regla como unidad

```python
class Regla(Protocol):
    codigo: str          # "V1"
    bloqueante: bool
    campo: str           # campo al que se asocia el mensaje
    mensaje: str         # literal, con marcadores como {placa}

    def datos_completos(self, datos: DatosTicket) -> bool: ...
    def cumple(self, datos: DatosTicket) -> bool: ...
```

Cada regla vive en su archivo, no conoce a las demás y no accede a la base: recibe los datos ya
reunidos, incluida la capacidad del vehículo. Esto hace que cada una se pruebe sin base de datos ni
petición HTTP (RNF-M05-07), y que añadir una sea crear una clase y registrarla (RNF-M05-06).

El servicio recorre la colección registrada y **no nombra ninguna regla concreta**. Un `if` por
regla dentro del servicio anularía esa propiedad y es el error más probable al implementar.

### Composición y resultado

```python
class ValidadorConsistencia:
    def __init__(self, reglas: list[Regla]):
        self._reglas = reglas

    def validar(self, datos: DatosTicket) -> list[Inconsistencia]:
        return [
            Inconsistencia(r.codigo, r.campo, r.mensaje.format(**datos.marcadores), r.bloqueante)
            for r in self._reglas
            if r.datos_completos(datos) and not r.cumple(datos)
        ]
```

El resultado es una lista, nunca una excepción: la primera inconsistencia no interrumpe la
evaluación (RN-M05-04). Quien decide si la operación continúa es M03.

### Parámetros

La tolerancia de V1 y el patrón de placa de V3 se leen de la configuración (RNF-M05-08), no se
escriben en las clases. La capacidad de V4 llega en los datos, leída del catálogo por el servicio
de registro: la regla no consulta la base.

### Persistencia del resultado

`RESULTADO_VALIDACION` guarda una fila por regla evaluada, con su momento —sobre los datos
propuestos o sobre los confirmados—, si cumplió, el detalle con los valores concretos y la
resolución. Se escribe dentro de la transacción del ingreso: un resultado sin ingreso no describe
nada.

El detalle conserva los valores que motivaron el incumplimiento, no solo el hecho de que ocurrió.
Saber que V1 falló sirve de poco; saber que el ticket decía 28,50 cuando bruto menos tara daba 28,30
permite entender qué pasó.

## Frontend (Angular)

**Feature:** `features/ingresos/` — la validación no tiene pantalla propia.

- Las inconsistencias se muestran junto al campo afectado, con el **mensaje literal** que devuelve el
  servidor (RN-M05-08). La interfaz no los reformula ni los acorta.
- Las bloqueantes y la advertencia de V4 se distinguen visualmente: las primeras impiden confirmar,
  la segunda habilita el campo de justificación.
- Puede replicarse la comprobación de pesos en el formulario para dar respuesta inmediata, pero es
  una ayuda visual: la decisión siempre la toma el servidor (D-08). Si ambas discrepan, manda el
  servidor.

## Riesgo de implementación identificado

**El riesgo principal es que la validación del cliente termine sustituyendo a la del servidor.**

La tentación es evidente: replicar las cinco reglas en Angular da una experiencia más fluida, y
entonces alguien observa que el servidor «ya recibe datos validados» y omite la segunda evaluación
por eficiencia. A partir de ese momento cualquier petición que no pase por el formulario entra sin
validar.

La prueba obvia —registrar desde la interfaz y comprobar que rechaza— no lo detecta, porque pasa por
el formulario. La prueba que sí lo detecta envía la petición directamente a la API con datos
incoherentes y espera el rechazo con el mensaje literal (HU-M05-01 CA07). Debe existir una por cada
regla bloqueante.

**Riesgo secundario:** que las reglas se evalúen solo sobre los datos propuestos y no sobre los
confirmados, porque en el camino feliz ambos coinciden. El error solo aparece cuando el usuario
corrige un dato e introduce una incoherencia nueva, que es justamente el caso que RN-M05-05 protege.

## Dependencias

| Depende de | Para |
|---|---|
| M01 | Autenticación y atribución de la consulta |
| M02 | La capacidad declarada del vehículo, que necesita V4 |
| M03 | Los datos a evaluar y la transacción en que se persiste el resultado |
| M09 | Registro del evento de validación |

| Es requerido por | Para |
|---|---|
| M03 | Evaluar los datos propuestos y los confirmados antes de persistir |

## Pendientes que afectan a este módulo

| Pendiente | Efecto |
|---|---|
| Tolerancia de V1, a confirmar con la empresa | Es configuración, de modo que no bloquea la implementación, pero sí el cierre del conjunto de prueba |
| Patrón de placa peruana vigente | Define la expresión regular de V3; conviene contrastarla con las placas reales del catálogo |
| Conjunto de inconsistencias sembradas | Necesario para verificar RNF-M05-02 y RNF-M05-03 |
