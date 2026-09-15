# Diagramas de actividades — M07 Captura sin conexión

## A-M07-01 · Ciclo de vida de un ingreso capturado sin conexión

```mermaid
flowchart TD
    Start([Volquete llega a planta sin senal]) --> C1[Supervisor abre la aplicacion]
    C1 --> C2[Aplicacion carga desde cache del service worker]
    C2 --> C3[Formulario lee catalogos de IndexedDB]
    C3 --> V1{Catalogo con mas de 7 dias?}
    V1 -->|Si| W1[Mostrar advertencia y permitir continuar]
    V1 -->|No| L1[Transcribir datos del ticket]
    W1 --> L1
    L1 --> V2{Validacion local correcta?}
    V2 -->|No| E1[Mostrar el mismo mensaje que en linea]
    E1 --> L1
    V2 -->|Si| G1[Generar UUID local y capturar hora del dispositivo]
    G1 --> G2[Guardar en cola de IndexedDB]
    G2 --> M1[Mostrar: Guardado en el dispositivo]
    M1 --> W2[Esperar recuperacion de conexion]
    W2 --> D1{Conexion disponible?}
    D1 -->|No| W2
    D1 -->|Si| S1[Enviar lote en orden de captura]
    S1 --> D2{Respuesta del servidor?}
    D2 -->|ACEPTADO| A1[Retirar de la cola y mostrar correlativo]
    A1 --> Fin([Ingreso sincronizado])
    D2 -->|RECHAZADO| R1[Conservar en cola con el motivo]
    R1 --> D3{Usuario corrige?}
    D3 -->|Si| S1
    D3 -->|No| R2[Permanece pendiente de intervencion]
    R2 --> Fin2([Requiere decision del usuario])
    D2 -->|Sin respuesta| C4[Incrementar contador de intentos]
    C4 --> D4{Tres intentos fallidos?}
    D4 -->|No| W2
    D4 -->|Si| R2
```

## A-M07-02 · Asignación de la hora de registro en sincronización (RN-M07-01, RN-M07-02)

```mermaid
flowchart TD
    Start([Servidor recibe ingreso sincronizado]) --> L1[Leer hora_captura_local del elemento]
    L1 --> V1{Hora de captura posterior a la hora del servidor?}
    V1 -->|Si| E1[Rechazar: hora de captura invalida]
    E1 --> Fin([Fin])
    V1 -->|No| A1[hora_registro = hora_captura_local]
    A1 --> A2[hora_sincronizacion = hora actual del servidor]
    A2 --> A3[Persistir ambos campos por separado]
    A3 --> N1[Latencia I1 se calcula sobre hora_registro]
    N1 --> Fin
```

Este es el diagrama más importante del módulo para la confiabilidad de la medición. Si la asignación de A1 tomara la hora del servidor en lugar de la hora de captura, el indicador I1 mediría disponibilidad de red y no oportunidad del registro. El error no produciría ningún síntoma visible en el funcionamiento del sistema.

## A-M07-03 · Decisión de reintento y límite de intentos (RN-M07-09)

```mermaid
flowchart TD
    Start([Elemento en cola]) --> D1{Conexion disponible?}
    D1 -->|No| W1[Esperar evento de reconexion]
    W1 --> D1
    D1 -->|Si| S1[Intentar envio]
    S1 --> D2{Resultado?}
    D2 -->|Aceptado| OK[Retirar de la cola]
    OK --> Fin([Fin])
    D2 -->|Rechazado por validacion| M1[Marcar con motivo y detener reintentos]
    M1 --> Fin
    D2 -->|Fallo de red| I1[Incrementar contador de intentos]
    I1 --> D3{Contador igual a tres?}
    D3 -->|No| W1
    D3 -->|Si| M2[Detener reintento automatico y solicitar intervencion]
    M2 --> Fin
```

La distinción entre "rechazado por validación" y "fallo de red" importa: el primero no mejora reintentando —el dato es inválido y requiere corrección—, el segundo sí. Reintentar indefinidamente un elemento inválido consumiría batería y datos sin resolver nada.
