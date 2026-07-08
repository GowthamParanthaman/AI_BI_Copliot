# AI BI Copilot Development Guide

## Architecture

Python 3.12

FastAPI

LangGraph

Dataclasses

ReportLab

SQLite

Loguru

Pydantic v2

---

## Current Migration

The project is migrating from legacy dictionary-based models to dataclass-based schemas.

Old:

DataFrame → dict KPI → dict Business Analysis

New:

DataFrame → KPIResult → BusinessAnalysisResult → ExecutiveReport

Dataclasses are the single source of truth.

---

## Rules

1. Never invent schema fields.
2. Never use `.get()` on dataclasses.
3. Only use attributes defined in schemas.
4. Preserve public APIs unless instructed.
5. Keep Loguru logging.
6. Keep type hints.
7. Return complete files.
8. Do not mix legacy and new models.
9. When migrating a service, remove all legacy dictionary access.
10. If a service depends on another migrated service, update both.

---

## Migration Order

1. KPIService
2. BusinessAnalystService
3. InsightService
4. RecommendationService
5. HealthScoreService
6. AlertService
7. RootCauseService
8. ExecutiveSummaryService
9. ReportService

Never migrate services out of order.