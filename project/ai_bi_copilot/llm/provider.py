from __future__ import annotations

from functools import lru_cache
from typing import Final

from langchain_openai import ChatOpenAI
from loguru import logger

from core.config import settings


class LLMProvider:
    """
    Enterprise LLM Provider

    Responsibilities
    ----------------
    - Centralized LLM initialization
    - Connection reuse
    - Configuration validation
    - Health monitoring
    - Provider abstraction
    - Future multi-provider support

    Supported Providers
    -------------------
    - OpenAI
    - Azure OpenAI (future)
    - Gemini (future)
    - Claude (future)
    """

    PROVIDER_NAME: Final[str] = "OpenAI"

    @staticmethod
    def _validate_configuration() -> None:
        """
        Validate required LLM configuration.
        """

        if not settings.OPENAI_API_KEY.get_secret_value():

            raise ValueError(
                "OPENAI_API_KEY is missing"
            )

        if not settings.OPENAI_MODEL:
            raise ValueError(
                "OPENAI_MODEL is missing"
            )

    @staticmethod
    @lru_cache(maxsize=1)
    def get_model() -> ChatOpenAI:
        """
        Returns cached ChatOpenAI instance.
        """

        LLMProvider._validate_configuration()

        logger.info(
            "Initializing LLM | Provider={} | Model={}",
            LLMProvider.PROVIDER_NAME,
            settings.OPENAI_MODEL
        )

        try:

            return ChatOpenAI(
                model=settings.OPENAI_MODEL,
                api_key=settings.OPENAI_API_KEY,
                temperature=settings.OPENAI_TEMPERATURE,
                max_retries=3,
                timeout=120,
            )

        except Exception as exc:

            logger.exception(
                "Failed to initialize LLM"
            )

            raise RuntimeError(
                f"LLM initialization failed: {exc}"
            ) from exc

    @classmethod
    def validate_connection(cls) -> bool:
        """
        Validate LLM connectivity.
        """

        try:

            llm = cls.get_model()

            response = llm.invoke(
                "Reply with exactly: OK"
            )

            if not response.content:

                raise RuntimeError(
                    "Empty LLM response"
                )

            logger.success(
                "LLM connection validated successfully"
            )

            return True

        except Exception as exc:

            logger.exception(
                "LLM connectivity validation failed"
            )

            raise RuntimeError(
                f"LLM validation failed: {exc}"
            ) from exc

    @classmethod
    def get_provider_info(cls) -> dict[str, str | float]:
        """
        Provider metadata.
        """

        return {
            "provider": cls.PROVIDER_NAME,
            "model": settings.OPENAI_MODEL,
            "temperature": settings.OPENAI_TEMPERATURE,
        }

    @classmethod
    def clear_cache(cls) -> None:
        """
        Clear cached model instance.
        Useful during testing.
        """

        cls.get_model.cache_clear()