#!/usr/bin/env bash
# Auto-despliegue de EVAS Admin en el HomeLab.
#
# Se ejecuta por timer y SOLO actualiza si `origin/main` avanza en línea recta
# (fast-forward) desde el commit desplegado. Nunca hace downgrade.
#
# Requisitos: repo en /opt/apps/eva_admin, docker compose, acceso de LECTURA a
# GitHub (repo público). Al hacer push a origin/main, el servidor se actualiza.
set -euo pipefail

REPO=/opt/apps/eva_admin
cd "$REPO"

git config --global --add safe.directory "$REPO" 2>/dev/null || true

git fetch origin main --prune --quiet || { echo "fetch fallo"; exit 0; }
HEAD_SHA=$(git rev-parse HEAD)
REMOTE_SHA=$(git rev-parse origin/main)

if [ "$HEAD_SHA" = "$REMOTE_SHA" ]; then
  exit 0
fi

if ! git merge-base --is-ancestor "$HEAD_SHA" "$REMOTE_SHA"; then
  echo "origin/main no es descendiente del commit desplegado; se omite (evita downgrade)"
  exit 0
fi

echo "Actualizando de $HEAD_SHA a $REMOTE_SHA"
git reset --hard "$REMOTE_SHA"

COMPOSE="docker compose -f ops/compose.prod.yaml"
$COMPOSE build
$COMPOSE run --rm --no-deps api alembic upgrade head
$COMPOSE up -d
echo "desplegado: $(git log --oneline -1)"
