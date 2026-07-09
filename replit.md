# AI BI Copilot

An enterprise-grade AI-powered Business Intelligence platform built with FastAPI and LangGraph multi-agent workflows.

## Project Overview

- **Stack:** Python 3.12 · FastAPI · LangGraph · SQLAlchemy · pandas · scikit-learn · ReportLab · Chart.js
- **Architecture:** Multi-agent pipeline (data ingestion → KPI detection → trend analysis → insight generation → recommendations → report export)
- **Entry point:** `project/ai_bi_copilot/main.py`
- **Database:** SQLite (dev) via SQLAlchemy, stored in `project/ai_bi_copilot/database/`
- **Storage:** Uploaded CSVs in `project/ai_bi_copilot/storage/uploads/`, reports in `project/ai_bi_copilot/reports/`

## How to Run

```
cd project/ai_bi_copilot && python3 -m uvicorn main:app --host 0.0.0.0 --port 5000 --reload
```

The workflow **"Start AI BI Copilot"** is already configured and starts automatically.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Enterprise BI Dashboard (HTML) |
| GET | `/health` | Health check |
| GET | `/datasets` | List uploaded datasets |
| POST | `/upload/dataset` | Upload a CSV dataset |
| POST | `/analysis/run` | Run full AI analysis pipeline |
| GET | `/docs` | Swagger UI |

## Dashboard

Full-featured SPA at `/`:
- Dark sidebar navigation (Dashboard, Upload, Analytics, Forecast, Visualizations, Reports, Settings)
- KPI cards with sparklines
- Interactive Chart.js charts (bar, line, doughnut, radar, histogram)
- Business health score ring
- AI insights & recommendations panels
- Sortable/searchable/paginated data table with CSV export
- Drag-and-drop dataset upload
- Dark/light theme toggle (persisted)

## Key Notes

- **No OpenAI key configured** — `POST /analysis/run` will fail at the LangGraph LLM step without `OPENAI_API_KEY` set. Set it as a Replit Secret to enable full AI analysis.
- `dashboard.html` is served as a raw `HTMLResponse` (not via Jinja2Templates) to avoid a Jinja2 3.1.6 LRU cache bug with dict-typed globals in Starlette.
- Static files served from `project/ai_bi_copilot/static/`; chart images served from `project/ai_bi_copilot/reports/charts/`.
- Run the standalone pipeline without a server: `cd project/ai_bi_copilot && python3 generate_report.py`

## User Preferences

- Keep existing project structure — do not restructure or migrate.
- Backend architecture, API schema, and DB schema are fixed; changes go to frontend/pipeline only unless explicitly requested.
