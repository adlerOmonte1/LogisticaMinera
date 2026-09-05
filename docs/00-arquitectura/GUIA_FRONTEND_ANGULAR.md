# Guía del frontend — Angular en repositorio separado

**Documento:** transversal
**Aplica a:** repositorio `logistica-minera-frontend` (Angular 17+, PWA)
**Depende de:** `ARQ-02_Arquitectura_Tecnica.md` §4 y §6, `GUIA_MARCO_DE_TRABAJO.md`, `decisiones_diseno.md` D-04, D-08, D-11

---

## 1. Por qué un repositorio aparte

El frontend se despliega como estáticos y el backend como servicio con base de datos: son dos ciclos
de vida distintos. Separarlos evita reconstruir y volver a desplegar la API por un cambio de estilos,
que en la ventana de observación del postest es exactamente lo que hay que evitar (todo despliegue en
producción es una amenaza a la validez interna, `ARQ-02` §7).

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

Es la que hoy describe `ARQ-02` §4. Funciona hasta unos cinco o seis archivos por feature. M03
(formulario de alta, lista, detalle, anulación, borrador offline) los supera en la semana 3, y a
partir de ahí la carpeta deja de decir qué hace cada archivo.

### Opción B — Feature con capas internas *(recomendada)*

```
features/ingresos/
  data-access/    servicio del feature: única puerta a HttpClient
  pages/          componentes ruteados (contenedores, con estado)
  ui/             componentes presentacionales (sin estado, solo entradas y salidas)
  ingresos.routes.ts
```

Reproduce en el cliente la separación que ya aplicas en el servidor, con la misma justificación:
cada capa tiene un motivo de cambio distinto.

| Backend | Frontend | Responsabilidad |
|---|---|---|
| `models/` | `models/` (raíz) | Formas del dominio |
| `repositories/` + `services/` | `features/<m>/data-access/` | Hablar con la fuente de datos |
| `views/` | `features/<m>/pages/` | Orquestar una pantalla |
| `serializers/` | `features/<m>/ui/` | Presentar |
| `utils/` | `core/` + `shared/` | Transversal |

La ganancia concreta: un componente de `ui/` que no inyecta servicios se prueba con entradas y
salidas, sin `HttpTestingController`. Eso sostiene la característica *capacidad de ser probado* de
ISO/IEC 25010 que afirma la tesis, y se enseña en sustentación abriendo una carpeta.

### Opción C — Monorepo Nx con librerías

Descartada. Aporta límites de dependencia y build incremental, cosas que rinden con varios equipos y
varias aplicaciones. Aquí hay una aplicación, un desarrollador y ocho semanas: el costo de aprender y
configurar Nx sale del presupuesto de M07, que es el módulo diferenciador.

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
          offline.interceptor.ts       encola cuando no hay red (M07)
        guards/
          sesion.guard.ts
          rol.guard.ts
        services/
          auth.service.ts
          conectividad.service.ts
          cola-sincronizacion.service.ts
          notificacion.service.ts
      shared/                        reutilizable y sin estado
        components/  directives/  pipes/
      models/                        espejo de los serializers del backend
        ingreso.model.ts  vehiculo.model.ts  producto.model.ts
        pagina.model.ts   error-api.model.ts
      features/
        autenticacion/   M01
        catalogo/        M02
        ingresos/        M03
        salidas/         M04
        existencias/     M05
        reportes/        M06
        auditoria/       M08
        busqueda/        M09
      app.config.ts   app.routes.ts   app.component.ts
    environments/
      environment.ts               desarrollo
      environment.preproduction.ts
      environment.production.ts
    styles.scss
  proxy.conf.json
  ngsw-config.json
  .env.example  (solo documenta; Angular no lee .env en tiempo de ejecución)
```

**M07 no tiene carpeta en `features/`.** La captura sin conexión es transversal: vive en
`core/` como interceptor más cola. Si fuera una pantalla más, M03 tendría que saber si hay red, y esa
es justamente la dependencia que D-04 prohíbe.

Simetría con el backend: M06 y M09 tampoco tienen `models/` propios aquí — consumen los de M03, M04 y
M05 (D-10).

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

Sin SSR: la aplicación debe funcionar sin red desde el dispositivo (D-04); un render en servidor
contradice el requisito central de M07.

### 4.3 PWA y componentes — en la semana 1, no al final

```bash
ng add @angular/pwa
ng add @angular/material
npm i idb
```

`ng add @angular/pwa` va **ahora**. D-04 es explícita: el service worker es arquitectura, no una
funcionalidad agregable. Angular Material y **nada más**: mezclarlo con otra librería de componentes
duplica el peso del bundle, que es lo que se descarga en un teléfono con conectividad intermitente.

### 4.4 Crear el esqueleto

```bash
cd src/app
mkdir -p core/{interceptors,guards,services} shared/{components,directives,pipes} models

for f in autenticacion catalogo ingresos salidas existencias reportes auditoria busqueda; do
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

## 5. Reglas de la estructura

**1. Solo `data-access/` inyecta `HttpClient`.** Ni `pages/`, ni `ui/`, ni `core/` fuera de sus
interceptores. Un `ApiService` global con treinta métodos obliga a cada componente a depender de todo
el sistema (ISP).

**2. `ui/` no inyecta servicios.** Recibe con `input()` y emite con `output()`. Si un componente de
`ui/` necesita un servicio, es un `pages/` mal ubicado.

**3. Las reglas de negocio no se replican como fuente de verdad** (D-08). Valida en el formulario para
la experiencia; la validación autoritativa es la del servidor, porque un registro que entra por la
cola de M07 no pasa por ningún formulario.

**4. Los campos calculados son `readonly`, nunca `disabled`.** Un control deshabilitado **no viaja en
el payload** de un formulario reactivo. Aplica al peso neto (HU-M03-01 CA03).

**5. Los mensajes de error del servidor se muestran literales**, en el campo que corresponde. Ese
texto coincide con el criterio de aceptación y las pruebas del backend lo verifican por igualdad
exacta. No lo reformules.

**6. Un feature no importa de otro feature.** Lo compartido sube a `shared/` o a `models/`. Sin esta
regla la carga diferida deja de serlo: importar de un feature vecino arrastra su bundle.

---

## 6. Orden de construcción

| Semana | Frontend |
|---|---|
| 1 | Esqueleto, PWA, Material, `core/` (interceptores y guards), login de M01 |
| 2 | M02 catálogo; inicio del formulario de M03 |
| 3 | M03 completo: alta, lista, detalle, anulación |
| 4 | Cola offline en `core/`: IndexedDB, indicador de pendientes, reintento |
| 5 | M04 y M05 |
| 6 | M09 búsqueda |
| 7 | M06 reportes y descargas |
| 8 | Ajustes de RNF tras las pruebas de carga |

Coincide con `ARQ-01` §3. El frontend de un módulo va en la misma semana que su backend: un módulo
terminado es el par completo, no la mitad.

---

## 7. Trabajar con dos repositorios

Lo que se pierde al separarlos hay que reponerlo con disciplina. Tres reglas:

**1. La documentación no se duplica.** `docs/` vive solo en el repositorio de la tesis. El repositorio
del frontend lleva un `README.md` que enlaza a él y no repite ni requerimientos ni historias. Dos
copias de una historia divergen y la trazabilidad muere ahí.

**2. Misma convención de commits, en ambos repositorios.** `M03: registra hora de pesaje separada de
hora de registro (HU-M03-01)`. La cadena `indicador → RF → módulo → HU → caso de prueba → commit`
tiene que poder reconstruirse aunque los commits estén repartidos en dos historiales.

**3. Etiqueta las dos puntas cuando el par module esté cerrado.** `git tag M03-cerrado` en los dos
repositorios, el mismo día. Es lo que permite responder en sustentación con qué versión exacta del
sistema se recolectó el postest.

Y una consecuencia operativa: `/api/v1/docs/` (el esquema OpenAPI que sirve el backend) pasa a ser el
contrato entre ambos repositorios. Si cambia un serializer, se revisa ahí antes de tocar `models/`.
