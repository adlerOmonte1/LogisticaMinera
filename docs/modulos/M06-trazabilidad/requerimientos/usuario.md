# Requerimientos de usuario — M06 Trazabilidad del proceso

| Código | Requerimiento |
|---|---|
| RU-M06-01 | Como el mineral de varios volquetes se junta en cancha, quiero agruparlos y seguirlos como una sola carga |
| RU-M06-02 | Quiero marcar que la carga ya pasó por el secado, el zarandeo, la molienda o el ensacado |
| RU-M06-03 | No quiero poder marcar una etapa si la carga todavía no pasó por la que le toca antes: el sistema debería avisarme |
| RU-M06-04 | Quiero saber, para un volquete cualquiera, por dónde va su mineral y qué le falta |
| RU-M06-05 | Quiero ver qué volquetes componen una carga y cuántas toneladas suma |
| RU-M06-06 | No todo el mineral se muele: después del secado decidimos si va a zaranda, a molino o a los dos, y así quiero anotarlo |
| RU-M06-07 | A veces una parte de la carga se muele y otra no; quiero partirla a ojo, en fracciones, porque en cancha no se pesa |
| RU-M06-08 | Siguen llegando volquetes cuando la carga ya empezó a secarse, y quiero sumarlos sin desordenar lo que ya se anotó |
| RU-M06-09 | Quiero anotar cuántos bigbags salieron y cuántas horas trabajó el molino |
| RU-M06-10 | Cuando todo está ensacado, quiero cerrar la carga y dejar anotado si se vendió o se llevó a otro lado |

## Contexto del diagnóstico

| Requerimiento | Situación que resuelve |
|---|---|
| RU-M06-01 | El mineral no se procesa volquete por volquete: se acumula en cancha y se trabaja por cargas. Cualquier registro que suponga lo contrario describe algo que no ocurre |
| RU-M06-02, RU-M06-03 | El avance del proceso se lleva de memoria o en anotaciones sueltas, y cuando alguien falta nadie sabe con certeza qué se hizo y qué no |
| RU-M06-04 | Responder dónde está el mineral de un ingreso obliga hoy a recorrer la planta preguntando |
| RU-M06-05 | No hay forma de saber cuántas toneladas componen una carga sin sumar a mano los tickets |
| RU-M06-06, RU-M06-07 | El destino de cada carga dentro de la planta lo decide quien la ve en cancha, según el mineral; un registro con las cuatro etapas obligatorias mostraría como incompleta una carga que siguió el camino correcto |
| RU-M06-08 | Los volquetes no llegan todos juntos: una carga se completa mientras ya avanza, y hoy esa mezcla no queda registrada en ningún lado |
| RU-M06-09 | Los bigbags y el rendimiento del molino se cuentan al final de la jornada y se pierden si no se anotan |
| RU-M06-10 | Cuando una carga termina, no queda constancia de cuánto produjo ni de a dónde se fue |
