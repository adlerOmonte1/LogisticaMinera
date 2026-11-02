#!/usr/bin/env bash
# Respaldo minimo ejecutable (D-20): volcado de la base y copia del volumen media,
# tomados en el mismo momento y fechados juntos. Uso, desde la raiz del repositorio:
#   bash scripts/respaldo.sh [directorio_destino]
# Por defecto deja los archivos en respaldos/ (fuera de git).
set -euo pipefail

destino="${1:-respaldos}"
marca="$(date +%Y%m%d-%H%M%S)"
mkdir -p "$destino"

docker compose exec -T db pg_dump -U logistica -d logistica_minera_dev --format=custom \
  > "$destino/base-$marca.dump"
docker compose exec -T backend tar -czf - -C /app media > "$destino/media-$marca.tar.gz"

echo "Respaldo creado: $destino/base-$marca.dump y $destino/media-$marca.tar.gz"
