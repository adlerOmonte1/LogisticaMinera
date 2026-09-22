# Requerimientos no funcionales — M09 Auditoría

| Código | Característica ISO/IEC 25010:2023 | Requerimiento | Verificación |
|---|---|---|---|
| RNF-M09-01 | Eficiencia de desempeño — comportamiento temporal | El registro de un evento añade menos de 50 milisegundos a la operación que audita | Prueba automatizada con medición del tiempo |
| RNF-M09-02 | Seguridad — no repudio | Ningún evento puede modificarse ni eliminarse a través de la API, con independencia del rol | Prueba automatizada que intenta editar y borrar eventos con cada rol |
| RNF-M09-03 | Fiabilidad — capacidad de recuperación | Si el registro del evento falla, la operación completa se revierte: no queda un cambio sin su evento | Prueba automatizada que fuerza el fallo del registro de auditoría |
| RNF-M09-04 | Eficiencia de desempeño — capacidad | El volumen de eventos generado durante la ventana de operación no degrada el tiempo de respuesta de las operaciones auditadas | Prueba de carga con el volumen esperado de eventos |
| RNF-M09-05 | Usabilidad — reconocibilidad | El historial de una entidad distingue visualmente las acciones de escritura de los accesos rechazados | Inspección en dispositivo real |
| RNF-M09-06 | Mantenibilidad — modularidad | Añadir una acción auditable al catálogo no exige modificar el modelo de `EVENTO_AUDITORIA` | Inspección de código |

## Nota sobre RNF-M09-03

Es la contrapartida operativa de RN-M09-01. Si el registro del evento fallara y la operación
principal continuara de todas formas, quedaría un cambio en el sistema sin su rastro de auditoría.
La forma correcta de fallar es revertir toda la transacción: la operación no se completa si su
evento no puede registrarse, porque ambos viven en la misma unidad atómica.

## Nota sobre RNF-M09-04

El volumen de `EVENTO_AUDITORIA` crece con cada operación de escritura de todo el sistema, no solo
con los ingresos. Es la tabla que más rápido acumula filas, y su índice por entidad e identificador
(`idx_evento_entidad`) existe precisamente para que las consultas de historial no se degraden
conforme ese volumen aumenta.
