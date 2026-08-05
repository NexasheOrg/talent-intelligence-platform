#!/usr/bin/env bash
# macOS / Linux equivalent of scripts/start-local.ps1: run the app without Docker.
#
# Uses SQLite (built into Python) instead of Postgres, so there is no database to install.
# Needs Python 3.10+ and Node 20+. See docs/RUN-WITHOUT-DOCKER.md.

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

WEB_URL="http://localhost:5173"

step() { printf "\n==> %s\n" "$1"; }
ok()   { printf "    OK  %s\n" "$1"; }
warn() { printf "    !   %s\n" "$1"; }
info() { printf "    %s\n" "$1"; }

problem() {
  printf "\n  X  %s\n\n     How to fix it:\n" "$1"
  shift
  for line in "$@"; do printf "       %s\n" "$line"; done
}

cleanup() {
  printf "\n  Stopping...\n"
  [ -n "${API_PID:-}" ] && kill "$API_PID" 2>/dev/null
  [ -n "${WEB_PID:-}" ] && kill "$WEB_PID" 2>/dev/null
  wait 2>/dev/null
}
trap cleanup EXIT INT TERM

printf "\n  Running without Docker (Python + Node)\n"

step "Checking Python"
PYTHON=""
for candidate in python3 python; do
  if command -v "$candidate" >/dev/null 2>&1 && "$candidate" -c 'import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)' 2>/dev/null; then
    PYTHON="$candidate"
    ok "$($candidate --version)"
    break
  fi
done
if [ -z "$PYTHON" ]; then
  problem "Python 3.10 or newer was not found." "Install it from https://www.python.org/downloads"
  exit 1
fi

step "Checking Node.js"
if ! command -v npm >/dev/null 2>&1; then
  problem "Node.js was not found." "Install the LTS version from https://nodejs.org"
  exit 1
fi
ok "Node $(node --version)"

VENV_PY="$ROOT/.venv/bin/python"
if [ ! -x "$VENV_PY" ]; then
  step "Creating a private Python environment (.venv)"
  "$PYTHON" -m venv "$ROOT/.venv"
  ok "Created."
fi

step "Installing Python packages"
"$VENV_PY" -m pip install --quiet --upgrade pip
"$VENV_PY" -m pip install --quiet -r "$ROOT/api/requirements.txt" || {
  problem "Installing the Python packages failed." "Usually a connection problem - check your internet."
  exit 1
}
ok "Python packages ready."

step "Building the local database from synthetic seed data"
export DATABASE_URL="sqlite:///data/local/tip.db"
"$VENV_PY" "$ROOT/data-platform/load_seed.py" || exit 1

if [ ! -d "$ROOT/web/node_modules" ]; then
  step "Installing the dashboard packages (first time only)"
  (cd "$ROOT/web" && npm install) || exit 1
fi

step "Starting the API and the dashboard"
"$VENV_PY" -m uvicorn app.main:app --app-dir api --port 8000 --reload &
API_PID=$!
(cd "$ROOT/web" && npm run dev) &
WEB_PID=$!

for _ in $(seq 1 45); do
  curl -sf -o /dev/null http://localhost:8000/health && break
  sleep 2
done

printf "\n  The app is running.\n\n"
printf "    Dashboard   %s\n" "$WEB_URL"
printf "    API docs    http://localhost:8000/docs\n\n"
printf "  Both restart automatically when you save a file.\n"
printf "  Press Ctrl+C to stop.\n\n"

if command -v open >/dev/null 2>&1; then open "$WEB_URL"; fi

wait
