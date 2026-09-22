# Guía del frontend — Angular en repositorio separado

**Documento:** transversal
**Aplica a:** repositorio `logistica-minera-frontend` (Angular 17+)
**Depende de:** `../model-c4/ARQ-02_Arquitectura_Tecnica.md` §4 y §6, `GUIA_MARCO_DE_TRABAJO.md`,
`decisiones_diseno.md` D-08, D-11, D-13

---

## 1. Por qué un repositorio aparte

El frontend se despliega como estáticos y el backend como servicio con base de datos: son dos ciclos
de vida distintos. Separarlos evita reconstruir y volver a desplegar la API por un cambio de
estilos, que durante el periodo de operación en planta es exactamente lo que hay que evitar (todo
despliegue en producción es un cambio no controlado en las condiciones de trabajo, `ARQ-02` §7).

El precio es que el contrato de la API deja de estar garantizado por el compilador. Las tres reglas
que lo compensan están en §7.

---

## 2. Arquitectura de carpetas: tres opciones

### Opción A — Plana por feature

```
features/ingresos/
  ingreso-form.component.ts
  ingreso-lista.component.ts
  ingresos.service.ts
  ingresos.routes.ts
```

Funciona hasta unos cinco o seis archivos por feature. M03 (captura de imagen, confirmación de
datos reconocidos, lista, detalle, corrección, anulación) los supera pronto, y a partir de ahí la
carpeta deja de decir qué hace cada archivo.

### Opción B — Feature con capas internas *(recomendada)*

```
features/ingresos/
  data-access/    servicio del feature: única puerta a HttpClient
  pages/          componentes ruteados (contenedores, con estado)
  ui/             componentes presentacionales (sin estado, solo entradas y salidas)
  ingresos.routes.ts
```

Reproduce en el cliente la separación que ya se aplica en el servidor, con la misma justificación:
cada capa tiene un motivo de cambio distinto.

| Backend | Frontend | Responsabilidad |
|---|---|---|
| `models/` | `models/` (raíz) | Formas del dominio |
| `repositories/` + `services/` | `features/<m>/data-access/` | Hablar con la fuente de datos |
| `views/` | `features/<m>/pages/` | Orquestar una pantalla |
| `serializers/` | `features/<m>/ui/` | Presentar |
| `utils/` | `core/` + `shared/` | Transversal |

La ganancia concreta: un componente de `ui/` que no inyecta servicios se prueba con entradas y
salidas, sin `HttpTestingController`. Eso se enseña en la revisión técnica abriendo una carpeta.

### Opción C — Monorepo Nx con librerías

Descartada. Aporta límites de dependencia y build incremental, cosas que rinden con varios equipos y
varias aplicaciones. Aquí hay una aplicación y un equipo reducido: el costo de aprender y configurar
Nx no se justifica.

**Decisión: opción B.** Registrada como D-11.

---

## 3. Estructura completa

```
logistica-minera-frontend/
  src/
    app/
      core/                          se instancia una sola vez
        interceptors/
          auth.interceptor.ts          adjunta el JWT
          error.interceptor.ts         traduce {codigo, mensaje, detalles}
        guards/
          sesion.guard.ts
          rol.guard.ts
        services/
          auth.service.ts
          borrador-registro.service.ts   conserva imagen y campos mientras no hay señal (RNF-M03-05)
          notificacion.service.ts
      shared/                        reutilizable y sin estado
        components/  directives/  pipes/
      models/                        espejo de los serializers del backend
        ingreso.model.ts  vehiculo.model.ts  tipo-mineral.model.ts
        reconocimiento.model.ts  validacion.model.ts  lote.model.ts
        pagina.model.ts   error-api.model.ts
      features/
        auth/               M01
        catalogo/            M02
        ingresos/             M03 (incluye las pantallas de reconocimiento y validacion, M04 y M05)
        trazabilidad/         M06
        consulta/             M07
        consolidacion/        M08
        auditoria/            M09
      app.config.ts   app.routes.ts   app.component.ts
    environments/
      environment.ts               desarrollo
      environment.preproduction.ts
      environment.production.ts
    styles.scss
  proxy.conf.json
  .env.example  (solo documenta; Angular no lee .env en tiempo de ejecución)
```

**M04 y M05 no tienen carpeta propia en `features/`.** Sus pantallas —los campos reconocidos con su
confianza, las inconsistencias señaladas— son parte del mismo flujo de registro y viven dentro de
`features/ingresos/`. Si fueran features aparte, M03 tendría que orquestar la navegación entre tres
pantallas para una sola operación, lo que fragmentaría un flujo que el usuario percibe como uno solo.

Simetría con el backend: M07 y M08 tampoco tienen `models/` propios aquí — consumen los de M03, M04,
M05 y M06 (D-10).

---

## 4. Instalación

### 4.1 Crear el repositorio

```bash
mkdir logistica-minera-frontend && cd logistica-minera-frontend
git init -b main
```

### 4.2 Generar el proyecto

```bash
npx @angular/cli@17 new logistica-minera-frontend \
  --directory . --standalone --routing --style=scss --ssr=false --skip-git
```

### 4.3 Componentes

```bash
ng add @angular/material
```

Angular Material y **nada más**: mezclarlo con otra librería de componentes duplica el peso del
bundle, que es lo que se descarga en un teléfono en planta.

No se agrega `@angular/pwa` ni ninguna librería de almacén con cola de reintento: la captura sin
señal de red no es un módulo del sistema (DR-01). El único requisito relacionado es RNF-M03-05
—conservar el borrador del registro en curso mientras no hay señal— y se resuelve con el
almacenamiento propio del navegador, sin service worker.

### 4.4 Crear el esqueleto

```bash
cd src/app
mkdir -p core/{interceptors,guards,services} shared/{components,directives,pipes} models

for f in auth catalogo ingresos trazabilidad consulta consolidacion auditoria; do
  mkdir -p features/$f/{data-access,pages,ui}
done
```

### 4.5 Entornos

Los nombres espejan los del backend (`development`, `preproduction`, `production`), para que no haya
que traducir mentalmente al desplegar.

```typescript
// src/environments/environment.ts
export const environment = {
  production: false,
  apiUrl: '/api/v1',            // el proxy lo redirige en desarrollo
  nombreEntorno: 'development',
};
```

```typescript
// src/environments/environment.production.ts
export const environment = {
  production: true,
  apiUrl: 'https://api.<dominio>/api/v1',
  nombreEntorno: 'production',
};
```

Declara los reemplazos en `angular.json`, bajo `fileReplacements` de cada configuración.

### 4.6 Proxy de desarrollo

```json
// proxy.conf.json
{
  "/api": {
    "target": "http://localhost:8000",
    "secure": false,
    "changeOrigin": true
  }
}
```

```bash
ng serve --proxy-config proxy.conf.json
```

Con el proxy, en desarrollo el navegador ve un solo origen y CORS deja de existir como problema. En
preproducción y producción sí hace falta: el backend debe declarar el origen del frontend en
`CORS_ALLOWED_ORIGINS` de su `.env`.

### 4.7 Calidad

```bash
ng add @angular-eslint/schematics
npm i -D prettier
```

---

## 5. La captura de imagen y la confirmación, en detalle

Es el flujo que distingue a este sistema de un formulario convencional, y el que más frontend nuevo
exige frente a un CRUD ordinario.

### 5.1 Captura

```html
<input type="file" accept="image/*" capture="environment" (change)="onImagen($event)">
```

`capture="environment"` abre la cámara trasera directamente, sin pantalla intermedia de selección
(RNF-M03-07). La imagen se reduce en el cliente antes de enviarse —con `canvas`, no con una
librería— porque una fotografía de teléfono actual supera con facilidad los 5 MB y casi todo ese
peso es irrelevante para leer un ticket impreso (RNF-M03-04).

### 5.2 Confirmación

La pantalla que sigue a la captura muestra los seis campos que propone el reconocimiento, cada uno
con su nivel de confianza, y las inconsistencias que ya señala la validación sobre esos datos
propuestos. Es una sola pantalla, no dos: el usuario revisa lectura e inconsistencia al mismo
tiempo, porque corregir un dato puede resolver ambas cosas a la vez.

- Los campos con confianza por debajo del umbral se resaltan sin depender solo del color.
- Un campo sin lectura se muestra vacío y editable, nunca con un valor inventado.
- Las inconsistencias se muestran junto al campo afectado, con el mensaje literal de la regla.
- **Nada de esto se ha persistido.** El envío ocurre solo cuando el usuario confirma; hasta entonces
  todo vive en el estado del componente (D-13).

### 5.3 El borrador

```typescript
// core/services/borrador-registro.service.ts
@Injectable({ providedIn: 'root' })
export class BorradorRegistroService {
  private clave = 'borrador-ingreso';

  guardar(datos: BorradorIngreso): void {
    try {
      localStorage.setItem(this.clave, JSON.stringify(datos));
    } catch {
      // almacenamiento no disponible: el registro continua, solo sin borrador
    }
  }

  recuperar(): BorradorIngreso | null { /* ... */ }
  descartar(): void { localStorage.removeItem(this.clave); }
}
```

El borrador se guarda con cada cambio y se descarta al confirmar. No hay reintento automático ni
envío en segundo plano: si la conexión se pierde, el usuario ve el aviso, y al recuperarla retoma el
formulario con sus datos intactos y confirma manualmente. La diferencia con una cola de
sincronización es deliberada: el ingreso siempre se confirma contra el servidor, nunca se compone
localmente un registro que después se envía sin supervisión.

---

## 6. Reglas de la estructura

**1. Solo `data-access/` inyecta `HttpClient`.** Ni `pages/`, ni `ui/`, ni `core/` fuera de sus
interceptores. Un `ApiService` global con treinta métodos obliga a cada componente a depender de
todo el sistema (ISP).

**2. `ui/` no inyecta servicios.** Recibe con `input()` y emite con `output()`. Si un componente de
`ui/` necesita un servicio, es un `pages/` mal ubicado.

**3. Las reglas de negocio no se replican como fuente de verdad** (D-08). Valida en el formulario
para la experiencia; la validación autoritativa es la del servidor.

**4. Los campos derivados o asignados por el servidor son `readonly`, nunca `disabled`.** Un control
deshabilitado **no viaja en el payload** de un formulario reactivo. Aplica al tipo de vehículo
(derivado de la placa), al código y a las dos marcas de tiempo del servidor.

**5. Los mensajes de error del servidor se muestran literales**, en el campo que corresponde. Ese
texto coincide con el criterio de aceptación y las pruebas del backend lo verifican por igualdad
exacta. No lo reformules.

**6. Un feature no importa de otro feature.** Lo compartido sube a `shared/` o a `models/`. Sin esta
regla la carga diferida deja de serlo: importar de un feature vecino arrastra su bundle.

---

## 7. Trabajar con dos repositorios

Lo que se pierde al separarlos hay que reponerlo con disciplina. Tres reglas:

**1. La documentación no se duplica.** `docs/` vive solo en el repositorio de documentación. El
repositorio del frontend lleva un `README.md` que enlaza a él y no repite ni requerimientos ni
historias. Dos copias de una historia divergen y la trazabilidad muere ahí.

**2. Misma convención de commits, en ambos repositorios.** `M04: reconoce los seis campos del ticket
con su confianza (HU-M04-01)`. La cadena `RF → módulo → HU → caso de prueba → commit` tiene que
poder reconstruirse aunque los commits estén repartidos en dos historiales.

**3. Etiqueta las dos puntas cuando el par de módulo esté cerrado.** `git tag M03-cerrado` en los
dos repositorios, el mismo día. Es lo que permite responder qué versión exacta del sistema estaba
desplegada en un momento dado.

Y una consecuencia operativa: `/api/v1/docs/` (el esquema OpenAPI que sirve el backend) pasa a ser
el contrato entre ambos repositorios. Si cambia un serializer, se revisa ahí antes de tocar
`models/`.
