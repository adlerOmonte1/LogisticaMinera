---
name: despliegue-docker
description: Prepara y ejecuta el despliegue del sistema web inteligente de ingreso de mineral con Docker Compose — contenedores de backend Django, frontend Angular servido por Nginx, PostgreSQL y almacén de imágenes, entornos de desarrollo, preproducción y producción, y el registro de despliegues durante la ventana de operación controlada. Úsala cuando se mencione Docker, compose, Nginx, despliegue, hosting, entorno, variables de entorno o puesta en producción.
---

# Despliegue

Carga antes `contexto-tesis`. Fuente: `docs/model-c4/ARQ-02_Arquitectura_Tecnica.md` §7 y
`docs/model-c4/ARQ-03_Modelo_C4.md` §3.

## Los tres entornos y para qué sirve cada uno

| Entorno | Propósito | Regla |
|---|---|---|
| Desarrollo | Local, con datos de prueba | Libre |
| Preproducción | Donde se ejecutan las **pruebas de rendimiento** de la semana de estabilización | Nunca contra producción |
| Producción | Servidor en planta/administración | El sistema **no se usa aquí hasta que termine el pretest** de la investigación |

## La restricción que condiciona todo

**El sistema no entra en operación real en planta hasta que el pretest sobre el proceso manual haya
terminado** (`docs/00-tesis/marco_tesis.md` §11). Una vez en operación, todo despliegue posterior
introduce un cambio en las condiciones de trabajo y debe quedar registrado: fecha, hora, qué cambió
y por qué.

Consecuencias prácticas, no teóricas:

- Las **migraciones de índices** van en la primera migración de cada módulo, no a mitad de la
  ventana de operación controlada.
- El motor de reconocimiento y las reglas de validación quedan congelados durante la medición del
  postest (D-16): no se actualiza su versión ni sus parámetros sin documentarlo.
- Un despliegue de corrección urgente se hace y **se anota**, no se disimula.
- Las pruebas de rendimiento van a preproducción, porque saturar producción altera los tiempos de
  respuesta reales que el sistema debe ofrecer en planta.

Lleva una bitácora de despliegues desde el primer día en producción. Es un anexo barato de mantener
e imposible de reconstruir después.

## Compose

Cuatro piezas:

```
backend    Django + Gunicorn
frontend   build de Angular servido por Nginx
db         PostgreSQL 16 con volumen persistente
media      Almacen de imagenes del ticket (volumen o servicio de objetos, segun D-14)
```

El motor de reconocimiento **no** es necesariamente un contenedor de este compose: si D-12 elige un
servicio externo, el backend lo consume por red, con sus credenciales en variables de entorno; si
elige procesamiento local, sí se empaqueta como un servicio adicional o como parte de `backend`.

Nginx actúa además de reverse proxy: sirve los estáticos del frontend y enruta `/api/` al backend,
de modo que el navegador ve un solo origen y no hay que abrir CORS en producción.

## Puntos de atención

**Volumen de la base y del almacén de imágenes.** `db` y `media` deben montar volúmenes con nombre.
Un contenedor recreado sin volumen se lleva por delante tanto los registros como las fotografías de
los tickets, que son el respaldo verificable de cada ingreso: sin la imagen, un ingreso deja de
poder contrastarse contra el papel original.

**Copias de seguridad.** Programa un volcado periódico de la base **y** del almacén de imágenes
desde el primer día de producción, y verifica al menos una restauración de ambos antes de que
empiece la operación real. Una copia que nunca se restauró no es una copia.

**Límite de tamaño de subida.** El servidor web y Django deben admitir el tamaño máximo de imagen
declarado (10 MB, RS-M03-01: `DATA_UPLOAD_MAX_MEMORY_SIZE` en Django, `client_max_body_size` en
Nginx). Un límite más bajo en cualquiera de las dos capas rechaza fotografías válidas con un error
que no distingue la causa real.

**Zona horaria.** Fija la misma en base de datos, backend y contenedores. El ingreso guarda tres
marcas de tiempo independientes; un desfase de zona horaria las desalinea entre sí sin que ninguna
prueba lo note hasta comparar con la hora real de planta.

**Secretos.** `SECRET_KEY`, credenciales de base de datos, claves JWT y, si aplica, las credenciales
del motor de reconocimiento externo, todas por variables de entorno, nunca en el repositorio ni en
la imagen. Un `.env.example` versionado, el `.env` real fuera de git.

**HTTPS.** Obligatorio en producción, tanto para la sesión del usuario como para la transmisión de
la imagen del ticket hacia el almacén o hacia un motor de reconocimiento externo.

## Hosting

Railway, Render o un VPS son suficientes para la sustentación. Si el servidor está en la planta,
verifica que sea alcanzable desde los dispositivos que usarán los supervisores — una instalación
solo accesible desde la red local de la oficina reintroduce el problema que el sistema resuelve.

## Verificación antes de que el sistema entre en operación real

- [ ] Volumen persistente en `db` y en el almacén de imágenes, con una restauración de copia probada
      para ambos.
- [ ] HTTPS activo.
- [ ] Zona horaria idéntica en todos los servicios.
- [ ] Límite de subida de imagen coherente entre Nginx y Django.
- [ ] Secretos fuera del repositorio, incluidas las credenciales del motor externo si D-12 así lo
      decidió.
- [ ] Índices creados y migraciones aplicadas.
- [ ] Motor de reconocimiento y reglas de validación en su versión congelada (D-16).
- [ ] Bitácora de despliegues iniciada.
- [ ] Pruebas de rendimiento ejecutadas en preproducción, no aquí.
