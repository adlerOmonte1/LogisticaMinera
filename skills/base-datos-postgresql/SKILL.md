---
name: base-datos-postgresql
description: Diseña y modifica el esquema PostgreSQL del sistema de control de producción y existencias — entidades del modelo ER, tipos decimales, índices que sostienen los indicadores, secuencia del correlativo, migraciones y consultas de agregación para stock y kardex. Úsala al crear o cambiar un modelo o una migración, al escribir consultas de saldo, kardex o consolidado, y cuando se mencionen esquema, tablas, índices, migraciones o rendimiento de consultas.
---

# Base de datos

Carga antes `contexto-tesis`. **Fuente única del esquema:**
`docs/00-arquitectura/modelo_datos_entidad_relacion.md`. Una entidad se define una sola vez aunque la
usen varios módulos: `Ingreso` la escriben M03 y M07, la leen M05, M06 y M09, y la audita M08.

## Entidades

`USUARIO` · `ROL` · `PRODUCTO` · `VEHICULO` · `TRANSPORTISTA` · `CLIENTE` · `INGRESO` · `SALIDA` ·
`MOVIMIENTO_STOCK` · `EVENTO_AUDITORIA`. Los campos exactos están en el modelo ER; no los reinventes
ni los renombres al escribir la migración.

## Reglas no negociables

**1. `decimal`, nunca punto flotante.** Pesos y cantidades `decimal(8,2)`; saldo resultante
`decimal(10,2)`; capacidad de vehículo `decimal(6,2)`. El error acumulado del flotante sobre cientos
de movimientos se confundiría con desviación real de inventario y contaminaría el indicador I4. Es un
detalle técnico con consecuencia directa sobre la validez de los datos.

**2. `MOVIMIENTO_STOCK` es una tabla de asiento.** Todo ingreso y toda salida generan **exactamente
uno**; el stock **nunca se edita directamente**. `cantidad_tn` es siempre positiva y el signo lo da
`tipo` (ENTRADA / SALIDA / AJUSTE). No añadas una columna `stock_actual` en `PRODUCTO`: el saldo se
deriva de los movimientos, y esa derivación es lo que hace auditable el cálculo (HU-M05-02 CA02
exige que el saldo final del kardex coincida exactamente con la consulta de existencias).

`saldo_resultante_tn` sí está denormalizado en cada movimiento, deliberadamente, para sostener el
indicador I3. Se escribe dentro de la misma transacción que el movimiento, nunca por un proceso
posterior.

**3. Nada se borra.** `activo boolean` en catálogos, `estado enum REGISTRADO / ANULADO` en ingresos y
salidas (D-07). Sin `ON DELETE CASCADE` en ninguna relación que apunte a un registro histórico.

**4. El correlativo se asigna con garantía de unicidad bajo concurrencia** (D-02). Secuencia de
PostgreSQL con `nextval`, o tabla de contadores con `select_for_update()` dentro de la transacción.
La segunda es preferible porque el correlativo se reinicia por año y lleva prefijo
(`ING-{año}-{cinco dígitos}`). **Jamás `MAX(correlativo) + 1`.** Documenta la opción adoptada.

Un correlativo anulado **no se reutiliza** (HU-M03-07 CA03): la secuencia no retrocede.

## Índices — desde la primera migración

| Índice | Tabla | Indicador que sostiene |
|---|---|---|
| `idx_ingreso_correlativo` | INGRESO(correlativo) | I5 — búsqueda por padrón |
| `idx_ingreso_fecha_producto` | INGRESO(fecha_pesaje, id_producto) | I5, I6 — consolidados |
| `idx_ingreso_vehiculo` | INGRESO(id_vehiculo) | I2 — cobertura por titularidad |
| `idx_movimiento_producto_fecha` | MOVIMIENTO_STOCK(id_producto, fecha_movimiento) | I3 — cálculo de stock |

**Se crean en la primera migración, no se añaden al final.** I5 se mide sobre el sistema en
producción; una migración de índices a mitad de la ventana de observación introduce un cambio no
controlado en las condiciones de medición y es una amenaza a la validez interna que habría que
declarar ante el jurado.

Restricciones de unicidad que exigen las historias: `username`, `placa`, `codigo` de producto,
`ruc`, `correlativo`, y `numero_ticket` **entre los ingresos no anulados** (RN-M03-05) — unicidad
parcial, para que un ticket mal transcrito pueda reutilizarse tras anular el registro erróneo.

## Consultas

Las de lectura viven en `selectors.py`, separadas de la escritura, para poder optimizarlas sin tocar
la lógica de negocio (ver `solid-proyecto`).

**Stock por producto:** ingresos − salidas − mermas ± ajustes, agregando sobre `MOVIMIENTO_STOCK`.

**Stock a una fecha de corte** (HU-M05-03): filtra por `fecha_movimiento <= corte` — la **fecha del
movimiento**, no la de su registro en el sistema. Un ingreso registrado después pero con fecha de
pesaje anterior al corte **sí entra** (CA02). Los ingresos anulados quedan siempre excluidos (CA03).
Confundir ambas fechas invalida el indicador I4, que es exactamente lo que esta consulta alimenta.

**Kardex** (HU-M05-02): movimientos del periodo en orden cronológico con saldo acumulado, saldo
inicial y final. La referencia de un movimiento de ingreso es el **correlativo de padrón**, no el id
interno.

Un producto sin movimientos devuelve **cero, no error ni `None`** (HU-M05-01 CA04). Mantén ese
contrato idéntico en todos los selectores.

## Migraciones

Una migración por cambio con nombre descriptivo. Nunca edites una migración ya aplicada en
producción: durante la ventana de observación cualquier cambio de esquema debe quedar registrado
como despliegue, por la misma razón metodológica que los índices.

## Verificación

- [ ] Ningún `FloatField` ni `double precision` en cantidades o pesos.
- [ ] Ningún `ON DELETE CASCADE` hacia registros históricos.
- [ ] Los cuatro índices de la tabla están en la primera migración.
- [ ] La unicidad de `numero_ticket` es parcial (solo no anulados).
- [ ] El saldo del kardex coincide con la consulta de existencias a la misma fecha.
- [ ] La estrategia de correlativo está implementada con bloqueo o secuencia, y documentada.
