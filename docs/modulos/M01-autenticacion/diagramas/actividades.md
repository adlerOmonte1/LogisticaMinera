# Diagrama de actividades — M01 Autenticación

## A-M01-01 · Proceso de autenticación (RN-M01-05, RN-M01-07)

```mermaid
flowchart TD
    Start([Solicitud de inicio de sesion]) --> V1{Campos completos?}
    V1 -->|No| E1[Mostrar: Complete los campos obligatorios]
    E1 --> Fin([Fin])
    V1 -->|Si| B1[Buscar usuario por nombre de usuario]
    B1 --> V2{Usuario existe?}
    V2 -->|No| E2[Mostrar: Usuario o contrasena incorrectos]
    E2 --> Fin
    V2 -->|Si| V3{Cuenta bloqueada?}
    V3 -->|Si| E3[Mostrar: Cuenta bloqueada temporalmente]
    E3 --> Fin
    V3 -->|No| V4{Usuario activo?}
    V4 -->|No| E4[Mostrar: La cuenta se encuentra inactiva]
    E4 --> Fin
    V4 -->|Si| V5{Contrasena correcta?}
    V5 -->|No| I1[Incrementar intentos fallidos]
    I1 --> V6{Intentos = 5?}
    V6 -->|Si| B2[Bloquear 15 minutos]
    B2 --> E3
    V6 -->|No| E2
    V5 -->|Si| R1[Reiniciar intentos fallidos]
    R1 --> T1[Emitir token JWT]
    T1 --> A1[Registrar evento en auditoria]
    A1 --> D1[Dirigir a pantalla principal del rol]
    D1 --> Fin
```

## A-M01-02 · Desactivación de usuario (RN-M01-03)

```mermaid
flowchart TD
    Start([Administrador solicita eliminar usuario]) --> V1{Rol es Administrador?}
    V1 -->|No| E1[Rechazar: Accion no autorizada]
    E1 --> Fin([Fin])
    V1 -->|Si| V2{Usuario tiene registros asociados?}
    V2 -->|Si| B1[Baja logica: activo = falso]
    V2 -->|No| B1
    B1 --> A1[Registrar evento en auditoria]
    A1 --> M1[Confirmar: Usuario desactivado]
    M1 --> Fin
```

La bifurcación de V2 converge deliberadamente: el sistema **nunca** elimina físicamente, tenga o no registros asociados. Se representa la decisión para hacer explícito que fue evaluada y descartada (ver decisión D-07).
