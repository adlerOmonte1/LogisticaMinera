# Requerimientos no funcionales — M02 Catálogo maestro

| Código | Característica ISO/IEC 25010:2023 | Requerimiento | Verificación |
|---|---|---|---|
| RNF-M02-01 | Eficiencia de desempeño — comportamiento temporal | La lista de vehículos y tipos de mineral se entrega al cliente en menos de 1 segundo con 500 registros | Prueba automatizada con datos sintéticos |
| RNF-M02-02 | Eficiencia de desempeño — utilización de recursos | Los catálogos se conservan en memoria del cliente durante la sesión y solo se recargan al detectar un cambio | Inspección de red en navegador |
| RNF-M02-03 | Adecuación funcional — corrección | La validación de placa y RUC se ejecuta en el servidor, no solo en el formulario | Prueba automatizada: solicitud directa al endpoint con placa inválida devuelve 400 |
| RNF-M02-04 | Usabilidad — operabilidad | Los selectores permiten búsqueda por texto cuando superan diez elementos | Inspección funcional |
