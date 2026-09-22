#!/usr/bin/env bash
# Detecta conceptos del sistema anterior en docs/ y skills/.
# Uso: bash scripts/verificar_migracion.sh
#
# Este script es la fuente unica del patron de terminos retirados. Las skills y los
# documentos lo invocan en lugar de transcribirlo, para no reintroducir esos terminos.

patrones='Producci[oó]n y Existencias|RF-[0-9]{2}|\bstock\b|kardex|\bmerma\b|declaraci[oó]n semestral|Ley 32213|sin conexi[oó]n|IndexedDB|cobertura de registro|meses con consolidado|JMeter|m[oó]dulos implementados|hora_pesaje|hora_registro|Relaci[oó]n con el indicador|Indicador de tesis|M0[4-7]-(salidas|existencias|consolidados|sin-conexion)'

# Una linea puede eximirse marcandola con el comentario  <!-- migracion:ok -->  al final.
# Se usa solo para instrucciones que nombran el termino para prohibirlo, y para el historial
# de decisiones retiradas.

# Documentos que describen la propia migracion y deben conservar la terminologia antigua.
exclusiones='docs/REFORMULACION.md|docs/PLAN_TRABAJO.md|docs/00-tesis/auditoria_migracion.md|scripts/verificar_migracion.sh'

hallazgos=$(grep -rnE "$patrones" docs skills --include=*.md 2>/dev/null \
  | grep -vE "$exclusiones" \
  | grep -v 'migracion:ok')

if [ -z "$hallazgos" ]; then
  echo "OK: sin conceptos del sistema anterior"
  exit 0
fi

echo "$hallazgos"
echo "---"
echo "Hallazgos: $(echo "$hallazgos" | wc -l | tr -d ' ')"
exit 1
