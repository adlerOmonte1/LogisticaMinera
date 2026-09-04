# Diagramas de secuencia — M01 Autenticación

## S-M01-01 · Inicio de sesión exitoso (HU-M01-01)

```mermaid
sequenceDiagram
    actor U as Usuario
    participant NG as Angular
    participant API as Django REST
    participant SRV as ServicioAuth
    participant DB as PostgreSQL
    participant AUD as Auditoria M08

    U->>NG: Ingresa usuario y contrasena
    NG->>API: POST /api/v1/auth/login/
    API->>SRV: autenticar(usuario, clave)
    SRV->>DB: Buscar usuario activo
    DB-->>SRV: Usuario encontrado
    SRV->>SRV: Verificar hash de contrasena
    SRV->>DB: Reiniciar intentos fallidos
    SRV->>AUD: Registrar evento INICIAR_SESION
    SRV-->>API: Token JWT + datos de rol
    API-->>NG: 200 con token y perfil
    NG->>NG: Almacenar token y construir menu por rol
    NG-->>U: Pantalla principal segun rol
```

## S-M01-02 · Intento fallido y bloqueo (HU-M01-01, CA03)

```mermaid
sequenceDiagram
    actor U as Usuario
    participant NG as Angular
    participant API as Django REST
    participant SRV as ServicioAuth
    participant DB as PostgreSQL

    U->>NG: Credenciales incorrectas
    NG->>API: POST /api/v1/auth/login/
    API->>SRV: autenticar(usuario, clave)
    SRV->>DB: Buscar usuario
    SRV->>SRV: Verificacion de hash falla
    SRV->>DB: Incrementar intentos_fallidos
    alt intentos_fallidos < 5
        SRV-->>API: Error de credenciales
        API-->>NG: 401 Usuario o contrasena incorrectos
    else intentos_fallidos = 5
        SRV->>DB: Marcar bloqueo hasta ahora + 15 min
        SRV-->>API: Error de bloqueo
        API-->>NG: 423 Cuenta bloqueada temporalmente
    end
    NG-->>U: Mensaje correspondiente
```

## S-M01-03 · Acceso a endpoint protegido (HU-M01-04, CA02)

```mermaid
sequenceDiagram
    participant NG as Angular
    participant INT as Interceptor JWT
    participant API as Django REST
    participant PER as Permisos por rol

    NG->>INT: Solicitud a recurso protegido
    INT->>INT: Adjuntar cabecera Authorization
    INT->>API: Solicitud con token
    API->>API: Validar firma y vigencia del token
    alt Token invalido o expirado
        API-->>NG: 401 Sesion expirada
    else Token valido
        API->>PER: Evaluar permiso del rol para la accion
        alt Rol sin permiso
            PER-->>API: Denegado
            API-->>NG: 403 Accion no autorizada
        else Rol con permiso
            PER-->>API: Autorizado
            API-->>NG: 200 con el recurso
        end
    end
```
