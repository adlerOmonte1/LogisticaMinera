# Plan de ejecución — Laboratorio local de reconocimiento manuscrito

| Campo | Valor |
|---|---|
| Alcance | Medir en local la capacidad de leer **Peso**, **Placa** y **Día, Mes, Año** del ticket de la Balanza |
| Equipo | Ordenador del implementador: RTX 5080 (16 GB), CUDA 13.x, `uv` 0.13 |
| Paso del plan que atiende | 7.3 de F7, piloto de motores (D-12, D-15) |
| Estado | Etapa local cerrada (L0 a L7) el 04/11/2026; resultados y documentación en [README.md](README.md). Laboratorio fuera de `backend/` y de `docs/` hasta el saneamiento |

El ticket lo emite la Balanza, un agente externo, y su formato no cambia (DR-09). De él solo interesan
cinco zonas manuscritas. «Recibí», «La suma de», «Concepto», el número y las firmas sirven a la Balanza
y **no se leen**.

El laboratorio tiene tres etapas, en este orden:

1. **Local (L0 a L7):** medir la capacidad con las 30 fotos, sin tocar el sistema.
2. **Saneamiento (S1 a S5):** llevar al backend lo que funcionó, como un adaptador de `ReconocedorTicket`.
3. **Documentación (D1 a D4):** registrar las decisiones que resultaron.

---

## Etapa local

### L0 — Entorno

Se usa Python 3.12, la misma versión del backend y del CI, en un entorno propio del laboratorio.
`.venv/` ya está excluido de git.

```bash
cd laboratorio/ocr-manuscrito
uv venv --python 3.12 .venv
uv pip install --python .venv/Scripts/python.exe torch torchvision --index-url https://download.pytorch.org/whl/cu128
uv pip install --python .venv/Scripts/python.exe -r requirements.txt
.venv/Scripts/python.exe -c "import torch; print(torch.__version__, torch.cuda.get_device_name(0))"
```

- La serie RTX 50 exige PyTorch 2.7 o superior con CUDA 12.8 o superior. Una versión anterior no reconoce la tarjeta.
- La primera ejecución descarga los modelos de Hugging Face a la caché del usuario:
  `microsoft/trocr-small-handwritten` (unos 250 MB) y `microsoft/trocr-base-handwritten` (unos 1,3 GB).

**Hecho cuando:** el comando de verificación imprime el nombre de la tarjeta.

### L1 — Aprovisionamiento de las imágenes

Las fotos se colocan en `datos/originales/`. Toda la carpeta `datos/` está excluida de git, porque los
tickets contienen nombres de personas («Recibí»).

| Regla | Motivo |
|---|---|
| Nombre `T001.jpg` a `T030.jpg`, en cualquier orden | El nombre no debe revelar la placa ni el peso |
| Sin recortar, rotar, filtrar ni editar | El sistema recibirá la foto tal como sale de la cámara |
| Preferir el archivo original del teléfono (cable o nube en tamaño original) | WhatsApp reduce la foto a unos 720 × 1280 px y la comprime |
| Si solo existe la versión de WhatsApp, se usa y se anota | Es el peor caso: si funciona ahí, funciona con el original |

Junto a las fotos va `datos/inventario.csv`, separado por punto y coma (plantilla en `plantillas/`):

```
archivo;origen;ticket_no;duplicado_de;usable;escritor;observacion
T001.jpg;whatsapp;005853?;;si;A;Ticket inclinado, ocupa un cuarto de la foto, fondo con textura
```

- `origen` toma los valores `original` o `whatsapp`.
- `ticket_no` es el número impreso en rojo. Dos fotos del mismo ticket van siempre al mismo grupo en L3.
- `duplicado_de` marca las copias exactas del mismo archivo; esas filas llevan `usable=no`.
- `usable=no` también para las fotos con dos tickets.
- `escritor`: A para la letra cursiva y B para las mayúsculas de imprenta.
- `observacion` registra lo que pueda explicar un fallo: sombra, inclinación, desenfoque, reflejo, ticket doblado o tinta corrida.

Las notas no llevan punto y coma, que es el separador del archivo.

**Hecho cuando:** hay 30 fotos con nombre normalizado y una fila de inventario por foto.

### L2 — Transcripción: el valor verdadero

Para cada foto, una persona transcribe **lo que está escrito, tal cual**, sin normalizar, en
`datos/transcripcion.csv` (plantilla en `plantillas/`):

```
archivo;peso_texto;placa;dia;mes;anio;legible;nota
T001.jpg;13.400;A5S-939;15;07;26;si;
```

- `peso_texto` se copia como aparece: `13.400`, `13.4`, `13,4` o `13400`. Esa variación es justamente lo que se mide.
- Si la línea de peso trae cálculos de tara y neto, `peso_texto` es el peso bruto, el mayor de los números, y la línea completa se copia en `nota`.
- `legible=parcial` cuando ni la persona puede leer un campo (tapado o cortado); ese campo queda vacío. `legible=no` si no se lee ninguno. La foto se conserva: el motor debe dejar ese campo sin lectura (RN-M04-03).
- Una segunda persona revisa la transcripción. Un error aquí contamina el entrenamiento y la medición.

De este archivo, un script genera `datos/verdad.csv` con el formato que ya lee
`piloto_motores` (`archivo;placa;fecha;peso_bruto_tn`, con la fecha en AAAA-MM-DD), aplicando la regla de
normalización de L6.

**Hecho cuando:** las 30 filas están transcritas y revisadas, y `verdad.csv` se generó sin errores.

### L3 — Partición fija

Las fotos se reparten **una sola vez**, al azar con semilla 2026, en cinco grupos de seis
(`datos/particion.csv`). Cada modelo ajustado se evalúa siempre con un grupo que no vio al entrenar.

> **Regla del laboratorio.** Las 30 fotos son de **desarrollo**. La medición de la tesis (DR-08:
> 50 tickets) se hace con tickets **distintos**, tomados después de congelar el motor (D-16). Si se
> reutilizan estas fotos, la exactitud sale inflada y no se puede defender.

### L4 — Localización y recorte

| Script | Qué hace | Salida |
|---|---|---|
| `01_localizar.py` | Detecta el marco azul impreso, corrige la perspectiva y lleva el ticket a un tamaño fijo | `datos/enderezados/T001.png` |
| `02_recortar.py` | Recorta las cinco zonas por las coordenadas relativas de `plantilla.json` | `datos/recortes/{peso,placa,dia,mes,anio}/T001.png` |
| `03_hoja_revision.py` | Arma una hoja con todos los recortes para revisarlos a ojo | `datos/revision_recortes.png` |

- Las coordenadas de `plantilla.json` se calibran con las primeras fotos y se comprueban con las demás.
- Si no se encuentra el marco, se usa un respaldo: ubicar las etiquetas impresas «Peso:» y «Placa:» con Tesseract, que sí las lee bien, y tomar la zona a su derecha.

**Hecho cuando:** la hoja de revisión muestra cada valor manuscrito completo dentro de su recorte. Se
anota cuántas fotos se localizaron bien de las 30.

### L5 — Línea base sin entrenamiento

Se leen los recortes con TrOCR `small` y `base` tal como vienen. Cada campo admite solo su alfabeto:
dígitos y separador en el peso, dígitos en la fecha, letras, dígitos y guion en la placa. Luego se
aplican las reglas de L6.

Como referencia se mide también el adaptador actual de Tesseract, con la herramienta existente dentro
del contenedor:

```bash
docker cp datos logistica-minera-backend-1:/tmp/piloto
docker exec logistica-minera-backend-1 python manage.py piloto_motores /tmp/piloto --motores tesseract
```

**Hecho cuando:** existe la tabla de exactitud por campo de los tres lectores.

### L6 — Reglas de normalización y confianza

| Campo | Regla | Sin lectura cuando |
|---|---|---|
| Peso | Con separador (`.` o `,`) y parte entera de 1 o 2 dígitos: toneladas (`13.400`, `13.4` y `13,4` dan 13,40 t). Sin separador y 4 o 5 dígitos: kilogramos (`13400` da 13,40 t) | Tres dígitos sin separador (`134`) o fuera del rango `[PENDIENTE: rango con la empresa]` |
| Fecha | Día de 1 a 31, mes de 1 a 12, año de dos dígitos completado a 20AA; la fecha debe existir | La fecha no existe, por ejemplo 31/02 |
| Placa | Formato `XXX-NNN`; en las tres últimas posiciones se corrige O→0, S→5, B→8, I→1, Z→2, G→6 | No cumple el formato tras la corrección |

- La confianza de cada campo es la probabilidad media de los caracteres leídos (de 0 a 1, RN-M04-06). Si la regla tuvo que corregir algo, la confianza baja.
- Se cuentan las **lecturas equivocadas con confianza igual o mayor que el umbral de 0,80**: no se habrían resaltado. Es la misma métrica de `piloto_motores` y es la que más importa.
- `[PENDIENTE: confirmar con la empresa que el peso se escribe siempre en toneladas]`.
- La comparación de la placa con el catálogo de vehículos queda **fuera** del laboratorio: toca RN-M04-03 y requiere una decisión propia.

### L7 — Ajuste fino con las fotos

- **Datos:** 24 fotos de entrenamiento × 5 recortes = 120 muestras por grupo. Con aumentos (rotación de ±5°, desenfoque, contraste, grosor del trazo, ruido JPEG) se llega a unas 2 400.
- **Validación cruzada:** se entrena cinco veces, una por grupo, y cada vez se evalúa con las 6 fotos que quedaron fuera. Se informa el promedio y el peor grupo.
- **Modelo candidato:** al final se entrena una sola vez con las 30 fotos. Su exactitud real solo se conocerá con tickets nuevos.
- **Versión:** cada modelo se guarda en `datos/modelos/` con el hash de sus pesos. Ese hash formará parte de `version_motor` (RN-M04-04 y RN-M04-05).
- **Tiempo:** se mide el tiempo por ticket en GPU y en **CPU**. En la nube no habrá GPU, y D-15 se decide con el tiempo en CPU.

**Hecho cuando:** existe `datos/informe_capacidad.md` con esta tabla:

| Lector | Placa | Fecha | Peso | Errores con confianza ≥ 0,80 | s/ticket en CPU |
|---|---:|---:|---:|---:|---:|
| Tesseract actual | | | | | |
| TrOCR small sin ajuste | | | | | |
| TrOCR base sin ajuste | | | | | |
| TrOCR ajustado (promedio de 5 grupos) | | | | | |

Con esa tabla se decide si se pasa al saneamiento o se prueba otra alternativa local.

---

## Saneamiento

| Paso | Contenido |
|---|---|
| S1 | Corregir el adaptador de Tesseract según DR-09 —etiquetas `Peso:` y `Placa:`, casillas de fecha, peso sin `KG`— junto con su comentario y su prueba, que hoy contradicen DR-09 |
| S2 | Agregar `apps/reconocimiento/motores/trocr.py`, el único archivo que importa `transformers` y `torch`, y registrarlo en `MOTORES` |
| S3 | Ubicar los pesos del modelo fuera de git (volumen o descarga en la construcción), verificar su hash al iniciar y llevar PyTorch para CPU al `Dockerfile` |
| S4 | Pruebas: las automatizadas siguen con el adaptador determinista; se agregan pruebas de las reglas de L6 sin el modelo |
| S5 | Ejecutar `piloto_motores --motores tesseract,trocr` dentro del contenedor, con lo que se obtiene el informe oficial del paso 7.3 |

Rama y commit según la convención: `feature/M04-reconocimiento-manuscrito` y
`M04: Adaptador de reconocimiento manuscrito (HU-M04-01)`.

---

## Documentación

| Paso | Contenido | Tipo |
|---|---|---|
| D1 | Regla de interpretación del peso manuscrito, que precisa DR-09, una vez confirmada con la empresa | DR nueva (regla del dominio) |
| D2 | Cierre de D-12 con el motor elegido y de D-15 con el tiempo medido | Actualización de D-12 y D-15 |
| D3 | Notas y requerimientos de M04: localización por plantilla, alfabeto por campo y cálculo de la confianza | Revisión de lo dependiente (acta, §5) |
| D4 | Registro en la bitácora de puertas; `verificar_migracion.sh` y `validar_docs.py` sin hallazgos | Puerta |

---

## Pendientes

- `[PENDIENTE: unidad y rango del peso manuscrito, a confirmar con la empresa]`
- `[PENDIENTE: decisión sobre comparar la placa con el catálogo de vehículos (RN-M04-03)]`
- `[PENDIENTE: conjunto de 50 tickets nuevos para la medición de DR-08, distinto de las 30 fotos]`
