#!/bin/bash
set -e

echo "[ImmerseAI] Starting ADK api_server on 127.0.0.1:8001..."
uv run adk api_server --port 8001 --host 127.0.0.1 &

echo "[ImmerseAI] Starting web server on 0.0.0.0:${PORT:-8080}..."
exec uv run uvicorn server:app --host 0.0.0.0 --port "${PORT:-8080}"
