from __future__ import annotations

from workflows.state import BIWorkflowState

from agents.ingestion_agent import IngestionAgent
from agents.cleaning_agent import CleaningAgent
from agents.schema_agent import SchemaAgent
from agents.analysis_agent import AnalysisAgent
from agents.kpi_agent import KPIAgent
from agents.insight_agent import InsightAgent
from agents.recommendation_agent import RecommendationAgent
from agents.report_agent import ReportAgent
from agents.visualization_agent import VisualizationAgent
from agents.chat_agent import ChatAgent


INGESTION_AGENT = IngestionAgent()
CLEANING_AGENT = CleaningAgent()
SCHEMA_AGENT = SchemaAgent()
ANALYSIS_AGENT = AnalysisAgent()
KPI_AGENT = KPIAgent()
INSIGHT_AGENT = InsightAgent()
RECOMMENDATION_AGENT = RecommendationAgent()
REPORT_AGENT = ReportAgent()
VISUALIZATION_AGENT = VisualizationAgent()
CHAT_AGENT = ChatAgent()


def ingestion_node(state: BIWorkflowState) -> BIWorkflowState:
    return INGESTION_AGENT.run(state)

def cleaning_node(state: BIWorkflowState) -> BIWorkflowState:
    return CLEANING_AGENT.run(state)

def schema_node(state: BIWorkflowState) -> BIWorkflowState:
    return SCHEMA_AGENT.run(state)

def analysis_node(state: BIWorkflowState) -> BIWorkflowState:
    return ANALYSIS_AGENT.run(state)

def kpi_node(state: BIWorkflowState) -> BIWorkflowState:
    return KPI_AGENT.run(state)

def insight_node(state: BIWorkflowState) -> BIWorkflowState:
    return INSIGHT_AGENT.run(state)

def recommendation_node(state: BIWorkflowState) -> BIWorkflowState:
    return RECOMMENDATION_AGENT.run(state)

def report_node(state: BIWorkflowState) -> BIWorkflowState:
    return REPORT_AGENT.run(state)

def visualization_node(state: BIWorkflowState) -> BIWorkflowState:
    return VISUALIZATION_AGENT.run(state)

def chat_node(state: BIWorkflowState) -> BIWorkflowState:
    return CHAT_AGENT.run(state)