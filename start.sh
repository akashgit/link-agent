#!/usr/bin/env bash
set -e

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[start]${NC} $1"; }
warn() { echo -e "${YELLOW}[start]${NC} $1"; }

# --- PostgreSQL via Docker ---
log "Starting PostgreSQL..."
docker-compose -f "$ROOT_DIR/docker-compose.yml" up -d

# Wait for DB to be healthy
for i in {1..15}; do
  if docker-compose -f "$ROOT_DIR/docker-compose.yml" ps | grep -q "healthy"; then
    break
  fi
  sleep 1
done
log "PostgreSQL is ready."

# --- Backend ---
BACKEND_DIR="$ROOT_DIR/backend"
VENV="$BACKEND_DIR/.venv"

if [ ! -d "$VENV" ]; then
  warn "No virtualenv found. Creating one at $VENV..."
  python3 -m venv "$VENV"
fi

log "Installing backend dependencies..."
"$VENV/bin/pip" install -q -e "$BACKEND_DIR[dev]"

log "Running database migrations..."
cd "$BACKEND_DIR"
"$VENV/bin/alembic" upgrade head

log "Starting backend (uvicorn)..."
"$VENV/bin/uvicorn" app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# --- Frontend ---
FRONTEND_DIR="$ROOT_DIR/frontend"

cd "$FRONTEND_DIR"
if [ ! -d "node_modules" ]; then
  log "Installing frontend dependencies..."
  npm install
fi

log "Starting frontend (Next.js dev)..."
npm run dev &
FRONTEND_PID=$!

# --- Trap for cleanup ---
cleanup() {
  log "Shutting down..."
  kill $BACKEND_PID 2>/dev/null || true
  kill $FRONTEND_PID 2>/dev/null || true
  wait
  log "Done."
}
trap cleanup INT TERM

log "Ready!"
log "  Backend:  http://localhost:8000"
log "  Frontend: http://localhost:3000"
log "  Press Ctrl+C to stop."

wait
