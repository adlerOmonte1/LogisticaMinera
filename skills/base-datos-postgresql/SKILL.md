---
name: base-datos-postgresql
description: Diseña y modifica el esquema PostgreSQL del sistema web inteligente de ingreso de mineral — entidades del modelo entidad-relación, tipos decimales, índices que sostienen las consultas de M07 y M08, código único del ingreso, migraciones y consultas de agregación para consolidación y trazabilidad. Úsala al crear o cambiar un modelo o una migración, al escribir consultas de consolidación o trazabilidad, y cuando se mencionen esquema, tablas, índices, migraciones o rendimiento de consultas.
---

# Base de datos

Carga antes `contexto-tesis`. **Fuente única del esquema:**
`docs/00-arquitectura/modelo_datos_entidad_relacion.md`. Una entidad se define una sola vez aunque la
usen varios módulos: `INGRESO` la escribe M03, la leen M07 y M08, la referencian M04, M05 y M06, y la
audita M09.

## Entidades

`USUARIO` · `ROL` · `VEHICULO` · `TRANSPORTISTA` · `TIPO_MINERAL` · `INGRESO` ·
`RECONOCIMIENTO_TICKET` · `CAMPO_RECONOCIDO` · `RESULTADO_VALIDACION` · `ETAPA_PROCESO` ·
`LOTE_PROCESO` · `PASO_ETAPA` · `EVENTO_AUDITORIA`. Los campos exactos están en el modelo
entidad-relación; no los reinventes ni los renombres al escribir la migración.

## Reglas no negociables

**1. `decimal`, nunca punto flotante.** Pesos `decimal(8,2)`; capacidad de vehículo `decimal(6,2)`;
confianza de un campo reconocido `decimal(4,3)`. El error acumulado del flotante sobre cientos de
registros se confundiría con diferencias reales entre el ticket y lo registrado.

**2. `peso_neto_tn` se calcula en el servidor y se almacena junto con la tara aplicada.** El ticket
imprime solo el peso bruto (DR-09). `INGRESO.tara_tn` es la tara del vehículo **copiada** en el
momento de aplicarse y `peso_neto_tn` su diferencia con el bruto (D-17). No los derives al vuelo
del catálogo ni con una vista o una propiedad que lea `VEHICULO.tara_tn`: un cambio de tara decidido
por la Gerencia reescribiría todo el histórico. Ambos son nulos solo si `estado = 'EN_PROCESO'`; una
restricción `CHECK` lo garantiza, junto con `tara_tn < peso_bruto_tn`.

**3. `CAMPO_RECONOCIDO` guarda dos valores por campo, no uno.** `valor_reconocido` (nulo si el
motor no leyó nada) y `valor_confirmado` (el que el usuario aceptó o corrigió) son columnas
separadas. `fue_corregido` se deriva comparando ambas; no es una columna que el cliente pueda
escribir.

**4. Nada se borra.** `activo boolean` en catálogos, `estado enum REGISTRADO / ANULADO` en ingresos
(D-07). Sin `ON DELETE CASCADE` en ninguna relación que apunte a un registro histórico, con la única
excepción documentada de `RECONOCIMIENTO_TICKET` y `CAMPO_RECONOCIDO`, que sí se borran en cascada
con su ingreso: son un detalle del ingreso, no un registro del negocio por sí mismos.

**5. El código del ingreso se asigna con garantía de unicidad bajo concurrencia** (D-02). Secuencia
de PostgreSQL con `nextval`, o tabla de contadores con `select_for_update()` dentro de la
transacción. **Jamás `MAX(codigo) + 1`.** Documenta la opción adoptada.

Un código anulado **no se reutiliza**: el ingreso permanece marcado como anulado, no se libera su
código para otro registro.

## Índices — desde la primera migración

| Índice | Tabla | Consulta que sostiene |
|---|---|---|
| `idx_ingreso_codigo` | INGRESO(codigo) | Localizar un ingreso por su código. Cubierto por `unique=True` |
| `idx_ingreso_vehiculo_fecha` | INGRESO(id_vehiculo, fecha_hora_pesaje) | Consulta por placa y fecha de M07 |
| `idx_ingreso_fecha_mineral` | INGRESO(fecha_hora_pesaje, id_tipo_mineral) | Total acumulado mensual de M08 |
| `idx_ingreso_estado` | INGRESO(estado) | Excluir anulados de todo total, casi siempre combinada con otra condición |
| `idx_paso_lote` | PASO_ETAPA(id_lote) | Etapas recorridas por un lote, de M06 |
| `idx_evento_entidad` | EVENTO_AUDITORIA(entidad, id_entidad) | Historial de un registro concreto, de M09 |

**Se crean en la primera migración, no se añaden al final.** Un índice agregado a mitad de la
ventana de observación controlada cambia las condiciones de trabajo a mitad de la medición.

Restricciones de unicidad que exigen las historias: `username`, `placa`, `codigo` de tipo de
mineral, `ruc`, `codigo` del ingreso, y `numero_ticket` **entre los ingresos no anulados** —
unicidad parcial, para que un ticket mal transcrito pueda reutilizarse tras anular el registro
erróneo. También `(id_lote, id_etapa)` en `PASO_ETAPA`: una etapa se registra una sola vez por lote.

## Consultas

Las de lectura viven en `repositories/`, separadas de la escritura, para poder optimizarlas sin
tocar la lógica de negocio (ver `solid-proyecto`).

**Consulta por placa y fecha** (M07): filtra sobre `idx_ingreso_vehiculo_fecha`, con búsqueda
parcial de placa normalizada (sin guiones, sin distinguir mayúsculas). Devuelve tanto los ingresos
activos como los anulados, señalados como tales — ocultar los anulados haría creer que un volquete
nunca se registró.

**Total acumulado mensual** (M08): agregación en una sola consulta con `values().annotate()`,
agrupando por `tipo_mineral` y excluyendo `estado='ANULADO'` **antes** de agregar, no después. Un
tipo de mineral sin ingresos en el periodo se omite del resultado, no aparece con total en cero.

**Trazabilidad de un ingreso** (M06): parte de `INGRESO.id_lote`, no de una tabla intermedia —un
ingreso pertenece a un lote como máximo. Si el ingreso no tiene lote, el resultado son las cuatro
etapas marcadas como no recorridas, no un error.

**Comparación de reconocimiento** (M04): `CAMPO_RECONOCIDO` filtrado por `id_reconocimiento`, con
sus tres filas —placa, fecha y peso bruto— siempre presentes aunque alguna tenga
`valor_reconocido` nulo.

**Búsqueda de duplicados** (V1 de M05): ingreso no anulado con la misma placa, la misma fecha del
pesaje y el mismo peso bruto. La sostiene el índice `(vehiculo, fecha_hora_pesaje)`.

**Totales** (M06, M07, M08): siempre `estado = 'REGISTRADO'`, nunca «distinto de anulado»; los
ingresos En proceso no tienen peso neto.

## Migraciones

Una migración por cambio con nombre descriptivo. Nunca edites una migración ya aplicada en
producción: durante la ventana de operación controlada cualquier cambio de esquema debe quedar
registrado como despliegue.

La migración que retira `Cliente` del catálogo (preparación del repositorio heredado) se ejecuta **después**
de retirar `apps/salidas`, que es quien mantenía la clave foránea hacia esa entidad; en el orden
contrario, la migración falla o exige forzar el borrado en cascada sin que nadie lo decida
explícitamente.

## Verificación

- [ ] Ningún `FloatField` ni `double precision` en pesos, capacidades o confianzas.
- [ ] `peso_neto_tn` y `tara_tn` se almacenan en `INGRESO`; ninguna vista ni propiedad los deriva
      de `VEHICULO.tara_tn`.
- [ ] `CHECK`: tara y neto nulos solo en `EN_PROCESO`; tara menor que el bruto.
- [ ] Los totales filtran `estado = 'REGISTRADO'`.
- [ ] `valor_reconocido` y `valor_confirmado` son columnas separadas en `CAMPO_RECONOCIDO`.
- [ ] Ningún `ON DELETE CASCADE` hacia registros históricos, salvo la excepción documentada del
      reconocimiento sobre su ingreso.
- [ ] Los seis índices de la tabla están en la primera migración de su módulo.
- [ ] La unicidad de `numero_ticket` es parcial (solo no anulados).
- [ ] El total mensual de M08 coincide entre la consulta y la exportación para el mismo periodo.
- [ ] La estrategia del código único está implementada con bloqueo o secuencia, y documentada.
