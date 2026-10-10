#!/bin/bash
# Midnight: kill daytime embedding + Ollama, run full-speed overnight embedding.
pkill -f re_embed_pubmed_bge_m3 2>/dev/null
sleep 3
pkill -x ollama 2>/dev/null
pkill -f llama-server 2>/dev/null
sleep 5

cd /Users/fsantos/projects/3R_assist_basket2/backend
/Users/fsantos/miniconda3/bin/python scripts/re_embed_pubmed_bge_m3.py \
    --device mps --batch-size 1024 \
    >> /tmp/re_embed_night.log 2>&1
