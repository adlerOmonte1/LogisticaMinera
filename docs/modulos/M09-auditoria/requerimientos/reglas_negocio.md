# Reglas de negocio — M09 Auditoría

> Ubicación en el código: `apps/auditoria/models/` (invariantes del evento) y
> `apps/auditoria/services/` (el servicio de registro que invocan los demás módulos). Ninguna de
> estas reglas vive en `views/` ni en un componente Angular (D-08).

| Código | Regla | Consecuencia si se viola |
|---|---|---|
| RN-M09-01 | Todo evento se registra dentro de la misma transacción que la operación que describe | Podría quedar una operación sin su evento, o un evento sin la operación que dice describir |
| RN-M09-02 | Ningún evento se crea, modifica ni elimina fuera del flujo de la operación que lo genera | El histórico dejaría de ser una fuente confiable si pudiera reescribirse después de los hechos |
| RN-M09-03 | Una modificación registra el valor anterior y el nuevo del campo cambiado | No se podría reconstruir qué decía el registro antes del cambio |
| RN-M09-04 | Un intento de operación rechazado por falta de autorización se registra igual que uno completado | No se podría demostrar que el control de acceso funciona, solo que existe |
| RN-M09-05 | El catálogo de acciones auditables es único y compartido por todos los módulos | Cada módulo con su propio catálogo de acciones haría el historial incomparable entre entidades |
| RN-M09-06 | El usuario de un evento es el que ejecutó la operación, nunca uno indicado por el cliente | Un evento con autor falso invalidaría la atribución de todo el histórico |

## Nota sobre RN-M09-01

Es la regla más fácil de romper sin darse cuenta. Registrar el evento después del `commit` de la
operación principal parece inofensivo —"si la operación ya se guardó, el evento solo la describe"—
pero abre una ventana en la que la operación existe sin su evento si el proceso falla entre ambos
pasos. El evento se escribe dentro de la misma transacción precisamente para que ambos ocurran
juntos o ninguno ocurra.

## Nota sobre RN-M09-02

Un histórico que admitiera corrección dejaría de ser evidencia de nada: cualquier alteración
retroactiva sería indistinguible de un registro legítimo. Por eso el evento no tiene operación de
edición ni de borrado expuesta en ningún endpoint, con independencia del rol.
