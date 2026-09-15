# Requerimientos no funcionales — M07 Captura sin conexión

| Código | Característica ISO/IEC 25010:2023 | Requerimiento | Verificación |
|---|---|---|---|
| RNF-M07-01 | Fiabilidad — tolerancia a fallos | La pérdida de conexión no interrumpe ni bloquea el registro de un ingreso en curso | Prueba: activar modo avión durante el llenado |
| RNF-M07-02 | Fiabilidad — recuperabilidad | Los ingresos pendientes sobreviven al cierre de la aplicación, al reinicio del dispositivo y a la actualización de la aplicación | Prueba: capturar, cerrar, reiniciar, verificar |
| RNF-M07-03 | Fiabilidad — disponibilidad | La aplicación carga completamente sin conexión en menos de 3 segundos | Medición en dispositivo real |
| RNF-M07-04 | Eficiencia de desempeño | La sincronización de 20 ingresos pendientes se completa en menos de 15 segundos en red móvil | Medición en campo |
| RNF-M07-05 | Adecuación funcional — corrección | La hora de registro de un ingreso sincronizado es exactamente la hora de captura local, verificable en el detalle | Prueba: capturar offline, sincronizar horas después, comparar campos |
| RNF-M07-06 | Usabilidad — reconocibilidad | El estado de conexión y la cantidad de pendientes son visibles en todo momento sin abrir menús | Inspección funcional |
| RNF-M07-07 | Seguridad — integridad | Los datos en IndexedDB no contienen credenciales ni información de otros usuarios | Inspección del almacenamiento local |
| RNF-M07-08 | Compatibilidad | La aplicación funciona en Chrome para Android versión 90 o superior, que es el navegador disponible en los dispositivos del personal | Prueba en dispositivo real del personal |

## RNF-M07-05 y la confiabilidad del indicador I1

Este requisito es el más importante del módulo desde el punto de vista de la medición. Si la hora de registro fuera la de sincronización, el indicador I1 mediría el tiempo hasta que hubo señal, no el tiempo hasta que se capturó el dato. La medición quedaría invalidada precisamente en el módulo diseñado para mejorarla.

La verificación debe ser explícita y documentada: capturar un ingreso sin conexión, esperar varias horas, sincronizar, y comprobar que `hora_registro` corresponde al momento de captura y `hora_sincronizacion` al momento del envío.

## RNF-M07-08 y la restricción real

La compatibilidad no se especifica en abstracto sino contra los dispositivos que el personal usa efectivamente. Debe verificarse en el teléfono real del supervisor antes de la semana 4, no en un emulador. Un fallo de compatibilidad detectado en la semana 8 no deja margen de corrección.
