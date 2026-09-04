# Requerimientos no funcionales — M02 Catálogo maestro

| Código | Característica ISO/IEC 25010:2023 | Requerimiento | Verificación |
|---|---|---|---|
| RNF-M02-01 | Eficiencia de desempeño | La lista de vehículos y productos se entrega al cliente en menos de 1 segundo | Prueba de carga (JMeter) |
| RNF-M02-02 | Eficiencia de desempeño | Los catálogos se almacenan en caché en el cliente y solo se revalidan al detectar cambios, para no penalizar la carga del formulario de ingreso | Inspección de red en navegador |
| RNF-M02-03 | Fiabilidad — disponibilidad | Los catálogos están disponibles sin conexión, precargados por el service worker | Prueba: abrir formulario de ingreso en modo avión y verificar que los selectores tienen datos |
| RNF-M02-04 | Adecuación funcional — corrección | La validación de placa y RUC se ejecuta en servidor, no solo en el formulario | Prueba: solicitud directa al endpoint con placa inválida devuelve 400 |
| RNF-M02-05 | Usabilidad | Los selectores permiten búsqueda por texto cuando superan diez elementos | Inspección funcional |

**RNF-M02-03 es crítico para M07.** Si el catálogo no está disponible offline, el supervisor no puede seleccionar producto ni vehículo sin conexión, y la captura offline pierde sentido. Esta dependencia se documenta también en `../M07-sin-conexion/notas.md`.
