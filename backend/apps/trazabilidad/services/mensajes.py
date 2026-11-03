"""Mensajes literales de los criterios de aceptación de M06 (RN-M05-08: la
interfaz no los reformula). Los que no fija ningún criterio salen de la maqueta
o se deciden en D-26."""

# HU-M06-01
LOTE_ABIERTO = "Lote {nombre} abierto"
NOMBRE_DUPLICADO = "Ya existe un lote con el nombre «{nombre}»"
APERTURA_FUTURA = "La fecha de apertura no puede ser posterior a hoy"
CAMPOS_OBLIGATORIOS = "Debe completar los campos obligatorios"
INGRESO_ANULADO = "No se puede asignar un ingreso anulado"
INGRESO_EN_PROCESO = "El ingreso {codigo} está en proceso: falta el destare del vehículo"
YA_TRANSFORMADO = "El mineral del ingreso {codigo} ya pasó por zarandeo o molienda"
RECORRIDO_INICIADO = "Recorrido del lote {nombre} iniciado"
SIN_INGRESOS = "El lote no tiene ingresos asignados"
SELECCIONE_INGRESOS = "Seleccione al menos un ingreso"
MINERAL_YA_EN_LOTE = "El mineral {mineral} ya está en el lote"
MINERAL_CON_INGRESOS = "No se puede quitar {mineral}: tiene ingresos en el lote"
FALTA_AUTORIZACION = "Indique quién autorizó o el motivo para unificar otro tipo de mineral"
CONSERVAR_UN_INGRESO = "El lote {codigo} en recorrido debe conservar al menos un ingreso"
MINERAL_AGREGADO = "{mineral} agregado al lote"  # maqueta
MINERAL_QUITADO = "{mineral} quitado del lote"  # maqueta
QUITAR_SOLO_ABIERTO = "Solo se quitan minerales mientras el lote está Abierto"  # maqueta
CONSERVAR_UN_MINERAL = "El lote debe conservar al menos un tipo de mineral"  # maqueta
INGRESO_RETIRADO = "Ingreso retirado del lote"  # maqueta

# HU-M06-02
ETAPA_REGISTRADA = "Etapa {etapa} registrada para {nombre}"
ELIJA_RUTA = "Elija qué etapa sigue después del secado"
ETAPA_PREVIA = "El lote debe pasar primero por la etapa {etapa}"
ETAPA_REPETIDA = "La etapa {etapa} ya fue registrada para {nombre}"
LOTE_NO_INICIADO = "El lote debe iniciar su recorrido antes de registrar etapas"
ETAPA_FUTURA = "La fecha de la etapa no puede ser posterior a la fecha actual"
ETAPA_ANTES_DE_PREVIA = "La fecha de la etapa no puede ser anterior a la de la etapa {etapa}"
ETAPA_ANTES_DEL_INICIO = "La fecha de la etapa no puede ser anterior al inicio del recorrido"
SIN_ETAPAS_PENDIENTES = "No hay etapas pendientes para este lote"
HORAS_INVALIDAS = "Las horas de molienda deben ser mayores que cero"
YA_ENSACADO = "Lo registrado ya está ensacado: marque Recalcular e indique el peso de cada bigbag"
BIGBAGS_SIN_ENSACADO = "Los bigbags se asocian al registrar el ensacado"
LOTE_CERRADO = "El lote {codigo} ya fue cerrado"
SECADO_PROPIO = "Secado de {codigo} registrado"  # maqueta
BIGBAGS_ASOCIADOS = "{cantidad} bigbags asociados"  # maqueta

# HU-M06-04
LOTE_DIVIDIDO = "Lote dividido en {n} partes"
CAMPOS_DE_CADA_PARTE = "Debe completar los campos obligatorios de cada parte"
NOMBRES_REPETIDOS = "Cada parte debe tener un nombre distinto"
FRACCIONES_NO_SUMAN = "Las fracciones suman {suma} y deben sumar la unidad"
MAXIMO_SEIS = "Puede dividir el lote en seis partes como máximo"
YA_DIVIDIDO = "El lote ya fue dividido"
YA_AVANZO = "No se puede dividir: el lote ya avanzó por su ruta"
REPARTO_NO_SUMA = "Las fracciones del reparto suman {suma} y deben sumar la unidad"

# HU-M06-05
LOTE_CERRADO_CON_DESTINO = "Lote {nombre} cerrado con destino {destino}"
PENDIENTES = "Todavía no se puede cerrar el lote. Pendiente: {pendientes}"
SIN_DESTINO = "Debe indicar el destino del lote"
YA_CERRADO = "El lote ya fue cerrado"

# HU-M06-03
SIN_LOTE = "El ingreso aún no tiene lote y no ha recorrido ninguna etapa"

# Sin criterio que fije su texto: decididos en D-26.
MINIMO_DOS = "Divida el lote en dos partes como mínimo"
YA_INICIADO = "El recorrido del lote {nombre} ya se inició"
ETAPA_FUERA_DE_RUTA = "La etapa {etapa} no forma parte de la ruta de {nombre}"
INDIQUE_PARTE = "Indique la parte del lote dividido"
SECADO_CON_EL_LOTE = "El ingreso {codigo} se seca junto con el lote"
FRACCION_INVALIDA = "La fracción {fraccion} no es válida"
