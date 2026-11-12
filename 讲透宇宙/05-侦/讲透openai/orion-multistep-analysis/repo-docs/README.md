# Multistep Research & Analysis Agentic Framework — an extensible and general-purpose version of ORION

This repository provides a domain-agnostic, multi-agent workflow for multi-turn, AI-driven research + data analysis over structured datasets stored in SQLite (`.db`) files. It pairs a data analysis agent with a literature-review planning agent and a supervisor reviewer to keep analyses transparent, reproducible, and goal-aligned.

Key parts:
- Backend (FastAPI) for dataset management, run orchestration, and event streaming.
- Frontend (React/Vite) for launching runs and viewing logs/artifacts.
- Agents (Python) for data analysis, literature review planning, and supervision.

> [!WARNING]
> This repository is intended for trusted single-operator/local use only and is not production-hardened. It does not implement inbound authentication or authorization, and analysis runs may trigger host-side Python execution, so any shared or production deployment should add its own auth and execution isolation.

---

## Repository Layout

```
src/research_agent/   Python package (API, orchestration, agents, analysis)
frontend/             React UI (Vite) that talks to the backend
runtime/              Runtime data (datasets, runs, prompts, events)
scripts/              Utility scripts for running/dev smoke tests
requirements.txt      Python dependencies used across the project
tests/                Python tests
```

Inside `src/research_agent/`:
```
backend/              FastAPI app, job manager, storage and routes
agents/               Agent logic (analysis/literature/supervision)
analysis/             Generic analysis & ingestion utilities
supervisor/           Orchestration + review logic
interface/            CLI entrypoints
orchestrator/         Orchestrator shim (imported by the backend)
tools/                Tooling and execution helpers
reporters/            Streaming/persistence reporters
```

---

## Prerequisites

| Component | Requirement |
|-----------|-------------|
| Python    | 3.10 or newer |
| Node.js   | 18+ (for the React frontend) |
| OpenAI    | API key with access to the Responses API (set `OPENAI_API_KEY`) |

Note: The `run_python_code` capability executes Python directly via the local interpreter and is intended only for trusted local use; if you deploy this service beyond a single trusted operator environment, the appropriate authentication and execution isolation should be implemented.

---

## Initial Setup

1) Clone and install Python dependencies
```
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
export OPENAI_API_KEY="sk-..."
export PYTHONPATH="$PWD/src"
```

2) Install frontend dependencies
```
cd frontend
npm install
cd ..
```

Optional: copy the environment template
```
cp .env.example .env
```

---

## Running the Services

Start both backend and frontend (recommended for local development)
```
./scripts/run_dev.sh
```

Run services separately (useful for focused debugging)

Backend API
```
source .venv/bin/activate
export PYTHONPATH="$PWD/src"
uvicorn research_agent.backend.main:app --reload --port 8000
```

Environment variables:
- `OPENAI_API_KEY` (required)
- `OPENAI_BASE_URL` (optional)
- `ORION_DATA_ROOT` (default: `runtime/data`)
- `ORION_RUNS_ROOT` (default: `runtime/runs`)
- `ORION_EVENTS_DB` (default: `runtime/events.db`)
- `ORION_PROMPTS_STORE` (default: `runtime/prompts_store.json`)
- `ORION_MAX_CONCURRENT_RUNS` (default: `1`)
- `ORION_ALLOW_PARALLEL` (default: `false`)
- `ORION_MAX_UPLOAD_BYTES` (default: `104857600`)
- `ORION_MAX_ZIP_MEMBERS` (default: `1000`)
- `ORION_MAX_ZIP_UNCOMPRESSED_BYTES` (default: `524288000`)

Legacy `MRDAA_*` environment variable names are still accepted for backward compatibility.

OpenAPI docs: `http://127.0.0.1:8000/api/docs`.

Frontend
```
cd frontend
npm run dev
# open http://127.0.0.1:3000
```

---

## Scripts

Convenience wrappers live in `scripts/`:

- `scripts/run_dev.sh` starts backend + frontend together and stops both on Ctrl+C.
- `scripts/run_backend.sh` runs the FastAPI server with `PYTHONPATH` set.
- `scripts/run_frontend.sh` starts the Vite dev server.
- `scripts/run_cli.sh` runs the CLI entrypoint (`python -m research_agent.interface.cli`).
- `scripts/backend_smoke.py` runs a lightweight API smoke test against the app instance.

---

## Working With Data

- Datasets: Upload a `.db` via the UI or place it in `runtime/data/`.
- CSV/ZIP import: You can also upload a single `.csv` or a `.zip` containing multiple CSV files. The backend will create a new SQLite `.db` with one table per CSV (table names derived from filenames) using pandas. The new database will then appear in the Datasets list for browsing.
- The backend lists available databases from `runtime/data/` and supports browsing table schemas and previews.
- Runs: Launch a run by selecting a database and providing a goal. Logs stream to the UI and artifacts are written under `runtime/runs/<session-id>/`.

---

## Runtime Artifacts

Runtime output lives under `runtime/` by default:
- `runtime/data/`: user datasets and CSV imports (SQLite databases).
- `runtime/runs/`: per-run transcripts, JSON payloads, and generated artifacts.
- `runtime/events.db`: persistent SQLite log of run metadata.
- `runtime/prompts_store.json`: editable prompt overrides.

---

## Next Steps

- Implement the generic orchestrator with the data-analysis, literature, and supervisor agents.
- Map existing UI flows to the generalized endpoints.

---

## License

This project is licensed under the [Apache License 2.0](LICENSE).
