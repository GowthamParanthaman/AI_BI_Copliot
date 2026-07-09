'''
from services.email_service import EmailService

service = EmailService()

success = service.send_email(

    recipient="iamgowtham5631@gmail.com",

    subject="AI BI Copilot Test",

    body="""
Hello,

This is a test email from AI BI Copilot.

SMTP service is working successfully.

Regards,
AI BI Copilot
"""
)

print(success)
'''
'''
from services.email_service import EmailService

service = EmailService()

html = """
<html>

<body>

<h1>AI BI Copilot</h1>

<h2>Executive Decision</h2>

<p><b>Decision:</b> EXPAND BUSINESS</p>

<p><b>Confidence:</b> 91%</p>

<p><b>Expected ROI:</b> 18%</p>

</body>

</html>
"""

print(

    service.send_html_email(

        recipient="iamgowtham5631@gmail.com",

        subject="HTML Email Test",

        html_body=html
    )
)

from pathlib import Path

from services.email_service import EmailService

service = EmailService()

success = service.send_attachment(

    recipient="iamgowtham5631@gmail.com",

    subject="Attachment Test",

    body="Testing attachment from AI BI Copilot.",

    attachment_path=Path(
        "storage/uploads/629d2b20-7927-4261-8de5-0a24775c5f89.csv"
    )
)

print(success)


from services.email_service import EmailService

service = EmailService()

success = service.send_email(

    recipient="iamgowtham5631@gmail.com",

    subject="Plain Text Email Test",

    body="""
Hello Gowtham,

This is a plain text email from AI BI Copilot.

EmailService is working correctly.

Regards,
AI BI Copilot
"""
)

print(success)

from services.email_service import EmailService

service = EmailService()

print(service.get_health())

print(service.get_statistics())

service.reset_statistics()

print(service.get_statistics())

from services.email_template_service import EmailTemplateService

service = EmailTemplateService()

print(service.template_directory)

print(service.statistics)''


from services.email_template_service import EmailTemplateService

service = EmailTemplateService()

print(service.list_templates())

print(service.validate_template(
    "executive_report.html"
))

html = service.load_template(
    "executive_report.html"
)

print(type(html))

print(len(html))''


from services.email_template_service import EmailTemplateService

service = EmailTemplateService()

html = service.render(
    "executive_report.html",
    {
        "company_name": "AI BI Copilot",
        "dataset_name": "Sales Dataset",
        "total_revenue": "$1,250,000",
        "generated_at": "2026-06-28"
    }
)

print(html)''''''

from services.email_template_service import EmailTemplateService

service = EmailTemplateService()

context = {
    "company_name": "AI BI Copilot",
    "dataset_name": "Sales Dataset",
    "total_revenue": "$1,250,000",
    "generated_at": "2026-06-28"
}

html = service.render_executive_report(
    context
)

print(html)''


from services.email_template_service import EmailTemplateService

service = EmailTemplateService()

print(service.template_exists("executive_report.html"))

print(service.list_templates())

print(service.get_statistics())

service.clear_cache()

service.reload_template(
    "executive_report.html"
)

print(service.get_statistics())

from agents.email_agent import EmailAgent
from services.email_service import EmailService
from services.email_template_service import EmailTemplateService

agent = EmailAgent(

    email_service=EmailService(),

    template_service=EmailTemplateService()

)

print(agent.statistics)

from agents.email_agent import EmailAgent
from services.email_service import EmailService
from services.email_template_service import EmailTemplateService

agent = EmailAgent(
    EmailService(),
    EmailTemplateService()
)

print(
    agent._build_context(
        dataset_name="Sales",
        total_revenue="$500000"
    )
)

print(
    agent._validate_recipient(
        "iamgowtham5631@gmail.com"
    )
)''

from agents.email_agent import EmailAgent
from services.email_service import EmailService
from services.email_template_service import EmailTemplateService

agent = EmailAgent(
    EmailService(),
    EmailTemplateService()
)

context = {
    "company_name": "AI BI Copilot",
    "dataset_name": "Sales Dashboard",
    "total_revenue": "$2,750,000",
    "generated_at": "2026-06-28"
}

success = agent.send_executive_report(
    recipient="iamgowtham5631@gmail.com",
    subject="Executive Business Report",
    context=context
)

print(success)
print(agent.statistics)''

from workflows.workflow_orchestrator import WorkflowOrchestrator

from agents.email_agent import EmailAgent

from services.email_service import EmailService

from services.email_template_service import EmailTemplateService

workflow = WorkflowOrchestrator(

    email_agent=EmailAgent(

        EmailService(),

        EmailTemplateService()

    )

)

print(workflow.statistics)''

from workflows.workflow_orchestrator import WorkflowOrchestrator

from agents.email_agent import EmailAgent
from services.email_service import EmailService
from services.email_template_service import EmailTemplateService

workflow = WorkflowOrchestrator(
    email_agent=EmailAgent(
        EmailService(),
        EmailTemplateService()
    )
)

workflow._start_workflow()

print(workflow.state)

workflow._finish_workflow()

print(workflow.state)

print(workflow.statistics)''

from workflows.workflow_orchestrator import WorkflowOrchestrator

from agents.email_agent import EmailAgent
from services.email_service import EmailService
from services.email_template_service import EmailTemplateService

workflow = WorkflowOrchestrator(
    email_agent=EmailAgent(
        EmailService(),
        EmailTemplateService()
    )
)

context = {
    "company_name": "AI BI Copilot",
    "dataset_name": "Sales Dataset",
    "total_revenue": "$2,500,000",
    "generated_at": "2026-06-29"
}

success = workflow.run_workflow(
    recipient="iamgowtham5631@gmail.com",
    subject="Executive Business Report",
    context=context
)

print(success)
print(workflow.state)
print(workflow.statistics)''


from agents.business_analysis_agent import BusinessAnalysisAgent

agent = BusinessAnalysisAgent()

print(agent.statistics)'

from agents.business_analysis_agent import BusinessAnalysisAgent

agent = BusinessAnalysisAgent()

kpis = {
    "revenue_growth": 18,
    "profit_margin": 21,
    "customer_satisfaction": 91,
    "customer_churn": 6,
}

print(agent._evaluate_business_health(kpis))''

from agents.business_analysis_agent import BusinessAnalysisAgent

agent = BusinessAnalysisAgent()

kpis = {
    "revenue_growth": 18,
    "profit_margin": 21,
    "customer_satisfaction": 91,
    "customer_churn": 6,
}

print(agent._generate_executive_summary(kpis))''
from agents.business_analysis_agent import BusinessAnalysisAgent

agent = BusinessAnalysisAgent()

kpis = {

    "revenue_growth": 18,

    "profit_margin": 21,

    "customer_satisfaction": 91,

    "customer_churn": 6

}

print(agent._identify_risks(kpis))

print(agent._identify_opportunities(kpis))
''

from agents.business_analysis_agent import BusinessAnalysisAgent

agent = BusinessAnalysisAgent()

kpis = {

    "revenue_growth": 18,

    "profit_margin": 21,

    "customer_satisfaction": 91,

    "customer_churn": 6

}

print(
    agent._generate_recommendations(kpis)
)
''
from agents.business_analysis_agent import BusinessAnalysisAgent

agent = BusinessAnalysisAgent()

kpis = {
    "revenue_growth": 18,
    "profit_margin": 21,
    "customer_satisfaction": 91,
    "customer_churn": 6,
}

result = agent.analyze(kpis)

print(result)''

from datetime import datetime

from schemas.kpi_schema import *

result = KPIResult(

    financial=FinancialKPIs(
        total_revenue=1250000,
        total_profit=250000,
        profit_margin=20,
        revenue_growth=18
    ),

    customer=CustomerKPIs(
        customer_count=4500,
        customer_satisfaction=91,
        customer_churn=6,
        average_order_value=245
    ),

    product=ProductKPIs(
        top_product="Laptop",
        top_category="Electronics",
        total_products=150,
        category_distribution=[]
    ),

    region=RegionKPIs(
        top_region="South",
        total_regions=5
    ),

    health=KPIHealth(
        business_health="GOOD",
        score=85
    ),

    generated_at=datetime.utcnow()
)

print(result)'''

from services.pdf_exporter import PDFExporter

html = """
<h1>AI BI Copilot</h1>

Executive Report

Revenue Growth : 18%

Profit Margin : 27%

Customer Satisfaction : 91%
"""

pdf = PDFExporter()

path = pdf.export(html)

print(path)