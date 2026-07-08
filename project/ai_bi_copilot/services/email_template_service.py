from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from string import Template
from typing import Any

from loguru import logger


# =====================================================
# TEMPLATE EXCEPTIONS
# =====================================================

class TemplateNotFoundError(FileNotFoundError):
    """
    Raised when an HTML template cannot be found.
    """
    pass


class TemplateRenderError(Exception):
    """
    Raised when template rendering fails.
    """
    pass

class TemplateVariableError(Exception):
            """
            Raised when required template variables are missing.
            """
            pass


# =====================================================
# TEMPLATE STATISTICS
# =====================================================

@dataclass(slots=True)
class TemplateStatistics:

    templates_loaded: int = 0

    templates_rendered: int = 0

    cache_hits: int = 0

    cache_misses: int = 0

    render_failures: int = 0


# =====================================================
# EMAIL TEMPLATE SERVICE
# =====================================================

class EmailTemplateService:
    """
    Enterprise Email Template Service.

    Responsibilities
    ----------------
    - Load HTML templates
    - Validate templates
    - Render placeholders
    - Generate executive reports
    - Generate alert emails

    Used By
    -------
    - Email Agent
    - Scheduler
    - Report Agent
    """

    def __init__(self) -> None:

        logger.info(
            "Initializing EmailTemplateService..."
        )

        self.template_directory = Path(
            "storage/email_templates"
        )

        self.statistics = TemplateStatistics()

        self._cache: dict[str, str] = {}

        logger.success(
            "EmailTemplateService initialized."
        )
        
    # =====================================================
    # LOAD TEMPLATE
    # =====================================================

    def load_template(
        self,
        template_name: str
    ) -> str:
        """
        Load an HTML template from disk.
        """

        logger.info(
            f"Loading template: {template_name}"
        )

        try:

            # Return cached template
            if template_name in self._cache:

                self.statistics.cache_hits += 1

                logger.debug(
                    "Template loaded from cache."
                )

                return self._cache[template_name]

            self.statistics.cache_misses += 1

            template_path = (
                self.template_directory /
                template_name
            )

            if not template_path.exists():

                raise TemplateNotFoundError(
                    f"Template '{template_name}' not found."
                )

            html = template_path.read_text(
                encoding="utf-8"
            )

            self._cache[template_name] = html

            self.statistics.templates_loaded += 1

            logger.success(
                f"Loaded template: {template_name}"
            )

            return html

        except Exception:

            logger.exception(
                "Failed to load template."
            )

            raise    
        
    # =====================================================
    # VALIDATE TEMPLATE
    # =====================================================

    def validate_template(
        self,
        template_name: str
    ) -> bool:
        """
        Validate that a template exists.
        """

        try:

            self.load_template(
                template_name
            )

            return True

        except TemplateNotFoundError:

            return False    
        
    # =====================================================
    # LIST TEMPLATES
    # =====================================================

    def list_templates(
        self
    ) -> list[str]:
        """
        Return available HTML templates.
        """

        logger.info(
            "Listing templates."
        )

        return sorted(

            template.name

            for template in

            self.template_directory.glob(
                "*.html"
            )

        )    

        
    # =====================================================
    # RENDER TEMPLATE
    # =====================================================

    def render(
        self,
        template_name: str,
        context: dict[str, Any]
    ) -> str:

        logger.info(
            f"Rendering template: {template_name}"
        )

        try:

            html = self.load_template(
                template_name
            )

            template = Template(html)

            rendered = template.safe_substitute(
                context
            )

            self.statistics.templates_rendered += 1

            logger.success(
                f"Template rendered: {template_name}"
            )

            return rendered

        except Exception as exc:

            self.statistics.render_failures += 1

            logger.exception(
                "Template rendering failed."
            )

            raise TemplateRenderError(
                str(exc)
            ) from exc    

        
            
    # =====================================================
    # EXECUTIVE REPORT
    # =====================================================

    def render_executive_report(
        self,
        context: dict[str, Any]
    ) -> str:
        """
        Render Executive Business Report.
        """

        logger.info(
            "Rendering Executive Report."
        )

        return self.render(
            "executive_report.html",
            context
        )        
    
    # =====================================================
    # FORECAST ALERT
    # =====================================================

    def render_forecast_alert(
        self,
        context: dict[str, Any]
    ) -> str:
        """
        Render Forecast Alert.
        """

        logger.info(
            "Rendering Forecast Alert."
        )

        return self.render(
            "forecast_alert.html",
            context
        )
        
    # =====================================================
    # ANOMALY ALERT
    # =====================================================

    def render_anomaly_alert(
        self,
        context: dict[str, Any]
    ) -> str:
        """
        Render Anomaly Alert.
        """

        logger.info(
            "Rendering Anomaly Alert."
        )

        return self.render(
            "anomaly_alert.html",
            context
        )  
        
    # =====================================================
    # TEMPLATE EXISTS
    # =====================================================

    def template_exists(
        self,
        template_name: str
    ) -> bool:
        """
        Check whether a template exists.
        """

        return (
            self.template_directory /
            template_name
        ).exists()    
        
    # =====================================================
    # CLEAR CACHE
    # =====================================================

    def clear_cache(
        self
    ) -> None:
        """
        Clear template cache.
        """

        logger.info(
            "Clearing template cache."
        )

        self._cache.clear()

        logger.success(
            "Template cache cleared."
        )    
        
    # =====================================================
    # RELOAD TEMPLATE
    # =====================================================

    def reload_template(
        self,
        template_name: str
    ) -> str:
        """
        Reload template from disk.
        """

        logger.info(
            f"Reloading template: {template_name}"
        )

        self._cache.pop(
            template_name,
            None
        )

        return self.load_template(
            template_name
        )    
        
    # =====================================================
    # STATISTICS
    # =====================================================

    def get_statistics(
        self
    ) -> TemplateStatistics:
        """
        Return template statistics.
        """

        return self.statistics    