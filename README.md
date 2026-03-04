# ClipForge AI

**Agentic YouTube Shorts automation platform.** Accept a YouTube URL, run it through an agent pipeline (scout → clip → caption), and produce viral-worthy clip metadata with captions. Built for scalability and local development.

---

## Architecture Overview

```
                    ┌─────────────────────────────────────────────────────────┐
                    │                     ClipForge AI                         │
                    └─────────────────────────────────────────────────────────┘
                                              │
         ┌───────────────────────────────────┼───────────────────────────────────┐
         │                                   │                                   │
         ▼                                   ▼                                   ▼
┌─────────────────┐               ┌─────────────────┐               ┌─────────────────┐
│   React + Vite   │   proxy       │    FastAPI      │   enqueue     │  Background      │
│   Dashboard      │ ────────────► │    Backend      │ ◄──────────── │  Worker         │
│   (port 5173)    │   /api        │   (port 8000)   │   poll        │  (pipeline)     │
└─────────────────┘               └────────┬────────┘               └────────┬────────┘
                                           │                                  │
                                           │  job state                        │  read/write
                                           ▼                                  ▼
                                  ┌─────────────────────────────────────────────────┐
                                  │                    Redis                         │
                                  │   jobs, captions cache, intermediate state       │
                                  └─────────────────────────────────────────────────┘
                                           │
         ┌─────────────────────────────────┼─────────────────────────────────┐
         │                                 │                                 │
         ▼                                 ▼                                 ▼
  ScoutAgent (YouTube)            ClipAgent (LLM)                 CaptionAgent (LLM)
  transcript + metadata            timestamps                       hook, caption, hashtags
         │                                 │                                 │
         └─────────────────────────────────┴─────────────────────────────────┘
                                              │
                                              ▼
                                    FFmpeg (clip_video) — optional
```

- **Frontend:** React + Vite dashboard; polls `/api/jobs` every 5s; create job via YouTube URL.
- **Backend:** FastAPI with job CRUD; Redis for persistence and cache.
- **Worker:** Polls for queued jobs, runs Scout → Clip → Caption agents, updates Redis (retries with exponential backoff).
- **Agents:** Scout (metadata/transcript), Clip (timestamp selection), Caption (LLM hook/caption/hashtags).
- **Services:** YouTube (mock transcript), LLM (OpenAI/Claude abstraction), FFmpeg (subprocess clipping).

---

## Tech Stack

| Layer      | Technology                          |
|-----------|--------------------------------------|
| Frontend  | React 18, Vite 5                     |
| Backend   | FastAPI, Uvicorn                     |
| Worker    | Python (same app, separate process)   |
| Storage   | Redis (jobs, cache)                  |
| LLM       | Abstract (OpenAI / Claude stubs)     |
| Video     | FFmpeg (subprocess)                  |

---

## Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- Redis (local or Docker)
- (Optional) FFmpeg for clipping

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # Edit with Redis and API keys if needed
uvicorn app.main:app --reload
```

API: `http://localhost:8000`  
Docs: `http://localhost:8000/docs`

### Worker (separate terminal)

```bash
cd backend
source venv/bin/activate
python -m app.worker
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Dashboard: `http://localhost:5173` (proxies `/api` to backend).

### Environment Variables

Copy `backend/.env.example` to `backend/.env` and adjust:

| Variable         | Description                | Default   |
|------------------|----------------------------|-----------|
| `REDIS_HOST`     | Redis host                 | localhost |
| `REDIS_PORT`     | Redis port                 | 6379      |
| `REDIS_PASSWORD` | Redis password (optional)  | —         |
| `LLM_PROVIDER`   | `openai` or `claude`       | openai    |
| `OPENAI_API_KEY` | OpenAI API key (optional)  | —         |
| `CLAUDE_API_KEY` | Claude API key (optional)  | —         |

Without LLM keys, the app uses mock clip ideas and captions.

### Troubleshooting: "Failed to fetch"

1. **Backend must be running.** In a terminal: `cd backend && source venv/bin/activate && uvicorn app.main:app --reload`. Then open `http://127.0.0.1:8000` — you should see `{"service":"ClipForge AI","status":"ok"}`.
2. **Redis** must be running for job APIs (e.g. `redis-server` or Docker). If Redis is down, the app may still start but job endpoints will error.
3. If the dashboard still can’t reach the backend, set the API URL explicitly. In `frontend` create `.env` with: `VITE_API_URL=http://127.0.0.1:8000/api`, then restart `npm run dev`.

---

## API

| Method | Endpoint    | Description              |
|--------|-------------|--------------------------|
| POST   | `/api/jobs` | Create job (body: `{ "youtube_url": "..." }`) |
| GET    | `/api/jobs` | List all jobs            |
| GET    | `/api/jobs/{id}` | Get job by ID      |

Job statuses: `queued` → `processing` → `completed` or `failed`.

---

## Future Roadmap

- **Real YouTube transcript** — Integrate `youtube-transcript-api` or official Data API.
- **True Shorts upload** — YouTube Data API v3 upload flow for Shorts.
- **Multi-agent orchestration** — LangGraph or custom DAG for branching/retries.
- **Viral scoring model** — ML or LLM-based scoring for clip selection.
- **Download + FFmpeg** — yt-dlp to fetch video, then clip to local files.

---

## License

MIT.
