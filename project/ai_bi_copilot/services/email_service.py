from __future__ import annotations

import mimetypes
import re
import smtplib
import ssl
import threading
import time

from dataclasses import dataclass, field
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path
from typing import Any

from loguru import logger

from core.config import settings


# ==========================================================
# EXCEPTIONS
# ==========================================================


class EmailServiceError(Exception):
    """Base Email Service Exception."""


class EmailConfigurationError(EmailServiceError):
    """Raised when SMTP configuration is invalid."""


class EmailConnectionError(EmailServiceError):
    """Raised when SMTP connection fails."""


class EmailValidationError(EmailServiceError):
    """Raised when email validation fails."""


class EmailDeliveryError(EmailServiceError):
    """Raised when email delivery fails."""


# ==========================================================
# EMAIL STATISTICS
# ==========================================================


@dataclass(slots=True)
class EmailStatistics:
    """
    Runtime statistics for Email Service.
    """

    emails_sent: int = 0

    emails_failed: int = 0

    connection_attempts: int = 0

    successful_connections: int = 0

    failed_connections: int = 0

    attachments_sent: int = 0

    html_emails_sent: int = 0

    plain_text_emails_sent: int = 0

    total_retries: int = 0

    last_sent_at: datetime | None = None

    last_connection_at: datetime | None = None

    last_error: str | None = None


# ==========================================================
# EMAIL HEALTH
# ==========================================================


@dataclass(slots=True)
class EmailHealth:
    """
    Health status of Email Service.
    """

    status: str

    smtp_connected: bool

    emails_sent: int

    emails_failed: int

    successful_connections: int

    failed_connections: int

    last_error: str | None


# ==========================================================
# EMAIL RESPONSE
# ==========================================================


@dataclass(slots=True)
class EmailResponse:
    """
    Standard response returned by EmailService.
    """

    success: bool

    message: str

    recipient: str | None = None

    subject: str | None = None

    timestamp: datetime = field(default_factory=datetime.utcnow)

    error: str | None = None


# ==========================================================
# EMAIL SERVICE
# ==========================================================


class EmailService:
    """
    Enterprise Email Service

    Features
    --------
    - SMTP Connection Management
    - HTML Email Support
    - Attachments
    - Multiple Recipients
    - Retry Mechanism
    - Health Monitoring
    - Runtime Statistics
    - Executive Report Delivery
    - Alert Notifications
    """

    EMAIL_PATTERN = re.compile(
        r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    )

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(self) -> None:
        """
        Initialize Email Service.
        """

        self.settings = settings

        self.server: smtplib.SMTP | None = None

        self.ssl_context = ssl.create_default_context()

        self.connected = False

        self.lock = threading.Lock()

        self.statistics = EmailStatistics()

        logger.info(
            "Initializing Enterprise Email Service..."
        )

        logger.info(
            f"SMTP Host : {self.settings.EMAIL_HOST}"
        )

        logger.info(
            f"SMTP Port : {self.settings.EMAIL_PORT}"
        )

        logger.info(
            f"Sender    : {self.settings.EMAIL_FROM_ADDRESS}"
        )

        logger.success(
            "Enterprise Email Service initialized successfully."
        )

    # =====================================================
    # PRIVATE HELPERS
    # =====================================================

    def _validate_configuration(self) -> bool:
        """
        Validate SMTP configuration.

        Returns
        -------
        bool
            True if configuration is valid.

        Raises
        ------
        EmailConfigurationError
        """

        logger.info(
            "Validating email configuration..."
        )

        required_settings = {

            "EMAIL_HOST":
                self.settings.EMAIL_HOST,

            "EMAIL_PORT":
                self.settings.EMAIL_PORT,

            "EMAIL_USERNAME":
                self.settings.EMAIL_USERNAME,

            "EMAIL_PASSWORD":
                self.settings.EMAIL_PASSWORD,

            "EMAIL_FROM_NAME":
                self.settings.EMAIL_FROM_NAME,

            "EMAIL_FROM_ADDRESS":
                self.settings.EMAIL_FROM_ADDRESS
        }

        missing_settings = []

        for key, value in required_settings.items():

            if value is None:

                missing_settings.append(key)

                continue

            if isinstance(value, str):

                if not value.strip():

                    missing_settings.append(key)

        if missing_settings:

            message = (

                "Missing email configuration: "

                + ", ".join(missing_settings)
            )

            logger.error(message)

            raise EmailConfigurationError(
                message
            )

        if not isinstance(
            self.settings.EMAIL_PORT,
            int
        ):

            raise EmailConfigurationError(
                "EMAIL_PORT must be an integer."
            )

        if self.settings.EMAIL_PORT <= 0:

            raise EmailConfigurationError(
                "EMAIL_PORT must be greater than zero."
            )

        logger.success(
            "Email configuration validated successfully."
        )

        return True

    def _validate_email(
        self,
        email: str
    ) -> bool:
        """
        Validate email address.

        Parameters
        ----------
        email : str

        Returns
        -------
        bool

        Raises
        ------
        EmailValidationError
        """

        if not isinstance(
            email,
            str
        ):

            raise EmailValidationError(
                "Email must be a string."
            )

        email = email.strip()

        if not email:

            raise EmailValidationError(
                "Email address cannot be empty."
            )

        if len(email) > 254:

            raise EmailValidationError(
                "Email address exceeds maximum length."
            )

        if not self.EMAIL_PATTERN.match(email):

            raise EmailValidationError(

                f"Invalid email address: {email}"
            )

        logger.debug(

            f"Validated email: {email}"
        )

        return True

    def _connect(self) -> None:
        """
        Establish SMTP connection.

        Raises
        ------
        EmailConnectionError
        """

        if self.connected and self.server is not None:

            logger.debug(
                "SMTP connection already established."
            )

            return

        self._validate_configuration()

        logger.info(
            "Connecting to SMTP server..."
        )

        self.statistics.connection_attempts += 1

        try:

            server = smtplib.SMTP(

                host=self.settings.EMAIL_HOST,

                port=self.settings.EMAIL_PORT,

                timeout=self.settings.EMAIL_TIMEOUT
            )

            server.ehlo()

            if self.settings.EMAIL_USE_TLS:

                logger.info(
                    "Starting TLS encryption..."
                )

                server.starttls(
                    context=self.ssl_context
                )

                server.ehlo()

            server.login(

                self.settings.EMAIL_USERNAME,

                self.settings.EMAIL_PASSWORD
            )

            self.server = server

            self.connected = True

            self.statistics.successful_connections += 1

            self.statistics.last_connection_at = (
                datetime.utcnow()
            )

            logger.success(
                "SMTP connection established successfully."
            )

        except Exception as exc:

            self.connected = False

            self.server = None

            self.statistics.failed_connections += 1

            self.statistics.last_error = str(exc)

            logger.exception(
                "Failed to connect to SMTP server."
            )

            raise EmailConnectionError(
                str(exc)
            ) from exc

    def _disconnect(self) -> None:
        """
        Close SMTP connection.
        """

        if self.server is None:

            return

        try:

            self.server.quit()

            logger.info(
                "SMTP connection closed."
            )

        except Exception:

            logger.warning(
                "SMTP connection terminated unexpectedly."
            )

        finally:

            self.server = None

            self.connected = False
    
    def verify_connection(self) -> bool:
        """
        Verify SMTP connectivity.

        Returns
        -------
        bool
        """

        logger.info(
            "Verifying SMTP connection..."
        )

        try:

            self._connect()

            logger.success(
                "SMTP verification successful."
            )

            return True

        except EmailConnectionError:

            return False

        finally:

            self._disconnect()        

    def _build_message(
        self,
        recipient: str,
        subject: str,
        body: str,
        html: bool = False
    ) -> EmailMessage:
        """
        Build an email message.

        Parameters
        ----------
        recipient : str
        subject : str
        body : str
        html : bool

        Returns
        -------
        EmailMessage
        """

        self._validate_email(recipient)

        message = EmailMessage()

        message["From"] = (
            f"{self.settings.EMAIL_FROM_NAME} "
            f"<{self.settings.EMAIL_FROM_ADDRESS}>"
        )

        message["To"] = recipient

        message["Subject"] = subject

        if html:

            message.set_content(
                "This email requires an HTML compatible email client."
            )

            message.add_alternative(
                body,
                subtype="html"
            )

        else:

            message.set_content(body)

        return message
    
    
    def _send_message(
        self,
        message: EmailMessage
    ) -> bool:
        """
        Send a prepared EmailMessage.
        """

        try:

            self._connect()

            assert self.server is not None

            self._retry_operation(

                self.server.send_message,

                message
            )

            self.statistics.emails_sent += 1

            self.statistics.last_sent_at = (
                datetime.utcnow()
            )

            logger.success(
                "Email delivered successfully."
            )

            return True

        except Exception as exc:

            self.statistics.emails_failed += 1

            self.statistics.last_error = str(exc)

            logger.exception(
                "Email delivery failed."
            )

            return False

        finally:

            self._disconnect()
        
    def send_html_email(
        self,
        recipient: str,
        subject: str,
        html_body: str
    ) -> bool:
        """
        Send an HTML email.

        Parameters
        ----------
        recipient : str
        subject : str
        html_body : str

        Returns
        -------
        bool
        """

        logger.info(
            f"Sending HTML email to {recipient}"
        )

        try:

            message = self._build_message(

                recipient,

                subject,

                html_body,

                True
            )

            self.statistics.html_emails_sent += 1

            return self._send_message(message)

        except Exception as exc:

            self.statistics.emails_failed += 1

            self.statistics.last_error = str(exc)

            logger.exception(
                "Failed to send HTML email."
            )

            return False

        finally:

            self._disconnect()      
    
    # =====================================================
    # PLAIN TEXT EMAIL
    # =====================================================

    def send_email(
        self,
        recipient: str,
        subject: str,
        body: str
    ) -> bool:
        """
        Send a plain text email.

        Parameters
        ----------
        recipient : str
        subject : str
        body : str

        Returns
        -------
        bool
        """

        logger.info(
            f"Sending email to {recipient}"
        )

        try:

            message = self._build_message(

                recipient=recipient,

                subject=subject,

                body=body,

                html=False
            )

            self.statistics.plain_text_emails_sent += 1

            return self._send_message(message)

        except Exception as exc:

            self.statistics.emails_failed += 1

            self.statistics.last_error = str(exc)

            logger.exception(
                "Failed to send plain text email."
            )

            return False          
    
    def send_attachment(
        self,
        recipient: str,
        subject: str,
        body: str,
        attachment_path: Path
    ) -> bool:
        """
        Send email with attachment.

        Parameters
        ----------
        recipient : str
        subject : str
        body : str
        attachment_path : Path

        Returns
        -------
        bool
        """

        logger.info(
            f"Sending attachment email to {recipient}"
        )

        try:

            if not attachment_path.exists():

                raise FileNotFoundError(

                    f"{attachment_path} does not exist."
                )

            message = self._build_message(

                recipient=recipient,

                subject=subject,

                body=body,

                html=False
            )

            mime_type, _ = mimetypes.guess_type(
                attachment_path
            )

            if mime_type:

                maintype, subtype = (
                    mime_type.split("/", 1)
                )

            else:

                maintype = "application"

                subtype = "octet-stream"

            with open(
                attachment_path,
                "rb"
            ) as file:

                message.add_attachment(

                    file.read(),

                    maintype=maintype,

                    subtype=subtype,

                    filename=attachment_path.name
                )

            self.statistics.attachments_sent += 1

            return self._send_message(message)

        except Exception as exc:

            self.statistics.emails_failed += 1

            self.statistics.last_error = str(exc)

            logger.exception(
                "Failed to send attachment email."
            )

            return False


    # =====================================================
    # RETRY OPERATION
    # =====================================================

    def _retry_operation(
        self,
        operation,
        *args,
        **kwargs
    ):
        """
        Retry a failed SMTP operation.
        """

        last_exception = None

        for attempt in range(
            1,
            self.settings.EMAIL_MAX_RETRIES + 1
        ):

            try:

                return operation(
                    *args,
                    **kwargs
                )

            except Exception as exc:

                last_exception = exc

                self.statistics.total_retries += 1

                logger.warning(

                    f"Retry "

                    f"{attempt}/"

                    f"{self.settings.EMAIL_MAX_RETRIES}"

                    f" failed."
                )

                time.sleep(attempt)

        raise EmailDeliveryError(
            str(last_exception)
        )
        
    def send_multiple(
        self,
        recipients: list[str],
        subject: str,
        body: str
    ) -> bool:
        """
        Send email to multiple recipients.
        """

        logger.info(

            f"Sending email to "

            f"{len(recipients)} recipients."
        )

        success = True

        for recipient in recipients:

            if not self.send_email(

                recipient,

                subject,

                body
            ):

                success = False

        return success    
    
    # =====================================================
    # STATISTICS
    # =====================================================

    def get_statistics(
        self
    ) -> EmailStatistics:
        """
        Return runtime statistics.
        """

        logger.debug(
            "Returning email statistics."
        )

        return self.statistics
    
    # =====================================================
    # HEALTH
    # =====================================================

    def get_health(
        self
    ) -> EmailHealth:
        """
        Return service health.
        """

        logger.debug(
            "Returning email health."
        )

        return EmailHealth(

            status=(
                "HEALTHY"
                if self.connected
                else "DISCONNECTED"
            ),

            smtp_connected=self.connected,

            emails_sent=self.statistics.emails_sent,

            emails_failed=self.statistics.emails_failed,

            successful_connections=self.statistics.successful_connections,

            failed_connections=self.statistics.failed_connections,

            last_error=self.statistics.last_error
        )
        
    # =====================================================
    # RESET STATISTICS
    # =====================================================

    def reset_statistics(
        self
    ) -> None:
        """
        Reset runtime statistics.
        """

        self.statistics = EmailStatistics()

        logger.info(
            "Email statistics reset successfully."
        )    