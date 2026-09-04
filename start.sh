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

echo "==> Checking Ollama..."
if ! pgrep -x ollama > /dev/null; then
    echo "    Starting Ollama in background..."
    ollama serve > /tmp/ollama.log 2>&1 &
    sleep 2
else
    echo "    Ollama already running."
fi

echo "==> Opening backend (port 8000)..."
osascript -e "
tell application \"Terminal\"
    activate
    do script \"echo '=== BACKEND ===' && cd '$PROJECT/backend' && $UVICORN app.main:app --reload --host 127.0.0.1 --port 8000\"
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
