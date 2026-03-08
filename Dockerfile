# ─────────────────────────────────────────────
# Stage 1: Build React frontend
# ─────────────────────────────────────────────
FROM node:20-slim AS frontend-builder
WORKDIR /app

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --silent

COPY frontend/ ./
RUN npm run build

# ─────────────────────────────────────────────
# Stage 2: Python backend + serve everything
# ─────────────────────────────────────────────
FROM python:3.11-slim
WORKDIR /app

# Install uv
RUN pip install uv

# Install Python dependencies
COPY pyproject.toml uv.lock ./
COPY agent/ ./agent/
RUN uv sync --no-dev --frozen

# Copy built React app
COPY --from=frontend-builder /app/dist ./static

# Copy server and startup script
COPY server.py .
COPY start.sh .
RUN chmod +x start.sh

ENV PORT=8080
EXPOSE 8080

CMD ["./start.sh"]
