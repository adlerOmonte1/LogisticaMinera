# Requerimientos no funcionales — M04 Reconocimiento automático del ticket

| Código | Característica ISO/IEC 25010:2023 | Requerimiento | Verificación |
|---|---|---|---|
| RNF-M04-01 | Eficiencia de desempeño — comportamiento temporal | El reconocimiento de un ticket devuelve resultado en menos de 5 segundos con una imagen de hasta 5 MB | Cronometraje sobre el conjunto de tickets de prueba |
| RNF-M04-02 | Fiabilidad — tolerancia a fallos | Si el motor no responde en 10 segundos, el sistema cancela la espera y ofrece el registro manual | Prueba automatizada con un doble de prueba que no responde |
| RNF-M04-03 | Fiabilidad — disponibilidad | La indisponibilidad del motor no impide registrar ingresos | Prueba automatizada con el motor desactivado |
| RNF-M04-04 | Adecuación funcional — corrección | El sistema reconoce los seis campos sobre tickets de la balanza en uso, incluidos los impresos en papel térmico con desgaste | Contraste del resultado con la lectura humana sobre el conjunto de tickets de prueba |
| RNF-M04-05 | Mantenibilidad — modularidad | Sustituir el motor exige escribir un adaptador nuevo y no modificar ningún otro módulo | Inspección de código: solo `motores/` importa la librería del proveedor |
| RNF-M04-06 | Mantenibilidad — capacidad de ser probado | Las pruebas del registro y de la validación se ejecutan sin invocar al motor real | Inspección de código: el motor se inyecta y se sustituye por un doble en las pruebas |
| RNF-M04-07 | Seguridad — confidencialidad | Si el motor es un servicio externo, la imagen se transmite cifrada y sus credenciales viven en variables de entorno | Inspección de configuración |
| RNF-M04-08 | Seguridad — integridad | El motor y su versión quedan registrados en cada reconocimiento y no son modificables desde la API | Prueba automatizada que intenta alterarlos |
| RNF-M04-09 | Usabilidad — protección contra errores del usuario | Los campos con confianza bajo el umbral se distinguen visualmente de los demás sin depender solo del color | Inspección en dispositivo real |

## Nota sobre RNF-M04-01 y RNF-M04-02

El reconocimiento ocurre con el supervisor de pie junto al volquete. Una espera larga anula la
ventaja frente a escribir los seis datos, que toma alrededor de un minuto. Por eso el límite duro de
RNF-M04-02 es tan importante como el objetivo de RNF-M04-01: es preferible ofrecer el registro
manual a los diez segundos que mantener al usuario esperando un resultado que quizá no llegue.

Si el piloto de motores muestra que el tiempo habitual supera estos umbrales, la decisión de
procesar de forma síncrona debe revisarse (D-15).

## Nota sobre RNF-M04-04

La exactitud depende del motor elegido y del estado del papel, y por eso no se fija aquí como un
número: se mide sobre el conjunto de tickets de prueba antes de cerrar D-12, y el resultado de esa
medición es el criterio de elección. Documentar un umbral antes del piloto sería fijar una
expectativa sin fundamento.

## Nota sobre RNF-M04-05 y RNF-M04-06

Son la contrapartida técnica de que D-12 siga abierta. Mientras el motor no esté elegido, todo el
sistema debe poder construirse y probarse contra la interfaz. Si la librería del proveedor se
importara fuera de `motores/`, esa elección quedaría de hecho tomada por el código.
