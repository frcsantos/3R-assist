#!/bin/bash
# Start (or restart) the full 3R-assist stack.
# Usage: ./start.sh

PROJECT="$HOME/projects/3R_assist_basket2"
UVICORN="/Users/fsantos/miniconda3/bin/uvicorn"
NPM="/opt/homebrew/bin/npm"

echo "==> Stopping any existing processes on ports 8000 and 5173..."
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:5173 | xargs kill -9 2>/dev/null
sleep 1

echo "==> Restarting Cloudflare tunnel..."
if launchctl kickstart -k "gui/$(id -u)/com.3rassist.cloudflared" 2>/dev/null; then
    echo "    Tunnel restarted."
else
    echo "    Tunnel not loaded — loading it..."
    launchctl load ~/Library/LaunchAgents/com.3rassist.cloudflared.plist 2>/dev/null
fi

echo "==> Restarting Ollama (num_ctx=16384)..."
pkill -x ollama 2>/dev/null
pkill -f llama-server 2>/dev/null
sleep 2
OLLAMA_NUM_CTX=16384 OLLAMA_KEEP_ALIVE=-1 ollama serve > /tmp/ollama.log 2>&1 &
sleep 3

echo "==> Clearing Python bytecode cache..."
find "$PROJECT/backend" -name "*.pyc" -delete 2>/dev/null
find "$PROJECT/backend" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
echo "    Done."

echo "==> Opening backend (port 8000)..."
osascript -e "
tell application \"Terminal\"
    activate
    do script \"echo '=== BACKEND ===' && cd '$PROJECT/backend' && PYTHONDONTWRITEBYTECODE=1 $UVICORN app.main:app --reload --host 127.0.0.1 --port 8000\"
end tell"

echo "==> Opening frontend (port 5173)..."
osascript -e "
tell application \"Terminal\"
    activate
    do script \"echo '=== FRONTEND ===' && cd '$PROJECT/frontend' && $NPM run dev\"
end tell"

echo "==> Waiting for servers to start..."
sleep 4

echo "==> Opening browser..."
open http://localhost:5173

echo ""
echo "Done. App is at http://localhost:5173"
echo "To restart: run ./start.sh again (kills old processes first)."
