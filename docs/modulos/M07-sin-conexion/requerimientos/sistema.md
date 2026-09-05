# Requerimientos de sistema — M07 Captura sin conexión

| Código | Requerimiento | Deriva de |
|---|---|---|
| RS-M07-01 | El sistema se distribuye como aplicación web progresiva instalable, con service worker que cachea la interfaz y los recursos estáticos | RU-M07-01 |
| RS-M07-02 | El sistema almacena los catálogos de producto y vehículo en IndexedDB y los revalida en cada reconexión | RU-M07-01 |
| RS-M07-03 | El sistema persiste los ingresos capturados sin conexión en IndexedDB con identificador local UUID y hora de captura del dispositivo | RU-M07-02 |
| RS-M07-04 | El sistema aplica en el cliente las mismas validaciones de formato que aplica el servidor, sin sustituir la validación autoritativa del servidor | RU-M07-01 |
| RS-M07-05 | El sistema detecta la recuperación de conectividad y dispara la sincronización de la cola en orden de captura | RU-M07-03 |
| RS-M07-06 | El sistema envía los pendientes en lote a un endpoint de sincronización que procesa cada elemento de forma independiente | RU-M07-03 |
| RS-M07-07 | El servidor asigna como hora de registro la hora de captura local recibida y almacena la hora de sincronización en un campo separado | — (decisión D-03) |
| RS-M07-08 | El servidor rechaza toda hora de captura local posterior a su propia hora | — (integridad temporal) |
| RS-M07-09 | El sistema conserva en la cola los elementos rechazados con el motivo, permitiendo corrección y reintento | RU-M07-04 |
| RS-M07-10 | El sistema conserva la cola íntegra ante la expiración del token, solicitando reautenticación sin descartar elementos | RU-M07-02 |
| RS-M07-11 | El sistema detiene el reintento automático tras tres fallos consecutivos de un mismo elemento | RU-M07-04 |
