#!/bin/bash
# Start the test environment (ports 8001 + 5174, no Cloudflare tunnel).
# Does NOT touch the production stack (ports 8000 / 5173).
# Usage: ./start_test.sh

PROJECT="$HOME/projects/3R_assist_basket2"
UVICORN="/Users/fsantos/miniconda3/bin/uvicorn"
NPM="/opt/homebrew/bin/npm"

echo "==> Stopping any existing test processes on ports 8001 and 5174..."
lsof -ti:8001 | xargs kill -9 2>/dev/null
lsof -ti:5174 | xargs kill -9 2>/dev/null
sleep 1

echo "==> Clearing Python bytecode cache..."
find "$PROJECT/backend" -name "*.pyc" -delete 2>/dev/null
find "$PROJECT/backend" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null

echo "==> Opening test backend (port 8001)..."
osascript -e "
tell application \"Terminal\"
    activate
    do script \"echo '=== TEST BACKEND (8001) ===' && cd '$PROJECT/backend' && set -a && source .env.test && set +a && PYTHONDONTWRITEBYTECODE=1 $UVICORN app.main:app --reload --host 127.0.0.1 --port 8001\"
end tell"

echo "==> Waiting for backend to start..."
sleep 3

echo "==> Opening test frontend (port 5174)..."
osascript -e "
tell application \"Terminal\"
    activate
    do script \"echo '=== TEST FRONTEND (5174) ===' && cd '$PROJECT/frontend' && $NPM run dev -- --config vite.config.test.js\"
end tell"

echo ""
echo "Done. Test app is at http://localhost:5174"
echo "Production stack on 8000 / 5173 is untouched."
