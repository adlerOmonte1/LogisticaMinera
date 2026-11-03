"""Mensajes literales de los criterios de aceptación de M03 (RN-M05-08: la
interfaz no los reformula)."""

REGISTRADO = "Ingreso registrado con el código {codigo}"
REGISTRADO_EN_PROCESO = "Ingreso {codigo} registrado en proceso: pendiente del destare del vehículo {placa}"
SIN_IMAGEN = "Debe adjuntar la imagen del ticket de balanza"
CAMPOS_OBLIGATORIOS = "Debe completar los campos obligatorios"
PLACA_NO_REGISTRADA = "La placa {placa} no está registrada. Complete los datos del vehículo para continuar"
INCONSISTENCIAS = "Debe corregir o justificar las inconsistencias señaladas"
IMAGEN_INVALIDA = "La imagen debe estar en formato JPG o PNG y no superar los 10 MB"
VEHICULO_DE_BAJA = "El vehículo {placa} está dado de baja: no puede asociarse a un ingreso"
SUPERVISOR_SIN_ALTA_MINERAL = "Si no está en la lista, pida a un administrativo que lo registre"

ACTUALIZADO = "Ingreso {codigo} actualizado"
MOTIVO_CORRECCION = "Debe indicar el motivo de la corrección"
CORREGIR_ANULADO = "No se puede corregir un ingreso anulado"
MINERAL_FUERA_DEL_LOTE = "{mineral} no está en el lote {lote}. Agregue ese mineral al lote para corregir el ingreso"
SIN_CAMBIOS = "No hay cambios que guardar"
REVERTIDA = "Corrección revertida en el ingreso {codigo}"
SOLO_ULTIMA_CORRECCION = "Solo puede revertirse la última corrección del ingreso"

ANULADO = "Ingreso {codigo} anulado"
MOTIVO_ANULACION = "Debe indicar el motivo de la anulación"
YA_ANULADO = "El ingreso {codigo} ya fue anulado"

DESTARE_REGISTRADO = "Destare registrado"
TARA_OBLIGATORIA = "Debe indicar la tara del vehículo"
DESTARE_FUTURO = "La fecha del destare no puede ser posterior a la fecha actual"
SIN_PENDIENTES = "No hay vehículos pendientes de destare"

# Sin criterio que fije su texto: decididos en D-25.
BORRADOR_YA_REGISTRADO = "Este borrador ya se registró como el ingreso {codigo}"
SIN_CORRECCION_VIGENTE = "El ingreso {codigo} no tiene una corrección vigente que revertir"
