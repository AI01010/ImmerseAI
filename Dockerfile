FROM python:3.11-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy dependency files
COPY pyproject.toml .
COPY agent/ ./agent/

# Install dependencies
RUN uv sync --no-dev

# Expose port
ENV PORT=8080
EXPOSE 8080

# Run ADK web server
CMD ["uv", "run", "adk", "web", "--port", "8080", "--host", "0.0.0.0"]
