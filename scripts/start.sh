#!/usr/bin/env bash
# macOS / Linux equivalent of START-HERE.bat.
#
# Double-click `start.command` in Finder, or run `./scripts/start.sh` in a terminal.
# Prefers Docker; falls back to Python + Node (SQLite) if Docker isn't available.

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

DASHBOARD_URL="http://localhost:8080"
API_URL="http://localhost:8000"

step() { printf "\n==> %s\n" "$1"; }
ok()   { printf "    OK  %s\n" "$1"; }
warn() { printf "    !   %s\n" "$1"; }
info() { printf "    %s\n" "$1"; }

problem() {
  printf "\n  X  %s\n\n     How to fix it:\n" "$1"
  shift
  for line in "$@"; do printf "       %s\n" "$line"; done
}

open_browser() {
  if command -v open >/dev/null 2>&1; then open "$1"
  elif command -v xdg-open >/dev/null 2>&1; then xdg-open "$1" >/dev/null 2>&1
  else info "Open $1 in your browser."
  fi
}

wait_for_url() {
  local url=$1 timeout=$2 what=$3 waited=0
  while [ "$waited" -lt "$timeout" ]; do
    if curl -sf -o /dev/null "$url"; then
      printf "\r    OK  %s is ready.                       \n" "$what"
      return 0
    fi
    printf "\r    . waiting for %s (%ss)" "$what" "$waited"
    sleep 2
    waited=$((waited + 2))
  done
  printf "\r                                                \r"
  return 1
}

printf "\n  Talent & Delivery Intelligence Platform\n"
printf "  Starting your local copy of the app.\n"

# ------------------------------------------------------------------ pick a route

use_docker=1
step "Checking Docker"
if ! command -v docker >/dev/null 2>&1; then
  warn "Docker is not installed."
  use_docker=0
elif ! docker info >/dev/null 2>&1; then
  warn "Docker is installed but not running."
  if [ -d "/Applications/Docker.app" ]; then
    info "Starting Docker Desktop; this takes a minute or two..."
    open -a Docker
    for _ in $(seq 1 90); do
      sleep 2
      docker info >/dev/null 2>&1 && break
    done
  fi
  docker info >/dev/null 2>&1 || use_docker=0
fi

if [ "$use_docker" -eq 0 ]; then
  problem "Docker Desktop is not available." \
    "Option 1 - install it: https://www.docker.com/products/docker-desktop" \
    "Option 2 - run without it (needs Python 3.12+ and Node 20+)."
  printf "\n"
  read -r -p "  Try running without Docker now? (y/n) " answer
  case "$answer" in
    [Yy]*) exec "$ROOT/scripts/start-local.sh" ;;
    *) exit 1 ;;
  esac
fi
ok "Docker is running."

# ------------------------------------------------------------------ ports

step "Checking ports 8080, 8000 and 5433"
busy=""
for port in 8080 8000 5433; do
  if lsof -nP -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1; then busy="$busy $port"; fi
done

if [ -n "$busy" ]; then
  warn "In use:$busy - stopping any previous run of this app..."
  docker compose down >/dev/null 2>&1
  sleep 2
  still=""
  for port in 8080 8000 5433; do
    if lsof -nP -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1; then still="$still $port"; fi
  done
  if [ -n "$still" ]; then
    problem "Port(s)$still are still in use by another program." \
      "Find it with:  lsof -nP -iTCP:${still# } -sTCP:LISTEN" \
      "Close it, then run this again."
    exit 1
  fi
else
  ok "All free."
fi

# ------------------------------------------------------------------ build & run

step "Building and starting the app"
info "The first run takes 3 to 10 minutes. Later runs take seconds."
printf "\n"

if ! docker compose up --build -d; then
  problem "Docker could not start the app." \
    "The real reason is in the output above." \
    "Common causes: no internet, or Docker is out of disk space."
  exit 1
fi

step "Waiting for the app to finish starting"
if ! wait_for_url "$API_URL/health" 240 "the API"; then
  problem "The app started but the API never came up." \
    "Run:  docker compose logs api" \
    "and:  docker compose logs loader"
  exit 1
fi
wait_for_url "$DASHBOARD_URL" 60 "the dashboard" || warn "Dashboard slow to answer; try it anyway."

printf "\n  The app is running.\n\n"
printf "    Dashboard   %s\n" "$DASHBOARD_URL"
printf "    API docs    %s/docs\n\n" "$API_URL"
printf "  Stop it with: docker compose down\n"

open_browser "$DASHBOARD_URL"
