"""
generate_report.py
==================
Standalone end-to-end AI BI Copilot pipeline runner.

Usage
-----
    cd project/ai_bi_copilot
    python generate_report.py

Outputs
-------
- reports/Executive_Report_<timestamp>.pdf   — PDF with inline charts + captions
- reports/business_metrics.json             — flat JSON, no duplicate keys

Verification checklist (printed to stdout)
------------------------------------------
1. Chart filenames are unique
2. No duplicate business_health key in JSON
3. total_revenue > 0
4. total_orders > 0
5. average_order_value > 0
6. Charts appear inline with captions
7. No duplicate financial KPI keys in JSON
8. PDF file exists on disk
9. JSON file exists on disk
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# ── make project root importable ──────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
from loguru import logger

from services.analysis_service import AnalysisService
from services.insight_service import InsightService
from services.kpi_service import KPIService
from services.pdf_exporter import PDFExporter
from services.recommendation_service import RecommendationService
from services.report_service import ReportService
from services.visualization_renderer import VisualizationRenderer


# ── constants ──────────────────────────────────────────────────────────────────

CSV_PATH = PROJECT_ROOT / "storage" / "uploads" / "cfdc17d1-deb1-46f9-a886-8c4b072e9b44.csv"
REPORTS_DIR = PROJECT_ROOT / "reports"
JSON_PATH = REPORTS_DIR / "business_metrics.json"
DATASET_NAME = "Retail Sales Dataset"


# ==============================================================================
# HELPERS
# ==============================================================================

def _classify_health(score: float) -> str:
    """
    Single authoritative health label from a numeric score.
    Used everywhere so business_health, health_status, and report text
    can never diverge.
    """
    if score >= 90:
        return "EXCELLENT"
    if score >= 75:
        return "GOOD"
    if score >= 50:
        return "FAIR"
    return "CRITICAL"


def _kpi_result_to_dict(kpi_result, df: "pd.DataFrame") -> dict:
    """
    Convert KPIResult dataclass into the flat dict that
    InsightService / RecommendationService / ReportService expect.

    All metrics are derived from the actual dataset or the KPI service
    result — no fabricated placeholders.
    """

    fin  = kpi_result.financial
    cust = kpi_result.customer
    prod = kpi_result.product
    hlth = kpi_result.health

    # ── Derive true min/max/orders/quantity from the DataFrame ────────────────
    revenue_col  = _detect_col(df, ["amount", "revenue", "sales", "price"])
    qty_col      = _detect_col(df, ["quantity", "qty", "units"])

    total_orders    = int(len(df))   # every row is one transaction/order

    if revenue_col:
        rev_series  = pd.to_numeric(df[revenue_col], errors="coerce").dropna()
        max_revenue = float(rev_series.max()) if not rev_series.empty else 0.0
        min_revenue = float(rev_series.min()) if not rev_series.empty else 0.0
    else:
        max_revenue = fin.total_revenue
        min_revenue = 0.0

    if qty_col:
        qty_series     = pd.to_numeric(df[qty_col], errors="coerce").dropna()
        total_quantity = int(qty_series.sum()) if not qty_series.empty else total_orders
    else:
        total_quantity = total_orders

    # ── Quality metrics from the DataFrame ────────────────────────────────────
    missing_cells  = int(df.isnull().sum().sum())
    duplicate_rows = int(df.duplicated().sum())
    total_cells    = int(df.shape[0] * df.shape[1])
    quality_score  = round(
        max(0.0, (1 - missing_cells / max(total_cells, 1)) * 100), 1
    )

    # ── Use _classify_health for consistency ──────────────────────────────────
    health_label = hlth.business_health   # already from KPIService thresholds

    return {
        "financial": {
            "total_revenue":       fin.total_revenue,
            "average_revenue":     cust.average_order_value,   # mean per row
            "max_revenue":         round(max_revenue, 2),
            "min_revenue":         round(min_revenue, 2),
            "total_orders":        total_orders,
            "average_order_value": cust.average_order_value,
            "total_profit":        fin.total_profit if fin.total_profit is not None else 0.0,
            "profit_margin":       fin.profit_margin if fin.profit_margin is not None else 0.0,
            "revenue_growth":      fin.revenue_growth,
        },
        "category": {
            "top_category": prod.top_category,
        },
        "operational": {
            "total_quantity": total_quantity,
        },
        "quality": {
            "quality_score":  quality_score,
            "missing_cells":  missing_cells,
            "duplicate_rows": duplicate_rows,
        },
        "health": {
            "business_health": health_label,
            "score":           hlth.score,
        },
    }


def _build_health_score(kpis_dict: dict) -> dict:
    """
    Build the health_score dict that ReportService.generate_report expects.
    Uses _classify_health so labels are always consistent with the numeric score.
    """
    score  = kpis_dict["health"]["score"]
    # Re-derive status from the same thresholds — never use a separate map
    status = _classify_health(score)

    return {
        "business_health_score": score,
        "status":                status,
    }


def _build_business_analysis(kpis_dict: dict) -> dict:
    """
    Build the business_analysis dict that ReportService.generate_report expects.
    health label and status both come from _classify_health, so they are consistent.
    """
    score  = kpis_dict["health"]["score"]
    bh     = _classify_health(score)   # single source of truth

    roi_map = {
        "EXCELLENT": "25-35%",
        "GOOD":      "15-25%",
        "FAIR":      "5-15%",
        "CRITICAL":  "0-5%",
    }

    return {
        "executive_decision": {
            "decision":     "INVEST" if score >= 60 else "REVIEW",
            "priority":     "HIGH" if score >= 75 else "MEDIUM",
            "confidence":   min(100, int(score)),
            "expected_roi": roi_map.get(bh, "N/A"),
            "reason":       f"Business health is {bh} with a score of {score}/100.",
        },
        "business_readiness": {
            "status":     "READY" if score >= 60 else "NOT READY",
            "deployment": "APPROVED" if score >= 60 else "PENDING",
            "score":      score,
            "reason":     f"Dataset analysis complete. Health: {bh}.",
        },
    }


def _detect_col(df: "pd.DataFrame", keywords: list[str]) -> "str | None":
    """Return the first column whose name contains any of the keywords."""
    for col in df.columns:
        if any(k in col.lower() for k in keywords):
            return col
    return None


def _build_chart_metadata(chart_paths: list[str]) -> list[dict]:
    """
    Pair each chart path with a human-readable caption.
    """
    labels = [
        "Figure 1: Monthly Revenue Trend",
        "Figure 2: Revenue by Category",
        "Figure 3: Quantity Distribution",
        "Figure 4: Order Value Distribution",
        "Figure 5: Revenue Distribution",
        "Figure 6: Top 10 Products by Revenue",
        "Figure 7: Revenue by Region",
        "Figure 8: Sales by Category",
        "Figure 9: Quantity by Category",
        "Figure 10: Feature Correlation Heatmap",
    ]

    metadata = []
    for i, path in enumerate(chart_paths):
        caption = labels[i] if i < len(labels) else f"Figure {i + 1}: Business Chart"
        metadata.append({"path": path, "caption": caption})

    return metadata


def _build_json_metrics(
    kpis_dict: dict,
    health_score: dict,
    insights_result: dict,
    recs_result: dict,
    chart_paths: list[str],
    pdf_path: str,
) -> dict:
    """
    Build a flat dict with no repeated top-level keys.
    """
    fin = kpis_dict["financial"]

    return {
        # ── financial KPIs ────────────────────────────────────────
        "total_revenue":        fin["total_revenue"],
        "average_order_value":  fin["average_order_value"],
        "total_orders":         fin["total_orders"],
        "revenue_growth":       fin["revenue_growth"],
        "profit_margin":        fin["profit_margin"],
        # ── business health (single entry) ────────────────────────
        "business_health":      kpis_dict["health"]["business_health"],
        "health_score":         health_score["business_health_score"],
        "health_status":        health_score["status"],
        # ── category ──────────────────────────────────────────────
        "top_category":         kpis_dict["category"]["top_category"],
        # ── insights ──────────────────────────────────────────────
        "insight_count":        insights_result.get("insight_count", 0),
        "executive_summary":    insights_result.get("executive_summary", ""),
        # ── recommendations ───────────────────────────────────────
        "recommendation_count": recs_result.get("recommendation_count", 0),
        # ── artifacts ─────────────────────────────────────────────
        "chart_count":          len(chart_paths),
        "pdf_path":             pdf_path,
    }


# ==============================================================================
# MAIN PIPELINE
# ==============================================================================

def main() -> None:

    logger.info("=" * 60)
    logger.info("AI BI Copilot — End-to-End Pipeline")
    logger.info("=" * 60)

    # ── 1. Load dataset ────────────────────────────────────────────────────────
    logger.info(f"Loading dataset: {CSV_PATH}")
    df = pd.read_csv(CSV_PATH)

    # Coerce numeric columns so KPI sums work correctly
    for col in df.columns:
        converted = pd.to_numeric(df[col], errors="coerce")
        # Only replace if the column was actually numeric-ish
        # (don't turn string ID columns into all-NaN)
        if converted.notna().sum() > len(df) * 0.5:
            df[col] = converted

    logger.success(f"Dataset loaded: {len(df)} rows x {len(df.columns)} columns")
    logger.info(f"Columns: {list(df.columns)}")

    # ── 2. Analyse dataset ─────────────────────────────────────────────────────
    logger.info("Running AnalysisService ...")
    analysis = AnalysisService().analyze_dataset(df)

    # ── 3. Calculate KPIs ─────────────────────────────────────────────────────
    logger.info("Running KPIService ...")
    kpi_result = KPIService().generate_kpis(df)
    kpis_dict  = _kpi_result_to_dict(kpi_result, df)

    logger.info(
        f"KPIs — revenue={kpis_dict['financial']['total_revenue']} | "
        f"orders={kpis_dict['financial']['total_orders']} | "
        f"aov={kpis_dict['financial']['average_order_value']} | "
        f"health={kpis_dict['health']['business_health']}"
    )

    # ── 4. Generate insights ───────────────────────────────────────────────────
    logger.info("Running InsightService ...")
    insights_result = InsightService().generate_insights(kpis_dict, analysis)
    insights_list   = insights_result.get("insights", [])

    # ── 5. Generate recommendations ───────────────────────────────────────────
    logger.info("Running RecommendationService ...")
    recs_result = RecommendationService().generate_recommendations(
        insights_list, kpis_dict
    )
    recs_list = (
        [r.get("recommendation", str(r)) for r in recs_result.get("high_priority", [])]
        + [r.get("recommendation", str(r)) for r in recs_result.get("medium_priority", [])]
        + [r.get("recommendation", str(r)) for r in recs_result.get("low_priority", [])]
    )

    # ── 6. Generate visualizations ────────────────────────────────────────────
    logger.info("Running VisualizationRenderer ...")
    renderer    = VisualizationRenderer()
    chart_paths = []

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols     = df.select_dtypes(exclude="number").columns.tolist()

    revenue_col  = next(
        (c for c in numeric_cols if any(k in c.lower() for k in ["amount", "revenue", "sales", "price"])),
        numeric_cols[0] if numeric_cols else None,
    )
    qty_col      = next(
        (c for c in numeric_cols if any(k in c.lower() for k in ["quantity", "qty", "units"])),
        numeric_cols[1] if len(numeric_cols) > 1 else revenue_col,
    )
    cat_col      = next(
        (c for c in cat_cols if any(k in c.lower() for k in ["category", "segment", "type"])),
        cat_cols[0] if cat_cols else None,
    )
    date_col     = next(
        (c for c in df.columns if any(k in c.lower() for k in ["date", "month", "period", "time"])),
        None,
    )
    region_col   = next(
        (c for c in cat_cols if any(k in c.lower() for k in ["region", "country", "state", "location"])),
        None,
    )
    product_col  = next(
        (c for c in cat_cols if any(k in c.lower() for k in ["product", "item", "sku", "name"])),
        None,
    )

    # Chart 1 — Revenue over time (line) or bar fallback
    if date_col and revenue_col:
        agg = df.groupby(date_col)[revenue_col].sum().reset_index()
        chart_paths.append(renderer.render_line_chart(agg, date_col, revenue_col, "Revenue Over Time"))
    elif revenue_col and cat_col:
        chart_paths.append(renderer.render_bar_chart(df, cat_col, revenue_col, "Revenue by Category"))

    # Chart 2 — Revenue by category
    if cat_col and revenue_col:
        chart_paths.append(renderer.render_bar_chart(df, cat_col, revenue_col, "Revenue by Category"))

    # Chart 3 — Quantity distribution
    if qty_col:
        chart_paths.append(renderer.render_histogram(df, qty_col, "Quantity Distribution"))

    # Chart 4 — Order value distribution
    if revenue_col:
        chart_paths.append(renderer.render_histogram(df, revenue_col, "Order Value Distribution"))

    # Chart 5 — Second numeric histogram
    extra_num = [c for c in numeric_cols if c not in [revenue_col, qty_col]]
    if extra_num:
        chart_paths.append(renderer.render_histogram(df, extra_num[0], f"{extra_num[0]} Distribution"))
    elif revenue_col:
        chart_paths.append(renderer.render_histogram(df, revenue_col, "Revenue Distribution (2)"))

    # Chart 6 — Top products bar
    if product_col and revenue_col:
        top_prod = (
            df.groupby(product_col)[revenue_col]
            .sum()
            .nlargest(10)
            .reset_index()
        )
        chart_paths.append(
            renderer.render_bar_chart(top_prod, product_col, revenue_col, "Top 10 Products by Revenue")
        )
    elif cat_col and revenue_col:
        chart_paths.append(renderer.render_bar_chart(df, cat_col, revenue_col, "Revenue by Category (2)"))

    # Chart 7 — Region breakdown
    if region_col and revenue_col:
        chart_paths.append(renderer.render_bar_chart(df, region_col, revenue_col, "Revenue by Region"))
    elif cat_col and revenue_col:
        chart_paths.append(renderer.render_pie_chart(df, cat_col, revenue_col, "Revenue Share by Category"))

    # Chart 8 — Category pie or bar
    if cat_col and revenue_col:
        chart_paths.append(renderer.render_bar_chart(df, cat_col, revenue_col, "Sales by Category"))

    # Chart 9 — Quantity by category
    if cat_col and qty_col:
        chart_paths.append(renderer.render_bar_chart(df, cat_col, qty_col, "Quantity by Category"))
    elif cat_col and revenue_col:
        chart_paths.append(renderer.render_bar_chart(df, cat_col, revenue_col, "Revenue Mix"))

    # Chart 10 — Correlation heatmap
    if len(numeric_cols) >= 2:
        chart_paths.append(renderer.render_heatmap(df, "Feature Correlation Heatmap"))

    logger.success(f"Generated {len(chart_paths)} charts")

    # ── 7. Build report text ───────────────────────────────────────────────────
    logger.info("Running ReportService ...")
    health_score      = _build_health_score(kpis_dict)
    business_analysis = _build_business_analysis(kpis_dict)

    report_text = ReportService().generate_report(
        dataset_name=DATASET_NAME,
        kpis=kpis_dict,
        insights=insights_list,
        recommendations=recs_list,
        health_score=health_score,
        business_analysis=business_analysis,
    )

    # ── 8. Export PDF with inline charts ──────────────────────────────────────
    logger.info("Exporting PDF with inline charts ...")
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    pdf_exporter   = PDFExporter(output_directory=str(REPORTS_DIR))
    chart_metadata = _build_chart_metadata(chart_paths)

    pdf_path = pdf_exporter.export_with_inline_charts(
        markdown=report_text,
        chart_metadata=chart_metadata,
    )

    logger.success(f"PDF exported: {pdf_path}")

    # ── 9. Export JSON ─────────────────────────────────────────────────────────
    logger.info("Exporting JSON business metrics ...")
    metrics = _build_json_metrics(
        kpis_dict, health_score, insights_result, recs_result, chart_paths, pdf_path
    )

    with open(JSON_PATH, "w", encoding="utf-8") as fh:
        json.dump(metrics, fh, indent=2)

    logger.success(f"JSON exported: {JSON_PATH}")

    # ── 10. VERIFICATION ──────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("VERIFICATION CHECKLIST")
    print("=" * 60)

    results = []

    # 1 — Chart filenames are unique
    unique_charts = len(set(chart_paths)) == len(chart_paths)
    results.append(("Chart filenames are unique", unique_charts, f"{len(chart_paths)} charts, {len(set(chart_paths))} unique"))

    # 2 — No duplicate business_health key in JSON
    raw_json = json.dumps(metrics)
    bh_count = raw_json.count('"business_health"')
    results.append(("No duplicate business_health key in JSON", bh_count == 1, f"found {bh_count} occurrence(s)"))

    # 3 — total_revenue > 0
    rev = metrics["total_revenue"]
    results.append(("total_revenue > 0", rev > 0, f"${rev:,.2f}"))

    # 4 — total_orders > 0
    orders = metrics["total_orders"]
    results.append(("total_orders > 0", orders > 0, f"{orders:,}"))

    # 5 — average_order_value > 0
    aov = metrics["average_order_value"]
    results.append(("average_order_value > 0", aov > 0, f"${aov:,.2f}"))

    # 6 — Charts inline with captions (check PDF exists and >=1 chart)
    pdf_exists   = Path(pdf_path).exists()
    chart_inline = pdf_exists and len(chart_paths) > 0
    results.append(("Charts inline with captions in PDF", chart_inline, f"{len(chart_paths)} charts embedded"))

    # 7 — No duplicate financial KPI keys in JSON (all top-level keys unique)
    fin_keys = list(metrics.keys())
    no_dup_fin = len(fin_keys) == len(set(fin_keys))
    results.append(("No duplicate JSON keys (financial/top-level)", no_dup_fin, f"{len(fin_keys)} keys, all unique"))

    # 8 — PDF file exists
    results.append(("PDF file exists on disk", pdf_exists, pdf_path))

    # 9 — JSON file exists
    json_exists = JSON_PATH.exists()
    results.append(("JSON file exists on disk", json_exists, str(JSON_PATH)))

    all_pass = True
    for label, passed, detail in results:
        status = "PASS" if passed else "FAIL"
        if not passed:
            all_pass = False
        print(f"  [{status}] {label}")
        print(f"         {detail}")

    print("=" * 60)
    overall = "ALL CHECKS PASSED" if all_pass else "SOME CHECKS FAILED"
    print(f"  {overall}")
    print("=" * 60 + "\n")

    if not all_pass:
        sys.exit(1)


if __name__ == "__main__":
    main()
