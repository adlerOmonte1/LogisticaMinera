# Historias de usuario — M04 Reconocimiento automático del ticket

**RF asociado:** RF02 · **Historias:** 2

> Módulo que convierte la fotografía del ticket de balanza en seis datos con su nivel de confianza.
> Entrega una propuesta, nunca un dato definitivo: quien decide qué se guarda es el usuario a través
> de M03. El motor concreto queda detrás de la interfaz `ReconocedorTicket`, de modo que sustituirlo
> no afecta a ningún otro módulo.

---

## HU-M04-01 — Reconocimiento automático de los datos del ticket

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M04-01 |
| **Épica** | Reconocimiento automático del ticket |
| **Prioridad** | Crítica |

**Historia**

Como supervisor de planta, quiero que el sistema lea automáticamente los datos del ticket a partir
de su fotografía, para no transcribirlos a mano y terminar el registro en menos tiempo.

**Descripción**

El motor procesa la imagen y devuelve seis campos —placa, fecha, hora, peso bruto, tara y peso
neto—, cada uno con un nivel de confianza entre 0 y 1. Los campos cuya confianza queda por debajo
del umbral se presentan resaltados, para que el usuario los verifique antes de confirmar.

El resultado es una propuesta. Nada de lo que devuelve el motor se guarda como dato del ingreso
hasta que el usuario lo revisa y confirma. Al confirmarse el ingreso, el sistema conserva por
separado el valor que leyó el motor y el valor que quedó confirmado, junto con la confianza, el
identificador del motor y su versión.

Cuando el motor no logra leer un campo, el sistema deja ese campo vacío y editable. No propone un
valor aproximado: un dato inventado con apariencia de lectura es peor que un campo en blanco, porque
el usuario podría aceptarlo sin verificarlo.

**Detalles**
- Campos reconocidos: placa, fecha, hora, peso bruto, tara y peso neto.
- Confianza por campo: valor entre 0 y 1; vacía si no hubo lectura.
- Umbral de confianza: configurable, 0,80 por defecto.
- Motor y versión: se registran en cada reconocimiento y no cambian durante la operación.
- Un reconocimiento por ingreso.

**Criterios de aceptación**

> **CA01.** Dado que la imagen es legible, cuando el sistema la procesa, entonces presenta los seis
> campos precargados junto con su nivel de confianza.

> **CA02.** Dado que un campo tiene una confianza inferior al umbral, cuando se presentan los
> resultados, entonces el sistema lo resalta y muestra "Verifique este dato: lectura con baja
> confianza".

> **CA03.** Dado que el motor no logra leer un campo, cuando se presentan los resultados, entonces
> el sistema deja ese campo vacío y editable, sin proponer ningún valor.

> **CA04.** Dado que la imagen es ilegible o tiene un formato no admitido, cuando el sistema intenta
> procesarla, entonces muestra "No fue posible leer el ticket. Tome una nueva fotografía o ingrese
> los datos manualmente" y permite continuar con el registro manual.

> **CA05.** Dado que el motor no responde o excede el tiempo de espera, cuando el sistema intenta
> procesarla, entonces muestra "El reconocimiento no está disponible. Puede ingresar los datos
> manualmente" y permite continuar.

> **CA06.** Dado que el sistema obtiene un resultado, cuando lo presenta al usuario, entonces no ha
> persistido ninguno de esos valores como dato del ingreso.

> **CA07.** Dado que el usuario confirma el ingreso, cuando el sistema lo persiste, entonces guarda
> para cada uno de los seis campos el valor reconocido, el valor confirmado y la confianza, junto
> con el motor y su versión.

---

## HU-M04-02 — Consulta del dato reconocido frente al confirmado

| Campo | Descripción |
|:--|:--|
| **Identificador** | HU-M04-02 |
| **Épica** | Reconocimiento automático del ticket |
| **Prioridad** | Media |

**Historia**

Como administrativo, quiero ver qué leyó el sistema y qué se corrigió en un ingreso, para saber si
el reconocimiento está funcionando bien y en qué campos falla.

**Descripción**

La consulta muestra, campo por campo, el valor que propuso el motor, el que quedó confirmado, la
confianza de la lectura y si hubo corrección. Incluye el motor y la versión que procesaron la
imagen, porque un mismo ingreso leído por motores distintos no es comparable.

Es la vista que permite decidir si conviene cambiar de motor, ajustar el umbral o mejorar las
condiciones de la fotografía: si un campo concreto se corrige casi siempre, el problema está en ese
campo y no en el motor en conjunto.

**Detalles**
- Se consulta desde el detalle del ingreso.
- Campos visibles: nombre, valor reconocido, valor confirmado, confianza, si fue corregido.
- Cabecera: motor, versión, fecha de proceso y umbral vigente al procesar.
- Roles autorizados: Administrativo y Administrador.

**Criterios de aceptación**

> **CA01.** Dado que un ingreso tiene reconocimiento asociado, cuando el usuario consulta su
> detalle, entonces el sistema muestra los seis campos con su valor reconocido, su valor confirmado
> y su confianza.

> **CA02.** Dado que un campo fue corregido por el usuario, cuando se muestra la comparación,
> entonces el sistema lo señala como corregido.

> **CA03.** Dado que un ingreso se registró manualmente porque la imagen era ilegible, cuando el
> usuario consulta su detalle, entonces el sistema indica que no hubo reconocimiento y muestra el
> motivo.

> **CA04.** Dado que el usuario tiene rol de Supervisor de planta, cuando intenta consultar la
> comparación, entonces el sistema rechaza la operación mostrando "Acción no autorizada".

> **CA05.** Dado que se consulta un reconocimiento, cuando el sistema lo presenta, entonces muestra
> el motor y la versión que lo produjeron.
