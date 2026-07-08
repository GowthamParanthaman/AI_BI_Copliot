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
    - Markdown/HTML text -> PDF
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
    # EXPORT — charts appended as a separate section
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
    # EXPORT — charts inline with captions
    # =====================================================

    def export_with_inline_charts(
        self,
        markdown: str,
        chart_metadata: list[dict],
    ) -> str:
        """
        Build a PDF where each chart is embedded inline, directly after
        the report narrative, with a centred caption beneath it.

        ``chart_metadata`` is a list of dicts::

            [{"path": "/abs/path/to/chart.png", "caption": "Figure 1: ..."}, ...]

        Duplicate paths are silently skipped so the same chart is never
        embedded twice.
        """

        try:

            filename = self._generate_filename()
            output_path = self.output_directory / filename

            story = self._markdown_to_story(markdown)

            if chart_metadata:

                story.append(PageBreak())

                story.append(
                    Paragraph(
                        "Business Visualizations",
                        ReportTheme.HEADING1,
                    )
                )

                story.append(Spacer(1, 20))

                seen_paths: set[str] = set()
                chart_added = False

                for meta in chart_metadata:

                    chart_path = meta.get("path", "")
                    caption = meta.get("caption", "")

                    if not chart_path or not Path(chart_path).exists():
                        logger.warning(f"Chart not found, skipping: {chart_path}")
                        continue

                    if chart_path in seen_paths:
                        logger.warning(f"Duplicate chart path, skipping: {chart_path}")
                        continue

                    seen_paths.add(chart_path)

                    if chart_added:
                        story.append(PageBreak())

                    story.append(
                        Image(
                            chart_path,
                            width=450,
                            height=280,
                        )
                    )

                    if caption:
                        story.append(
                            Paragraph(
                                self._escape_paragraph_text(caption),
                                ReportTheme.CAPTION,
                            )
                        )

                    chart_added = True

            document = SimpleDocTemplate(str(output_path))

            document.build(
                story,
                onFirstPage=self._draw_footer,
                onLaterPages=self._draw_footer,
            )

            logger.success(f"PDF exported (inline charts): {output_path}")

            return str(output_path)

        except Exception as exc:

            logger.exception("PDF export (inline) failed.")

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
    # MARKDOWN -> STORY
    # =====================================================

    def _markdown_to_story(
        self,
        markdown: str,
    ) -> list:

        story = []

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

        table_buffer: list[str] = []

        for line in markdown.splitlines():

            line = line.strip()

            if line.startswith("|"):
                table_buffer.append(line)
                continue

            if table_buffer:
                story.append(
                    self._parse_markdown_table(table_buffer)
                )
                story.append(Spacer(1, 6))
                table_buffer.clear()

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

            elif line.startswith("- "):
                story.append(
                    Paragraph(
                        "&#8226; "
                        + self._escape_paragraph_text(line[2:]),
                        ReportTheme.BODY,
                    )
                )
                story.append(Spacer(1, 5))

            elif line == "---":
                story.append(Spacer(1, 15))

            elif line:
                story.append(
                    Paragraph(
                        self._escape_paragraph_text(line),
                        ReportTheme.BODY,
                    )
                )

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
