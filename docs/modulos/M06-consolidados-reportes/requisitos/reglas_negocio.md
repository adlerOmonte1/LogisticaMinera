# Reglas de negocio — M06 Consolidados y reportes

> Ubicación en el código: `apps/reportes/services/` y `apps/reportes/repositories/`.

| Código | Regla | Consecuencia si se viola |
|---|---|---|
| RN-M06-01 | El consolidado incluye únicamente documentos en estado REGISTRADO; los anulados se excluyen del cálculo | Se contarían toneladas de ingresos invalidados |
| RN-M06-02 | El consolidado reporta la cantidad de documentos anulados del periodo por separado | Se ocultaría la magnitud de las correcciones realizadas |
| RN-M06-03 | La producción se desagrega siempre por titularidad del vehículo | Se perdería el hallazgo central del estudio en el reporte que la gerencia consulta |
| RN-M06-04 | Un periodo sin movimientos genera consolidado con valores en cero, no un error | El indicador I6 se degradaría por una causa ajena a la operación |
| RN-M06-05 | El consolidado es un cálculo derivado: no se almacena como dato editable | Un reporte editado dejaría de reflejar los registros y sería inauditable |
| RN-M06-06 | Toda exportación identifica el periodo, la fecha de generación y el usuario responsable | Un archivo circulando sin contexto podría atribuirse a un periodo equivocado |
| RN-M06-07 | El sistema no transmite la declaración semestral a ninguna entidad externa; solo produce el archivo | Se asumiría una responsabilidad legal fuera del alcance del proyecto |
| RN-M06-08 | El saldo de cierre del consolidado proviene de M05 y no se recalcula de forma independiente | Dos cálculos paralelos del stock podrían divergir |

## Nota sobre RN-M06-05

El consolidado no se guarda como un registro con sus cifras congeladas. Se recalcula cada vez a partir de los documentos vigentes. Esto significa que si un ingreso de marzo se anula en abril, el consolidado de marzo cambia.

Es la decisión correcta —el reporte debe reflejar el estado real de los registros—, pero tiene una consecuencia que debe documentarse: **los archivos exportados son fotografías de un momento**. Por eso RN-M06-06 exige que toda exportación lleve su fecha de generación: dos archivos del mismo mes generados en fechas distintas pueden diferir legítimamente, y el encabezado permite explicar por qué.

## Nota sobre RN-M06-07

El alcance termina en la generación del archivo. La revisión, validación y presentación de la declaración semestral son responsabilidad del personal de la empresa. Esta frontera está declarada en `../../00-arquitectura/ARQ-01_Modulos_del_Sistema.md` §5 y conviene tenerla presente para sustentación.
