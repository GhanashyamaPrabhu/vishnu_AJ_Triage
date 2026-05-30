#!/bin/bash
# ─────────────────────────────────────────────────────────────
#  AJ Institute SATS AI Co-Pilot — single launch script
#  Usage:  ./start.sh
#  Stop:   Ctrl+C  (kills both backend and frontend)
# ─────────────────────────────────────────────────────────────

ROOT="$(cd "$(dirname "$0")" && pwd)"

# Colours
GREEN='\033[0;32m'; BLUE='\033[0;34m'; RESET='\033[0m'

echo -e "${BLUE}"
echo "  ╔══════════════════════════════════════════════╗"
echo "  ║   AJ Institute — SATS AI Co-Pilot            ║"
echo "  ║   Paediatric Triage System                   ║"
echo "  ╚══════════════════════════════════════════════╝"
echo -e "${RESET}"

# Kill any stale instances
pkill -f "uvicorn main:app" 2>/dev/null
pkill -f "vite"             2>/dev/null
sleep 0.5

# ── Backend ──────────────────────────────────────────────────
echo -e "${GREEN}▶  Starting backend  (http://localhost:8000)${RESET}"
cd "$ROOT/backend"
python3 -m uvicorn main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --env-file "$ROOT/.env" \
    --log-level warning &
BACKEND_PID=$!

# Wait until backend is up (max 10 s)
for i in $(seq 1 20); do
    curl -s http://localhost:8000/health >/dev/null 2>&1 && break
    sleep 0.5
done

echo -e "${GREEN}▶  Starting frontend (http://localhost:3000)${RESET}"
echo ""
echo "  ┌──────────────────────────────────────┐"
echo "  │  Triage Form   → http://localhost:3000        │"
echo "  │  Case History  → http://localhost:3000/history│"
echo "  │  Dashboard     → http://localhost:3000/admin  │"
echo "  │  API Docs      → http://localhost:8000/docs   │"
echo "  └──────────────────────────────────────┘"
echo ""
echo "  Press Ctrl+C to stop everything"
echo ""

# ── Frontend (foreground) ─────────────────────────────────────
cd "$ROOT/frontend"
npm run dev

# ── Cleanup when frontend exits ───────────────────────────────
echo ""
echo "Shutting down backend (PID $BACKEND_PID)…"
kill "$BACKEND_PID" 2>/dev/null
pkill -f "uvicorn main:app" 2>/dev/null
echo "Done."
