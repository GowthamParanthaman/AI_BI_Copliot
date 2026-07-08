from __future__ import annotations

import sys

from loguru import logger

from llm.provider import LLMProvider


class LLMProviderTester:
    """
    Enterprise LLM Provider Test Runner

    Validates:
    - Provider initialization
    - Model loading
    - OpenAI connectivity
    - Response generation
    """

    @staticmethod
    def run() -> None:

        logger.info(
            "=" * 60
        )

        logger.info(
            "Starting LLM Provider Validation"
        )

        logger.info(
            "=" * 60
        )

        try:

            # ==========================================
            # LOAD MODEL
            # ==========================================

            llm = LLMProvider.get_model()

            logger.success(
                f"Model Loaded: "
                f"{type(llm).__name__}"
            )

            # ==========================================
            # TEST INVOCATION
            # ==========================================

            response = llm.invoke(
                "Reply with exactly: OK"
            )

            content = str(
                response.content
            ).strip()

            logger.success(
                f"LLM Response: {content}"
            )

            print("\n")
            print("=" * 60)
            print("LLM PROVIDER TEST PASSED")
            print("=" * 60)
            print(
                f"Model Type : "
                f"{type(llm).__name__}"
            )
            print(
                f"Response   : "
                f"{content}"
            )
            print("=" * 60)

        except Exception as exc:

            logger.exception(
                "LLM Provider Test Failed"
            )

            print("\n")
            print("=" * 60)
            print("LLM PROVIDER TEST FAILED")
            print("=" * 60)
            print(str(exc))
            print("=" * 60)

            sys.exit(1)


def main() -> None:

    LLMProviderTester.run()


if __name__ == "__main__":

    main()