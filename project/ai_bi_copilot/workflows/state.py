from __future__ import annotations

from typing import Any
from typing import TypedDict
from schemas.kpi_schema import KPIResult


from schemas.report_schema import ExecutiveReport
from schemas.business_analysis_schema import BusinessAnalysisResult



class BIWorkflowState(
    TypedDict,
    total=False
):
    """
    Enterprise AI Business Intelligence Workflow State

    Shared State Across:
    - Analysis Agent
    - KPI Agent
    - Insight Agent
    - Recommendation Agent
    - Forecast Agent
    - Visualization Agent
    - Report Agent
    - Alert Agent
    - Email Agent
    """

    # ==================================================
    # EXECUTION METADATA
    # ==================================================

    execution_id: str

    execution_status: str
    
    chart_paths: list[str]

    chart_metadata: list[dict[str, Any]]

    started_at: str

    completed_at: str

    execution_time_seconds: float

    error: str

    # ==================================================
    # DATASET
    # ==================================================

    dataset_id: int

    dataset_name: str

    file_path: str

    dataframe: Any

    row_count: int

    column_count: int

    uploaded_by: str

    department: str

    business_domain: str

    # ==================================================
    # USER INPUT
    # ==================================================

    question: str

    # ==================================================
    # DATA QUALITY
    # ==================================================

    cleaning_status: str

    quality_score: float

    cleaning_report: dict[str, Any]

    schema: dict[str, Any]

    profile: dict[str, Any]

    # ==================================================
    # ANALYSIS AGENT
    # ==================================================

    analysis_results: dict[str, Any]

    anomaly_analysis: dict[str, Any]

    trend_analysis: dict[str, Any]

    business_readiness: dict[str, Any]

    analysis_status: str

    analysis_completed_at: str

    dataset_profile: dict[str, Any]

    numerical_summary: dict[str, Any]

    correlation_analysis: dict[str, Any]

    distribution_analysis: dict[str, Any]

    outlier_analysis: dict[str, Any]

    top_performers: dict[str, Any]

    business_insights: list[str]

    # ==================================================
    # KPI AGENT
    # ==================================================

    # New enterprise KPI schema
    kpi_result: KPIResult

    # Legacy fields (keep during migration)
    kpis: dict[str, Any]

    kpi_summary: dict[str, Any]

    kpi_status: str

    kpi_generated_at: str

    discovered_kpis: dict[str, list[str]]

    kpi_metrics: dict[str, Any]

    kpi_health: dict[str, Any]

    executive_kpi_summary: list[str]

    kpi_llm_context: str



    # ==================================================
    # INSIGHT AGENT
    # ==================================================

    insights: dict[str, Any]

    risks: list[str]

    opportunities: list[str]

    executive_summary: str

    insight_count: int

    insight_metadata: dict[str, Any]

    insight_status: str

    insight_started_at: str

    insight_completed_at: str

    insight_error: str


    # ==================================================
    # RECOMMENDATION AGENT
    # ==================================================

    recommendations: dict[str, Any]

    recommendation_metadata: dict[str, Any]

    recommendation_status: str

    recommendation_started_at: str

    recommendation_completed_at: str

    recommendation_error: str

    high_priority_actions: list[dict[str, Any]]

    medium_priority_actions: list[dict[str, Any]]

    low_priority_actions: list[dict[str, Any]]

    executive_actions: list[str]

    operational_actions: list[str]

    automation_candidates: list[str]

    recommendation_count: int

    # ==================================================
    # FORECAST AGENT
    # ==================================================

    forecast_results: dict[str, Any]

    forecast_accuracy: float

    forecast_horizon_days: int

    # ==================================================
    # ALERT AGENT
    # ==================================================

    alerts: dict[str, Any]

    critical_alerts: list[dict[str, Any]]

    alert_count: int

    # ==================================================
    # REPORT AGENT
    # ==================================================

    report: str

    structured_report: ExecutiveReport

    report_metadata: dict[str, Any]

    report_status: str

    report_started_at: str

    report_completed_at: str

    report_error: str

    report_html: str

    report_markdown: str

    report_pdf_path: str

    # ==================================================
    # VISUALIZATION AGENT
    # ==================================================

    visualizations: list[dict[str, Any]]

    dashboard_layout: dict[str, Any]

    dashboard_config: dict[str, Any]

    visualization_count: int

    visualization_generated_at: str

    visualization_status: str

    visualization_error: str

    # ==================================================
    # EMAIL AGENT
    # ==================================================

    email_subject: str

    email_body: str

    email_recipients: list[str]

    email_status: str

    # ==================================================
    # CHAT AGENT
    # ==================================================



    chat_response: str

    chat_history: list[dict[str, Any]]

    chat_metadata: dict[str, Any]

    chat_status: str

    chat_started_at: str

    chat_completed_at: str

    chat_error: str

    # ==================================================
    # LLM METRICS
    # ==================================================

    llm_provider: str

    llm_model: str

    llm_tokens_used: int

    llm_prompt_tokens: int

    llm_completion_tokens: int

    llm_cost: float

    # ==================================================
    # AGENT MONITORING
    # ==================================================

    agent_metrics: dict[str, Any]

    agent_errors: list[dict[str, Any]]
    
    #====================================================
    # INGESTION AGENT
    #====================================================
    file_name: str

    file_extension: str

    file_size_mb: float

    missing_values_count: int

    duplicate_rows_count: int

    memory_usage_mb: float

    columns: list[str]

    ingested_at: str

    ingestion_status: str
    
    # ==================================================
    # CLEANING AGENT
    # ==================================================

    cleaning_status: str

    quality_score: float

    cleaning_report: dict[str, Any]

    cleaned_at: str

    duplicate_rows_removed: int

    missing_values_by_column: dict[str, int]

    data_types: dict[str, str]

    cardinality: dict[str, int]

    numeric_profile: dict[str, Any]

    outlier_summary: dict[str, int]
    
    # ==================================================
    # SCHEMA AGENT
    # ==================================================

    schema_status: str

    schema_generated_at: str

    schema_info: dict[str, Any]

    business_entities: dict[str, Any]

    fact_columns: list[str]

    dimension_columns: list[str]

    kpi_candidates: list[str]

    semantic_description: str
    
    #=================================================
    #FORECAST AGENT
    #=================================================
    forecast_results: dict[str, Any]

    forecast_status: str

    forecast_generated_at: str

    growth_rate: float

    forecast_horizon_days: int
    
    # ==================================================
    # ANOMALY AGENT
    # ==================================================

    anomalies: list[dict[str, Any]]

    anomaly_count: int

    anomaly_status: str

    anomaly_generated_at: str
    
    # ==================================================
    # ROOT CAUSE AGENT
    # ==================================================

    root_causes: dict[str, Any]

    root_cause_count: int
    # ==================================================
    # HEALTH SCORE AGENT
    # ==================================================

    health_score: dict[str, Any]

    business_health_score: float

    health_status: str
    
    # ==================================================
    # ACTION PLAN AGENT
    # ==================================================

    action_plan: dict[str, Any]

    action_count: int

    executive_roadmap: list[str]
    
    # ==================================================
    # BUSINESS ANALYST AGENT
    # ==================================================

    business_analysis: BusinessAnalysisResult

    risk_score: float

    opportunity_score: float

    decision_confidence: float

    executive_status: str
    
    # ==================================================
    # EXECUTIVE DASHBOARD AGENT
    # ==================================================

    dashboard: dict[str, Any]

    dashboard_status: dict[str, Any]

    dashboard_generated_at: str
    
    # ==================================================
    # VISUALIZATION RENDERER
    # ==================================================

    visualizations: list[dict[str, Any]]

    chart_paths: list[str]

    dashboard_layout: dict[str, Any]

    chart_metadata: list[dict[str, Any]]

    visualization_output_directory: str