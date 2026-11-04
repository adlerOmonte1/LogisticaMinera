> **Ensayo de la herramienta, no es el piloto de D-12.** Tres tickets sintéticos generados con el
> formato de la maqueta, uno nítido y dos degradados. Comprueba que `piloto_motores` funciona de punta
> a punta. El piloto se ejecuta con 20 a 30 tickets reales de la planta (DR-08) y cierra D-12 y D-15.

# Informe del piloto de motores de reconocimiento

Conjunto: `ensayo`, 3 tickets, 9 lecturas. Umbral de confianza: 0.8.

| Motor | Versión | Éxito | Placa | Fecha | Peso bruto | Global | Tiempo medio (s) | Tiempo máximo (s) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| tesseract | 5.5.0 | 3/3 | 66.7 % | 100.0 % | 100.0 % | 88.9 % | 0.16 | 0.25 |
| determinista | 1.0 | 3/3 | 0.0 % | 0.0 % | 0.0 % | 0.0 % | 0.0 | 0.0 |

## Utilidad del umbral

Lecturas equivocadas con confianza igual o mayor que el umbral: no se habrían resaltado (notas de M04).

| Motor | Placa | Fecha | Peso bruto |
|---|---:|---:|---:|
| tesseract | 1 | 0 | 0 |
| determinista | 0 | 0 | 0 |

## Para completar a mano

- Costo por ticket y dependencia de conexión de cada motor (D-12).
- Motor elegido y su justificación; con él se cierran D-12 y, por el tiempo por ticket, D-15.
