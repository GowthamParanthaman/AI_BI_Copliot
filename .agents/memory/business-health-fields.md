---
name: Business Health field mapping
description: Which JSON fields the frontend uses for Business Health, and why they differ from KPIService.
---

# Business Health field mapping

HealthScoreService returns (at result.health_score):
- business_health_score (float, 0-100)
- status (str: EXCELLENT/HEALTHY/STABLE/AT_RISK/CRITICAL)
- score_breakdown.quality_score / .forecast_score / .anomaly_score / .revenue_score / .root_cause_score (weighted)
- quality_score (raw 0-100, directly available)
- growth_rate, high_anomalies, medium_anomalies, high_impact_causes

KPIService returns (at result.kpis.health): score + business_health (EXCELLENT/GOOD/FAIR/CRITICAL). Different scale, different status labels.

**Why:** Business Health components must be consistent across Health Ring, KPI Card, Radar Chart, and Data Table. Only HealthScoreService provides the 5-component breakdown needed for the radar.

**How to apply:**
- JS always reads result.health_score for any Business Health display
- Radar component scores = score_breakdown.X / weight (quality=0.30, forecast=0.25, anomaly=0.20, revenue=0.15, root_cause=0.10)
- Never use result.kpis.health for Business Health display
- Pipeline requires OPENAI_API_KEY at step 14 (ReportAgent) — without it the pipeline throws and health_score is null in the API response, even though HealthScoreService runs successfully at step 7
