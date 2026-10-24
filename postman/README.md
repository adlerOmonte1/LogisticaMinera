# Colección de Postman

Validación de la API fase por fase, según
[`docs/01-plan/PLAN_IMPLEMENTACION.md`](../docs/01-plan/PLAN_IMPLEMENTACION.md) (PLAN-02 §4).

| Archivo | Contenido |
|---|---|
| `LogisticaMinera.postman_collection.json` | La colección: «00 · Sesiones» y una carpeta por fase |
| `entornos/local.postman_environment.json` | Backend en el equipo, con las cuentas de prueba del comando de carga |
| `archivos/` | Imágenes de prueba del registro de ingresos (se agregan en F3) |

Las credenciales del entorno local son de prueba: las crea `cargar_datos_prueba`, que solo corre con
`DEBUG` activo. Ninguna credencial real entra en este directorio.

## Preparar el backend

Con Docker Compose, desde la raíz del repositorio:

```bash
docker compose up -d --build
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py cargar_datos_prueba
```

Para repetir una ejecución desde cero:

```bash
docker compose exec backend python manage.py flush --no-input
docker compose exec backend python manage.py cargar_datos_prueba
```

## Ejecutar en Postman

1. *Import* → los dos archivos JSON de este directorio.
2. Seleccionar el entorno «LogisticaMinera · local».
3. *Runner* → la colección → marcar «00 · Sesiones» y la carpeta de la fase, y las de las fases
   anteriores para la regresión → *Run*.

## Ejecutar con Newman

```bash
npx newman run postman/LogisticaMinera.postman_collection.json \
  -e postman/entornos/local.postman_environment.json \
  --folder "00 · Sesiones" --folder "F0 · Salud y esquema" \
  --reporters cli,junit --reporter-junit-export docs/03-pruebas/evidencias/F0/newman.xml
```

## Convenciones

- Cada solicitud se nombra `HU-Mxx-nn · CAnn · Caso -> código HTTP`; en F0, `F0 · Caso -> código`.
- Cada solicitud declara su rol con `Authorization: Bearer {{token_rol}}`.
- Los rechazos comprueban el cuerpo uniforme `{codigo, mensaje, detalles}` y el mensaje literal del
  criterio de aceptación (D-23).
