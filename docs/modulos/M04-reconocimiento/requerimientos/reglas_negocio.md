# Reglas de negocio — M04 Reconocimiento automático del ticket

> Ubicación en el código: `apps/reconocimiento/models/` (invariantes de la entidad),
> `apps/reconocimiento/services/` (proceso de reconocimiento) y `apps/reconocimiento/motores/` (los
> adaptadores concretos). Ninguna de estas reglas vive en `views/` ni en un componente Angular (D-08).

| Código | Regla | Consecuencia si se viola |
|---|---|---|
| RN-M04-01 | El resultado del reconocimiento es una propuesta y no se persiste como dato del ingreso sin confirmación del usuario | Un error de lectura se convertiría en dato oficial sin que nadie lo revisara |
| RN-M04-02 | El valor reconocido y el valor confirmado se conservan como datos separados | Se perdería la distinción entre lo que leyó el motor y lo que corrigió la persona, y no habría forma de saber si el reconocimiento funciona |
| RN-M04-03 | Un campo sin lectura queda vacío; el sistema no propone un valor estimado en su lugar | El usuario aceptaría como lectura un valor que nadie leyó, y el dato sería inventado con apariencia de comprobado |
| RN-M04-04 | Cada reconocimiento registra el motor y su versión | Dos ingresos procesados por motores distintos parecerían comparables sin serlo |
| RN-M04-05 | El motor y su versión no cambian durante la ventana de operación controlada (D-16) | Los resultados de un mismo periodo provendrían de sistemas distintos |
| RN-M04-06 | La confianza es un valor entre 0 y 1; un campo sin lectura no tiene confianza, y no se le asigna cero | Un cero se confundiría con una lectura de calidad nula, que es un hecho distinto de no haber leído |
| RN-M04-07 | El fallo del motor no impide registrar el ingreso | La planta quedaría detenida por la indisponibilidad de un componente auxiliar |
| RN-M04-08 | El código de negocio no depende de un motor concreto, sino de la interfaz `ReconocedorTicket` | Cambiar de motor obligaría a modificar el servicio de registro y a rehacer sus pruebas |
| RN-M04-09 | Un ingreso tiene como máximo un reconocimiento | Habría varias lecturas candidatas para el mismo ticket y ninguna sería la de referencia |
| RN-M04-10 | El indicador de corrección se deriva de comparar los dos valores y no se acepta desde el cliente | El cliente podría declarar que no hubo corrección cuando sí la hubo |

## Nota sobre RN-M04-02

Es la regla que da sentido al módulo. Guardar un solo valor por campo —el confirmado— haría el
sistema más simple y dejaría el reconocimiento sin forma de evaluarse: no se sabría en qué campos
acierta, ni si conviene cambiar de motor, ni si el umbral está bien puesto. La comparación entre
ambos valores es la única evidencia de que la lectura automática aporta algo.

## Nota sobre RN-M04-03 y RN-M04-06

Las dos distinguen «no hay dato» de «hay un dato malo», que son situaciones distintas y exigen
respuestas distintas. Un campo vacío obliga al usuario a escribirlo; un campo con lectura dudosa
solo le pide verificarlo. Rellenar los vacíos con ceros o con estimaciones borra esa diferencia y
convierte un hueco visible en un error silencioso.

## Nota sobre RN-M04-07 y RN-M04-08

El reconocimiento es una ayuda, no un requisito del registro. Si el motor está caído, el supervisor
escribe los seis datos y el ingreso se registra igual: lo único que se pierde es tiempo. Por eso el
adaptador del motor vive aislado detrás de una interfaz y su fallo se trata como un caso previsto,
no como un error del sistema.
