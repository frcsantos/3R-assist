#!/bin/bash
# 7am: kill overnight embedding, restart Ollama on MPS, run throttled daytime embedding.
pkill -f re_embed_pubmed_bge_m3 2>/dev/null
sleep 3

OLLAMA_NUM_CTX=16384 OLLAMA_KEEP_ALIVE=-1 /opt/homebrew/bin/ollama serve > /tmp/ollama.log 2>&1 &

# Wait until Ollama is actually responding before starting re-embedding
echo "Waiting for Ollama..."
for i in $(seq 1 30); do
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "Ollama ready after ${i}s"
        break
    fi
    sleep 2
done

# Extra buffer so the model can load into MPS before we compete for it
sleep 30

cd /Users/fsantos/projects/3R_assist_basket2/backend
/Users/fsantos/miniconda3/bin/python scripts/re_embed_pubmed_bge_m3.py \
    --device mps --batch-size 32 --sleep 3 \
    >> /tmp/re_embed_day.log 2>&1
