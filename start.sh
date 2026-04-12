#!/bin/bash
# Start backend + frontend in parallel. Ctrl+C stops both.

ROOT="$(cd "$(dirname "$0")" && pwd)"
trap 'kill 0; exit' INT TERM

# --- Backend (FastAPI) ---
(
  cd "$ROOT/backend"
  if [ -d ".venv" ]; then
    source .venv/bin/activate
  elif [ -d "$ROOT/.venv" ]; then
    source "$ROOT/.venv/bin/activate"
  else
    echo "[backend] No .venv found – skipping backend"
    exit 1
  fi
  echo "[backend] Starting on :8000 ..."
  uvicorn main:app --reload --port 8000 --host 0.0.0.0
) &

# --- Frontend (Astro) ---
(
  cd "$ROOT/frontend"
  if [ ! -d "node_modules" ]; then
    echo "[frontend] Installing dependencies ..."
    npm install
  fi
  echo "[frontend] Starting dev server ..."
  npm run dev
) &

wait
