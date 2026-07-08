from __future__ import annotations

from time import perf_counter
from typing import Callable

from loguru import logger
from dataclasses import asdict

from langgraph.graph import (
    END,
    StateGraph
)

from workflows.state import BIWorkflowState

from services.analysis_service import AnalysisService
from services.kpi_service import KPIService
from services.insight_service import InsightService
from services.recommendation_service import RecommendationService
from agents.report_agent import ReportAgent
from services.visualization_service import VisualizationService
from services.forecast_service import ForecastService
from services.anomaly_service import AnomalyService
from schemas.business_analysis_schema import BusinessAnalysisResult
from agents.kpi_agent import KPIAgent
from services.root_cause_service import (
    RootCauseService
)

from services.health_score_service import (
    HealthScoreService
)

from services.alert_service import (
    AlertService
)

from services.action_plan_service import (
    ActionPlanService
)

from agents.business_analysis_agent import (
    BusinessAnalysisAgent
)

from services.executive_dashboard_service import (
    ExecutiveDashboardService
)

from typing import Any, cast



class BIWorkflow:
    """
    Enterprise AI Business Intelligence Workflow

    Validation
        ↓
    Analysis Agent
        ↓
    KPI Agent
        ↓
    Insight Agent
        ↓
    Recommendation Agent
        ↓
    Report Agent
        ↓
    Visualization Agent
        ↓
    END
    """

    analysis_service = AnalysisService()

    kpi_agent = KPIAgent()

    insight_service = InsightService()

    recommendation_service = (
        RecommendationService()
    )

    report_agent = ReportAgent()

    visualization_service = (
        VisualizationService()
    )
    
    forecast_service = (
        ForecastService()
    )

    anomaly_service = (
        AnomalyService()
    )
    
    root_cause_service = (
        RootCauseService()
    )

    health_score_service = (
        HealthScoreService()
    )

    alert_service = (
        AlertService()
    )

    action_plan_service = (
        ActionPlanService()
    )

    business_analysis_agent = (
        BusinessAnalysisAgent()
    )

    executive_dashboard_service = (
        ExecutiveDashboardService()
    )
    # ==================================================
    # COMMON AGENT EXECUTOR
    # ==================================================

    @staticmethod
    def _execute_agent(
        state: BIWorkflowState,
        agent_name: str,
        handler: Callable[
            [BIWorkflowState],
            BIWorkflowState
        ]
    ) -> BIWorkflowState:

        start_time = perf_counter()

        logger.info(
            f"{agent_name} started"
        )

        try:

            updated_state = handler(
                state
            )

            execution_time = round(
                perf_counter()
                - start_time,
                4
            )

            if (
                "agent_metrics"
                not in updated_state
            ):
                updated_state[
                    "agent_metrics"
                ] = {}

            updated_state[
                "agent_metrics"
            ][agent_name] = {
                "status":
                    "SUCCESS",

                "execution_time_seconds":
                    execution_time
            }

            logger.success(
                f"{agent_name} completed "
                f"in {execution_time}s"
            )

            return updated_state

        except Exception as exc:

            logger.exception(
                f"{agent_name} failed"
            )

            if (
                "agent_errors"
                not in state
            ):
                state[
                    "agent_errors"
                ] = []

            state[
                "agent_errors"
            ].append(
                {
                    "agent":
                        agent_name,

                    "error":
                        str(exc)
                }
            )

            raise

    # ==================================================
    # VALIDATION NODE
    # ==================================================

    @staticmethod
    def validation_node(
        state: BIWorkflowState
    ) -> BIWorkflowState:

        dataframe = state.get(
            "dataframe"
        )

        if dataframe is None:

            raise ValueError(
                "Dataframe not found"
            )

        if dataframe.empty:

            raise ValueError(
                "Dataframe is empty"
            )

        logger.info(
            "Workflow validation passed"
        )

        return state

    # ==================================================
    # ANALYSIS NODE
    # ==================================================

    @classmethod
    def analysis_node(
        cls,
        state: BIWorkflowState
    ) -> BIWorkflowState:

        def handler(
            s: BIWorkflowState
        ) -> BIWorkflowState:

            dataframe = s.get(
                "dataframe"
            )

            if dataframe is None:
                raise ValueError(
                    "Dataframe missing"
                )

            s[
                "analysis_results"
            ] = (
                cls.analysis_service
                .analyze_dataset(
                    dataframe
                )
            )

            return s

        return cls._execute_agent(
            state,
            "AnalysisAgent",
            handler
        )

    # ==================================================
    # KPI NODE
    # ==================================================

    @classmethod
    def kpi_node(
        cls,
        state: BIWorkflowState,
    ) -> BIWorkflowState:

        def handler(
            s: BIWorkflowState,
        ) -> BIWorkflowState:

            return cls.kpi_agent.execute(s)

        return cls._execute_agent(
            state,
            "KPIAgent",
            handler,
        )
        
        
    # ==================================================
    # FORECAST NODE
    # ==================================================

    @classmethod
    def forecast_node(
        cls,
        state: BIWorkflowState
    ) -> BIWorkflowState:

        def handler(
            s: BIWorkflowState
        ) -> BIWorkflowState:

            dataframe = s.get(
                "dataframe"
            )

            if dataframe is None:

                raise ValueError(
                    "Dataframe missing"
                )

            s["forecast_results"] = (
                cls.forecast_service
                .generate_forecast(
                    dataframe
                )
            )

            return s

        return cls._execute_agent(
            state,
            "ForecastAgent",
            handler
        )
    # ==================================================
    # ANOMALY NODE
    # ==================================================

    @classmethod
    def anomaly_node(
        cls,
        state: BIWorkflowState
    ) -> BIWorkflowState:

        def handler(
            s: BIWorkflowState
        ) -> BIWorkflowState:

            dataframe = s.get(
                "dataframe"
            )

            if dataframe is None:

                raise ValueError(
                    "Dataframe missing"
                )

            anomaly_payload = (
                cls.anomaly_service
                .detect_anomalies(
                    dataframe
                )
            )

            s["anomalies"] = (
                anomaly_payload
            )

            return s

        return cls._execute_agent(
            state,
            "AnomalyAgent",
            handler
        )
        
    # ==================================================
    # root_cause_service
    # ==================================================   
    @classmethod
    def root_cause_node(
        cls,
        state: BIWorkflowState
    ) -> BIWorkflowState:

        def handler(
            s: BIWorkflowState
        ) -> BIWorkflowState:

            dataframe = s.get(
                "dataframe"
            )

            if dataframe is None:

                raise ValueError(
                    "Dataframe missing"
                )

            s["root_causes"] = (
                cls.root_cause_service
                .analyze(
                    dataframe,
                    s.get("kpis", {}),
                    s.get("anomalies", [])
                )
            )

            return s

        return cls._execute_agent(
            state,
            "RootCauseAgent",
            handler
        )
    # ==================================================
    # HEALTH SCORE NODE
    # ==================================================
    @classmethod
    def health_score_node(
        cls,
        state: BIWorkflowState
    ) -> BIWorkflowState:

        def handler(s):

            s["health_score"] = (

                cls.health_score_service
                .calculate(

                    s.get("kpis", {}),

                    s.get(
                        "forecast_results",
                        {}
                    ),

                    s.get(
                        "anomalies",
                        []
                    ),

                    s.get(
                        "root_causes",
                        {}
                    )
                )
            )

            return s

        return cls._execute_agent(
            state,
            "HealthScoreAgent",
            handler
        )
    # ==================================================
    # Alert Node
    # ==================================================  
    @classmethod
    def alert_node(
        cls,
        state
    ):

        def handler(s):

            s["alerts"] = (

                cls.alert_service
                .generate_alerts(

                    s.get("kpis", {}),

                    s.get(
                        "forecast_results",
                        {}
                    ),

                    s.get(
                        "anomalies",
                        []
                    ),

                    s.get(
                        "health_score",
                        {}
                    )
                )
            )

            return s

        return cls._execute_agent(
            state,
            "AlertAgent",
            handler
        ) 
    # ==================================================
    # Action Plan Node
    # ================================================== 
    @classmethod
    def action_plan_node(
        cls,
        state
    ):

        def handler(s):

            s["action_plan"] = (

                cls.action_plan_service
                .generate_action_plan(

                    s.get(
                        "recommendations",
                        {}
                    ),

                    s.get(
                        "alerts",
                        {}
                    ),

                    s.get(
                        "health_score",
                        {}
                    )
                )
            )

            return s

        return cls._execute_agent(
            state,
            "ActionPlanAgent",
            handler
        )    
        
    # ==================================================
    # Business Analyst Node
    # ==================================================
    @classmethod
    def business_analyst_node(
        cls,
        state
    ):

        def handler(s):

            analysis = cls.business_analysis_agent.analyze(
                s["kpi_result"]
            )

            s["business_analysis"] = analysis

            return s

        return cls._execute_agent(
            state,
            "BusinessAnalystAgent",
            handler
        )
    # ==================================================
    # Executive Dashboard Node
    # ==================================================  
    @classmethod
    def executive_dashboard_node(
        cls,
        state
    ):

        def handler(s):

            dashboard = (

                cls
                .executive_dashboard_service
                .build_dashboard(

                    s.get("kpis", {}),

                    s.get(
                        "forecast_results",
                        {}
                    ),

                    s.get(
                        "anomalies",
                        []
                    ),

                    s.get(
                        "root_causes",
                        {}
                    ),

                    s.get(
                        "health_score",
                        {}
                    ),

                    s.get(
                        "alerts",
                        {}
                    ),

                    s.get(
                        "recommendations",
                        {}
                    ),

                    s.get(
                        "action_plan",
                        {}
                    ),

                    s.get(
                        "executive_summary",
                        {}
                    ),

                    s.get(
                        "business_analysis",
                        {}
                    )
                )
            )

            logger.warning(
                f"DASHBOARD GENERATED: {dashboard}"
            )

            s["dashboard"] = dashboard
            return s

        return cls._execute_agent(
            state,
            "ExecutiveDashboardAgent",
            handler
        )

    # ==================================================
    # INSIGHT NODE
    # ==================================================

    @classmethod
    def insight_node(
        cls,
        state: BIWorkflowState
    ) -> BIWorkflowState:

        def handler(
            s: BIWorkflowState
        ) -> BIWorkflowState:

            kpis = s.get(
                "kpis",
                {}
            )

            analysis_results = s.get(
                "analysis_results",
                {}
            )

            insight_payload = (
                cls.insight_service
                .generate_insights(
                    kpis,
                    analysis_results
                )
            )

            s["insights"] = insight_payload

            s["risks"] = (
                insight_payload.get(
                    "risks",
                    []
                )
            )

            s["opportunities"] = (
                insight_payload.get(
                    "opportunities",
                    []
                )
            )

            s["executive_summary"] = (
                insight_payload.get(
                    "executive_summary",
                    ""
                )
            )

            s["insight_count"] = (
                insight_payload.get(
                    "insight_count",
                    0
                )
            )

            return s

        return cls._execute_agent(
            state,
            "InsightAgent",
            handler
        )
    # ==================================================
    # Recommendation Node
    # ==================================================

    @classmethod
    def recommendation_node(
        cls,
        state: BIWorkflowState
    ) -> BIWorkflowState:

        def handler(
            s: BIWorkflowState
        ) -> BIWorkflowState:

            # ------------------------------------------
            # Get insight list
            # ------------------------------------------

            insight_payload = s.get(
                "insights",
                {}
            )

            if isinstance(insight_payload, dict):

                insight_list = insight_payload.get(
                    "insights",
                    []
                )

            else:

                insight_list = insight_payload

            # ------------------------------------------
            # Generate recommendations
            # ------------------------------------------

            recommendation_payload = (
                cls.recommendation_service.generate_recommendations(
                    insight_list,
                    s.get("kpis", {})
                )
            )

            # ------------------------------------------
            # Store complete payload
            # ------------------------------------------

            s["recommendations"] = recommendation_payload

            # ------------------------------------------
            # Store individual sections
            # ------------------------------------------

            s["high_priority_actions"] = (
                recommendation_payload["high_priority"]
            )

            s["medium_priority_actions"] = (
                recommendation_payload["medium_priority"]
            )

            s["low_priority_actions"] = (
                recommendation_payload["low_priority"]
            )

            s["executive_actions"] = (
                recommendation_payload["executive_actions"]
            )

            s["operational_actions"] = (
                recommendation_payload["operational_actions"]
            )

            s["automation_candidates"] = (
                recommendation_payload["automation_candidates"]
            )

            s["recommendation_count"] = (
                recommendation_payload["recommendation_count"]
            )

            return s

        return cls._execute_agent(
            state,
            "RecommendationAgent",
            handler
        )
    # ==================================================
    # REPORT NODE
    # ==================================================

    @classmethod
    def report_node(
        cls,
        state: BIWorkflowState,
    ) -> BIWorkflowState:

        def handler(
            s: BIWorkflowState,
        ) -> BIWorkflowState:

            return cls.report_agent.run(s)

        return cls._execute_agent(
            state,
            "ReportAgent",
            handler,
        )

    # ==================================================
    # VISUALIZATION NODE
    # ==================================================

    @classmethod
    def visualization_node(
        cls,
        state: BIWorkflowState
    ) -> BIWorkflowState:

        def handler(
            s: BIWorkflowState
        ) -> BIWorkflowState:

            dataframe = s.get(
                "dataframe"
            )

            if dataframe is None:

                raise ValueError(
                    "Dataframe missing"
                )

            result = cast(
                dict[str, Any],
                cls.visualization_service.generate_visualizations(
                    dataframe
                ),
            )
            

            s["visualizations"] = result["visualizations"]

            s["chart_paths"] = result["chart_paths"]
            
            s["chart_metadata"] = result["chart_metadata"]
            
            logger.info(
                f"Generated Charts: {len(result['chart_paths'])}"
            )

            logger.info(
                result["chart_paths"]
            )

            s["chart_metadata"] = result["chart_metadata"]

            return s

        return cls._execute_agent(
            state,
            "VisualizationAgent",
            handler
        )

    # ==================================================
    # BUILD WORKFLOW
    # ==================================================

    @classmethod
    def build(cls):

        workflow = StateGraph(
            BIWorkflowState
        )

        # ==================================
        # REGISTER NODES
        # ==================================

        workflow.add_node(
            "validation",
            cls.validation_node
        )

        workflow.add_node(
            "analysis",
            cls.analysis_node
        )

        workflow.add_node(
            "kpi",
            cls.kpi_node
        )

        workflow.add_node(
            "forecast",
            cls.forecast_node
        )

        workflow.add_node(
            "anomaly",
            cls.anomaly_node
        )

        workflow.add_node(
            "root_cause",
            cls.root_cause_node
        )

        workflow.add_node(
            "health_score",
            cls.health_score_node
        )

        workflow.add_node(
            "alert",
            cls.alert_node
        )

        workflow.add_node(
            "insight",
            cls.insight_node
        )

        workflow.add_node(
            "recommendation",
            cls.recommendation_node
        )

        workflow.add_node(
            "action_plan",
            cls.action_plan_node
        )

        workflow.add_node(
            "business_analyst",
            cls.business_analyst_node
        )

        workflow.add_node(
            "executive_dashboard",
            cls.executive_dashboard_node
        )

        workflow.add_node(
            "report",
            cls.report_node
        )

        workflow.add_node(
            "visualization",
            cls.visualization_node
        )

        # ==================================
        # ENTRY POINT
        # ==================================

        workflow.set_entry_point(
            "validation"
        )

        # ==================================
        # WORKFLOW EDGES
        # ==================================

        workflow.add_edge(
            "validation",
            "analysis"
        )

        workflow.add_edge(
            "analysis",
            "kpi"
        )

        workflow.add_edge(
            "kpi",
            "forecast"
        )

        workflow.add_edge(
            "forecast",
            "anomaly"
        )

        workflow.add_edge(
            "anomaly",
            "root_cause"
        )

        workflow.add_edge(
            "root_cause",
            "health_score"
        )

        workflow.add_edge(
            "health_score",
            "alert"
        )

        workflow.add_edge(
            "alert",
            "insight"
        )

        workflow.add_edge(
            "insight",
            "recommendation"
        )

        workflow.add_edge(
            "recommendation",
            "action_plan"
        )

        workflow.add_edge(
            "action_plan",
            "business_analyst"
        )

        workflow.add_edge(
            "business_analyst",
            "executive_dashboard"
        )

        workflow.add_edge(
            "executive_dashboard",
            "visualization"
        )

        workflow.add_edge(
            "visualization",
            "report"
        )

        workflow.add_edge(
            "report",
            END
        )

        logger.success(
            "BI Workflow compiled successfully"
        )

        return workflow.compile()