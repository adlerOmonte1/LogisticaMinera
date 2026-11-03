#!/usr/bin/env bash
# Restauracion del respaldo de D-20. Reemplaza la base y las imagenes actuales.
# Uso, desde la raiz del repositorio:
#   bash scripts/restaurar.sh respaldos/base-AAAAMMDD-HHMMSS.dump respaldos/media-AAAAMMDD-HHMMSS.tar.gz
set -euo pipefail

base="$1"
media="$2"

docker compose exec -T db pg_restore -U logistica -d logistica_minera_dev --clean --if-exists \
  --no-owner < "$base"
docker compose exec -T backend sh -c 'rm -rf /app/media/* && tar -xzf - -C /app' < "$media"

echo "Restaurados $base y $media"
