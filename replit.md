# AI BI Copilot

## Project Overview
A FastAPI + LangGraph business intelligence dashboard. Upload CSV datasets, run AI-powered KPI analysis, generate reports, and get insights via chat.

**Stack:** Python 3.13 · FastAPI · LangGraph · SQLite · Chart.js · Loguru

**Entry point:** `project/ai_bi_copilot/main.py`  
**Run command:** `cd project/ai_bi_copilot && python3 -m uvicorn main:app --host 0.0.0.0 --port 5000 --reload`

## Key Architecture
- **Workflow:** 14-node LangGraph pipeline: validation → analysis → kpi → forecast → anomaly → root_cause → health_score → alert → insight → recommendation → action_plan → business_analyst → executive_dashboard → visualization → report
- **HealthScoreService:** Weighted score (quality 30%, forecast 25%, anomaly 20%, revenue 15%, root_cause 10%). Returns `business_health_score`, `status`, `score_breakdown`.
- **Database:** SQLite (`ai_bi.db`) — no setup required
- **Frontend:** Single-page dashboard at `/` — `static/js/app.js` + `templates/dashboard.html`

## Required Secrets
- `OPENAI_API_KEY` — required for AI agents (insights, recommendations, report, business analysis). Without it the pipeline fails at the ReportAgent (step 14). All non-AI steps (KPI, forecast, anomaly, health score) work without it.

## User Preferences
- Do not modify CSS or HTML — only JavaScript and Python backend changes.
- Business Health components must use HealthScoreService exclusively (not KPIService.health).
- Follow CODEX_GUIDE.md rules: no `.get()` on dataclasses, keep type hints, use Loguru.
