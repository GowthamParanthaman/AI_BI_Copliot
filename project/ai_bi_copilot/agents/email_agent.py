from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from loguru import logger

from services.email_service import EmailService
from services.email_template_service import EmailTemplateService


# =====================================================
# EMAIL AGENT STATISTICS
# =====================================================

@dataclass(slots=True)
class EmailAgentStatistics:
    """
    Runtime statistics for Email Agent.
    """

    reports_sent: int = 0

    alerts_sent: int = 0

    failed_operations: int = 0

    last_execution: datetime | None = None

    last_error: str | None = None


# =====================================================
# EMAIL AGENT HEALTH
# =====================================================

@dataclass(slots=True)
class EmailAgentHealth:
    """
    Email Agent health status.
    """

    status: str

    reports_sent: int

    alerts_sent: int

    failed_operations: int

    last_error: str | None


# =====================================================
# EMAIL AGENT
# =====================================================

class EmailAgent:
    """
    Enterprise Email Agent.

    Responsibilities
    ----------------
    - Orchestrate email workflow
    - Render templates
    - Send executive reports
    - Send business alerts
    - Monitor email operations

    Used By
    -------
    - BI Workflow
    - Scheduler
    - Dashboard
    """

    def __init__(
        self,
        email_service: EmailService,
        template_service: EmailTemplateService,
    ) -> None:
        """
        Initialize Email Agent.
        """

        logger.info(
            "Initializing EmailAgent..."
        )

        self.email_service = email_service

        self.template_service = template_service

        self.statistics = EmailAgentStatistics()

        logger.success(
            "EmailAgent initialized successfully."
        )
        
    # =====================================================
    # VALIDATE RECIPIENT
    # =====================================================

    def _validate_recipient(
        self,
        recipient: str
    ) -> bool:
        """
        Validate recipient email address.
        """

        logger.debug(
            f"Validating recipient: {recipient}"
        )

        return self.email_service._validate_email(
            recipient
        )    
        
    # =====================================================
    # BUILD TEMPLATE CONTEXT
    # =====================================================

    def _build_context(
        self,
        **kwargs: Any
    ) -> dict[str, Any]:
        """
        Build template rendering context.
        """

        logger.debug(
            "Building email template context."
        )

        context = dict(kwargs)

        context.setdefault(
            "generated_at",
            datetime.utcnow().strftime(
                "%Y-%m-%d %H:%M UTC"
            )
        )

        context.setdefault(
            "company_name",
            "AI BI Copilot"
        )

        return context    
    
    # =====================================================
    # LOG SUCCESS
    # =====================================================

    def _log_success(
        self
    ) -> None:
        """
        Record successful email operation.
        """

        self.statistics.reports_sent += 1

        self.statistics.last_execution = datetime.utcnow()

        logger.success(
            "Email Agent completed successfully."
        )
        
    # =====================================================
    # LOG FAILURE
    # =====================================================

    def _log_failure(
        self,
        error: Exception
    ) -> None:
        """
        Record failed email operation.
        """

        self.statistics.failed_operations += 1

        self.statistics.last_execution = datetime.utcnow()

        self.statistics.last_error = str(error)

        logger.exception(
            "Email Agent operation failed."
        )    
        
    # =====================================================
    # SEND EXECUTIVE REPORT
    # =====================================================

    def send_executive_report(
        self,
        recipient: str,
        subject: str,
        context: dict[str, Any]
    ) -> bool:
        """
        Send an executive business report.
        """

        logger.info(
            f"Sending executive report to {recipient}"
        )

        try:

            # Validate recipient
            if not self._validate_recipient(recipient):

                raise ValueError(
                    f"Invalid email address: {recipient}"
                )

            # Build rendering context
            render_context = self._build_context(
                **context
            )

            # Generate HTML
            html = (
                self.template_service
                .render_executive_report(
                    render_context
                )
            )

            # Send email
            success = (
                self.email_service
                .send_html_email(
                    recipient=recipient,
                    subject=subject,
                    html_body=html
                )
            )

            if success:

                self._log_success()

                logger.success(
                    "Executive report sent successfully."
                )

                return True

            raise RuntimeError(
                "EmailService failed to send email."
            )

        except Exception as exc:

            self._log_failure(exc)

            return False    
        