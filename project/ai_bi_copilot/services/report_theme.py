from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.styles import ParagraphStyle


class ReportTheme:

    styles = getSampleStyleSheet()

    TITLE = ParagraphStyle(
        "ExecutiveTitle",
        parent=styles["Title"],
        fontSize=26,
        leading=30,
        textColor=colors.HexColor("#0B5CAD"),
        spaceAfter=25,
    )

    HEADING1 = ParagraphStyle(
        "Heading1Blue",
        parent=styles["Heading1"],
        textColor=colors.HexColor("#0B5CAD"),
        spaceBefore=20,
        spaceAfter=10,
    )

    HEADING2 = ParagraphStyle(
        "Heading2Blue",
        parent=styles["Heading2"],
        textColor=colors.HexColor("#1565C0"),
        spaceBefore=12,
        spaceAfter=8,
    )

    BODY = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontSize=11,
        leading=18,
    )

    CAPTION = ParagraphStyle(
        "Caption",
        parent=styles["BodyText"],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#444444"),
        alignment=1,  # centered
        spaceAfter=6,
    )

    FOOTER = ParagraphStyle(
        "Footer",
        parent=styles["BodyText"],
        fontSize=8,
        textColor=colors.grey,
        alignment=1,
    )
