# Requerimientos no funcionales — M05 Existencias

| Código | Característica ISO/IEC 25010:2023 | Requerimiento | Verificación |
|---|---|---|---|
| RNF-M05-01 | Eficiencia de desempeño — comportamiento temporal | La consulta de existencias de todos los productos responde en menos de 1 segundo con 5000 movimientos en base | Prueba de carga con datos sintéticos |
| RNF-M05-02 | Eficiencia de desempeño — capacidad | El tiempo de consulta no crece de forma apreciable con el volumen del histórico | Medición comparativa con 1000 y 5000 movimientos |
| RNF-M05-03 | Adecuación funcional — corrección | El saldo denormalizado coincide con el cálculo íntegro sobre los movimientos en el 100 % de los casos | Rutina de verificación periódica que compara ambos cálculos |
| RNF-M05-04 | Adecuación funcional — corrección | Los cálculos usan aritmética decimal exacta, no punto flotante | Inspección: campos `Decimal` en Django, `numeric` en PostgreSQL |
| RNF-M05-05 | Seguridad — integridad | No existe ningún camino, ni por interfaz ni por API, para escribir el saldo directamente | Revisión del contrato de la API y pruebas de intento de escritura |
| RNF-M05-06 | Usabilidad | La pantalla de existencias es la vista predeterminada al iniciar sesión para el rol Administrativo | Inspección funcional |

## Relación directa con el indicador I3

RNF-M05-01 y RNF-M05-02 son la traducción técnica del indicador I3. El instrumento de la tesis mide el tiempo que un usuario tarda en determinar el stock de un producto; ese tiempo se compone del tiempo de respuesta del sistema más el tiempo de navegación del usuario. RNF-M05-06 reduce el segundo componente al eliminar pasos de navegación.

## Sobre RNF-M05-04

El uso de punto flotante para cantidades en toneladas produciría desviaciones acumuladas de centésimas que, sumadas sobre cientos de movimientos, podrían confundirse con una desviación real de inventario y contaminar el indicador I4. Es un detalle técnico con consecuencia directa sobre la validez de los datos.
