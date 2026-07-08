from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from xml.sax.saxutils import escape

from loguru import logger
from reportlab.lib import colors
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from services.report_theme import ReportTheme


class PDFExporter:
    """
    Enterprise PDF Export Service

    Responsibilities
    ----------------
    - Markdown/HTML text → PDF
    - Automatic file naming
    - Output directory management
    """

    def __init__(
        self,
        output_directory: str = "reports",
    ) -> None:

        self.output_directory = Path(output_directory)

        self.output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    # =====================================================
    # FILENAME GENERATION
    # =====================================================

    def _generate_filename(self) -> str:

        timestamp = datetime.now(UTC).strftime(
            "%Y%m%d_%H%M%S"
        )

        return f"Executive_Report_{timestamp}.pdf"

    # =====================================================
    # TEXT ESCAPING
    # =====================================================

    def _escape_paragraph_text(self, text: str) -> str:

        return escape(text)

    # =====================================================
    # EXPORT
    # =====================================================

    def export(
        self,
        markdown: str,
        chart_paths: list[str] | None = None,
    ) -> str:

        try:

            filename = self._generate_filename()

            output_path = self.output_directory / filename

            story = self._markdown_to_story(markdown)

            if chart_paths:

                story.append(PageBreak())

                story.append(
                    Paragraph(
                        "Business Visualizations",
                        ReportTheme.HEADING1,
                    )
                )

                story.append(Spacer(1, 20))

                chart_added = False

                for chart in chart_paths:

                    logger.info(f"Embedding chart: {chart}")
                    logger.info(f"Exists: {Path(chart).exists()}")

                    if Path(chart).exists():

                        # PageBreak only between charts — never after the
                        # last one, so no trailing blank page is created.
                        if chart_added:
                            story.append(PageBreak())

                        story.append(
                            Image(
                                chart,
                                width=450,
                                height=280,
                            )
                        )

                        chart_added = True

            document = SimpleDocTemplate(str(output_path))

            document.build(
                story,
                onFirstPage=self._draw_footer,
                onLaterPages=self._draw_footer,
            )

            logger.success(f"PDF exported: {output_path}")

            return str(output_path)

        except Exception as exc:

            logger.exception("PDF export failed.")

            raise RuntimeError(
                f"PDF export failed: {exc}"
            ) from exc

    # =====================================================
    # TABLE PARSER
    # =====================================================

    def _parse_markdown_table(
        self,
        lines: list[str],
    ) -> Table:

        rows = []

        for line in lines:

            line = line.strip()

            # Skip separator rows  (| --- | --- |)
            separator = (
                line.replace("|", "")
                    .replace("-", "")
                    .replace(":", "")
                    .strip()
            )

            if not separator:
                continue

            cells = [
                Paragraph(
                    self._escape_paragraph_text(cell.strip()),
                    ReportTheme.BODY,
                )
                for cell in line.split("|")
                if cell.strip()
            ]

            if cells:
                rows.append(cells)

        table = Table(rows)

        table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.HexColor("#0B5CAD"),
                    ),
                    (
                        "TEXTCOLOR",
                        (0, 0),
                        (-1, 0),
                        colors.white,
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.grey,
                    ),
                    (
                        "BACKGROUND",
                        (0, 1),
                        (-1, -1),
                        colors.whitesmoke,
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold",
                    ),
                    (
                        "ALIGN",
                        (0, 0),
                        (-1, -1),
                        "CENTER",
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, 0),
                        10,
                    ),
                ]
            )
        )

        return table

    # =====================================================
    # MARKDOWN → STORY
    # =====================================================

    def _markdown_to_story(
        self,
        markdown: str,
    ) -> list:

        story = []

        # --------------------------------------------------
        # Cover / Header
        # --------------------------------------------------

        story.append(
            Paragraph("AI BI Copilot", ReportTheme.TITLE)
        )

        story.append(Spacer(1, 20))

        story.append(
            Paragraph(
                "Executive Business Intelligence Report",
                ReportTheme.HEADING1,
            )
        )

        story.append(Spacer(1, 12))

        story.append(
            Paragraph(
                datetime.now(UTC).strftime("%d %B %Y"),
                ReportTheme.BODY,
            )
        )

        story.append(Spacer(1, 10))

        story.append(
            Paragraph("Version 1.0.0", ReportTheme.BODY)
        )

        story.append(
            Paragraph(
                "Confidential Executive Report",
                ReportTheme.BODY,
            )
        )

        story.append(Spacer(1, 35))

        # --------------------------------------------------
        # Body — line-by-line markdown parse
        # --------------------------------------------------

        table_buffer: list[str] = []

        for line in markdown.splitlines():

            line = line.strip()

            # ---- TABLE ACCUMULATOR ----
            # Require line to start with | so normal prose containing
            # a pipe character is never misidentified as a table row.
            if line.startswith("|"):
                table_buffer.append(line)
                continue

            # Flush table buffer when a non-table line arrives
            if table_buffer:
                story.append(
                    self._parse_markdown_table(table_buffer)
                )
                story.append(Spacer(1, 6))
                table_buffer.clear()

            # ---- HEADINGS ----
            if line.startswith("# "):
                story.append(Spacer(1, 18))
                story.append(
                    Paragraph(
                        self._escape_paragraph_text(line[2:]),
                        ReportTheme.HEADING1,
                    )
                )

            elif line.startswith("## "):
                story.append(Spacer(1, 15))
                story.append(
                    Paragraph(
                        self._escape_paragraph_text(line[3:]),
                        ReportTheme.HEADING2,
                    )
                )

            # ---- BULLET ----
            elif line.startswith("- "):
                story.append(
                    Paragraph(
                        "&#8226; "
                        + self._escape_paragraph_text(line[2:]),
                        ReportTheme.BODY,
                    )
                )
                story.append(Spacer(1, 5))

            # ---- HORIZONTAL RULE ----
            elif line == "---":
                story.append(Spacer(1, 15))

            # ---- BODY TEXT ----
            elif line:
                story.append(
                    Paragraph(
                        self._escape_paragraph_text(line),
                        ReportTheme.BODY,
                    )
                )

        # Flush any trailing table
        if table_buffer:
            story.append(
                self._parse_markdown_table(table_buffer)
            )
            story.append(Spacer(1, 6))

        return story

    # =====================================================
    # FOOTER
    # =====================================================

    def _draw_footer(
        self,
        canvas,
        document,
    ) -> None:

        canvas.saveState()

        canvas.setFont("Helvetica", 8)

        canvas.drawString(
            40,
            25,
            "AI BI Copilot - Confidential",
        )

        canvas.drawRightString(
            560,
            25,
            "Page " + str(canvas.getPageNumber()),
        )

        canvas.restoreState()
