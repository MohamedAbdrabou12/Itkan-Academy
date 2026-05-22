#!/bin/bash
set -e

# ══════════════════════════════════════════════════════════
#  Itkan Academy – Production Deploy Script
#  Run on your Hostinger VPS after cloning both repos.
# ══════════════════════════════════════════════════════════

DEPLOY_DIR="$(cd "$(dirname "$0")" && pwd)"
ENV_FILE="$DEPLOY_DIR/.env.production"

echo "─── Itkan Academy Deployment ───"

# 1. Check .env.production exists
if [ ! -f "$ENV_FILE" ]; then
  echo "ERROR: .env.production not found."
  echo "Copy .env.production.example to .env.production and fill in real values."
  exit 1
fi

# 2. Check frontend directory exists
if [ ! -d "$DEPLOY_DIR/frontend" ]; then
  echo "ERROR: frontend/ directory not found."
  echo "Clone or symlink Itkan-Academy-FE into $DEPLOY_DIR/frontend"
  exit 1
fi

# 3. Load env vars for docker-compose build args
set -a
source "$ENV_FILE"
set +a

# 4. Build and start
echo "Building images..."
docker compose -f docker-compose.prod.yml build --no-cache

echo "Starting services..."
docker compose -f docker-compose.prod.yml up -d

echo "─── Deployment complete ───"
echo "Services running:"
docker compose -f docker-compose.prod.yml ps
