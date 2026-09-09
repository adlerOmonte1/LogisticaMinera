---
name: despliegue-docker
description: Prepara y ejecuta el despliegue del sistema de control de producción y existencias con Docker Compose — contenedores de backend Django, frontend Angular servido por Nginx y PostgreSQL, entornos de desarrollo, preproducción y producción, y el registro de despliegues durante la ventana de observación de la tesis. Úsala cuando se mencione Docker, compose, Nginx, despliegue, hosting, entorno, variables de entorno o puesta en producción.
---

# Despliegue

Carga antes `contexto-tesis`. Fuente: `docs/00-arquitectura/ARQ-02_Arquitectura_Tecnica.md` §7.

## Los tres entornos y para qué sirve cada uno

| Entorno | Propósito | Regla |
|---|---|---|
| Desarrollo | Local, con datos de prueba | Libre |
| Preproducción | Donde se ejecutan las **pruebas de carga** (semana 8) | Nunca contra producción |
| Producción | Servidor en planta/administración | **Aquí se recolecta el postest** |

## La restricción que condiciona todo

**Todo despliegue posterior al inicio de la ventana de observación introduce una amenaza a la validez
interna y debe quedar registrado**: fecha, hora, qué cambió y por qué. El postest solo puede
recolectarse en producción con usuarios reales; si el sistema cambia a mitad de la medición, el
jurado puede preguntar —con razón— si la mejora del indicador se debe al sistema o al cambio.

Consecuencias prácticas, no teóricas:

- Las **migraciones de índices** van en la primera migración, no a mitad de la ventana (afecta a I5).
- Un despliegue de corrección urgente se hace y **se anota**, no se disimula.
- Las pruebas de carga van a preproducción, porque saturar producción altera los tiempos que mide I3.

Lleva una bitácora de despliegues desde el primer día en producción. Es un anexo barato de mantener e
imposible de reconstruir después.

## Compose

Tres servicios:

```
backend    Django + Gunicorn
frontend   build de Angular servido por Nginx
db         PostgreSQL 16 con volumen persistente
```

Nginx actúa además de reverse proxy: sirve los estáticos del frontend y enruta `/api/` al backend,
de modo que el navegador ve un solo origen y no hay que abrir CORS en producción.

## Puntos de atención

**Volumen de la base.** `db` debe montar un volumen con nombre. Un contenedor recreado sin volumen se
lleva por delante los datos del postest, que son irreproducibles: no se puede volver a pedir a la
planta que registre otra vez seis semanas de volquetes.

**Copias de seguridad.** Programa un volcado periódico desde el primer día de producción y verifica
al menos una restauración antes de que empiece la ventana de observación. Una copia que nunca se
restauró no es una copia.

**Service worker y caché.** El frontend es una PWA: un `index.html` cacheado de forma agresiva deja a
los supervisores con una versión vieja tras un despliegue. Sirve `index.html` sin caché y los
recursos con hash en el nombre. Si un supervisor queda con una versión anterior del formulario, los
datos que capture pueden no coincidir con el contrato de la API y perderse en la sincronización.

**Zona horaria.** Fija la misma en base de datos, backend y contenedores. I1 es una diferencia entre
dos marcas de tiempo; un desfase de zona horaria produce latencias sistemáticamente desplazadas, o
negativas, y no se detecta a simple vista.

**Secretos.** `SECRET_KEY`, credenciales de base de datos y claves JWT por variables de entorno,
nunca en el repositorio ni en la imagen. Un `.env.example` versionado, el `.env` real fuera de git.

**HTTPS.** Obligatorio en producción: sin él, el service worker no se registra en la mayoría de los
navegadores y la PWA de M07 simplemente no funciona en el teléfono del supervisor.

## Hosting

Railway, Render o un VPS son suficientes para la sustentación. Si el servidor está en la planta,
verifica que sea alcanzable desde los dispositivos que usarán los supervisores — una instalación
solo accesible desde la red local de la oficina reintroduce el problema que el sistema resuelve.

## Verificación antes de abrir la ventana de observación

- [ ] Volumen persistente en `db` y una restauración de copia probada.
- [ ] HTTPS activo y service worker registrándose en un teléfono real.
- [ ] Zona horaria idéntica en los tres servicios.
- [ ] Secretos fuera del repositorio.
- [ ] Índices creados y migraciones aplicadas.
- [ ] Bitácora de despliegues iniciada.
- [ ] Pruebas de carga ejecutadas en preproducción, no aquí.
