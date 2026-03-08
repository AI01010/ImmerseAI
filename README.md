# ImmerseAI 🎓

> Multi-agent personalized learning advisor powered by Google ADK, Gemini 2.5 Flash, s(CASP) logic engine, MongoDB Atlas, and React.

## Architecture

```
User Input (goal + skill level) via React Frontend
  ↓
OrchestratorAgent (Gemini 2.5 Flash · Google ADK)
  ↓
ParallelAgent (LearningCrew) — 3 specialists run simultaneously
  ├── ProfileAgent    → MongoDB Atlas (learning history, skill level, gaps)
  ├── CurriculumAgent → YouTube Data API (ranked resources by level)
  └── LogicAgent      → s(CASP) engine (prerequisite checking, sequencing)
  ↓
Synthesized Personalized Roadmap
  ├── Phase-by-phase learning plan
  ├── Curated YouTube resources with links
  ├── Knowledge gap analysis (explainable via s(CASP))
  └── Single next action
```

## Stack

- **Frontend** — React + Vite (`frontend/`)
- **Backend / Orchestration** — Google ADK (`agent/`) + FastAPI Server (`server.py`)
- **LLM Reasoning** — Gemini 2.5 Flash (Vertex AI)
- **Logic Engine** — s(CASP)/Prolog for explainable prerequisite validation
- **Database** — MongoDB Atlas for user profiles & learning history
- **External APIs** — YouTube Data API for curated educational content
- **Deployment** — Google Cloud Run (Dockerized)

## Setup & Running Locally

### 1. Prerequisites and Environment Setup

```bash
# Install backend dependencies via uv
uv sync

# Configure environment variables
cp set_env.sh set_env_local.sh

# Edit set_env_local.sh with your API keys:
# - GOOGLE_CLOUD_PROJECT
# - MONGODB_URI
# - YOUTUBE_API_KEY
# etc.
source set_env_local.sh

# Install frontend dependencies
cd frontend
npm install
cd ..
```

### 2. Running for Development

To work on both the React frontend and the ADK multi-agent backend locally:

**Terminal 1 (ADK Backend API):**
```bash
uv run adk api_server --port 8001 --host 127.0.0.1
```

**Terminal 2 (React Frontend Development Server):**
```bash
cd frontend
npm run dev
```

> If you only want to use the ADK Studio UI for testing agents:
> `uv run adk web`

## Production Deployment (Google Cloud Run)

The application is fully containerized and can be deployed to Google Cloud Run using the provided `deploy.sh` script.

```bash
# Ensure your environment variables are loaded
source set_env_local.sh

# Deploy to Cloud Run
bash deploy.sh
```

This script will:
1. Build the React frontend into static files.
2. Package the Python API and FastAPI static server (`server.py`) using Docker.
3. Push the image to Google Container Registry and deploy it to a Cloud Run service named `immerse-ai`.

## Tracks

- **Dallas AI** — Personalized next steps learning recommendation
- **RIQE** — NLP signal pipeline (content classification + ranking)
- **MLH Best Use of Gemini API**
- **MLH Best Use of MongoDB Atlas**
- **HackAI Data Science/ML Mini Track**
- **MLH Best Use of Google Antigravity**
