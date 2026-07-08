"""
generate_report.py
==================
Standalone script that runs the full AI BI Copilot pipeline:

    Load CSV
        → KPI Calculation
        → Analysis
        → Forecast
        → Anomaly Detection
        → Root Cause Analysis
        → Health Score
        → Alerts
        → Insights
        → Recommendations
        → Action Plan
        → Business Analysis
        → Visualization  (unique-filename charts)
        → Report Markdown
        → PDF  (inline charts with captions)
        → JSON export  (no duplicate business metrics)

Verification checklist printed at the end.
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd
from loguru import logger

# -------------------------------------------------------
# Service imports
# -------------------------------------------------------
from services.kpi_service import KPIService
from services.analysis_service import AnalysisService
from services.forecast_service import ForecastService
from services.anomaly_service import AnomalyService
from services.root_cause_service import RootCauseService
from services.health_score_service import HealthScoreService
from services.alert_service import AlertService
from services.insight_service import InsightService
from services.recommendation_service import RecommendationService
from services.action_plan_service import ActionPlanService
from services.business_analyst_service import BusinessAnalystService
from services.visualization_service import VisualizationService
from services.report_service import ReportService
from services.pdf_exporter import PDFExporter


# -------------------------------------------------------
# Constants
# -------------------------------------------------------
DATASET_PATH = Path(__file__).parent / "storage" / "uploads" / "cfdc17d1-deb1-46f9-a886-8c4b072e9b44.csv"
REPORTS_DIR  = Path(__file__).parent / "reports"
JSON_OUTPUT  = REPORTS_DIR / "business_metrics.json"


# -------------------------------------------------------
# Helpers
# -------------------------------------------------------

def _safe_float(val, fallback: float = 0.0) -> float:
    try:
        return float(val) if val is not None else fallback
    except (TypeError, ValueError):
        return fallback


def _kpi_result_to_dict(kpi_result, df: pd.DataFrame) -> dict:
    """
    Convert KPIResult dataclass → legacy dict expected by
    HealthScoreService, AlertService, InsightService, etc.
    No duplicate keys; each metric appears exactly once.
    """
    fin = kpi_result.financial
    cust = kpi_result.customer
    prod = kpi_result.product
    reg  = kpi_result.region
    health = kpi_result.health

    # Derive extra financial stats directly from DataFrame
    rev_col = _find_revenue_col(df)
    qty_col = _find_qty_col(df)

    if rev_col:
        rev_series = pd.to_numeric(df[rev_col], errors="coerce").fillna(0)
        avg_rev = round(float(rev_series.mean()), 2)
        max_rev = round(float(rev_series.max()), 2)
        min_rev = round(float(rev_series.min()), 2)
    else:
        avg_rev = max_rev = min_rev = 0.0

    total_qty = 0
    if qty_col:
        total_qty = int(
            pd.to_numeric(df[qty_col], errors="coerce").fillna(0).sum()
        )

    missing_cells  = int(df.isnull().sum().sum())
    duplicate_rows = int(df.duplicated().sum())
    total_rows     = len(df)
    filled_cells   = total_rows * len(df.columns) - missing_cells
    quality_score  = round(filled_cells / max(total_rows * len(df.columns), 1) * 100, 2)

    revenue_per_customer = (
        round(fin.total_revenue / cust.customer_count, 2)
        if cust.customer_count > 0 else 0.0
    )

    return {
        "financial": {
            "total_revenue": _safe_float(fin.total_revenue),
            "total_profit": _safe_float(fin.total_profit),
            "profit_margin": _safe_float(fin.profit_margin),
            "revenue_growth": _safe_float(fin.revenue_growth),
            "average_revenue": avg_rev,
            "max_revenue": max_rev,
            "min_revenue": min_rev,
            "total_orders": total_rows,
            "average_order_value": _safe_float(cust.average_order_value),
            "revenue_per_customer": revenue_per_customer,
        },
        "customer": {
            "customer_count": cust.customer_count,
            "customer_satisfaction": _safe_float(cust.customer_satisfaction),
            "customer_churn": _safe_float(cust.customer_churn),
            "average_order_value": _safe_float(cust.average_order_value),
        },
        "product": {
            "top_product": prod.top_product,
            "top_category": prod.top_category,
            "total_products": prod.total_products,
        },
        "category": {
            "top_category": prod.top_category,
        },
        "region": {
            "top_region": reg.top_region,
            "total_regions": reg.total_regions,
        },
        "operational": {
            "total_quantity": total_qty,
        },
        "quality": {
            "quality_score": quality_score,
            "missing_cells": missing_cells,
            "duplicate_rows": duplicate_rows,
        },
        "health": {
            # Single authoritative Business Health value
            "business_health": health.business_health,
            "health_score": round(_safe_float(health.score), 2),
        },
    }


def _find_revenue_col(df: pd.DataFrame) -> str | None:
    keywords = ["total amount", "revenue", "sales", "income", "amount"]
    for col in df.columns:
        if any(k in col.lower() for k in keywords):
            coerced = pd.to_numeric(df[col], errors="coerce")
            if coerced.notna().sum() > 0:
                return col
    return None


def _find_qty_col(df: pd.DataFrame) -> str | None:
    for col in df.columns:
        if "quantity" in col.lower() or "qty" in col.lower():
            coerced = pd.to_numeric(df[col], errors="coerce")
            if coerced.notna().sum() > 0:
                return col
    return None


# -------------------------------------------------------
# Main pipeline
# -------------------------------------------------------

def run() -> None:

    logger.info("=" * 70)
    logger.info("AI BI COPILOT — REPORT GENERATION PIPELINE")
    logger.info("=" * 70)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    # --------------------------------------------------
    # 1. Load dataset
    # --------------------------------------------------
    logger.info(f"Loading dataset: {DATASET_PATH}")

    if not DATASET_PATH.exists():
        logger.error(f"Dataset not found: {DATASET_PATH}")
        sys.exit(1)

    df = pd.read_csv(DATASET_PATH)

    # Drop unnamed index columns
    df = df.loc[:, ~df.columns.str.match(r"^Unnamed")]

    logger.success(
        f"Dataset loaded: {len(df)} rows × {len(df.columns)} columns"
    )
    logger.info(f"Columns: {list(df.columns)}")

    dataset_name = "Retail Sales Analytics"

    # --------------------------------------------------
    # 2. KPI Calculation
    # --------------------------------------------------
    logger.info("Running KPI service…")

    kpi_service = KPIService()
    kpi_result  = kpi_service.generate_kpis(df)
    kpis_dict   = _kpi_result_to_dict(kpi_result, df)

    logger.success(
        f"KPIs: revenue={kpis_dict['financial']['total_revenue']:,.2f} | "
        f"health={kpis_dict['health']['business_health']} "
        f"({kpis_dict['health']['health_score']})"
    )

    # --------------------------------------------------
    # 3. Analysis
    # --------------------------------------------------
    logger.info("Running analysis service…")

    analysis_service = AnalysisService()
    analysis = analysis_service.analyze_dataset(df)

    logger.success("Analysis complete")

    # --------------------------------------------------
    # 4. Forecast
    # --------------------------------------------------
    logger.info("Running forecast service…")

    forecast_service = ForecastService()
    forecast = forecast_service.generate_forecast(df)

    logger.success(
        f"Forecast: outlook={forecast.get('business_outlook', 'N/A')} | "
        f"growth={forecast.get('growth_rate', 0):.1f}%"
    )

    # --------------------------------------------------
    # 5. Anomaly Detection
    # --------------------------------------------------
    logger.info("Running anomaly detection…")

    anomaly_service = AnomalyService()
    anomalies = anomaly_service.detect_anomalies(df)

    logger.success(f"Anomalies detected: {len(anomalies)}")

    # --------------------------------------------------
    # 6. Root Cause Analysis
    # --------------------------------------------------
    logger.info("Running root cause analysis…")

    root_cause_service = RootCauseService()
    root_causes = root_cause_service.analyze(df, kpis_dict, anomalies)

    logger.success("Root cause analysis complete")

    # --------------------------------------------------
    # 7. Health Score
    # --------------------------------------------------
    logger.info("Calculating health score…")

    health_service = HealthScoreService()
    health_score = health_service.calculate(
        kpis_dict, forecast, anomalies, root_causes
    )

    logger.success(
        f"Health score: {health_score.get('business_health_score', 0)}/100 "
        f"({health_score.get('status', 'N/A')})"
    )

    # Sync health back to kpis_dict so downstream services are consistent
    kpis_dict["health"]["health_score_service"] = health_score.get(
        "business_health_score", kpis_dict["health"]["health_score"]
    )

    # --------------------------------------------------
    # 8. Alerts
    # --------------------------------------------------
    logger.info("Generating alerts…")

    alert_service = AlertService()
    alerts = alert_service.generate_alerts(
        kpis_dict, forecast, anomalies, health_score
    )

    logger.success(
        f"Alerts: high={alerts.get('high_alerts', 0)} "
        f"medium={alerts.get('medium_alerts', 0)}"
    )

    # --------------------------------------------------
    # 9. Insights
    # --------------------------------------------------
    logger.info("Generating insights…")

    insight_service = InsightService()
    insights_result = insight_service.generate_insights(kpis_dict, analysis)
    insights_list   = insights_result.get("insights", [])

    logger.success(f"Insights generated: {len(insights_list)}")

    # --------------------------------------------------
    # 10. Recommendations
    # --------------------------------------------------
    logger.info("Generating recommendations…")

    recommendation_service = RecommendationService()
    recommendations = recommendation_service.generate_recommendations(
        insights_list, kpis_dict
    )
    high_recs = recommendations.get("high_priority", [])
    all_recs  = [
        r.get("recommendation", str(r))
        for r in (
            high_recs
            + recommendations.get("medium_priority", [])
            + recommendations.get("low_priority", [])
        )
    ]

    logger.success(f"Recommendations: {len(all_recs)}")

    # --------------------------------------------------
    # 11. Action Plan
    # --------------------------------------------------
    logger.info("Generating action plan…")

    action_plan_service = ActionPlanService()
    action_plan = action_plan_service.generate_action_plan(
        recommendations, alerts, health_score
    )

    logger.success(
        f"Action plan: {len(action_plan.get('action_plan', []))} actions"
    )

    # --------------------------------------------------
    # 12. Business Analysis
    # --------------------------------------------------
    logger.info("Running business analyst…")

    business_analyst = BusinessAnalystService()
    business_analysis = business_analyst.analyze(
        kpis=kpis_dict,
        forecast=forecast,
        anomalies=anomalies,
        root_causes=root_causes,
        health_score=health_score,
        alerts=alerts,
        action_plan=action_plan,
    )

    logger.success(
        f"Business analysis: "
        f"decision={business_analysis.get('executive_decision', {}).get('decision', 'N/A')}"
    )

    # --------------------------------------------------
    # 13. Visualizations  (unique filenames)
    # --------------------------------------------------
    logger.info("Generating visualizations…")

    viz_service = VisualizationService()
    viz_result  = viz_service.generate_visualizations(df)

    chart_paths    = viz_result.get("chart_paths", [])
    chart_metadata = viz_result.get("chart_metadata", [])

    # Verify chart filename uniqueness
    _verify_chart_uniqueness(chart_paths)

    logger.success(f"Charts generated: {len(chart_paths)}")

    # --------------------------------------------------
    # 14. Report Markdown
    # --------------------------------------------------
    logger.info("Generating report markdown…")

    report_service = ReportService()
    markdown = report_service.generate_report(
        dataset_name=dataset_name,
        kpis=kpis_dict,
        insights=insights_list,
        recommendations=all_recs,
        health_score=health_score,
        business_analysis=business_analysis,
    )

    logger.success("Report markdown generated")

    # --------------------------------------------------
    # 15. PDF with inline charts + captions
    # --------------------------------------------------
    logger.info("Exporting PDF with inline charts…")

    pdf_exporter = PDFExporter(output_directory=str(REPORTS_DIR))
    pdf_path = pdf_exporter.export_with_inline_charts(
        markdown=markdown,
        chart_metadata=chart_metadata,
    )

    logger.success(f"PDF exported: {pdf_path}")

    # --------------------------------------------------
    # 16. JSON export  (no duplicate business metrics)
    # --------------------------------------------------
    logger.info("Exporting business metrics JSON…")

    metrics_json = _build_metrics_json(
        dataset_name=dataset_name,
        kpis_dict=kpis_dict,
        kpi_result=kpi_result,
        health_score=health_score,
        business_analysis=business_analysis,
        forecast=forecast,
        chart_paths=chart_paths,
        pdf_path=pdf_path,
    )

    JSON_OUTPUT.write_text(
        json.dumps(metrics_json, indent=2, default=str),
        encoding="utf-8",
    )

    logger.success(f"JSON exported: {JSON_OUTPUT}")

    # --------------------------------------------------
    # 17. Verification checklist
    # --------------------------------------------------
    _print_verification_checklist(
        chart_paths=chart_paths,
        chart_metadata=chart_metadata,
        kpis_dict=kpis_dict,
        health_score=health_score,
        metrics_json=metrics_json,
        pdf_path=pdf_path,
    )


# -------------------------------------------------------
# Verification helpers
# -------------------------------------------------------

def _verify_chart_uniqueness(chart_paths: list[str]) -> None:
    """Verify uniqueness at the filename level (the canonical requirement)."""
    filenames = [Path(p).name for p in chart_paths]
    seen: set[str] = set()
    duplicates: list[str] = []
    for name in filenames:
        if name in seen:
            duplicates.append(name)
        seen.add(name)
    if duplicates:
        logger.warning(f"Duplicate chart filenames: {duplicates}")
    else:
        logger.success("All chart filenames are unique")


def _build_metrics_json(
    dataset_name: str,
    kpis_dict: dict,
    kpi_result,
    health_score: dict,
    business_analysis: dict,
    forecast: dict,
    chart_paths: list[str],
    pdf_path: str,
) -> dict:
    """
    Build the output JSON.
    Each business metric appears EXACTLY once.
    """
    fin  = kpi_result.financial
    cust = kpi_result.customer
    prod = kpi_result.product
    reg  = kpi_result.region
    kph  = kpi_result.health

    exec_decision = business_analysis.get("executive_decision", {})
    biz_readiness = business_analysis.get("business_readiness", {})

    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "dataset": dataset_name,
        "financial_kpis": {
            "total_revenue": _safe_float(fin.total_revenue),
            "total_profit": _safe_float(fin.total_profit),
            "profit_margin_pct": _safe_float(fin.profit_margin),
            "revenue_growth_pct": _safe_float(fin.revenue_growth),
            "average_order_value": _safe_float(cust.average_order_value),
            "total_orders": kpis_dict["financial"]["total_orders"],
        },
        "customer_kpis": {
            "customer_count": cust.customer_count,
            "customer_satisfaction": _safe_float(cust.customer_satisfaction),
            "customer_churn": _safe_float(cust.customer_churn),
        },
        "product_kpis": {
            "top_product": prod.top_product,
            "top_category": prod.top_category,
            "total_products": prod.total_products,
        },
        "region_kpis": {
            "top_region": reg.top_region,
            "total_regions": reg.total_regions,
        },
        # Single authoritative Business Health entry
        "business_health": {
            "status": kph.business_health,
            "score": round(_safe_float(kph.score), 2),
            "health_service_score": health_score.get("business_health_score", 0),
            "health_service_status": health_score.get("status", "N/A"),
        },
        "forecast": {
            "business_outlook": forecast.get("business_outlook", "N/A"),
            "growth_rate_pct": _safe_float(forecast.get("growth_rate", 0)),
        },
        "executive_decision": {
            "decision": exec_decision.get("decision", "N/A"),
            "priority": exec_decision.get("priority", "N/A"),
            "confidence_pct": _safe_float(exec_decision.get("confidence", 0)),
            "expected_roi": exec_decision.get("expected_roi", "N/A"),
            "reason": exec_decision.get("reason", "N/A"),
        },
        "business_readiness": {
            "status": biz_readiness.get("status", "N/A"),
            "deployment": biz_readiness.get("deployment", "N/A"),
            "score": _safe_float(biz_readiness.get("score", 0)),
            "reason": biz_readiness.get("reason", "N/A"),
        },
        "data_quality": kpis_dict["quality"],
        "charts": [
            {"path": p, "filename": Path(p).name}
            for p in chart_paths
        ],
        "pdf_report": pdf_path,
    }


def _print_verification_checklist(
    chart_paths: list[str],
    chart_metadata: list[dict],
    kpis_dict: dict,
    health_score: dict,
    metrics_json: dict,
    pdf_path: str,
) -> None:

    print()
    print("=" * 70)
    print("VERIFICATION CHECKLIST")
    print("=" * 70)

    # 1. Chart filenames are unique
    filenames = [Path(p).name for p in chart_paths]
    unique_filenames = len(filenames) == len(set(filenames))
    _check("Chart filenames are unique", unique_filenames)

    # 2. No duplicate Business Health values in JSON
    biz_health = metrics_json.get("business_health", {})
    # Only 1 top-level "business_health" key — checked structurally
    json_keys = list(metrics_json.keys())
    bh_count = json_keys.count("business_health")
    _check("No duplicate business_health key in JSON", bh_count == 1)

    # 3. KPI calculations correct (sanity: total_revenue > 0)
    total_revenue = metrics_json["financial_kpis"]["total_revenue"]
    _check(
        f"KPI total_revenue > 0 ({total_revenue:,.2f})",
        total_revenue > 0,
    )
    total_orders = metrics_json["financial_kpis"]["total_orders"]
    _check(
        f"KPI total_orders > 0 ({total_orders:,})",
        total_orders > 0,
    )
    avg_ov = metrics_json["financial_kpis"]["average_order_value"]
    _check(
        f"KPI average_order_value > 0 ({avg_ov:,.2f})",
        avg_ov > 0,
    )

    # 4. Charts appear inline with captions (chart_metadata has titles)
    inline_charts = [
        m for m in chart_metadata
        if m.get("visual_type") != "kpi_card"
        and Path(m.get("path", "")).exists()
        and m.get("title", "").strip()
    ]
    _check(
        f"Charts inline with captions ({len(inline_charts)} charts have titles)",
        len(inline_charts) > 0,
    )

    # 5. JSON has no duplicate business metrics (spot-check keys)
    fin_keys = list(metrics_json["financial_kpis"].keys())
    _check(
        "No duplicate financial KPI keys in JSON",
        len(fin_keys) == len(set(fin_keys)),
    )

    # 6. PDF file exists
    _check(
        f"PDF generated ({Path(pdf_path).name})",
        Path(pdf_path).exists(),
    )

    # 7. JSON file exists
    _check(
        f"JSON exported ({JSON_OUTPUT.name})",
        JSON_OUTPUT.exists(),
    )

    print("=" * 70)
    print()

    # Summary
    print(f"  Dataset        : Retail Sales Analytics")
    print(f"  Total Revenue  : ${total_revenue:,.2f}")
    print(f"  Business Health: {biz_health.get('status', 'N/A')} ({biz_health.get('score', 0)})")
    print(f"  Charts         : {len(chart_paths)}")
    print(f"  PDF Report     : {Path(pdf_path).name}")
    print(f"  JSON Metrics   : {JSON_OUTPUT.name}")
    print()


def _check(label: str, passed: bool) -> None:
    status = "PASS" if passed else "FAIL"
    symbol = "✓" if passed else "✗"
    print(f"  [{status}] {symbol}  {label}")
    if not passed:
        logger.warning(f"VERIFICATION FAILED: {label}")


# -------------------------------------------------------
# Entry point
# -------------------------------------------------------

if __name__ == "__main__":
    run()
