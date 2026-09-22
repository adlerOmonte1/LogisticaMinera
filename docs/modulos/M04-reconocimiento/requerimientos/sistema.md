# Requerimientos de sistema — M04 Reconocimiento automático del ticket

| Código | Requerimiento | Deriva de |
|---|---|---|
| RS-M04-01 | El sistema expone la operación de reconocimiento a través de la interfaz `ReconocedorTicket`, que recibe una imagen y devuelve seis campos con su confianza | RU-M04-01 |
| RS-M04-02 | El sistema devuelve, por cada campo, `nombre_campo`, `valor_reconocido` y `confianza` entre 0 y 1 | RU-M04-01, RU-M04-02 |
| RS-M04-03 | El sistema deja `valor_reconocido` vacío cuando el motor no obtiene lectura, y no sustituye ese vacío por ningún valor estimado | RU-M04-03 |
| RS-M04-04 | El sistema compara cada `confianza` con el umbral vigente y marca como dudosos los campos por debajo de él | RU-M04-02 |
| RS-M04-05 | El sistema admite configurar el umbral de confianza, con 0,80 como valor por defecto | RU-M04-02 |
| RS-M04-06 | El sistema registra `motor`, `version_motor`, `fecha_proceso` y `umbral_confianza` en cada reconocimiento | RU-M04-05 |
| RS-M04-07 | El sistema devuelve el control al registro cuando el motor falla o excede el tiempo de espera, sin interrumpir la operación del usuario | RU-M04-04 |
| RS-M04-08 | El sistema no persiste ningún valor reconocido hasta que el ingreso se confirma | — (integridad con M03) |
| RS-M04-09 | El sistema persiste, al confirmarse el ingreso, `valor_reconocido` y `valor_confirmado` como campos separados de cada uno de los seis datos | RU-M04-05 |
| RS-M04-10 | El sistema deriva `fue_corregido` de la diferencia entre el valor reconocido y el confirmado, y no lo acepta como dato de entrada | RU-M04-05 |
| RS-M04-11 | El sistema expone la consulta de un reconocimiento con sus seis campos, el motor y la versión | RU-M04-05 |
| RS-M04-12 | El sistema mantiene un reconocimiento como máximo por ingreso | — (integridad del registro) |
