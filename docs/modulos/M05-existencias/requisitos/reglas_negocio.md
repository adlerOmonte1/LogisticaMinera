# Reglas de negocio — M05 Existencias

> Ubicación en el código: `apps/existencias/models.py` y `apps/existencias/services.py`.

| Código | Regla | Consecuencia si se viola |
|---|---|---|
| RN-M05-01 | El saldo de un producto es siempre la suma algebraica de sus movimientos no anulados; nunca un valor independiente | El stock dejaría de ser trazable a sus documentos fuente |
| RN-M05-02 | El saldo no se escribe directamente por ninguna vía | Se podría "cuadrar" el inventario sin dejar rastro |
| RN-M05-03 | Todo movimiento de stock proviene de un ingreso, una salida o un ajuste; no existen movimientos huérfanos | Un movimiento sin origen sería inexplicable ante una auditoría |
| RN-M05-04 | Las cantidades de los movimientos son siempre positivas; el signo lo determina el tipo | Errores de signo en cálculos agregados |
| RN-M05-05 | El saldo de un producto puede ser negativo si las salidas superan a las entradas registradas | Forzar saldo no negativo obligaría a inventar ingresos (ver RN-M04-06) |
| RN-M05-06 | Un ajuste registra la diferencia, no el valor final medido | Se perdería la magnitud de la desviación, que es el indicador I4 |
| RN-M05-07 | Un ajuste exige motivo y solo lo registra el rol Administrador | Las desviaciones podrían normalizarse sin responsable identificable |
| RN-M05-08 | Un ajuste de diferencia cero no genera movimiento | Se ensuciaría el kardex con asientos sin efecto |
| RN-M05-09 | La anulación de un documento fuente genera un movimiento de reversión; el movimiento original permanece en el kardex | Se perdería la evidencia de que hubo una corrección |

## Nota sobre RN-M05-05

Un saldo negativo es un dato válido, no un error del sistema. Indica que se despachó más de lo que se registró como ingresado, y su magnitud es información valiosa: señala precisamente la brecha de cobertura de registro que el indicador I2 mide. Ocultarlo forzando el saldo a cero destruiría esa evidencia.

## Nota sobre RN-M05-06

Registrar la diferencia en lugar del valor final es lo que permite que el kardex siga siendo una cadena continua de asientos. Si un ajuste sobrescribiera el saldo, el kardex tendría un salto inexplicable y la trazabilidad se rompería en ese punto.
